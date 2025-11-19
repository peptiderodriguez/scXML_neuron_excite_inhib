"""
Command-line interface for single-cell sorting pipeline
"""
import argparse
import os
import sys
from typing import List

from .reduce import reduce_xml_file
from .assign import assign_wells


def cmd_reduce(args):
    """Execute reduce command"""
    print(f"=== Shape Reduction (epsilon={args.epsilon}) ===\n")

    for input_file in args.input_files:
        if not os.path.exists(input_file):
            print(f"Error: File not found: {input_file}", file=sys.stderr)
            continue

        # Generate output filename
        base, ext = os.path.splitext(input_file)
        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            basename = os.path.basename(base)
            output_file = os.path.join(args.output_dir, f"{basename}_reduced{ext}")
        else:
            output_file = f"{base}_reduced{ext}"

        try:
            reduce_xml_file(input_file, output_file, epsilon=args.epsilon, verbose=True)
        except Exception as e:
            print(f"Error processing {input_file}: {e}", file=sys.stderr)
            if args.debug:
                raise

    print("=== Reduction Complete ===")


def cmd_assign(args):
    """Execute assign command"""
    # Validate input files
    if not os.path.exists(args.inhib_file):
        print(f"Error: Inhibitory file not found: {args.inhib_file}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.excite_file):
        print(f"Error: Excitatory file not found: {args.excite_file}", file=sys.stderr)
        sys.exit(1)

    # Generate output filenames
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        output_xml = os.path.join(args.output_dir, args.output_name + ".xml")
        output_csv = os.path.join(args.output_dir, args.output_name + "_tracking.csv")
    else:
        output_dir = os.path.dirname(args.inhib_file)
        output_xml = os.path.join(output_dir, args.output_name + ".xml")
        output_csv = os.path.join(output_dir, args.output_name + "_tracking.csv")

    try:
        assign_wells(
            args.inhib_file,
            args.excite_file,
            output_xml,
            output_csv,
            random_seed=args.seed,
            verbose=True
        )
    except Exception as e:
        print(f"Error during well assignment: {e}", file=sys.stderr)
        if args.debug:
            raise
        sys.exit(1)


def cmd_pipeline(args):
    """Execute complete pipeline (reduce + assign)"""
    print("=== Complete Single-Cell Sorting Pipeline ===\n")

    # Step 1: Reduce shapes
    print("Step 1: Shape Reduction\n")

    # Generate reduced filenames
    inhib_base, inhib_ext = os.path.splitext(args.inhib_file)
    excite_base, excite_ext = os.path.splitext(args.excite_file)

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        inhib_reduced = os.path.join(args.output_dir,
                                     f"{os.path.basename(inhib_base)}_reduced{inhib_ext}")
        excite_reduced = os.path.join(args.output_dir,
                                      f"{os.path.basename(excite_base)}_reduced{excite_ext}")
    else:
        inhib_reduced = f"{inhib_base}_reduced{inhib_ext}"
        excite_reduced = f"{excite_base}_reduced{excite_ext}"

    try:
        reduce_xml_file(args.inhib_file, inhib_reduced, epsilon=args.epsilon, verbose=True)
        reduce_xml_file(args.excite_file, excite_reduced, epsilon=args.epsilon, verbose=True)
    except Exception as e:
        print(f"Error during reduction: {e}", file=sys.stderr)
        if args.debug:
            raise
        sys.exit(1)

    # Step 2: Assign wells
    print("\nStep 2: Well Assignment\n")

    output_xml = os.path.join(args.output_dir if args.output_dir else os.path.dirname(args.inhib_file),
                              args.output_name + "_combined_wellassigned.xml")
    output_csv = os.path.join(args.output_dir if args.output_dir else os.path.dirname(args.inhib_file),
                              args.output_name + "_tracking.csv")

    try:
        assign_wells(
            inhib_reduced,
            excite_reduced,
            output_xml,
            output_csv,
            random_seed=args.seed,
            verbose=True
        )
    except Exception as e:
        print(f"Error during well assignment: {e}", file=sys.stderr)
        if args.debug:
            raise
        sys.exit(1)

    print("\n=== Pipeline Complete ===")
    print(f"Output files:")
    print(f"  XML: {output_xml}")
    print(f"  CSV: {output_csv}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='scXML_neuron_excite_inhib',
        description='Single-cell sorting pipeline for Leica LMD7 well assignment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Reduce shapes in XML files
  scXML_neuron_excite_inhib reduce cells_inhib.xml cells_excite.xml --epsilon 60

  # Assign wells to reduced files
  scXML_neuron_excite_inhib assign inhib_reduced.xml excite_reduced.xml --output-name experiment1

  # Run complete pipeline
  scXML_neuron_excite_inhib pipeline cells_inhib.xml cells_excite.xml --epsilon 60 --output-dir ./output
        """
    )

    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (show full tracebacks)')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Reduce command
    parser_reduce = subparsers.add_parser('reduce', help='Reduce shape complexity with RDP algorithm')
    parser_reduce.add_argument('input_files', nargs='+', help='Input XML files to reduce')
    parser_reduce.add_argument('--epsilon', type=float, default=60,
                             help='RDP distance threshold (default: 60)')
    parser_reduce.add_argument('--output-dir', help='Output directory (default: same as input)')
    parser_reduce.set_defaults(func=cmd_reduce)

    # Assign command
    parser_assign = subparsers.add_parser('assign', help='Assign cells to 384-well plate')
    parser_assign.add_argument('inhib_file', help='Inhibitory cells XML file')
    parser_assign.add_argument('excite_file', help='Excitatory cells XML file')
    parser_assign.add_argument('--output-name', default='combined',
                              help='Output filename prefix (default: combined)')
    parser_assign.add_argument('--output-dir', help='Output directory (default: same as input)')
    parser_assign.add_argument('--seed', type=int, default=25,
                              help='Random seed for blank distribution (default: 25)')
    parser_assign.set_defaults(func=cmd_assign)

    # Pipeline command (complete workflow)
    parser_pipeline = subparsers.add_parser('pipeline', help='Run complete pipeline (reduce + assign)')
    parser_pipeline.add_argument('inhib_file', help='Inhibitory cells XML file')
    parser_pipeline.add_argument('excite_file', help='Excitatory cells XML file')
    parser_pipeline.add_argument('--epsilon', type=float, default=60,
                                help='RDP distance threshold (default: 60)')
    parser_pipeline.add_argument('--seed', type=int, default=25,
                                help='Random seed for blank distribution (default: 25)')
    parser_pipeline.add_argument('--output-name', default='scNeuron',
                                help='Output filename prefix (default: scNeuron)')
    parser_pipeline.add_argument('--output-dir', help='Output directory (default: same as input)')
    parser_pipeline.set_defaults(func=cmd_pipeline)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
