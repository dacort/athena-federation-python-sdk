from setuptools import find_packages, setup

setup(
    name="unoffical_athena_federation_sdk",
    package_dir={'': 'src'},
    packages=find_packages(where='src'), 
    version="0.0.0",
    description="Unofficial Python SDK for Athena Federation",
    install_requires=[
        'pyarrow==0.16.0'
    ]
)