from setuptools import setup, find_packages

with open('README.md', 'rt') as f:
    readme = f.read().strip()

package_name = 'sydney_magic'
version = '0.25'
ext = 'tar.gz'

setup(
    name=package_name,
    url="https://github.com/KPEKEP/sydney-magic/", 
    download_url='https://github.com/KPEKEP/sydney-magic/{0}-{1}{2}'.format(package_name, version, ext),
    version=version,
    packages=find_packages(),
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=[
        'IPython',
        'sydney-py',
        'nest_asyncio',
        'ipynbname',
    ],
    author='Pavel Nakaznenko',
    author_email='p.nakaznenko@gmail.com',
    description='An IPython magic extension for interacting with Sydney.py',
    keywords='ipython magic sydney',
)