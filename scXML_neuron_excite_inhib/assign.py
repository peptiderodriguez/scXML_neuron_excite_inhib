"""
Well assignment orchestration for cell sorting

Combines TSP optimization, serpentine pattern generation, and blank
distribution to assign cells to 384-well plates efficiently.
"""
from typing import List, Tuple, Dict
import random
import numpy as np
import csv

from .xml_utils import (
    read_xml_file, write_xml_file, parse_shapes,
    replace_shapes, calculate_centroid
)
from .tsp import optimize_tsp, find_closest_point
from .serpentine import generate_serpentine_wells, get_quadrant, calculate_dynamic_blanks


def assign_wells(inhib_file: str, excite_file: str,
                output_xml: str, output_csv: str,
                random_seed: int = 25,
                verbose: bool = True) -> Dict:
    """
    Assign cells to 384-well plate with full optimization

    Process:
    1. Load and parse both cell type files
    2. TSP optimize inhibitory cells
    3. Find closest excitatory cell to last inhibitory cell
    4. TSP optimize excitatory cells starting from closest
    5. Generate serpentine well pattern
    6. Calculate and randomly distribute blanks
    7. Create well assignments
    8. Export XML and tracking CSV

    Args:
        inhib_file: Path to inhibitory cells XML
        excite_file: Path to excitatory cells XML
        output_xml: Path for output XML file
        output_csv: Path for output CSV file
        random_seed: Random seed for reproducible blank positions
        verbose: If True, print progress information

    Returns:
        Dictionary with assignment statistics
    """
    if verbose:
        print("=== Serpentine Well Assignment ===\n")

    # Read files
    if verbose:
        print(f"Reading {inhib_file.split('/')[-1]}...")
    inhib_lines = read_xml_file(inhib_file)
    inhib_shapes, _ = parse_shapes(inhib_lines, return_cap=True)
    if verbose:
        print(f"Found {len(inhib_shapes)} shapes in inhib file")

    if verbose:
        print(f"Reading {excite_file.split('/')[-1]}...")
    excite_lines = read_xml_file(excite_file)
    excite_shapes, _ = parse_shapes(excite_lines, return_cap=True)
    if verbose:
        print(f"Found {len(excite_shapes)} shapes in excite file")

    # Calculate centroids and optimize inhib ordering
    if verbose:
        print("\nOptimizing inhib0 spatial ordering...")

    inhib_centroids = []
    for idx in range(len(inhib_shapes)):
        x, y = inhib_shapes[idx]
        centroid_x, centroid_y = calculate_centroid(x, y)
        inhib_centroids.append((centroid_x, centroid_y))

    inhib_tour, inhib_dist = optimize_tsp(inhib_centroids, verbose=verbose)

    # Get last inhib cell position
    last_inhib_idx = inhib_tour[-1]
    last_inhib_centroid = inhib_centroids[last_inhib_idx]
    if verbose:
        print(f"    Last inhib cell (index {last_inhib_idx}): "
              f"centroid = ({last_inhib_centroid[0]:.2f}, {last_inhib_centroid[1]:.2f})")

    # Calculate centroids for excite cells
    if verbose:
        print("\nOptimizing excite0 spatial ordering...")

    excite_centroids = []
    for idx in range(len(excite_shapes)):
        x, y = excite_shapes[idx]
        centroid_x, centroid_y = calculate_centroid(x, y)
        excite_centroids.append((centroid_x, centroid_y))

    # Find closest excite cell to last inhib
    closest_excite_idx, closest_distance = find_closest_point(
        last_inhib_centroid, excite_centroids
    )
    if verbose:
        print(f"    Closest excite cell to last inhib: "
              f"index {closest_excite_idx}, distance = {closest_distance:.2f}")

    # Optimize excite tour starting from closest
    excite_tour, excite_dist = optimize_tsp(
        excite_centroids, start_index=closest_excite_idx, verbose=verbose
    )

    # Combine shapes in optimized order
    if verbose:
        print("\nCombining shapes in optimized order...")

    combined_shapes = []
    combined_metadata = []

    for tour_idx in inhib_tour:
        x, y = inhib_shapes[tour_idx]
        centroid_x, centroid_y = calculate_centroid(x, y)
        points = np.array([x, y]).T
        combined_shapes.append(points)
        combined_metadata.append({
            'source': 'inhib0',
            'original_idx': tour_idx,
            'centroid_x': centroid_x,
            'centroid_y': centroid_y
        })

    for tour_idx in excite_tour:
        x, y = excite_shapes[tour_idx]
        centroid_x, centroid_y = calculate_centroid(x, y)
        points = np.array([x, y]).T
        combined_shapes.append(points)
        combined_metadata.append({
            'source': 'excite0',
            'original_idx': tour_idx,
            'centroid_x': centroid_x,
            'centroid_y': centroid_y
        })

    total_samples = len(combined_shapes)
    if verbose:
        print(f"Total combined shapes: {total_samples}")

    # Generate serpentine well pattern
    if verbose:
        print("\nGenerating serpentine well pattern...")
    wells = generate_serpentine_wells()
    if verbose:
        print(f"Generated {len(wells)} wells")

    # Calculate blanks needed
    num_blanks = calculate_dynamic_blanks(total_samples)
    if verbose:
        print(f"\nBlank calculation:")
        print(f"  Total samples: {total_samples}")
        print(f"  Blanks needed to complete quadrant: {num_blanks}")

    # Randomly distribute blanks
    random.seed(random_seed)
    np.random.seed(random_seed)

    if num_blanks > 0:
        blank_positions = sorted(random.sample(range(len(wells)), num_blanks))
        blank_wells = [wells[i] for i in blank_positions]
        if verbose:
            print(f"\nRandomly selected {num_blanks} blank positions (seed={random_seed})")
            print(f"Blank wells: {blank_wells}")
    else:
        blank_positions = []
        if verbose:
            print(f"\nNo blanks needed")

    # Create well assignments
    sample_idx = 0
    well_mapping = []
    shapes_for_xml = []
    well_labels_for_xml = []

    for position_idx in range(len(wells)):
        well = wells[position_idx]
        quadrant = get_quadrant(well)

        if position_idx in blank_positions:
            # Blank well
            well_mapping.append({
                'well_position': well,
                'serpentine_order': position_idx,
                'sample_index': 'BLANK',
                'source_file': 'BLANK',
                'original_shape_index': 'BLANK',
                'centroid_x': '',
                'centroid_y': '',
                'quadrant': quadrant
            })
        else:
            # Sample well
            if sample_idx < len(combined_shapes):
                well_mapping.append({
                    'well_position': well,
                    'serpentine_order': position_idx,
                    'sample_index': sample_idx,
                    'source_file': combined_metadata[sample_idx]['source'],
                    'original_shape_index': combined_metadata[sample_idx]['original_idx'],
                    'centroid_x': f"{combined_metadata[sample_idx]['centroid_x']:.2f}",
                    'centroid_y': f"{combined_metadata[sample_idx]['centroid_y']:.2f}",
                    'quadrant': quadrant
                })
                shapes_for_xml.append(combined_shapes[sample_idx])
                well_labels_for_xml.append(well)
                sample_idx += 1

    # Write CSV
    if verbose:
        print(f"\nWriting tracking CSV to {output_csv}...")

    with open(output_csv, 'w', newline='') as csvfile:
        csvfile.write(f"# Random seed: {random_seed}\n")

        fieldnames = ['Well_Position', 'Serpentine_Order', 'Sample_Index', 'Source_File',
                      'Original_Shape_Index', 'Centroid_X', 'Centroid_Y', 'Quadrant']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for entry in well_mapping:
            writer.writerow(entry)

    if verbose:
        print(f"CSV created with {len(well_mapping)} entries")

    # Write XML
    if verbose:
        print(f"\nWriting output XML to {output_xml}...")

    output_content = replace_shapes(
        inhib_lines, shapes_for_xml,
        new_annotations=well_labels_for_xml, update_count=True
    )
    write_xml_file(output_xml, output_content)

    # Summary
    stats = {
        'total_samples': total_samples,
        'inhib_count': len(inhib_shapes),
        'excite_count': len(excite_shapes),
        'blanks': num_blanks,
        'inhib_path_distance': inhib_dist,
        'excite_path_distance': excite_dist,
        'transition_distance': closest_distance,
        'random_seed': random_seed
    }

    if verbose:
        print("\n=== Summary ===")
        print(f"Total shapes: {total_samples}")
        print(f"  - inhib0: {len(inhib_shapes)} shapes (TSP optimized)")
        print(f"  - excite0: {len(excite_shapes)} shapes (TSP optimized)")
        print(f"Blanks: {num_blanks}")
        print(f"Transition distance: {closest_distance:.2f} pixels")
        print(f"Random seed: {random_seed}")
        print("\n=== Complete ===")

    return stats
