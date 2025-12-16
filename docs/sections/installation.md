# **Installation**

## Step 1: Clone the Repository

Clone the repository from GitHub:

```bash
$ git clone git@github.com:quantumion/thorlabs_cube.git
$ cd thorlabs_cube
```

## Step 2: Create a Python Virtual Environment

It is recommended to create a Python virtual environment using [venv](https://docs.python.org/3/library/venv.html) for repository dependency isolation.

```bash
$ python3 -m venv venv
$ source venv/bin/activate
```

**Note**: `venv` is the standard naming convention for Python virtual environments.

## Step 3: Install the Package

Install the package with pip:

```bash
$ pip install .
```

This will install the core package dependencies defined in `setup.py`.

## Step 4: Build the Documentation (Optional)

To build and view the documentation locally, first install the documentation dependencies:

```bash
$ pip install -e '.[docs]'
```

**Note**: Some shells (like zsh) require quoting the brackets. If you encounter errors, use the quoted form shown above.

Then build and serve the documentation:

```bash
$ mkdocs build
$ mkdocs serve
```

After running `mkdocs serve`, open your web browser and navigate to `http://127.0.0.1:8000` to view the documentation.

## Step 5: Install Development Dependencies (Optional)

For development work, you can install additional development tools for linting, formatting, and testing.

First, ensure you have the package installed in editable mode:

```bash
$ pip install -e .
```

Install pre-commit hooks for code quality:

```bash
$ pip install pre-commit
$ pre-commit install
```

This will automatically run linters and formatters (configured in `.pre-commit-config.yaml`) before each commit.
