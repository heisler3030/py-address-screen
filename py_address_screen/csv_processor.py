"""
CSV processing utilities for address screening.
"""

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

class CSVProcessor:
    """Handles reading and writing CSV files for address screening."""
    
    @staticmethod
    def read_addresses_from_csv(file_path: str, address_column: str = "address") -> List[str]:
        """
        Read cryptocurrency addresses from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            address_column: Name of the column containing addresses
            
        Returns:
            List of addresses
        """
        addresses = []
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            
            if address_column not in df.columns:
                raise ValueError(f"Column '{address_column}' not found in CSV. Available columns: {list(df.columns)}")
            
            # Extract addresses and remove duplicates while preserving order
            addresses_series = df[address_column].dropna().astype(str)
            addresses = list(dict.fromkeys(addresses_series.tolist()))
            
            logger.info(f"Read {len(addresses)} unique addresses from {file_path}")
            return addresses
            
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise
    
    @staticmethod
    def write_results_to_csv(results: List[Dict[str, Any]], output_path: str, include_indirect: bool = True) -> None:
        """
        Write screening results to a CSV file.
        
        Args:
            results: List of screening result dictionaries
            output_path: Path for the output CSV file
            include_indirect: Whether to include indirect exposure columns
        """
        if not results:
            logger.warning("No results to write")
            return
        
        try:
            # Extract categories from successful results
            categories_set = set()
            
            for result in results:
                if result.get("status") == "success" and "row_data" in result:
                    row_data = result["row_data"]
                    for key in row_data.keys():
                        if include_indirect:
                            if key.endswith("_direct"):
                                categories_set.add(key[:-7])
                            elif key.endswith("_indirect"):
                                categories_set.add(key[:-9])
                        else:
                            if key not in ["address", "screenStatus", "risk", "riskReason", "category", "name"]:
                                categories_set.add(key)
            
            categories = sorted(list(categories_set))
            
            if not categories:
                raise ValueError("No exposure categories found in results")
            
            # Build header
            header = ["address", "screenStatus", "risk", "riskReason", "category", "name"]
            for cat in categories:
                if include_indirect:
                    header.extend([f"{cat}_direct", f"{cat}_indirect"])
                else:
                    header.append(cat)
            
            # Build rows - all results have row_data now
            rows = []
            for result in results:
                row_data = result["row_data"]
                
                # Basic fields
                row = [
                    row_data.get("address", ""),
                    row_data.get("screenStatus", ""),
                    row_data.get("risk", ""),
                    row_data.get("riskReason", ""),
                    row_data.get("category", ""),
                    row_data.get("name", "")
                ]
                
                # Category exposures
                for cat in categories:
                    if include_indirect:
                        direct_val = row_data.get(f"{cat}_direct", "")
                        indirect_val = row_data.get(f"{cat}_indirect", "")
                        row.extend([direct_val or "", indirect_val or ""])
                    else:
                        val = row_data.get(cat, "")
                        row.append(val or "")
                
                rows.append(row)
            
            # Write to CSV
            df = pd.DataFrame(rows, columns=header)
            df.to_csv(output_path, index=False)
            
            logger.info(f"Results written to {output_path}")
            
        except Exception as e:
            logger.error(f"Error writing results to CSV: {e}")
            raise
    
    @staticmethod
    def results_to_dataframe(results: List[Dict[str, Any]], include_indirect: bool = True) -> pd.DataFrame:
        """
        Convert screening results to a pandas DataFrame.
        
        Args:
            results: List of screening result dictionaries
            include_indirect: Whether to include indirect exposure columns
            
        Returns:
            DataFrame with screening results
        """
        if not results:
            logger.warning("No results to convert")
            return pd.DataFrame()

        try:
            # Extract categories from successful results
            categories_set = set()
            
            for result in results:
                if result.get("status") == "success" and "row_data" in result:
                    row_data = result["row_data"]
                    for key in row_data.keys():
                        if include_indirect:
                            if key.endswith("_direct"):
                                categories_set.add(key[:-7])
                            elif key.endswith("_indirect"):
                                categories_set.add(key[:-9])
                        else:
                            if key not in ["address", "screenStatus", "risk", "riskReason", "category", "name"]:
                                categories_set.add(key)
            
            categories = sorted(list(categories_set))
            
            # Build header
            columns = ["address", "screenStatus", "risk", "riskReason", "category", "name"]
            for cat in categories:
                if include_indirect:
                    columns.extend([f"{cat}_direct", f"{cat}_indirect"])
                else:
                    columns.append(cat)
            
            # Build rows - all results have row_data now
            rows = []
            for result in results:
                row_data = result["row_data"]
                
                # Basic fields
                row = [
                    row_data.get("address", ""),
                    row_data.get("screenStatus", ""),
                    row_data.get("risk", ""),
                    row_data.get("riskReason", ""),
                    row_data.get("category", ""),
                    row_data.get("name", "")
                ]
                
                # Category exposures
                for cat in categories:
                    if include_indirect:
                        direct_val = row_data.get(f"{cat}_direct", "")
                        indirect_val = row_data.get(f"{cat}_indirect", "")
                        row.extend([direct_val or "", indirect_val or ""])
                    else:
                        val = row_data.get(cat, "")
                        row.append(val or "")
                
                rows.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=columns)
            
            logger.info(f"Converted {len(results)} results to DataFrame with shape {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error converting results to DataFrame: {e}")
            raise
    
    @staticmethod
    def validate_csv_format(file_path: str, required_columns: Optional[List[str]] = None) -> bool:
        """
        Validate that a CSV file has the required format.
        
        Args:
            file_path: Path to the CSV file
            required_columns: List of required column names
            
        Returns:
            True if valid, False otherwise
        """
        if required_columns is None:
            required_columns = ["address"]
        
        try:
            df = pd.read_csv(file_path, nrows=1)  # Read only first row to check columns
            
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating CSV format: {e}")
            return False