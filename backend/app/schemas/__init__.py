import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class _EmailMixin(BaseModel):
    @field_validator("email", check_fields=False)
    @classmethod
    def _validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValueError("Format email tidak valid")
        return v

class RegisterRequest(_EmailMixin):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)

class LoginRequest(_EmailMixin):
    email: str = Field(max_length=255)
    password: str = Field(min_length=1, max_length=128)

class SubmitURL(BaseModel):
    url: str = Field(min_length=10, max_length=500)
    mode: str = Field(default="heuristic", pattern="^(heuristic|ai)$")
    tracking: str = Field(default="auto", pattern="^(center|face|speaker|auto|mix|none)$")
    num_clips: Optional[int] = Field(default=5, ge=1, le=10)
    sub_lang: Optional[str] = Field(default="id")

class ClipEditRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=500)
    start: Optional[float] = Field(default=None, ge=0)
    end: Optional[float] = Field(default=None, ge=0)
    subtitle: Optional[str] = Field(default=None, max_length=2000)
    is_featured: Optional[bool] = None  # hanya diproses jika requester admin

class CheckoutRequest(BaseModel):
    package_id: str = Field(min_length=1, max_length=50)

class AdminSetCreditsRequest(BaseModel):
    credits: Optional[int] = Field(default=None, ge=0)
    role: Optional[str] = Field(default=None, pattern="^(admin|paid|free|user)$")

class AdminUpdateRoleRequest(BaseModel):
    role: str = Field(pattern="^(admin|paid|free)$")

class AdminCreateUserRequest(_EmailMixin):
    email: str = Field(max_length=255)
    name: str = Field(default="User", max_length=100)
    credits: int = Field(default=3, ge=0)
    role: str = Field(default="free", pattern="^(admin|paid|free)$")
