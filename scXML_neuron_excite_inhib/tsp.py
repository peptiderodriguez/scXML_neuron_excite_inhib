"""
Traveling Salesman Problem (TSP) optimization algorithms

Implements greedy nearest neighbor with 2-opt improvement for
optimizing cell collection order to minimize travel distance.
"""
from typing import List, Tuple
import numpy as np


def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points

    Args:
        p1: First point (x, y)
        p2: Second point (x, y)

    Returns:
        Euclidean distance between points
    """
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def greedy_tsp(centroids: List[Tuple[float, float]], start_index: int = 0) -> List[int]:
    """
    Greedy nearest neighbor TSP heuristic

    Constructs a tour by always visiting the nearest unvisited point.
    Not optimal but provides a good starting solution.

    Args:
        centroids: List of (x, y) coordinates
        start_index: Index of starting point (default: 0)

    Returns:
        List of indices representing visit order
    """
    n = len(centroids)
    unvisited = set(range(n))
    current = start_index
    unvisited.remove(current)
    tour = [current]

    while unvisited:
        nearest = min(unvisited, key=lambda i: calculate_distance(centroids[current], centroids[i]))
        tour.append(nearest)
        current = nearest
        unvisited.remove(current)

    return tour


def two_opt_improve(tour: List[int], centroids: List[Tuple[float, float]],
                    max_iterations: int = 1000) -> List[int]:
    """
    Improve TSP tour using 2-opt algorithm

    Iteratively swaps edges to reduce total path length.
    Continues until no improvement is found or max iterations reached.

    Args:
        tour: Initial tour (list of indices)
        centroids: List of (x, y) coordinates
        max_iterations: Maximum optimization iterations

    Returns:
        Improved tour (list of indices)
    """
    n = len(tour)
    improved = True
    iteration = 0

    while improved and iteration < max_iterations:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                # Calculate current edge lengths
                current_dist = (calculate_distance(centroids[tour[i-1]], centroids[tour[i]]) +
                               calculate_distance(centroids[tour[j]], centroids[tour[(j+1) % n]]))

                # Calculate distance after reversing segment
                new_dist = (calculate_distance(centroids[tour[i-1]], centroids[tour[j]]) +
                           calculate_distance(centroids[tour[i]], centroids[tour[(j+1) % n]]))

                if new_dist < current_dist:
                    # Reverse segment between i and j
                    tour[i:j+1] = list(reversed(tour[i:j+1]))
                    improved = True
        iteration += 1

    return tour


def optimize_tsp(centroids: List[Tuple[float, float]], start_index: int = 0,
                 verbose: bool = True) -> Tuple[List[int], float]:
    """
    Optimize TSP tour using greedy + 2-opt

    Combines greedy nearest neighbor for initial solution with
    2-opt iterative improvement.

    Args:
        centroids: List of (x, y) coordinates
        start_index: Index to start tour from
        verbose: If True, print optimization progress

    Returns:
        Tuple of (optimized_tour, total_distance)
        - optimized_tour: List of indices in visit order
        - total_distance: Total path length in pixels
    """
    if verbose:
        if start_index != 0:
            print(f"    Optimizing TSP for {len(centroids)} points (starting from index {start_index})...")
        else:
            print(f"    Optimizing TSP for {len(centroids)} points...")

    # Generate initial greedy solution
    tour = greedy_tsp(centroids, start_index)

    # Improve with 2-opt
    tour = two_opt_improve(tour, centroids)

    # Calculate total distance
    total_dist = sum(calculate_distance(centroids[tour[i]], centroids[tour[(i+1) % len(tour)]])
                     for i in range(len(tour)))

    if verbose:
        print(f"    Total path distance: {total_dist:.2f} pixels")

    return tour, total_dist


def find_closest_point(reference_point: Tuple[float, float],
                       points: List[Tuple[float, float]]) -> Tuple[int, float]:
    """
    Find closest point to a reference point

    Args:
        reference_point: Reference (x, y) coordinate
        points: List of candidate (x, y) coordinates

    Returns:
        Tuple of (closest_index, distance)
    """
    closest_idx = min(range(len(points)),
                     key=lambda i: calculate_distance(reference_point, points[i]))
    distance = calculate_distance(reference_point, points[closest_idx])
    return closest_idx, distance
