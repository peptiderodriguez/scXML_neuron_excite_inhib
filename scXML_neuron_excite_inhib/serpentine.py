"""
Serpentine well plate pattern generation

Generates efficient serpentine collection patterns for 384-well plates,
avoiding outer edge wells and following a snake-like path through quadrants.
"""
from typing import List, Tuple


def get_quadrant(well: str) -> str:
    """
    Determine which quadrant a well belongs to

    Quadrants are defined by row/column parity:
    - B2: Even rows (B,D,F...), Even columns (2,4,6...)
    - B3: Even rows (B,D,F...), Odd columns (3,5,7...)
    - C2: Odd rows (C,E,G...), Even columns (2,4,6...)
    - C3: Odd rows (C,E,G...), Odd columns (3,5,7...)

    Args:
        well: Well position string (e.g., "B2", "D15")

    Returns:
        Quadrant label: "B2", "B3", "C2", or "C3"
    """
    row_letter = well[0]
    col_number = int(well[1:])

    # Map letters to indices (A=0, B=1, C=2, etc.)
    abc = 'ABCDEFGHIJKLMNOPQRST'
    row_idx = abc.index(row_letter)

    # Determine if row/column are even/odd
    row_is_even = (row_idx % 2 == 1)  # B=1, D=3, F=5 etc. are odd indices but "even" rows
    col_is_even = (col_number % 2 == 0)

    if row_is_even and col_is_even:
        return "B2"
    elif row_is_even and not col_is_even:
        return "B3"
    elif not row_is_even and col_is_even:
        return "C2"
    else:
        return "C3"


def generate_serpentine_wells() -> List[str]:
    """
    Generate serpentine well pattern for 384-well plate

    Working area: B2 to O23 (avoids outer edges A, P-T, columns 1 & 24)

    Pattern follows 4 phases:
    1. Even columns (2,4,6...22), rows B→N (serpentine)
    2. Odd columns (23,21,19...3), row N only (register switch)
    3. Odd columns (3,5,7...23), rows L→B (serpentine back)
    4. Even columns (2,4,6...22), rows C→O (serpentine)

    Total: 231 wells across 3 complete quadrants

    Returns:
        List of well position strings in collection order
    """
    abc = 'ABCDEFGHIJKLMNOPQRST'
    wells = []

    # Phase 1: Even columns (2,4...22), rows B,D,F,H,J,L,N (serpentine)
    phase1_rows = ['B', 'D', 'F', 'H', 'J', 'L', 'N']
    phase1_cols = list(range(2, 23, 2))

    for row_idx, row in enumerate(phase1_rows):
        if row_idx % 2 == 0:  # Left to right
            for col in phase1_cols:
                wells.append(f"{row}{col}")
        else:  # Right to left (serpentine)
            for col in reversed(phase1_cols):
                wells.append(f"{row}{col}")

    # Phase 2: Register switch - Row N, odd columns (23,21...3)
    phase2_cols = list(range(23, 2, -2))
    for col in phase2_cols:
        wells.append(f"N{col}")

    # Phase 3: Odd columns (3,5...23), rows L,J,H,F,D,B (serpentine back up)
    phase3_rows = ['L', 'J', 'H', 'F', 'D', 'B']
    phase3_cols = list(range(3, 24, 2))

    for row_idx, row in enumerate(phase3_rows):
        if row_idx % 2 == 0:  # Left to right
            for col in phase3_cols:
                wells.append(f"{row}{col}")
        else:  # Right to left (serpentine)
            for col in reversed(phase3_cols):
                wells.append(f"{row}{col}")

    # Phase 4: Register switch - Even columns (2,4...22), rows C,E,G,I,K,M,O (serpentine)
    phase4_rows = ['C', 'E', 'G', 'I', 'K', 'M', 'O']
    phase4_cols = list(range(2, 23, 2))

    for row_idx, row in enumerate(phase4_rows):
        if row_idx % 2 == 0:  # Left to right
            for col in phase4_cols:
                wells.append(f"{row}{col}")
        else:  # Right to left (serpentine)
            for col in reversed(phase4_cols):
                wells.append(f"{row}{col}")

    return wells


def calculate_dynamic_blanks(num_samples: int, quadrant_size: int = 77) -> int:
    """
    Calculate number of blanks needed to complete current quadrant

    Args:
        num_samples: Total number of samples
        quadrant_size: Wells per quadrant (default: 77 for 384-well plate)

    Returns:
        Number of blanks needed to fill current quadrant (0 if already complete)
    """
    samples_in_current_quadrant = num_samples % quadrant_size
    if samples_in_current_quadrant > 0:
        return quadrant_size - samples_in_current_quadrant
    return 0
