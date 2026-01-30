import nox

PYTHON_FILES = [
    "gonto",
    "tests",
    "noxfile.py",
]


@nox.session(reuse_venv=True)
def lint(session):
    session.install("-e", ".[dev]")
    session.run("flake8", *PYTHON_FILES)
    session.run("black", "--check", "--diff", "--color", *PYTHON_FILES)
    session.run("mypy", *PYTHON_FILES)
    session.run("validate-pyproject", "pyproject.toml")


@nox.session(reuse_venv=True)
def black_fix(session):
    session.install("black")
    session.run("black", *PYTHON_FILES)


@nox.session(reuse_venv=True)
def gendoc(session):
    session.install("sphinx", "furo")
    session.install("-e", ".")
    session.run("sphinx-build", "-M", "html", "doc", "build")
