from setuptools import setup, find_packages

setup(
    name='sydney_magic',
    version='0.20',
    packages=find_packages(),
    install_requires=[
        'IPython',
        'sydney-py',
        'nest_asyncio'
    ],
    author='Pavel Nakaznenko',
    author_email='p.nakaznenko@gmail.com',
    description='An IPython magic extension for interacting with Sydney.py',
    keywords='ipython magic sydney',
)