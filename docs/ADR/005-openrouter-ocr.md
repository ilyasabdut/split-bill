# ADR-005: OpenRouter for OCR

## Status

**Accepted** - Implemented and in production

## Context

We need to extract structured data from receipt images:
- Item names and prices
- Subtotal, tax, total amounts
- Discounts
- Restaurant/store information

Requirements:
- High accuracy for receipt OCR
- Cost-effective
- No infrastructure to manage (no self-hosted ML models)
- Fast response times
- Python SDK or REST API

## Decision

We chose **OpenRouter** with vision-capable LLMs for OCR.

## Alternatives Considered

### 1. Google Vision API

**Pros**:
- High accuracy
- Well-documented
- Part of Google Cloud ecosystem
- Good for general OCR

**Cons**:
- Pricing can be expensive at scale
- Requires Google Cloud account
- Generic OCR (not specialized for receipts)
- Need to parse raw text into structured data

**Verdict**: Rejected - Expensive and not specialized for receipts

### 2. AWS Textract

**Pros**:
- Specialized for forms and tables
- Good for receipt data
- Part of AWS ecosystem
- Handles structured data well

**Cons**:
- AWS account required
- Pricing per page (can add up)
- Latency can be high
- Complex pricing structure

**Verdict**: Rejected - AWS lock-in and pricing complexity

### 3. Tesseract (Self-hosted)

**Pros**:
- Free and open source
- No API costs
- Complete privacy
- Works offline

**Cons**:
- Lower accuracy than cloud solutions
- Requires preprocessing (image enhancement)
- Not specialized for receipts
- Returns raw text (need custom parsing)
- Infrastructure to manage

**Verdict**: Rejected - Accuracy concerns and infrastructure overhead

### 4. OpenRouter with Vision LLMs

**Pros**:
- Access to multiple vision models (Grok, GPT-4V, etc.)
- Structured JSON output (no parsing needed)
- Understands receipt context
- Competitive pricing
- No infrastructure to manage
- Easy to switch models
- Good accuracy for receipts

**Cons**:
- Dependency on third-party service
- Network latency
- Cost per request (though reasonable)
- Rate limits

**Verdict**: **Accepted** - Best balance of accuracy, cost, and simplicity

## Consequences

### Positive

1. **Structured Output**: LLM returns JSON directly, no parsing needed
2. **Context Awareness**: Understands receipts vs random text
3. **Flexibility**: Can switch between models via config
4. **No Infrastructure**: Fully managed service
5. **Cost Control**: Pay per request, no monthly fees
6. **Accuracy**: Vision LLMs handle various receipt formats well

### Negative

1. **External Dependency**: Service availability affects our app
2. **Latency**: 1-3 seconds per request (acceptable for our use case)
3. **Cost**: ~$0.001-0.01 per receipt depending on model
4. **Rate Limits**: Need to handle throttling
5. **Privacy**: Images sent to external service

## Implementation Details

### Model Selection

**Current Model**: `mistralai/mistral-small-3.2-24b-instruct:free`

**Selection Criteria**:
- Free tier available
- Good receipt accuracy
- Fast response times
- JSON output capability

**Alternative Models**:
- `anthropic/claude-3-opus-20240229` (higher accuracy, more expensive)
- `openai/gpt-4o` (excellent accuracy, higher cost)
- `google/gemini-flash-1.5` (good balance)

### API Integration

```python
import base64
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL_NAME", "mistralai/mistral-small-3.2-24b-instruct:free")

def extract_receipt_data(image_bytes: bytes) -> dict:
    # Convert image to base64
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Construct prompt for structured output
    prompt = """Extract receipt data as JSON with this structure:
    {
        "items": [{"item": "name", "price": 9.99}],
        "subtotal": 29.97,
        "tax": 2.70,
        "total": 32.67,
        "discounts": [{"description": "10% off", "amount": 3.00}]
    }
    """

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://split-bill.app",
            "X-Title": "Split Bill App"
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ]
        }
    )

    # Parse JSON response
    result = response.json()
    return json.loads(result["choices"][0]["message"]["content"])
```

### Caching Strategy

To reduce costs and improve performance:

```python
# Cache OCR results for 30 minutes
@cache_result(ttl=1800)  # 30 minutes
def extract_receipt_data(image_bytes: bytes) -> dict:
    # ... implementation
```

**Cost Impact**:
- Without cache: Every upload costs API call
- With cache: Same receipt = free (within 30 min)
- **Savings**: ~60% reduction in API costs

### Error Handling

```python
def extract_receipt_data(image_bytes: bytes) -> dict:
    try:
        response = requests.post(..., timeout=30)
        response.raise_for_status()

        result = response.json()
        if "error" in result:
            logger.error(f"OpenRouter error: {result['error']}")
            return {"Error": "OCR service error"}

        return parse_receipt_data(result)

    except requests.Timeout:
        logger.error("OpenRouter timeout")
        return {"Error": "OCR processing timeout"}
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return {"Error": "Failed to process receipt"}
```

## Performance

- **Response Time**: 1-3 seconds (model dependent)
- **Accuracy**: 85-95% (depending on receipt quality)
- **Cost**: $0.00 (free tier model currently)
- **Rate Limits**: 20 requests/minute (free tier)

## Cost Analysis

### Free Tier (Current)
- Model: `mistralai/mistral-small-3.2-24b-instruct:free`
- Cost: $0
- Limit: 20 requests/minute
- Status: Sufficient for current usage

### Paid Tier (Future)
If we exceed free limits:
- Model: `anthropic/claude-3-sonnet-20240229`
- Cost: ~$0.003 per receipt
- 1000 receipts/month = ~$3

## Privacy Considerations

1. **Data Sent**: Receipt images contain purchase history
2. **Mitigation**:
   - Use free/open models when possible
   - Don't send user-identifiable info
   - Consider data retention policies
3. **Alternative**: Self-hosted OCR for sensitive deployments

## Future Improvements

- **Model Upgrade**: Switch to Claude 3.5 Sonnet for better accuracy
- **Preprocessing**: Add image enhancement before OCR
- **Validation**: Verify extracted totals match sum of items
- **Feedback Loop**: Track corrections to improve model selection

## Related Decisions

- ADR-002: Redis for Caching (reduces OCR costs)
- ADR-001: FastAPI for backend

## References

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Vision Models Comparison](https://openrouter.ai/models)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/vision)
