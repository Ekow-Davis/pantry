from fastapi import APIRouter
from sqlalchemy import select
from app.api.deps import DbDep, CurrentUser
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import ConflictException, UnauthorizedException
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])

_TIMEZONE_MAP = {
    "Ghana": "Africa/Accra",
    "Nigeria": "Africa/Lagos",
    "Kenya": "Africa/Nairobi",
    "South Africa": "Africa/Johannesburg",
    "United Kingdom": "Europe/London",
    "United States": "America/New_York",
    "Canada": "America/Toronto",
    "Australia": "Australia/Sydney",
}


@router.post("/register", response_model=UserOut, status_code=201)
async def register(payload: RegisterRequest, db: DbDep):
    if (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none():
        raise ConflictException("An account with this email already exists.")
    if (await db.execute(select(User).where(User.username == payload.username))).scalar_one_or_none():
        raise ConflictException("This username is already taken.")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        country=payload.country,
        timezone=_TIMEZONE_MAP.get(payload.country or "", "Africa/Accra"),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: DbDep):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password.")
    if not user.is_active:
        raise UnauthorizedException("Account is disabled.")
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: DbDep):
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise UnauthorizedException("Invalid or expired refresh token.")
    result = await db.execute(select(User).where(User.id == decoded.get("sub")))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or disabled.")
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserOut)
async def get_me(current_user: CurrentUser):
    return current_user
