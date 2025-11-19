# Cell Sorting Pipeline - Documentation

## Overview
Automated pipeline for processing BIAS XML files for Leica LMD7 laser microdissection with spatial optimization.

**Created:** November 2025
**Purpose:** MPIP Psilocybin Neuron Sorting Experiment (Leica LMD7)

**Two Datasets:**
- **All Cells:** Standard spatial region, all cell sizes
- **Size-Restricted Cells:** Wider spatial region (wider swatch), filtered to narrow band of size histogram

---

## Pipeline Components

### 1. Shape Reduction (`batch_reduce.py`, `batch_reduce_SR.py`)
**Purpose:** Reduce XML shape complexity using Ramer-Douglas-Peucker algorithm

**Features:**
- Reduces point count by ~95% (epsilon=60)
- Preserves shape geometry
- Maintains CapID annotations if present

**Usage:**
```bash
python3 batch_reduce.py
# Processes: All cells (xml_scNeuron/)
# Outputs: *_reduced.xml files

python3 batch_reduce_SR.py
# Processes: Size-restricted cells (xml_scNeuron_sizeRestrict/)
# Outputs: *_reduced.xml files
```

**Input Files:**
- `scNeuron_inhib0.xml` / `scNeuronSR_inhib0.xml`
- `scNeuron_excite0.xml` / `scNeuronSR_excite0.xml`
  - SR files: Wider spatial region, size-filtered to narrow histogram band

---

### 2. Well Assignment (`serpentine_well_assign.py`, `serpentine_well_assign_SR.py`)
**Purpose:** Assign cells to 384-well plate with spatial optimization

**Features:**
- **TSP Optimization:** Minimizes travel distance within each cell type (inhib/excite)
- **Optimized Transition:** First excite cell is closest to last inhib cell
- **Serpentine Pattern:** Efficient B2→O23 collection pattern across quadrants (B2, B3, C2, C3)
- **Dynamic Blanks:** Auto-calculates blanks to complete current quadrant
- **Random Distribution:** Blanks scattered throughout (seed=25 for reproducibility)

**Usage:**
```bash
python3 serpentine_well_assign.py
# Processes: All cells (xml_scNeuron/*_reduced.xml)
# Outputs: scNeuron_combined_wellassigned.xml, well_assignments_tracking.csv

python3 serpentine_well_assign_SR.py
# Processes: Size-restricted cells (xml_scNeuron_sizeRestrict/*_reduced.xml)
# Outputs: scNeuronSR_combined_wellassigned.xml, well_assignments_tracking_SR.csv
```

---

## Output Files

### XML Files (for cell sorter)
- `scNeuron_combined_wellassigned.xml` - 207 cells (all cells), 24 blanks
- `scNeuronSR_combined_wellassigned.xml` - 205 cells (size-restricted), 26 blanks

**Contains:**
- Reduced shape coordinates (95% fewer points)
- CapID well assignments (e.g., "B2", "D4", "F6")
- Combined inhib + excite cells in optimized order

### CSV Tracking Files
- `well_assignments_tracking.csv` (all cells)
- `well_assignments_tracking_SR.csv` (size-restricted cells)

**Columns:**
- `Well_Position`: Well location (e.g., B2, D4)
- `Serpentine_Order`: Collection order (0-230)
- `Sample_Index`: Sample number (0-206 or 0-204)
- `Source_File`: inhib0 or excite0
- `Original_Shape_Index`: Original index in source file
- `Centroid_X`, `Centroid_Y`: Cell coordinates
- `Quadrant`: B2, B3, C2, or C3

---

## Algorithm Details

### TSP Optimization
**Method:** Greedy nearest neighbor + 2-opt improvement

**Process:**
1. Optimize inhibitory cells independently
2. Find last inhib cell position
3. Find closest excite cell to last inhib
4. Optimize excitatory cells starting from that closest cell
5. Result: Minimized transition distance (~35-41% of average hop)

### Serpentine Pattern (4 Phases)
Working area: B2 to O23 (avoiding outer edges)

**Phase 1:** B2→B4→...→B22 (serpentine through B,D,F,H,J,L,N rows, even columns)
**Phase 2:** N23→N21→...→N3 (register switch, row N, odd columns)
**Phase 3:** L3→L5→...→L23 (serpentine back through L,J,H,F,D,B rows, odd columns)
**Phase 4:** C2→C4→...→C22 (serpentine through C,E,G,I,K,M,O rows, even columns)

**Total:** 231 wells across 3 complete quadrants

### Blank Calculation
```python
samples_in_current_quadrant = total_samples % 77
blanks_needed = 77 - samples_in_current_quadrant (if > 0)
```
Ensures all used quadrants are completely filled.

---

## Performance Metrics

### All Cells (xml_scNeuron)
- **Cells:** 87 inhib + 120 excite = 207 total
- **Point Reduction:** 95.34% (inhib), 95.65% (excite)
- **Blanks:** 24 (completes 3 quadrants)
- **Transition Distance:** 3,304 pixels (35% of avg hop)

### Size-Restricted Cells (xml_scNeuron_sizeRestrict)
- **Cells:** 85 inhib + 120 excite = 205 total
  - From wider spatial region (wider swatch)
  - Filtered to narrow band of size histogram
- **Point Reduction:** 95.42% (inhib), 95.69% (excite)
- **Blanks:** 26 (completes 3 quadrants)
- **Transition Distance:** 5,641 pixels (41% of avg hop)

---

## Running the Complete Pipeline

### For New Datasets:

1. **Place XML files in appropriate directory**
   ```
   xml_scNeuron/
   ├── your_inhib0.xml
   └── your_excite0.xml
   ```

2. **Update file paths in scripts**
   - Edit `batch_reduce.py`: Update `files` list with your filenames
   - Edit `serpentine_well_assign.py`: Update `inhib_file` and `excite_file` paths

3. **Run pipeline**
   ```bash
   python3 batch_reduce.py
   python3 serpentine_well_assign.py
   ```

4. **Load XML into cell sorter**
   - Use the `*_combined_wellassigned.xml` file
   - Reference CSV for tracking and analysis

---

## Configuration Parameters

### In `batch_reduce.py` / `batch_reduce_SR.py`:
```python
epsilon = 60              # RDP algorithm threshold
undersampling = 0         # Take every n-th shape (0=disabled)
deletion = 0              # Delete every n-th shape (0=disabled)
```

### In `serpentine_well_assign.py` / `serpentine_well_assign_SR.py`:
```python
RANDOM_SEED = 25          # For reproducible blank positions
QUADRANT_SIZE = 77        # Wells per quadrant
```

---

## Troubleshooting

**Files too large:**
- Increase `epsilon` value (e.g., 80, 100) for more aggressive reduction

**Different plate format:**
- Modify `generate_serpentine_wells()` function
- Update `QUADRANT_SIZE` accordingly

**Change blank distribution:**
- Modify `RANDOM_SEED` for different random positions
- Set `NUM_BLANKS` manually instead of auto-calculation

---

## Dependencies
```
numpy
csv (built-in)
random (built-in)
```

## Notes
- TSP optimization is heuristic (greedy + 2-opt), not exact solution
- Serpentine pattern matches typical FACS collection flow
- Blanks serve as quality control samples
- All coordinate tracking in pixels (BIAS coordinate system)
