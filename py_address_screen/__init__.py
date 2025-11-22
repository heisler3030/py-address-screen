"""
py-address-screen: A Python utility for cryptocurrency address screening.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from .api_client import ChanalysisAPIClient
from .config import Config
from .csv_processor import CSVProcessor

__version__ = "1.0.0"
__author__ = "Python Port of node-address-screen"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def screen_addresses_from_file(
    input_file: Path,
    output_file: Optional[Path] = None,
    include_indirect: bool = True
):
    """
    Screen cryptocurrency addresses from a CSV file.
    
    Args:
        input_file: Path to CSV file containing addresses to screen
        output_file: Output file path (default: adds _screened to input filename)
        include_indirect: Include indirect exposure in results (default: True)
    """
    try:
        # Load configuration
        config = Config.from_env()
        config.include_indirect_exposure = include_indirect
        
        # Set default output path if not provided
        if output_file is None:
            output_file = input_file.parent / f"{input_file.stem}_screened{input_file.suffix}"
        
        logger.info(f"Starting address screening: {input_file} -> {output_file}")
        logger.info(f"Rate limit: {config.rate_limit} req/s, Max concurrent: {config.max_concurrent_requests}")
        logger.info(f"Include indirect exposure: {include_indirect}")
        
        # Validate input file
        if not CSVProcessor.validate_csv_format(str(input_file), ["address"]):
            logger.error(f"Invalid CSV format or missing column 'address'")
            sys.exit(1)
        
        # Read addresses from CSV
        addresses = CSVProcessor.read_addresses_from_csv(str(input_file), "address")
        
        if not addresses:
            logger.error("No addresses found in input file")
            sys.exit(1)
        
        logger.info(f"Found {len(addresses)} addresses to screen")
        
        # Screen addresses
        async with ChanalysisAPIClient(config) as client:
            results = await client.screen_addresses(addresses)
        
        # Write results
        CSVProcessor.write_results_to_csv(results, str(output_file), include_indirect)
        
        # Summary
        success_count = sum(1 for r in results if r.get("status") == "success")
        error_count = len(results) - success_count
        
        logger.info(f"Screening complete: {success_count} successful, {error_count} errors")
        logger.info(f"Results written to: {output_file}")
        
        if error_count > 0:
            logger.warning(f"{error_count} addresses failed to screen - check output file for details")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def print_usage():
    """Print usage information."""
    print("py-address-screen: Cryptocurrency address screening using Chainalysis API")
    print()
    print("Usage:")
    print("  python main.py <input_file.csv> [output_file.csv]")
    print()
    print("Arguments:")
    print("  input_file.csv     Path to CSV file containing addresses to screen")
    print("  output_file.csv    Path for output file (optional)")
    print("                     Default: adds '_screened' to input filename")
    print()
    print("Examples:")
    print("  python main.py addresses.csv")
    print("  python main.py addresses.csv results.csv")
    print("  python main.py /path/to/my_addresses.csv /path/to/results.csv")
    print()
    print("Configuration:")
    print("  Set CHAINALYSIS_API_KEY environment variable or create .env file")
    print("  See README.md for full configuration options")


def main():
    """Main entry point for the application."""
    # Check if input file argument is provided
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print_usage()
        sys.exit(1)
    
    input_file_path = sys.argv[1]
    input_file = Path(input_file_path)
    
    # Check if file exists
    if not input_file.exists():
        print(f"Error: File '{input_file_path}' not found")
        print()
        print_usage()
        sys.exit(1)
    
    # Get output file if provided
    output_file = None
    if len(sys.argv) == 3:
        output_file = Path(sys.argv[2])
    
    asyncio.run(screen_addresses_from_file(input_file, output_file=output_file))