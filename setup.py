from typing import List
from setuptools import setup, find_packages
import codecs


def readfile(filename: str) -> List[str]:
    with codecs.open(filename, encoding="utf-8") as stream:
        return stream.read().split("\n")


def render_plugin(name: str) -> str:
    return f'{name} = rite.render.{name}:Render{name.capitalize()}'


def parse_plugin(name: str) -> str:
    return f'{name} = rite.parse.{name}:Parse{name.capitalize()}'


doclines = readfile("README.rst")
requires = readfile("requirements.txt")
version = readfile("VERSION")[0].strip()


setup(
    name='rite',
    version=version,
    url='https://github.com/mcmtroffaes/rite',
    download_url='http://pypi.python.org/pypi/rite',
    license='MIT',
    author='Matthias C. M. Troffaes',
    author_email='matthias.troffaes@gmail.com',
    description=doclines[0],
    long_description="\n".join(doclines[2:]),
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Text Editors :: Text Processing',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Text Processing :: Markup :: Markdown',
        'Topic :: Text Processing :: Markup :: XML',
        'Topic :: Text Processing :: Markup :: reStructuredText',
        'Typing :: Typed',
    ],
    platforms='any',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=requires,
    entry_points={
        'rite.render': [
            render_plugin('html'),
            render_plugin('latex'),
            render_plugin('markdown'),
            render_plugin('plaintext'),
            render_plugin('rst'),
            render_plugin('xml'),
        ],
        'rite.parse': [
            parse_plugin('html'),
            parse_plugin('latex'),
            parse_plugin('xml'),
        ],
    }
)
