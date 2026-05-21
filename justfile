# Default: list recipes
default:
    @just --list

# Install virtualenv + pre-commit hooks
install:
    @echo "🚀 Creating virtual environment using uv"
    uv sync
    uv run pre-commit install

# Lint + type check
check:
    @echo "🧹 Linting with ruff"
    uv run ruff check .
    @echo "🎨 Checking format with ruff"
    uv run ruff format --check .
    @echo "🧠 Type-checking with mypy (strict)"
    uv run mypy --strict
    @echo "🧠 Type-checking with pyright (pylance parity)"
    uv run pyright

# Run all pre-commit hooks + lock file consistency (CI parity)
check-all: check
    @echo "🔒 Checking lock file consistency"
    uv lock --locked
    @echo "🪝 Running pre-commit hooks"
    uv run pre-commit run -a

# Format code
fmt:
    @echo "✨ Formatting with ruff"
    uv run ruff format .
    uv run ruff check --fix .

# Run tests + per-module coverage gates
test:
    @echo "🧪 Running pytest"
    uv run python -m pytest --cov --cov-report=term-missing --cov-report=xml
    @echo "📊 Enforcing per-module coverage gates"
    uv run python scripts/check_coverage.py

# Remove build artifacts
clean:
    @echo "🧽 Cleaning build artifacts"
    rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml

# Build wheel + sdist
build: clean
    @echo "📦 Building distribution"
    uvx --from build pyproject-build --installer uv

# Show current project version
version:
    @uv run python -c "from __PKG__ import __version__; print(__version__)"

# Run the CLI
run *ARGS:
    uv run __PROJECT_NAME__ {{ARGS}}

# Serve docs with hot reload at http://127.0.0.1:8000
docs:
    @echo "📖 Serving docs at http://127.0.0.1:8000"
    uv run --group docs mkdocs serve

# Build docs and fail on warnings (CI parity)
docs-test:
    @echo "📖 Building docs (strict)"
    uv run --group docs mkdocs build -s
