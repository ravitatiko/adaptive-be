from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> JSONResponse:
    """Create a standardized success response."""
    response_data = {
        "success": True,
        "message": message,
        "data": data
    }
    return JSONResponse(content=response_data, status_code=status_code)


def error_response(
    message: str = "Error",
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> JSONResponse:
    """Create a standardized error response."""
    response_data = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "details": details
    }
    return JSONResponse(content=response_data, status_code=status_code)
