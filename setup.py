from setuptools import setup, find_packages

setup(
    name="thorlabs_cube",
    version="0.0.1",
    url="https://github.com/quantumion/thorlabs_cube",
    description="ARTIQ controller for Thorlabs T/KCube devices",
    install_requires=[
        "sipyco@git+https://github.com/m-labs/sipyco.git@v1.7",
        "asyncserial==0.1.0",
        "numpy==2.0.0", # hidden sipyco dependency
    ],
    extras_require={
        "docs": [
            "sphinx==7.3.7",
            "sphinx-argparse==0.4.0",
            "sphinx-autodoc-typehints==2.2.2",
        ]
    },
    packages=find_packages(
        where="src",
    ),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "aqctl_thorlabs_cube = thorlabs_cube.aqctl_thorlabs_cube:main",
        ],
    },
)
