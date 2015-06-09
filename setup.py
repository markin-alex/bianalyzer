import setuptools
from setuptools.command.install import install
import sys

nltk_dependencies = ['punkt', 'maxent_treebank_pos_tagger', 'wordnet']


class InstallWithPostCommand(install):
    def run(self):
        install.run(self)
        print 'running post install function'
        post_install()


def post_install():
    import nltk
    for resource in nltk_dependencies:
        if not nltk.download(resource):
            sys.stderr.write('ERROR: Could not download required NLTK resource:'
                             ' {}\n'.format(resource))
            sys.stderr.flush()

setuptools.setup(
    name='Bianalyzer',
    url='https://github.com/luntos/bianalyzer',
    version='0.1',
    description='Bicluster analysis library oriented towards work with unstructured text data and keyphrases',

    packages=setuptools.find_packages(),
    install_requires=[
        'east>=0.3.1',
        'enum34>=1.0.4',
        'lxml',
        'networkx',
        'nltk>=3.0.0'
    ],

    extras_require={
        'graphs':  ['nodebox-opengl', 'pyglet'],
        'spectral_coclustering': ['numpy>=1.6.1', 'scipy>=0.9', 'scikit-learn>=0.16.1']
    },
    cmdclass={'install': InstallWithPostCommand},

    entry_points={
        "console_scripts": [
            "bianalyzer = bianalyzer.main:main"
        ]
    },

    author='Alexey Markin',
    author_email='alex.markin57@gmail.com',
    license='MIT',
    keywords=['bicluster analysis', 'box clustering', 'text analysis', 'keyphrase biclustering']
)
