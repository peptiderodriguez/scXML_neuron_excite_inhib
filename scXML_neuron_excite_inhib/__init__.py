"""
scXML_neuron_excite_inhib Pipeline

An automated pipeline for processing BIAS XML files for Leica LMD7 laser microdissection
with spatial optimization using TSP algorithms and serpentine well patterns.

Main Features:
- Shape reduction using Ramer-Douglas-Peucker algorithm (95%+ reduction)
- TSP optimization for minimizing cell collection travel distance
- Optimized transition between cell types (inhibitory -> excitatory)
- Serpentine well pattern for efficient 384-well plate collection
- Dynamic blank calculation and random distribution

Usage:
    from scXML_neuron_excite_inhib import reduce_xml_file, assign_wells

    # Reduce shapes
    reduce_xml_file('input.xml', 'output_reduced.xml', epsilon=60)

    # Assign wells
    assign_wells('inhib_reduced.xml', 'excite_reduced.xml',
                'output.xml', 'tracking.csv')

Command-line usage:
    $ scXML_neuron_excite_inhib reduce input.xml --epsilon 60
    $ scXML_neuron_excite_inhib assign inhib.xml excite.xml
    $ scXML_neuron_excite_inhib pipeline inhib.xml excite.xml --output-dir ./results
"""

__version__ = '1.0.0'
__author__ = 'DVP Team'
__license__ = 'MIT'

# Import main functions for easy access
from .reduce import reduce_xml_file, reduce_shapes
from .assign import assign_wells
from .xml_utils import (
    read_xml_file,
    write_xml_file,
    parse_shapes,
    calculate_centroid
)
from .tsp import optimize_tsp
from .serpentine import generate_serpentine_wells, get_quadrant

__all__ = [
    'reduce_xml_file',
    'reduce_shapes',
    'assign_wells',
    'read_xml_file',
    'write_xml_file',
    'parse_shapes',
    'calculate_centroid',
    'optimize_tsp',
    'generate_serpentine_wells',
    'get_quadrant',
    '__version__',
]
