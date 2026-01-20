import nox

PYTHON_FILES = [
    "gonto",
    "noxfile.py",
]


@nox.session(reuse_venv=True)
def lint(session):
    session.install("-e", ".[dev]")
    session.run("flake8", *PYTHON_FILES)
    session.run("black", "--check", "--diff", "--color", *PYTHON_FILES)
    session.run("validate-pyproject", "pyproject.toml")


@nox.session(reuse_venv=True)
def black_fix(session):
    session.install("black")
    session.run("black", *PYTHON_FILES)
