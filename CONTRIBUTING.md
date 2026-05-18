# Contributing to VecTrade Examples

Thank you for contributing! This guide will help you submit high-quality examples.

## Adding an Example

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-example`
3. Add your example under the appropriate directory
4. Update the README table
5. Submit a pull request

## Example Guidelines

- **Self-contained** — Each example should run independently
- **Well-commented** — Explain what each section does
- **Error handling** — Show proper error handling patterns
- **Type hints** — Use type annotations for Python examples
- **Strict mode** — Use TypeScript strict mode
- **Dependencies** — Keep external dependencies minimal
- **Environment** — Use environment variables for secrets (never hardcode)

## File Structure

```
python/example_name.py       # Standalone script
typescript/example_name.ts   # Standalone script
use-cases/name/              # Multi-file use case with README
templates/name/              # Starter template with README
```

## Testing

All examples are validated via CI:

```bash
# Python — syntax check
python -m py_compile python/quickstart.py

# TypeScript — type check
npx tsc --noEmit typescript/quickstart.ts
```

## Code Style

- Python: Follow [ruff](https://docs.astral.sh/ruff/) defaults
- TypeScript: Follow project ESLint config
- Use 2 spaces for YAML/JSON, 4 spaces for Python

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add WebSocket streaming example`
- `fix: correct import in portfolio_analysis`
- `docs: update README with new example`
