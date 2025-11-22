"""
Configuration management for py-address-screen.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    """Configuration class for the application."""
    
    # API Configuration
    chainalysis_api_key: str
    chainalysis_base_url: str = "https://api.chainalysis.com"
    
    # Rate limiting
    rate_limit: int = 5  # requests per second
    max_concurrent_requests: int = 10
    
    # Output configuration
    include_indirect_exposure: bool = True
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        api_key = os.getenv("CHAINALYSIS_API_KEY")
        if not api_key:
            raise ValueError("CHAINALYSIS_API_KEY environment variable is required")
        
        return cls(
            chainalysis_api_key=api_key,
            chainalysis_base_url=os.getenv("CHAINALYSIS_BASE_URL", "https://api.chainalysis.com"),
            rate_limit=int(os.getenv("RATE_LIMIT", "5")),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "10")),
            include_indirect_exposure=os.getenv("INCLUDE_INDIRECT_EXPOSURE", "true").lower() == "true"
        )