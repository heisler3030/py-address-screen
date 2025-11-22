"""
Simple example showing DataFrame usage for documentation
"""
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import py_address_screen
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from py_address_screen import screen_dataframe

# Create a DataFrame with addresses
df = pd.DataFrame({
    'address': ['1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2', '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy']
})

print("Input DataFrame:")
print(df)

# Screen addresses (synchronous)
result_df = screen_dataframe(df, address_column='address', include_indirect=False)

print(f"\nScreened {len(result_df)} addresses")
print("\nKey results:")
print(result_df[['address', 'screenStatus', 'risk', 'riskReason']].to_string(index=False))