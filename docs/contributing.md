# Contributing to Hydraulics

Thank you for considering contributing to Hydraulics! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Hydraulics.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it and install dependencies:
   ```bash
   # Windows
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

   # Linux/Mac
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
5. Install the package in development mode: `pip install -e .`

## Development Workflow

### Branch Strategy

- `main`: Production-ready code (protected)
- `develop`: Integration branch for features
- `feature/description`: New features
- `bugfix/description`: Bug fixes
- `release/vX.Y.Z`: Release preparation

### Creating a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-new-feature
```

### Making Changes

1. Write your code following the style guidelines below
2. Add tests for new functionality
3. Run tests locally: `pytest tests/`
4. Run the smoke test: `python tests/integration/test_smoke.py`
5. Format code: `black src/` (optional but recommended)
6. Check linting: `flake8 src/` (optional)

### Commit Message Format

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(core): add Hazen-Williams equation support
fix(calculators): correct Reynolds number calculation for edge case
docs(readme): add installation instructions for macOS
```

### Submitting a Pull Request

1. Push your branch: `git push origin feature/my-new-feature`
2. Create a Pull Request to the `develop` branch
3. Fill out the PR template
4. Wait for review and address any feedback
5. Once approved, your PR will be merged

## Code Style Guidelines

### Python Style (PEP 8)

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all functions, classes, and modules

### Docstring Format

```python
def calculate_velocity(flow_m3s, diameter):
    """
    Calculate flow velocity from volumetric flow rate

    v = Q / A = Q / (π * D² / 4)

    Args:
        flow_m3s: Volumetric flow rate in m³/s
        diameter: Pipe internal diameter in m

    Returns:
        Flow velocity in m/s
    """
    # Implementation
```

### Type Hints

Use type hints where appropriate:

```python
def calculate_reynolds(velocity: float, diameter: float, kinematic_viscosity: float) -> float:
    return velocity * diameter / kinematic_viscosity
```

## Testing Requirements

### Unit Tests

- Write unit tests for all new functions
- Use pytest framework
- Place tests in appropriate `tests/test_*` directories
- Aim for high code coverage

Example:
```python
# tests/test_core/test_equations.py
import pytest
from hydraulics.core.equations import calculate_reynolds

def test_reynolds_number():
    """Test Reynolds number calculation"""
    velocity = 2.0  # m/s
    diameter = 0.0162  # m
    nu = 1.004e-6  # m²/s

    Re = calculate_reynolds(velocity, diameter, nu)
    expected = velocity * diameter / nu

    assert abs(Re - expected) < 1e-6
```

### Integration Tests

- Test complete workflows
- Place in `tests/integration/`
- Ensure smoke test passes

## Documentation Requirements

- Update README.md if adding user-facing features
- Update CHANGELOG.md with your changes
- Add docstrings to all new code
- Update or create documentation in `docs/` as needed

## Release Process

(For maintainers only)

1. Create release branch: `git checkout -b release/vX.Y.Z`
2. Update version in:
   - `src/hydraulics/__init__.py`
   - `pyproject.toml`
   - `CHANGELOG.md`
3. Test thoroughly
4. Merge to `main` and `develop`
5. Tag release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
6. Push tags: `git push origin --tags`

## Questions?

Open an issue or discussion on GitHub if you have questions!
