from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vjmap_py_client",
    version="0.1.4",
    author="Neo Wang",
    author_email="wang.neo@gmail.com",
    description="A package for interacting with the Vjmap Service-API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/twisker/vjmap-py-client",
    license='MIT',
    packages=['vjmap_py_client'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests"
    ],
    keywords='vjmap cad python sdk client',
    include_package_data=True,
)
