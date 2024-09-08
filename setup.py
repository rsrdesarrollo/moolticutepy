from setuptools import setup, find_packages
from datetime import date

setup(
    name="moolticutepy",
    description_short="Library an CLI to speak with moolticute service",
    author="Raúl Sampedro <5142014+rsrdesarrollo@users.noreply.github.com>",
    url="https://github.com/rsrdesarrollo/moolticutepy",
    home_page="https://github.com/rsrdesarrollo/moolticutepy",
    keywords=[
        "moolticute",
        "moolticuted",
        "mootlipass",
        "mooltipassminible",
        "mooltipassble",
        "password",
        "password manager",
    ],
    maintainer_email="5142014+rsrdesarrollo@users.noreply.github.com",
    version="1.0",
    release_date=date(2023, 2, 15),
    packages=find_packages(),
    install_requires=[
        "click==8.1.7",
        "websocket-client==1.8.0",
        "pydantic_core==2.20.1",
        "pydantic==2.8.2",
    ],
    entry_points={
        "console_scripts": ["moolticutepy=moolticutepy.cli:main"],
    },
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
    ],
    python_requires=">=3",
)
