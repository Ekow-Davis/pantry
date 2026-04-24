from fastapi import APIRouter
from sqlalchemy import select
from app.api.deps import DbDep, CurrentUser
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import ConflictException, UnauthorizedException, BadRequestException
from app.models import User
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserOut, MessageResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(payload: RegisterRequest, db: DbDep):
    # Check duplicate email
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise ConflictException("An account with this email already exists.")

    # Check duplicate username
    existing_name = await db.execute(select(User).where(User.username == payload.username))
    if existing_name.scalar_one_or_none():
        raise ConflictException("This username is already taken.")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        country=payload.country,
    )
    # Derive timezone from country if provided
    if payload.country:
        user.timezone = _timezone_from_country(payload.country)

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

    user_id = decoded.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _timezone_from_country(country: str) -> str:
    """Rough country → timezone mapping for common countries."""
    mapping = {
        "Ghana": "Africa/Accra",
        "Nigeria": "Africa/Lagos",
        "Kenya": "Africa/Nairobi",
        "South Africa": "Africa/Johannesburg",
        "United Kingdom": "Europe/London",
        "United States": "America/New_York",
    }
    return mapping.get(country, "Africa/Accra")
