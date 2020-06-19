from setuptools import setup, find_packages

setup(
    name='flask_app',
    packages=['flask_app'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)