# Mr. Freeze

![build](https://github.com/LEB-EPFL/mr-freeze/actions/workflows/build.yml/badge.svg)

Hardware control and image analysis code for Mr. Freeze, the LEB plunge freezer.

## leb-freeze - A Python package for Fourier Ptychography

### Getting Started

```python
from leb.freeze import fp_simulation, fp_recover

# Simulate a Fourier Ptychography dataset
dataset, unaberrated_pupil, ground_truth_object, ground_truth_pupil = fp_simulation()

# Recover the complex object function and pupil
obj, pupil = fp_recover(dataset=dataset, pupil=unaberrated_pupil)
```

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

To reformat the code automatically:

```console
black .
```

#### Adding/removing dependencies

1. Add or remove your dependency to [pyproject.toml](pyproject.toml)
2. Regenerate the lock file: `poetry lock`
3. Synchronize your virtual environment with the new lock file: `poetry install`

## LED Matrix Controller - Arduino code to control an LED matrix

See [arduino_src/led_matrix_controller/README.md](arduino_src/led_matrix_controller/README.md).

## uManager - Micro-Manager scripts for acquisition control

See [umanager/README.md](umanager/README.md).
