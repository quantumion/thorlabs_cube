from setuptools import setup, find_packages

setup(
    name="thorlabs_cube",
    install_requires=[
        "sipyco@git+ssh://git@github.com/m-labs/sipyco.git",
        "asyncserial",
        "numpy", # hidden sipyco dependency
    ],
    extras_require={
        "docs": [
            "sphinx",
            "sphinx-argparse",
        ]
    },
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "aqctl_thorlabs_cube = thorlabs_cube.aqctl_thorlabs_cube:main",
        ],
    },
)
