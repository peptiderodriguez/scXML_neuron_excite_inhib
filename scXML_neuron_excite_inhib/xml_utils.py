"""
XML utilities for parsing and writing BIAS XML files
"""
import numpy as np


def parse_shapes(file_lines, return_cap=False):
    """
    Parse shapes from XML file lines

    Args:
        file_lines: List of XML file lines (strings)
        return_cap: If True, also return CapID annotations

    Returns:
        shapes: Dict mapping shape index to (x_coords, y_coords)
        caps: Dict mapping shape index to CapID (if return_cap=True)
    """
    shapes = {}
    caps = {}
    x, y = [], []
    idx = 0
    reading = False

    for line in file_lines:
        if line.startswith('<ShapeCount'):
            reading = True
        if reading:
            if line.startswith('<Shape_'):
                if len(x) != 0:
                    shapes[idx] = (x, y)
                    idx += 1
                    x, y = [], []
            if line.startswith('<X'):
                x.append(int(line.split('>')[1].split('<')[0]))
            if line.startswith('<Y'):
                y.append(int(line.split('>')[1].split('<')[0]))
            if 'CapID' in line:
                caps[idx] = line.split('>')[1].split('<')[0]

    if len(x) != 0:
        shapes[idx] = (x, y)
        idx += 1

    if return_cap:
        return shapes, caps
    else:
        return shapes


def extract_shape_count(file_lines):
    """Extract ShapeCount from XML file lines"""
    for line in file_lines:
        if '<ShapeCount>' in line:
            return int(line[12:].split('<')[0])
    return 0


def replace_shapes(file_lines, shapes, new_annotations=None, update_count=False):
    """
    Replace shapes in XML file with new shapes

    Args:
        file_lines: Original XML file lines
        shapes: List of numpy arrays (N x 2) with shape coordinates
        new_annotations: List of CapID strings (optional)
        update_count: If True, update ShapeCount in XML

    Returns:
        String with complete XML content
    """
    converted = []
    overwrite = False

    for line in file_lines:
        if overwrite:
            # Write all new shapes
            for idx, shape in enumerate(shapes):
                converted.append(f'<Shape_{idx+1}>')
                converted.append(f'<PointCount>{len(shape)}</PointCount>')

                if new_annotations is not None:
                    cap = new_annotations[idx]
                    converted.append(f'<CapID>{cap}</CapID>')

                for i in range(len(shape)):
                    converted.append(f'<X_{i+1}>{shape[i,0]}</X_{i+1}>')
                    converted.append(f'<Y_{i+1}>{shape[i,1]}</Y_{i+1}>')

                converted.append(f'</Shape_{idx+1}>')
            break
        else:
            converted.append(line)

        if 'ShapeCount' in line:
            overwrite = True
            if update_count:
                converted[-1] = f'<ShapeCount>{len(shapes)}</ShapeCount>'

    converted.append(f'</ImageData>')
    return '\n'.join(converted)


def read_xml_file(filepath):
    """Read and decode XML file"""
    with open(filepath, 'r', encoding='utf8') as f:
        lines = [line.strip() for line in f.readlines()]
    return lines


def write_xml_file(filepath, content):
    """Write XML content to file"""
    with open(filepath, 'w', encoding='utf8') as f:
        f.write(content)


def calculate_centroid(x, y):
    """Calculate centroid of a shape"""
    return np.mean(x), np.mean(y)


def calculate_poly_area(x, y):
    """Calculate area of polygon using Shoelace formula"""
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
