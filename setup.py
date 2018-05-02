from setuptools import find_packages, setup

setup(
    name='aws-ubuntu-advantage',
    author='Casey Marshall',
    author_email='<casey.marshall@canonical.com>',
    description='Set up an AWS Account for Ubuntu Advantage',
    version='0.1',
    install_requires=[
        'awscli',
        'boto3',
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    entry_points = {
        'console_scripts': ['aws-ubuntu-advantage=canonical.awsua:main'],
    }
)
