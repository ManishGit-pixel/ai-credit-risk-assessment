import re
from typing import Dict, Any

class KYCService:
    @staticmethod
    def validate_aadhaar(aadhaar: str) -> bool:
        """Aadhaar must be exactly 12 digits"""
        return bool(re.match(r"^\d{12}$", aadhaar))

    @staticmethod
    def validate_pan(pan: str) -> bool:
        """PAN must be 10-character alphanumeric (uppercase)"""
        return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", pan))

    @classmethod
    def verify_kyc(cls, aadhaar: str = None, pan: str = None) -> Dict[str, Any]:
        """Mock KYC verification logic - Either Aadhaar or PAN is required"""
        if not aadhaar and not pan:
            return {
                "kyc_status": "Failed",
                "message": "KYC verification failed: Please provide Aadhaar or PAN"
            }

        errors = []
        is_aadhaar_present = bool(aadhaar)
        is_pan_present = bool(pan)

        if is_aadhaar_present:
            if not cls.validate_aadhaar(aadhaar):
                errors.append("Invalid Aadhaar format (must be 12 digits)")
        
        if is_pan_present:
            if not cls.validate_pan(pan):
                errors.append("Invalid PAN format (must be 5 uppercase letters + 4 digits + 1 uppercase letter)")

        if not errors:
            return {
                "kyc_status": "Verified",
                "message": f"KYC verification successful via {' & '.join([x for x, y in [('Aadhaar', is_aadhaar_present), ('PAN', is_pan_present)] if y])}"
            }
        else:
            return {
                "kyc_status": "Failed",
                "message": f"KYC verification failed: {', '.join(errors)}"
            }

kyc_service = KYCService()
