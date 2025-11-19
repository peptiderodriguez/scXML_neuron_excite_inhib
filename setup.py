"""
Setup script for single-cell-sorting package
"""
from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'single_cell_pipeline_readme.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='scXML_neuron_excite_inhib',
    version='1.0.0',
    author='DVP Team',
    author_email='',
    description='Automated pipeline for Leica LMD7 laser microdissection with spatial optimization',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'scXML_neuron_excite_inhib=scXML_neuron_excite_inhib.cli:main',
        ],
    },
    keywords='cell-sorting facs tsp optimization bioinformatics',
    project_urls={
        'Documentation': '',
        'Source': '',
    },
)
