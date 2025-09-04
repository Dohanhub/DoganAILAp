#!/usr/bin/env python3
"""
Regulatory Authority Authentication Manager
Handles authentication for real Saudi and GCC regulatory authority APIs
"""

import os
import time
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

@dataclass
class AuthToken:
    token: str
    expires_at: datetime
    token_type: str = "Bearer"
    
    def is_expired(self) -> bool:
        return datetime.now() >= self.expires_at
    
    def is_expiring_soon(self, minutes: int = 5) -> bool:
        return datetime.now() >= (self.expires_at - timedelta(minutes=minutes))

class RegulatoryAuthManager:
    """Manages authentication for regulatory authority APIs"""
    
    def __init__(self):
        self.oauth_tokens: Dict[str, AuthToken] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize HTTP session for authentication"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def get_nca_headers(self) -> Dict[str, str]:
        """Get authentication headers for NCA API"""
        api_key = os.getenv("NCA_API_KEY")
        if not api_key or api_key.startswith("your_"):
            raise ValueError("NCA_API_KEY not configured")
        
        return {
            "X-NCA-API-Key": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "DoganAI-Compliance-Kit/1.0"
        }
    
    async def get_sama_headers(self) -> Dict[str, str]:
        """Get authentication headers for SAMA API (OAuth2)"""
        token = await self._get_sama_token()
        
        return {
            "Authorization": f"Bearer {token.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "DoganAI-Compliance-Kit/1.0"
        }
    
    async def _get_sama_token(self) -> AuthToken:
        """Get or refresh SAMA OAuth2 token"""
        if "SAMA" in self.oauth_tokens:
            token = self.oauth_tokens["SAMA"]
            if not token.is_expiring_soon():
                return token
        
        # Get new token
        client_id = os.getenv("SAMA_CLIENT_ID")
        client_secret = os.getenv("SAMA_CLIENT_SECRET")
        token_endpoint = os.getenv("SAMA_TOKEN_ENDPOINT", "https://auth.sama.gov.sa/oauth/token")
        
        if not client_id or not client_secret:
            raise ValueError("SAMA OAuth2 credentials not configured")
        
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "banking.read compliance.read regulations.read"
        }
        
        async with self.session.post(token_endpoint, data=data) as response:
            if response.status == 200:
                token_data = await response.json()
                
                expires_in = token_data.get("expires_in", 3600)
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                token = AuthToken(
                    token=token_data["access_token"],
                    expires_at=expires_at,
                    token_type=token_data.get("token_type", "Bearer")
                )
                
                self.oauth_tokens["SAMA"] = token
                logging.info("Successfully obtained SAMA OAuth2 token")
                return token
            else:
                error_text = await response.text()
                raise Exception(f"Failed to get SAMA token: {response.status} - {error_text}")
    
    async def get_moh_headers(self) -> Dict[str, str]:
        """Get authentication headers for MoH API"""
        api_key = os.getenv("MOH_API_KEY")
        if not api_key or api_key.startswith("your_"):
            raise ValueError("MOH_API_KEY not configured")
        
        return {
            "X-MOH-API-Key": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "DoganAI-Compliance-Kit/1.0"
        }
    
    async def get_citc_headers(self) -> Dict[str, str]:
        """Get authentication headers for CITC API"""
        api_key = os.getenv("CITC_API_KEY")
        if not api_key or api_key.startswith("your_"):
            raise ValueError("CITC_API_KEY not configured")
        
        return {
            "X-CITC-API-Key": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "DoganAI-Compliance-Kit/1.0"
        }
    
    async def get_cma_headers(self) -> Dict[str, str]:
        """Get authentication headers for CMA API"""
        api_key = os.getenv("CMA_API_KEY")
        if not api_key or api_key.startswith("your_"):
            raise ValueError("CMA_API_KEY not configured")
        
        return {
            "X-CMA-API-Key": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "DoganAI-Compliance-Kit/1.0"
        }
    
    async def get_headers_for_authority(self, authority: str) -> Dict[str, str]:
        """Get authentication headers for any regulatory authority"""
        authority_upper = authority.upper()
        
        if authority_upper == "NCA":
            return await self.get_nca_headers()
        elif authority_upper == "SAMA":
            return await self.get_sama_headers()
        elif authority_upper == "MOH":
            return await self.get_moh_headers()
        elif authority_upper == "CITC":
            return await self.get_citc_headers()
        elif authority_upper == "CMA":
            return await self.get_cma_headers()
        else:
            # GCC authorities use API key pattern
            api_key = os.getenv(f"{authority_upper}_API_KEY")
            if not api_key or api_key.startswith("your_"):
                raise ValueError(f"{authority_upper}_API_KEY not configured")
            
            return {
                f"X-{authority_upper}-API-Key": api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "DoganAI-Compliance-Kit/1.0"
            }
    
    async def test_authority_connection(self, authority: str, base_url: str) -> Dict[str, Any]:
        """Test connection to a regulatory authority API"""
        try:
            headers = await self.get_headers_for_authority(authority)
            
            # Test with health endpoint or basic info endpoint
            test_endpoints = ["/health", "/api/v1/info", "/api/v1/status", "/"]
            
            for endpoint in test_endpoints:
                url = f"{base_url}{endpoint}"
                try:
                    async with self.session.get(url, headers=headers) as response:
                        return {
                            "authority": authority,
                            "status": "success",
                            "status_code": response.status,
                            "endpoint": endpoint,
                            "response_time": response.headers.get("response-time", "unknown"),
                            "tested_at": datetime.now().isoformat()
                        }
                except Exception as endpoint_error:
                    continue
            
            return {
                "authority": authority,
                "status": "error",
                "error": "No responsive endpoints found",
                "tested_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "authority": authority,
                "status": "error",
                "error": str(e),
                "tested_at": datetime.now().isoformat()
            }
    
    async def test_all_authorities(self) -> Dict[str, Dict[str, Any]]:
        """Test connections to all configured regulatory authorities"""
        
        authorities = {
            "NCA": "https://api.nca.gov.sa",
            "SAMA": "https://api.sama.gov.sa", 
            "MOH": "https://api.moh.gov.sa",
            "CITC": "https://api.citc.gov.sa",
            "CMA": "https://api.cma.org.sa",
            "UAE_CENTRAL_BANK": "https://api.centralbank.ae",
            "QATAR_CENTRAL_BANK": "https://api.qcb.gov.qa",
            "BAHRAIN_CENTRAL_BANK": "https://api.cbb.gov.bh",
            "KUWAIT_CENTRAL_BANK": "https://api.cbk.gov.kw",
            "OMAN_CENTRAL_BANK": "https://api.cbo.gov.om"
        }
        
        results = {}
        
        for authority, base_url in authorities.items():
            result = await self.test_authority_connection(authority, base_url)
            results[authority] = result
            
            # Add delay between requests to respect rate limits
            await asyncio.sleep(1)
        
        return results
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate authentication configuration"""
        
        validation = {
            "status": "success",
            "missing_keys": [],
            "invalid_keys": [],
            "warnings": []
        }
        
        # Check Saudi authority keys
        saudi_keys = {
            "NCA_API_KEY": "Required for NCA API access",
            "SAMA_CLIENT_ID": "Required for SAMA OAuth2", 
            "SAMA_CLIENT_SECRET": "Required for SAMA OAuth2",
            "MOH_API_KEY": "Required for MoH API access",
            "CITC_API_KEY": "Required for CITC API access",
            "CMA_API_KEY": "Required for CMA API access"
        }
        
        for key, description in saudi_keys.items():
            value = os.getenv(key)
            if not value:
                validation["missing_keys"].append({"key": key, "description": description})
            elif value.startswith("your_"):
                validation["invalid_keys"].append({"key": key, "description": "Placeholder value not replaced"})
        
        # Set overall status
        if validation["missing_keys"] or validation["invalid_keys"]:
            validation["status"] = "error"
        
        return validation

# Global auth manager instance
auth_manager = RegulatoryAuthManager()

async def get_auth_manager() -> RegulatoryAuthManager:
    """Get the global authentication manager"""
    if not auth_manager.session:
        await auth_manager.initialize()
    return auth_manager
