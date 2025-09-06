from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    """Custom HTTP exception class."""
    pass


class UserNotFoundError(CustomHTTPException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )


class ItemNotFoundError(CustomHTTPException):
    def __init__(self, item_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )


class UserAlreadyExistsError(CustomHTTPException):
    def __init__(self, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with {field} '{value}' already exists"
        )


class InsufficientPermissionsError(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to perform this action"
        )


class InvalidCredentialsError(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
