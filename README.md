# Thorlabs Cube
[ARTIQ NDSP](https://m-labs.hk/artiq/manual/developing_a_ndsp.html) for motors controlled by [Thorlabs T/K-Cube controllers](https://www.thorlabs.com/navigation.cfm?guide_id=6).
Derived from the [thorlabs_tcube](https://github.com/m-labs/thorlabs_tcube) package.

## Installation
Clone the repository then install using pip:
```sh
$ git clone git@github.com:quantumion/thorlabs_cube.git
$ cd thorlabs_cube
$ pip install .
```

Optionally, install with Sphinx to build autodocumentation:
```sh
$ pip install .[docs]
```

## Usage
See the [documentation](/doc/index.rst) for setup and usage instructions.

## Documentation
Build the documentation with Sphinx:
```sh
$ cd doc
$ make html
```
