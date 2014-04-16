import re
from setuptools import setup

init_py = open('overlay_parse/__init__.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
metadata['doc'] = re.findall('"""(.+)"""', init_py)[0]

setup(
    name='overlay_parse',
    version=metadata['version'],
    description=metadata['doc'],
    author=metadata['author'],
    author_email=metadata['email'],
    url=metadata['url'],
    packages=['overlay_parse'],
    include_package_data=True,
    install_requires=[
    ],

    test_suite='nose.collector',
    license=open('LICENSE').read(),
)
