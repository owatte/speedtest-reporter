#!/usr/bin/env python
 
from setuptools import setup, find_packages
 
import speedtest_reporter
 
setup(
 
    name='speedtest-reporter',
 
    version=speedtest_reporter.__version__,
 
    packages=find_packages(),
 
    author="Olivier Watte - GwadaLUG",
 
    author_email="olivier.watte@gmail.com",
 
    description="internet connection speedtest with results recorded and published",
 
    long_description=open('README.rst').read(),
 
    install_requires=['pygal', 'speedtest-cli'],
 
    include_package_data=True,
 
    url='https://github.com/owatte/speedtest-reporter',
 
    # Il est d'usage de mettre quelques metadata à propos de sa lib
    # Pour que les robots puissent facilement la classer.
    # La liste des marqueurs autorisées est longue, alors je vous
    # l'ai mise sur 0bin: http://is.gd/AajTjj
    #
    # Il n'y a pas vraiment de règle pour le contenu. Chacun fait un peu
    # comme il le sent. Il y en a qui ne mettent rien.
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: System Administrators"
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Networking :: Monitoring",
    ],
 
 
    # C'est un système de plugin, mais on s'en sert presque exclusivement
    # Pour créer des commandes, comme "django-admin".
    # Par exemple, si on veut créer la fabuleuse commande "proclame-sm", on
    # va faire pointer ce nom vers la fonction proclamer(). La commande sera
    # créé automatiquement. 
    # La syntaxe est "nom-de-commande-a-creer = package.module:fonction".
    entry_points = {
        'console_scripts': [
            'speedtest-reporter = speedtest_reporter:main',
        ],
    },
)
