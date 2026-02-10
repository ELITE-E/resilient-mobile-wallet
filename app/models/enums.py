from enum import Enum

class kycStatus(str,Enum):
    PENDING="PENDIND"
    VERIFIED="VERIFIED"
    REJECTED="REJECTED"

class DepositStatus(str,Enum):
    PENDING_CALLBACK="PENDING_CALLBACK"
    SUCCESS="SUCCESS"
    FAILED="FAILED"
    