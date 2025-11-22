"""
Command line interface for py-address-screen.
"""
import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from . import print_usage, screen_addresses_from_file
from .config import Config


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Screen cryptocurrency addresses using Chainalysis API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s addresses.csv
  %(prog)s addresses.csv results.csv
  %(prog)s --help

The input CSV file must contain an 'address' column with cryptocurrency addresses.
Output file will be created automatically if not specified.
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Input CSV file containing cryptocurrency addresses"
    )
    
    parser.add_argument(
        "output_file",
        nargs="?",
        help="Output CSV file for screening results (optional)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="py-address-screen 1.0.0"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for the CLI application."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Validate input file
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
            sys.exit(1)
        
        if not input_path.suffix.lower() == '.csv':
            print(f"Error: Input file must be a CSV file.", file=sys.stderr)
            sys.exit(1)
        
        # Determine output file
        if args.output_file:
            output_file = args.output_file
        else:
            # Generate output filename by adding '_screened' before extension
            stem = input_path.stem
            suffix = input_path.suffix
            output_file = str(input_path.parent / f"{stem}_screened{suffix}")
        
        # Check configuration
        config = Config.from_env()
        if not config.chainalysis_api_key:
            print("Error: CHAINALYSIS_API_KEY environment variable not set.", file=sys.stderr)
            print_usage()
            sys.exit(1)
        
        # Run the screening
        print(f"Screening addresses from: {args.input_file}")
        print(f"Output will be saved to: {output_file}")
        print()
        
        asyncio.run(screen_addresses_from_file(Path(args.input_file), Path(output_file)))
        
        print(f"\nScreening complete! Results saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()