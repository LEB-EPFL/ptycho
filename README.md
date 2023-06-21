# Mr. Freeze

Hardware control and image analysis code for Mr. Freeze, the LEB plunge freezer.

## leb-freeze - A Python package for Fourier Ptychography

### Development

#### Setup the development environment

1. Install Python >= 3.11 OR install [pyenv](https://github.com/pyenv/pyenv): `curl https://pyenv.run | bash`, then install Python interpreter(s): `pyenv install 3.11.4`
2. Install [poetry](https://python-poetry.org/docs/):

```console
# Linux, macOS, WSL
curl -sSL https://install.python-poetry.org | python3 -

# Windows
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

3. Tell Poetry to use virtual environments in the project root directory: `poetry config virtualenvs.in-project true`
4. Set the virtual environment Python version to 3.11: `poetry env use 3.11`
4. Activate the virtual environment: `poetry shell`
5. Install the dependencies: `poetry install`

#### Testing

From inside the poetry shell:

```console
pytest
```

#### Linters

From inside the poetry shell:

```console
ruff check .
```

## LED Matrix Controller - Arduino code to control an LED matrix

See [arduino_src/led_matrix_controller/README.md](arduino_src/led_matrix_controller/README.md).

## uManager - Micro-Manager scripts for acquisition control
