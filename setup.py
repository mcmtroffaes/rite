from setuptools import setup, find_packages
import codecs


def readfile(filename):
    with codecs.open(filename, encoding="utf-8") as stream:
        return stream.read().split("\n")


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
        'Development Status :: 1 - Planning',
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
        'Topic :: Text Processing :: Markup :: reStructuredText',
        'Topic :: Text Processing :: Markup :: XML',
        'Typing :: Typed',
    ],
    platforms='any',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=requires,
    entry_points={
        'rite.backends': [
            'html = rite.backends.html:render_html',
            'markdown = rite.backends.html:render_markdown',
            'plaintext = rite.backends.html:render_plaintext',
        ],
    }
)
