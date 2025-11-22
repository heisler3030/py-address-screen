"""
Example: Using py-address-screen with DataFrames for Databricks
This example shows how to use the package with pandas DataFrames.
"""
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import py_address_screen
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio

import pandas as pd

from py_address_screen import screen_addresses_from_dataframe, screen_dataframe


def databricks_example():
    """Example usage pattern for Databricks notebooks"""
    
    print("=== Databricks DataFrame Example ===\n")
    
    # Example 1: Create a test DataFrame (simulating data from Spark)
    sample_data = pd.DataFrame({
        'transaction_id': ['tx1', 'tx2', 'tx3'],
        'wallet_address': [
            '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',  # Known risky address
            '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',    # Another test address
            'invalid_address'                        # Invalid address for testing
        ],
        'amount': [100.5, 250.0, 75.3]
    })
    
    print("Original DataFrame:")
    print(sample_data)
    print(f"Shape: {sample_data.shape}\n")
    
    # Example 2: Screen addresses synchronously
    print("Screening addresses synchronously...")
    try:
        screened_df = screen_dataframe(
            sample_data, 
            address_column='wallet_address',
            include_indirect=False  # Faster for this example
        )
        
        print(f"Screened DataFrame shape: {screened_df.shape}")
        print("\nKey columns from screening results:")
        key_columns = ['address', 'screenStatus', 'risk', 'riskReason', 'category']
        for col in key_columns:
            if col in screened_df.columns:
                print(f"  {col}: {screened_df[col].tolist()}")
        
    except Exception as e:
        print(f"Error during screening: {e}")
        return
    
    # Example 3: Filter high-risk addresses
    print("\n=== Risk Analysis ===")
    if 'risk' in screened_df.columns:
        risk_summary = screened_df['risk'].value_counts()
        print("Risk level summary:")
        for risk_level, count in risk_summary.items():
            print(f"  {risk_level}: {count} addresses")
        
        # Filter high-risk addresses
        high_risk = screened_df[screened_df['risk'].isin(['High', 'Severe'])]
        if not high_risk.empty:
            print(f"\nFound {len(high_risk)} high-risk addresses:")
            for _, row in high_risk.iterrows():
                print(f"  {row['address']}: {row['risk']} - {row['riskReason']}")
    
    # Example 4: Empty DataFrame handling
    print("\n=== Empty DataFrame Test ===")
    empty_df = pd.DataFrame({'address': []})
    empty_result = screen_dataframe(empty_df)
    print(f"Empty DataFrame result shape: {empty_result.shape}")
    
    print("\n=== Example Complete ===")

async def async_example():
    """Example of asynchronous screening"""
    print("\n=== Async Screening Example ===\n")
    
    df = pd.DataFrame({
        'crypto_address': ['1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2']
    })
    
    print("Screening asynchronously...")
    result = await screen_addresses_from_dataframe(
        df, 
        address_column='crypto_address',
        include_indirect=True
    )
    
    print(f"Async result shape: {result.shape}")
    if not result.empty:
        print(f"Address status: {result['screenStatus'].iloc[0]}")
        print(f"Risk level: {result['risk'].iloc[0]}")

if __name__ == "__main__":
    # Run the synchronous example
    databricks_example()
    
    # Run the asynchronous example
    print("\nRunning async example...")
    asyncio.run(async_example())