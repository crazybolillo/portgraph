from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='portgraph',
    version='0.0.2',
    author='Loïc Bartoletti',
    author_email='lbartoletti@tuxfamily.org',
    packages=find_packages(),
    entry_points=dict(console_scripts=[
        'portgraph=portgraph.portgraph:main',
    ]),
    zip_safe=False,
    include_package_data=True,
    url='https://gitlab.com/lbartoletti/portgraph/',
    license='LICENSE',
    description='Create a graph for a(ll) FreeBSD port(s).',
    long_description=long_description,
    install_requires=[
        "graphviz >= 0.8.2"
    ],
)
