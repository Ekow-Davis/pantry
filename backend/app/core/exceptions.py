from fastapi import HTTPException, status


class MealWiseException(HTTPException):
    """Base exception for all MealWise API errors."""
    pass


class NotFoundException(MealWiseException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found."
        )


class UnauthorizedException(MealWiseException):
    def __init__(self, detail: str = "Not authenticated."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(MealWiseException):
    def __init__(self, detail: str = "You do not have permission to perform this action."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ConflictException(MealWiseException):
    def __init__(self, detail: str = "A conflict occurred."):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class BadRequestException(MealWiseException):
    def __init__(self, detail: str = "Bad request."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class UnprocessableException(MealWiseException):
    def __init__(self, detail: str = "Unprocessable entity."):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
