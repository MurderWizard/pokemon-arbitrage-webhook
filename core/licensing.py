"""
Licensing System - Deploy the infrastructure for other collectors
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import jwt
import hashlib
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LicenseFeatures:
    """Features enabled for this license"""
    max_assets: int
    supported_asset_types: list
    alerts_enabled: bool
    api_access: bool
    multi_user: bool
    white_label: bool
    support_level: str
    custom_integrations: bool

class LicenseManager:
    """Handle deployment licenses for collectors/businesses"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.active_licenses = {}
        
    def generate_license(
        self,
        client_id: str,
        features: LicenseFeatures,
        duration_days: int = 365
    ) -> str:
        """Generate a new license key"""
        expiration = datetime.utcnow() + timedelta(days=duration_days)
        
        payload = {
            "client_id": client_id,
            "features": {
                "max_assets": features.max_assets,
                "asset_types": features.supported_asset_types,
                "alerts": features.alerts_enabled,
                "api_access": features.api_access,
                "multi_user": features.multi_user,
                "white_label": features.white_label,
                "support": features.support_level,
                "custom_integrations": features.custom_integrations
            },
            "exp": expiration.timestamp()
        }
        
        license_key = jwt.encode(payload, self.secret_key, algorithm="HS256")
        self.active_licenses[client_id] = {
            "license_key": license_key,
            "features": features,
            "expiration": expiration
        }
        
        return license_key
        
    def validate_license(self, license_key: str) -> Optional[Dict]:
        """Validate a license key and return its features"""
        try:
            payload = jwt.decode(license_key, self.secret_key, algorithms=["HS256"])
            if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                logger.warning(f"Expired license for client {payload['client_id']}")
                return None
                
            return payload["features"]
            
        except jwt.InvalidTokenError:
            logger.error(f"Invalid license key: {license_key[:10]}...")
            return None
            
    def get_license_metrics(self, client_id: str) -> Dict:
        """Get usage metrics for a license"""
        if client_id not in self.active_licenses:
            return {}
            
        license_data = self.active_licenses[client_id]
        days_remaining = (license_data["expiration"] - datetime.utcnow()).days
        
        return {
            "status": "active" if days_remaining > 0 else "expired",
            "days_remaining": max(0, days_remaining),
            "features": license_data["features"].__dict__
        }
        
    def extend_license(self, client_id: str, additional_days: int) -> bool:
        """Extend an existing license"""
        if client_id not in self.active_licenses:
            return False
            
        current_license = self.active_licenses[client_id]
        new_expiration = current_license["expiration"] + timedelta(days=additional_days)
        
        # Generate new license with extended expiration
        self.generate_license(
            client_id=client_id,
            features=current_license["features"],
            duration_days=(new_expiration - datetime.utcnow()).days
        )
        
        return True
        
class DeploymentManager:
    """Handle system deployment for licensees"""
    
    def __init__(self, license_manager: LicenseManager):
        self.license_manager = license_manager
        
    def create_deployment(
        self,
        client_id: str,
        license_key: str,
        config: Dict
    ) -> Dict:
        """Create a new deployment for a client"""
        features = self.license_manager.validate_license(license_key)
        if not features:
            raise ValueError("Invalid or expired license")
            
        # Configure supported asset types
        asset_configs = []
        for asset_type in features["asset_types"]:
            if asset_type == "trading_cards":
                asset_configs.append({
                    "type": "trading_cards",
                    "grading_services": ["PSA", "BGS", "CGC"],
                    "vaults": ["eBay", "PWCC"]
                })
            elif asset_type == "coins":
                asset_configs.append({
                    "type": "coins",
                    "grading_services": ["PCGS", "NGC"],
                    "vaults": ["PCGS", "NGC"]
                })
            # Add more asset types as needed
            
        deployment = {
            "client_id": client_id,
            "features": features,
            "asset_configs": asset_configs,
            "api_keys": self._generate_api_keys(client_id) if features["api_access"] else None,
            "webhook_url": config.get("webhook_url"),
            "alert_settings": config.get("alert_settings", {}),
            "custom_integrations": config.get("custom_integrations", {})
        }
        
        return deployment
        
    def _generate_api_keys(self, client_id: str) -> Dict[str, str]:
        """Generate API keys for client access"""
        timestamp = datetime.utcnow().timestamp()
        base = f"{client_id}:{timestamp}"
        
        return {
            "api_key": hashlib.sha256(f"{base}:key".encode()).hexdigest(),
            "api_secret": hashlib.sha256(f"{base}:secret".encode()).hexdigest()
        }
