import setuptools

from axisutilities import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', "r") as fh:
    requirements = fh.read().split("\n")

setuptools.setup(
    name="TimeAxis",
    version=__version__,
    author="Mohammad ABouali",
    author_email="maboualidev@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maboualidev/TimeAxis",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7'
)