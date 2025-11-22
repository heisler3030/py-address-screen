"""
Chainalysis API client for address screening.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_exponential)

from .config import Config

logger = logging.getLogger(__name__)

class ChanalysisAPIClient:
    """Async client for Chainalysis Address Screening API."""
    
    def __init__(self, config: Config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_semaphore = asyncio.Semaphore(config.rate_limit)
        self._categories: Optional[List[str]] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "Token": self.config.chainalysis_api_key,
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(aiohttp.ClientError),
        reraise=True
    )
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a rate-limited request to the API."""
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        async with self._rate_limit_semaphore:
            url = f"{self.config.chainalysis_base_url}{endpoint}"
            
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        # For non-200 status codes, raise for status which will raise an exception
                        response.raise_for_status()
                        # This line should never be reached due to the exception above
                        return {}
                        
            except aiohttp.ClientError as e:
                logger.error(f"Request failed: {e}")
                raise
            
            # Rate limiting - wait between requests
            await asyncio.sleep(1.0 / self.config.rate_limit)
    
    async def fetch_categories(self) -> List[str]:
        """Fetch available categories from the Chainalysis API."""
        if self._categories is not None:
            return self._categories
            
        try:
            endpoint = "/api/kyt/v2/categories"
            result = await self._make_request(endpoint)
            
            # Extract category names from the API response
            categories = []
            if isinstance(result, dict) and "categories" in result:
                # API returns {"categories": [{"categoryId": X, "categoryName": "name"}, ...]}
                categories = [cat.get("categoryName", "") for cat in result["categories"] if cat.get("categoryName")]
            else:
                # Raise exception if API format is unexpected
                raise ValueError(f"Unexpected categories API response format: {type(result)}")
            
            if not categories:
                raise ValueError("No categories returned from API")
            
            self._categories = sorted(categories)
            logger.info(f"Fetched {len(self._categories)} categories from API")
            return self._categories
            
        except Exception as e:
            logger.error(f"Failed to fetch categories from API: {e}")
            raise ValueError(f"Cannot proceed without categories from API: {e}")

    
    async def screen_address(self, address: str) -> Dict[str, Any]:
        endpoint = f"/api/risk/v2/entities/{address}"
        
        try:
            result = await self._make_request(endpoint)
            return await self._format_screening_result(address, result)
        except Exception as e:
            logger.error(f"Failed to screen address {address}: {e}")
            
            # Simplify error message for aiohttp ClientResponseError
            error_message = str(e)
            if isinstance(e, aiohttp.ClientResponseError):
                # Extract status code and message from ClientResponseError
                error_message = f"{e.status} {e.message}"
            
            return self._format_error_result(address, error_message)
    
    async def screen_addresses(self, addresses: List[str]) -> List[Dict[str, Any]]:
        """Screen multiple addresses concurrently."""
        # Fetch categories once before screening all addresses
        await self.fetch_categories()
        
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        async def screen_with_semaphore(address: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.screen_address(address)
        
        tasks = [screen_with_semaphore(addr) for addr in addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                formatted_results.append(self._format_error_result(addresses[i], str(result)))
            else:
                formatted_results.append(result)
                
        return formatted_results
    
    async def _format_screening_result(self, address: str, api_result: Dict[str, Any]) -> Dict[str, Any]:
        if self._categories is None:
            raise ValueError("Categories not initialized. Call fetch_categories() first.")
        categories = self._categories
        
        # Extract basic information
        screen_status = api_result.get("status", "COMPLETE").lower()
        risk = api_result.get("risk", "")
        risk_reason = api_result.get("riskReason", "")
        
        # Extract cluster information
        cluster = api_result.get("cluster")
        category = cluster.get("category", "") if cluster else ""
        name = cluster.get("name", "") if cluster else ""
        
        # Create the row data structure
        row_data = {
            "address": address,
            "screenStatus": screen_status,
            "risk": risk,
            "riskReason": risk_reason,
            "category": category,
            "name": name
        }
        
        # Process exposures for each category
        exposures = api_result.get("exposures", [])
        
        for cat in categories:
            if self.config.include_indirect_exposure:
                # Find direct and indirect exposures for this category
                direct_exposure = None
                indirect_exposure = None
                
                for exposure in exposures:
                    if exposure.get("category") == cat:
                        if exposure.get("exposureType") == "direct":
                            direct_exposure = exposure.get("value")
                        elif exposure.get("exposureType") == "indirect":
                            indirect_exposure = exposure.get("value")
                
                row_data[f"{cat}_direct"] = direct_exposure
                row_data[f"{cat}_indirect"] = indirect_exposure
            else:
                # Find any non-indirect exposure (constructed to work with both direct and indirect API keys)
                exposure_value = None
                for exposure in exposures:
                    if exposure.get("category") == cat and exposure.get("exposureType") != "indirect":
                        exposure_value = exposure.get("value")
                        break
                
                row_data[f"{cat}"] = exposure_value
        
        return {
            "address": address,
            "status": "success",
            "row_data": row_data,
            "raw_response": api_result
        }
    
    def _format_error_result(self, address: str, error_message: str) -> Dict[str, Any]:
        """Format an error result."""
        return {
            "address": address,
            "status": "error",
            "error": error_message,
            "row_data": {
                "address": address,
                "screenStatus": error_message,
                "risk": "",
                "riskReason": "",
                "category": "",
                "name": ""
            }
        }