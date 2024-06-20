from setuptools import setup, find_packages

setup(
    name='coupling',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'flask',
        'pandas',
        'pydriller',
        'gitpython',
        'tqdm',
        'celery',
    ],
)
