# ADR-004: Streamlit for Frontend

## Status

**Accepted** - Implemented and in production

## Context

We needed a frontend for the bill splitting application that would allow users to:
1. Upload receipt images
2. Add participants
3. Assign items to people
4. Adjust tax and tip
5. View and share results

Requirements:
- Rapid development (small team, single developer initially)
- Python-based (backend is Python, want to share expertise)
- Good for data-focused applications
- Easy deployment
- Mobile-responsive

## Decision

We chose **Streamlit** as our frontend framework.

## Alternatives Considered

### 1. React + TypeScript

**Pros**:
- Industry standard for web apps
- Large ecosystem
- Excellent performance
- Mobile-friendly
- Component reusability

**Cons**:
- Requires JavaScript/TypeScript expertise
- Build pipeline complexity (webpack, npm, etc.)
- Separate codebase from backend
- More development time
- Need API client layer

**Verdict**: Rejected - Too complex for our timeline and team expertise

### 2. Vue.js

**Pros**:
- Easier learning curve than React
- Good documentation
- Flexible architecture
- Great dev tools

**Cons**:
- Still requires JavaScript expertise
- Separate build process
- Smaller ecosystem than React

**Verdict**: Rejected - Still requires frontend specialization

### 3. Streamlit

**Pros**:
- Pure Python (same language as backend)
- Rapid prototyping (minutes to build UI)
- Built-in widgets (file upload, forms, tables)
- Automatic mobile responsiveness
- Easy deployment (single command)
- Great for data apps
- State management built-in

**Cons**:
- Less flexible than React/Vue
- Harder to customize styling
- Not ideal for complex SPAs
- Page reload on interaction (solved in newer versions)
- Limited component ecosystem

**Verdict**: **Accepted** - Best fit for rapid development with Python

## Consequences

### Positive

1. **Speed**: Built functional UI in hours, not days
2. **Python Only**: No context switching between languages
3. **Data Focus**: Excellent for displaying tables, charts, and forms
4. **State Management**: Built-in session state
5. **Deployment**: Single `streamlit run` command
6. **Iterative**: Easy to add features incrementally
7. **Community**: Growing ecosystem of components

### Negative

1. **Limited Customization**: Hard to achieve pixel-perfect designs
2. **Performance**: Slower than React for complex interactions
3. **SEO**: Not ideal for public-facing pages (no SSR)
4. **URL Structure**: Limited routing capabilities
5. **Component Limitations**: Can't create custom components easily
6. **Testing**: Limited testing framework support

## Implementation Details

### Architecture

```
Streamlit App (Port 8501)
├── Step 0: Upload Receipt
├── Step 1: Add People
├── Step 2: Assign Items
├── Step 3: Tax & Tip
└── Step 4: Results
```

### State Management

```python
# Streamlit session state for persistent data
if 'step' not in st.session_state:
    st.session_state.step = 0

if 'receipt_data' not in st.session_state:
    st.session_state.receipt_data = None

# Navigation between steps
def next_step():
    st.session_state.step += 1
```

### API Integration

```python
import requests

API_URL = "http://localhost:8000"

def upload_receipt(file):
    files = {"file": file}
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post(
        f"{API_URL}/receipts/upload",
        headers=headers,
        files=files
    )
    return response.json()
```

### Mobile Optimization

```python
# Streamlit config for mobile
st.set_page_config(
    page_title="Split Bill",
    page_icon="🧾",
    layout="centered",  # Better for mobile
    initial_sidebar_state="collapsed"
)
```

### Styling

```python
# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)
```

## Deployment

### Local Development

```bash
streamlit run app/src/main.py
```

### Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
EXPOSE 8501
CMD ["streamlit", "run", "app/src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Production Considerations

1. **Authentication**: Use Streamlit-Authenticator or reverse proxy auth
2. **HTTPS**: Terminate SSL at Nginx/Traefik
3. **Scaling**: Run multiple Streamlit instances behind load balancer
4. **Secrets**: Use environment variables, not hardcoded values

## Future Migration Path

If we outgrow Streamlit:

1. **API Already Exists**: Backend is already separate FastAPI
2. **Gradual Migration**: Can replace pages one at a time
3. **React Frontend**: Build React app that calls same API
4. **Hybrid**: Keep Streamlit for admin/internal, React for public

## Performance

- **Page Load**: 1-2 seconds (including Streamlit JS bundle)
- **Interactions**: <500ms for simple operations
- **File Upload**: Depends on image size (1-3 seconds for 2MB)
- **API Calls**: Same as backend (<200ms cached, <2s OCR)

## Related Decisions

- ADR-001: FastAPI as Backend Framework
- ADR-007: Docker for Containerization

## References

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit Components](https://streamlit.io/components)
