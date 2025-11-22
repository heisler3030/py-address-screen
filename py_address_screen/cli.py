"""
Command-line interface for py-address-screen.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .api_client import ChanalysisAPIClient
from .config import Config
from .csv_processor import CSVProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    help='Output file path (default: adds _screened to input filename)'
)
@click.option(
    '--address-column', '--column', '-c',
    default='address',
    help='Name of the column containing addresses (default: "address")'
)
@click.option(
    '--rate-limit', '-r',
    type=int,
    default=5,
    help='API requests per second (default: 5)'
)
@click.option(
    '--max-concurrent', '-m',
    type=int,
    default=10,
    help='Maximum concurrent requests (default: 10)'
)
@click.option(
    '--no-indirect',
    is_flag=True,
    help='Exclude indirect exposure from screening'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose logging'
)
def main(
    input_file: Path,
    output: Optional[Path],
    address_column: str,
    rate_limit: int,
    max_concurrent: int,
    no_indirect: bool,
    verbose: bool
):
    """
    Screen cryptocurrency addresses using the Chainalysis API.
    
    INPUT_FILE: Path to CSV file containing addresses to screen.
    """
    asyncio.run(async_main(
        input_file, output, address_column, rate_limit, 
        max_concurrent, no_indirect, verbose
    ))

async def async_main(
    input_file: Path,
    output: Optional[Path],
    address_column: str,
    rate_limit: int,
    max_concurrent: int,
    no_indirect: bool,
    verbose: bool
):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load configuration
        config = Config.from_env()
        
        # Override config with CLI options
        config.rate_limit = rate_limit
        config.max_concurrent_requests = max_concurrent
        config.include_indirect_exposure = not no_indirect
        
        # Set default output path if not provided
        if output is None:
            output = input_file.parent / f"{input_file.stem}_screened{input_file.suffix}"
        
        logger.info(f"Starting address screening: {input_file} -> {output}")
        logger.info(f"Rate limit: {rate_limit} req/s, Max concurrent: {max_concurrent}")
        logger.info(f"Include indirect exposure: {not no_indirect}")
        
        # Validate input file
        if not CSVProcessor.validate_csv_format(str(input_file), [address_column]):
            logger.error(f"Invalid CSV format or missing column '{address_column}'")
            sys.exit(1)
        
        # Read addresses from CSV
        addresses = CSVProcessor.read_addresses_from_csv(str(input_file), address_column)
        
        if not addresses:
            logger.error("No addresses found in input file")
            sys.exit(1)
        
        logger.info(f"Found {len(addresses)} addresses to screen")
        
        # Screen addresses
        async with ChanalysisAPIClient(config) as client:
            results = await client.screen_addresses(addresses)
        
        # Write results
        CSVProcessor.write_results_to_csv(results, str(output), not no_indirect)
        
        # Summary
        success_count = sum(1 for r in results if r.get("status") == "success")
        error_count = len(results) - success_count
        
        logger.info(f"Screening complete: {success_count} successful, {error_count} errors")
        logger.info(f"Results written to: {output}")
        
        if error_count > 0:
            logger.warning(f"{error_count} addresses failed to screen - check output file for details")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()