"""
Shape reduction using Ramer-Douglas-Peucker algorithm

Simplifies cell contours by reducing point count while preserving
geometric accuracy. Typically achieves 95%+ reduction in points.
"""
from typing import List, Tuple, Dict
import numpy as np

from .xml_utils import (
    read_xml_file, write_xml_file, parse_shapes,
    replace_shapes, calculate_poly_area
)


def rdp_algorithm(points: np.ndarray, epsilon: float) -> np.ndarray:
    """
    Ramer-Douglas-Peucker algorithm for polyline simplification

    Recursively finds the point farthest from the line connecting
    start and end points. If distance exceeds epsilon, splits and
    recurses. Otherwise returns only start and end points.

    Args:
        points: Array of shape (N, 2) containing point coordinates
        epsilon: Distance threshold for simplification

    Returns:
        Simplified array of points
    """
    # Get start and end points
    start = np.tile(np.expand_dims(points[0], axis=0), (points.shape[0], 1))
    end = np.tile(np.expand_dims(points[-1], axis=0), (points.shape[0], 1))

    # Calculate perpendicular distance from each point to line
    dist_point_to_line = (
        np.abs(np.cross(end - start, points - start, axis=-1)) /
        np.linalg.norm(end - start, axis=-1)
    )

    # Find point with maximum distance
    max_idx = np.argmax(dist_point_to_line)
    max_value = dist_point_to_line[max_idx]

    result = []
    if max_value > epsilon:
        # Recurse on both segments
        partial_results_left = rdp_algorithm(points[:max_idx+1], epsilon)
        result += [list(i) for i in partial_results_left if list(i) not in result]

        partial_results_right = rdp_algorithm(points[max_idx:], epsilon)
        result += [list(i) for i in partial_results_right if list(i) not in result]
    else:
        # Keep only endpoints
        result += [points[0], points[-1]]

    return np.array(result)


def reduce_shapes(shapes: Dict[int, Tuple[List[int], List[int]]],
                 epsilon: float,
                 preserve_cap: bool = False,
                 caps: Dict[int, str] = None) -> Tuple[List[np.ndarray], List[str], Dict[str, float]]:
    """
    Apply RDP reduction to all shapes

    Args:
        shapes: Dict mapping shape index to (x_coords, y_coords)
        epsilon: RDP distance threshold
        preserve_cap: Whether to preserve CapID annotations
        caps: Dict mapping shape index to CapID (if preserve_cap=True)

    Returns:
        Tuple of:
        - reduced_shapes: List of numpy arrays (N x 2)
        - annotations: List of CapID strings (if preserve_cap=True, else empty)
        - stats: Dict with reduction statistics
    """
    annotations = []
    reduced_shapes = []

    initial_points = 0
    final_points = 0
    total_area = 0.0

    for idx in range(len(shapes)):
        x, y = shapes[idx]

        # Calculate statistics
        total_area += calculate_poly_area(x, y)
        initial_points += len(x)

        # Convert to numpy array and apply RDP
        points = np.array([x, y]).T
        reduced_points = rdp_algorithm(points, epsilon)

        reduced_shapes.append(reduced_points)
        final_points += len(reduced_points)

        # Preserve annotations if requested
        if preserve_cap and caps:
            annotations.append(caps[idx])

    # Calculate statistics
    reduction_pct = 100 - (final_points / initial_points) * 100 if initial_points > 0 else 0

    stats = {
        'initial_points': initial_points,
        'final_points': final_points,
        'reduction_percent': reduction_pct,
        'total_area': total_area,
        'num_shapes': len(shapes)
    }

    return reduced_shapes, annotations, stats


def reduce_xml_file(input_path: str, output_path: str, epsilon: float = 60,
                   verbose: bool = True) -> Dict[str, float]:
    """
    Reduce shapes in XML file using RDP algorithm

    Args:
        input_path: Path to input XML file
        output_path: Path for output XML file
        epsilon: RDP distance threshold (default: 60)
        verbose: If True, print progress information

    Returns:
        Dictionary with reduction statistics
    """
    if verbose:
        print(f"Processing: {input_path}")

    # Read and parse XML
    file_lines = read_xml_file(input_path)
    shapes, caps = parse_shapes(file_lines, return_cap=True)

    if verbose:
        print(f"Found {len(shapes)} shapes")

    # Check if CapID annotations are valid
    preserve_cap = len(caps) == len(shapes)
    if preserve_cap and verbose:
        print("Valid CapID annotations found - preserving")

    # Apply reduction
    reduced_shapes, annotations, stats = reduce_shapes(
        shapes, epsilon, preserve_cap, caps
    )

    # Generate output XML
    if preserve_cap:
        output_content = replace_shapes(
            file_lines, reduced_shapes,
            new_annotations=annotations, update_count=True
        )
    else:
        output_content = replace_shapes(
            file_lines, reduced_shapes, update_count=True
        )

    # Write output
    write_xml_file(output_path, output_content)

    if verbose:
        print(f"Initial points: {stats['initial_points']:,}")
        print(f"Final points: {stats['final_points']:,}")
        print(f"Reduction: {stats['reduction_percent']:.2f}%")
        print(f"Total area: {stats['total_area']:,.0f} px²")
        print(f"Saved to: {output_path}\n")

    return stats
