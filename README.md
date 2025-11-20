# scXML_neuron_excite_inhib

**Automated pipeline for Leica LMD7 laser microdissection with spatial optimization**

Processing BIAS XML files for optimized cell collection with TSP path planning, serpentine well patterns, and dynamic blank distribution.

**Created:** November 2025
**Purpose:** MPIP Psilocybin Neuron Sorting Experiment (Leica LMD7)

---

## Features

- **Shape Reduction:** Ramer-Douglas-Peucker algorithm (95%+ point compression)
- **TSP Optimization:** Greedy nearest neighbor + 2-opt for spatial path planning
- **Optimized Transition:** First excitatory cell closest to last inhibitory cell
- **Serpentine Well Pattern:** Efficient 384-well plate collection (B2-O23 working area)
- **Dynamic Blank Calculation:** Auto-fills quadrants with randomly distributed blanks
- **Full Type Hints:** Industry-grade code with comprehensive documentation
- **CLI Tool:** Easy command-line interface with reduce/assign/pipeline commands

---

## Installation

```bash
git clone https://github.com/peptiderodriguez/scXML_neuron_excite_inhib.git
cd scXML_neuron_excite_inhib
pip install -e .
```

**Requirements:** Python ≥3.8, numpy ≥1.20.0

---

## Quick Start

### Complete Pipeline (Recommended)

Process both inhibitory and excitatory cells in one command:

```bash
scXML_neuron_excite_inhib pipeline \
  path/to/inhib.xml \
  path/to/excite.xml \
  --epsilon 60 \
  --seed 25 \
  --output-name experiment1 \
  --output-dir ./results
```

**This will:**
1. Reduce shapes with RDP algorithm (epsilon=60)
2. TSP optimize inhibitory cells
3. TSP optimize excitatory cells (starting from closest to last inhib)
4. Generate serpentine well pattern
5. Calculate and distribute blanks
6. Output final XML for Leica LMD7 + tracking CSV

### Individual Commands

**Shape reduction only:**
```bash
scXML_neuron_excite_inhib reduce input.xml --epsilon 60 --output-dir ./reduced
```

**Well assignment only** (requires pre-reduced files):
```bash
scXML_neuron_excite_inhib assign \
  inhib_reduced.xml \
  excite_reduced.xml \
  --output-name experiment1 \
  --seed 25
```

---

## Python API

```python
from scXML_neuron_excite_inhib import reduce_xml_file, assign_wells

# Reduce shapes
reduce_xml_file('input.xml', 'output_reduced.xml', epsilon=60)

# Assign wells with full optimization
assign_wells(
    'inhib_reduced.xml',
    'excite_reduced.xml',
    'output.xml',
    'tracking.csv',
    random_seed=25
)
```

---

## Pipeline Components

### 1. Shape Reduction
Applies Ramer-Douglas-Peucker algorithm to reduce polygon complexity while preserving shape geometry.

**Parameters:**
- `epsilon=60` - Distance threshold for point simplification
- Typical reduction: 95%+ fewer points
- CapID preservation available but not needed for standard workflow

### 2. TSP Optimization
Minimizes travel distance for laser microdissection collection.

**Algorithm:** Greedy nearest neighbor + 2-opt improvement

**Process:**
1. Optimize inhibitory cells independently
2. Find last inhibitory cell position
3. Find closest excitatory cell to last inhibitory
4. Optimize excitatory cells starting from closest point

**Result:** Minimized path distance + optimized inter-group transition

### 3. Serpentine Well Pattern
384-well plate collection pattern across B2-O23 working area.

**Pattern:** 4-phase serpentine with register switches
- Phase 1: Even columns (2,4,6...22), rows B→N
- Phase 2: Odd columns (23,21...3), row N (register switch)
- Phase 3: Odd columns (3,5,7...23), rows L→B
- Phase 4: Even columns (2,4,6...22), rows C→O

**Quadrants:** B2, B3, C2, C3 (77 wells each)

### 4. Dynamic Blank Distribution
Auto-calculates blanks needed to complete current quadrant, distributes randomly with seed=25 for reproducibility

---

## Output Files

### XML Output (for Leica LMD7)
Output file: `{output_name}_combined_wellassigned.xml`

**Contains:**
- Reduced shape coordinates (95% fewer points)
- Well position annotations as CapID tags (e.g., "B2", "D4", "F6")
- Combined inhibitory + excitatory cells in TSP-optimized order
- Randomly distributed blanks to complete quadrants

### CSV Tracking File
Output file: `{output_name}_tracking.csv`

**Columns:**
- `Well_Position` - Well location (e.g., B2, D4)
- `Serpentine_Order` - Collection order (0-230)
- `Sample_Index` - Sample number or "BLANK"
- `Source_File` - inhib or excite source
- `Original_Shape_Index` - Index in original file
- `Centroid_X`, `Centroid_Y` - Cell coordinates (pixels)
- `Quadrant` - B2, B3, C2, or C3

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

## CLI Reference

### Pipeline Command (Complete Workflow)
```bash
scXML_neuron_excite_inhib pipeline INHIB_FILE EXCITE_FILE [OPTIONS]

Options:
  --epsilon EPSILON         RDP distance threshold (default: 60)
  --seed SEED              Random seed for blanks (default: 25)
  --output-name NAME       Output filename prefix (default: scNeuron)
  --output-dir DIR         Output directory (default: same as input)
  --debug                  Show full tracebacks on error
```

### Reduce Command (Shape Reduction Only)
```bash
scXML_neuron_excite_inhib reduce INPUT_FILES... [OPTIONS]

Options:
  --epsilon EPSILON        RDP distance threshold (default: 60)
  --output-dir DIR         Output directory (default: same as input)
```

### Assign Command (Well Assignment Only)
```bash
scXML_neuron_excite_inhib assign INHIB_FILE EXCITE_FILE [OPTIONS]

Options:
  --output-name NAME       Output filename prefix (default: combined)
  --output-dir DIR         Output directory (default: same as input)
  --seed SEED             Random seed for blanks (default: 25)
```

---

## Configuration

### Key Parameters

**Epsilon (RDP threshold):**
- Default: 60
- Higher values = more aggressive reduction
- Typical range: 40-100
- Adjust via `--epsilon` flag

**Random Seed (blank distribution):**
- Default: 25
- Ensures reproducible blank positions
- Change via `--seed` flag for different random distribution

**Well Pattern:**
- 384-well plate, B2-O23 working area
- 77 wells per quadrant (hardcoded)
- 4-phase serpentine pattern
- Modify `serpentine.py` for custom patterns

---

## Troubleshooting

**Output files too large:**
```bash
# Increase epsilon for more aggressive compression
scXML_neuron_excite_inhib pipeline inhib.xml excite.xml --epsilon 80
```

**Need different blank distribution:**
```bash
# Change random seed
scXML_neuron_excite_inhib pipeline inhib.xml excite.xml --seed 42
```

**Custom plate format:**
- Modify `scXML_neuron_excite_inhib/serpentine.py`
- Update `generate_serpentine_wells()` function
- Adjust `QUADRANT_SIZE` constant

**Python API for advanced usage:**
```python
from scXML_neuron_excite_inhib import reduce_shapes, optimize_tsp, generate_serpentine_wells

# Custom workflow with fine-grained control
# See module docstrings for details
```

---

## Technical Notes

### About CapID Annotations
BIAS XML files can contain optional "CapID" annotations (identifiers for shapes).

**For the standard Leica LMD7 workflow:**
- CapID preservation is **not needed** and is disabled by default
- The well assignment step **replaces** any existing CapIDs with well positions (B2, D4, etc.)
- The tracking CSV provides all necessary metadata (cell type, position, order)

**When you might use CapID preservation:**
- Using shape reduction independently (without well assignment)
- Need to maintain original cell identifiers through reduction only
- Enable with `preserve_cap=True` parameter in reduction functions

**Bottom line:** For the complete pipeline (reduce → assign), CapID preservation is irrelevant since well positions become the new identifiers.

---

## Package Structure

```
scXML_neuron_excite_inhib/
├── __init__.py          # Package initialization, exports main functions
├── xml_utils.py         # XML parsing, writing, shape manipulation
├── tsp.py              # TSP algorithms (greedy, 2-opt, distance calculations)
├── serpentine.py       # Well pattern generation, quadrant logic
├── reduce.py           # RDP shape reduction algorithm
├── assign.py           # Well assignment orchestration
└── cli.py              # Command-line interface (argparse)
```

**All modules feature:**
- Comprehensive docstrings
- Full type hints (PEP 484)
- Error handling
- Verbose logging options

---

## Dependencies

**Required:**
- Python ≥3.8
- numpy ≥1.20.0

**Built-in modules:**
- argparse, csv, random, xml.etree.ElementTree

---

## Technical Notes

### Algorithm Characteristics
- **TSP:** Heuristic solution (greedy + 2-opt), not exact
- **Serpentine pattern:** Matches laser microdissection collection flow
- **Blanks:** Quality control samples, randomly distributed
- **Coordinates:** All tracking in pixels (BIAS coordinate system)

### Performance
- Typical shape reduction: 95%+ points removed
- TSP optimization: ~10-30% path improvement after 2-opt
- Transition optimization: 35-45% of average hop distance
- Processing time: <1 second for typical datasets (200-300 cells)

---

## Citation

If you use this package in your research, please cite:

```
scXML_neuron_excite_inhib: Automated pipeline for Leica LMD7 laser microdissection
MPIP Psilocybin Neuron Sorting Experiment
November 2025
https://github.com/peptiderodriguez/scXML_neuron_excite_inhib
```

---

## License

MIT License - See repository for details
