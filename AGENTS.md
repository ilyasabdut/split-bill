# AGENTS.md - Agent Coding Guidelines for Split Bill Repository

## Core Commands
- **Install**: `make install` (uv sync)
- **Test**: `make test` (pytest api/tests/) or single test: `uv run pytest api/tests/test_file.py::test_function -v`
- **Lint**: `make lint` (ruff check), auto-fix: `make lint-fix`
- **Format**: `make format` (black), sort imports: `make sort-imports`
- **Type Check**: `make type-check` (mypy api/src/)
- **Quality Gate**: `make check-all` (fast) or `make check-all-with-types` (comprehensive)
- **Run API**: `make run-api` (uvicorn src.main:app)
- **Pre-commit**: `make pre-commit` (runs all hooks)

## Code Style Guidelines
- **Line Length**: 88 characters (Black formatter)
- **Imports**: Sorted with isort (black profile), group: stdlib → third-party → local
- **Types**: Use type hints for all parameters/returns, prefer `Optional[T]` over `Union[T, None]`
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Docstrings**: Use """ for module/function docstrings, describe params and returns
- **Error Handling**: Use FastAPI HTTPException, proper status codes, log errors with logger
- **Async**: Use async/await for I/O operations, proper exception handling in try/except blocks
- **Architecture**: Single API entry (src/main.py), modular routers, dependency injection with Depends

## Quality Standards
- All code must pass `make check-all` before commit
- Pre-commit hooks enforce: trailing-whitespace, end-of-file-fixer, black, isort, ruff
- Tests required for new features, maintain >80% coverage
- Environment variables for configuration, no hardcoded secrets
- Security: API key auth, rate limiting, input validation, security headers enabled
