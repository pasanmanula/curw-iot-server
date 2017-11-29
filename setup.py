from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_file = f.read()

setup(
    name='curw-iot-server',
    version='0.1.0',
    description='Server for storing weather station data',
    long_description=readme,
    author='Gihan Karunarathne',
    author_email='gckarunarathne@gmail.com',
    url='https://github.com/gihankarunarathne/curw-iot-server',
    license=license_file,
    packages=find_packages(exclude=('tests', 'docs'))
)
