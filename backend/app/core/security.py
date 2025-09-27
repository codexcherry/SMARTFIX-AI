from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging
import time

from ..core.config import settings
from ..core.cache import cache_manager
from ..database import get_db
from ..database.models import User, UserSession
from ..models.schemas import TokenData, UserRole

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None:
            return None
        
        return TokenData(user_id=user_id, email=email, role=UserRole(role))
    except JWTError as e:
        logger.error(f"JWT token verification failed: {e}")
        return None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if session is still valid
    session = db.query(UserSession).filter(
        UserSession.session_token == token,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_role(required_role: UserRole):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    return role_checker

def require_minimum_role(minimum_role: UserRole):
    """Decorator to require minimum role level"""
    role_hierarchy = {
        UserRole.GUEST: 0,
        UserRole.USER: 1,
        UserRole.TECHNICIAN: 2,
        UserRole.ADMIN: 3
    }
    
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(minimum_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Minimum required role: {minimum_role.value}"
            )
        return current_user
    return role_checker

def create_user_session(
    db: Session,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> UserSession:
    """Create a new user session"""
    # Invalidate existing sessions for this user
    db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_active == True
    ).update({"is_active": False})
    
    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value}
    )
    
    # Create session record
    session = UserSession(
        user_id=user.id,
        session_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + access_token_expires,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Update user's last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return session

def revoke_user_session(db: Session, token: str) -> bool:
    """Revoke a user session"""
    session = db.query(UserSession).filter(
        UserSession.session_token == token,
        UserSession.is_active == True
    ).first()
    
    if session:
        session.is_active = False
        db.commit()
        return True
    return False

def refresh_access_token(
    db: Session,
    refresh_token: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[UserSession]:
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type = payload.get("type")
        
        if token_type != "refresh":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Check if refresh token exists and is active
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True
        ).first()
        
        if not session:
            return None
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user_id, "email": payload.get("email"), "role": payload.get("role")},
            expires_delta=access_token_expires
        )
        
        # Update session
        session.session_token = new_access_token
        session.expires_at = datetime.utcnow() + access_token_expires
        if ip_address:
            session.ip_address = ip_address
        if user_agent:
            session.user_agent = user_agent
        
        db.commit()
        db.refresh(session)
        
        return session
        
    except JWTError:
        return None

# Role-based access control functions
def can_access_query(user: User, query_user_id: str) -> bool:
    """Check if user can access a specific query"""
    return (user.id == query_user_id or 
            user.role in [UserRole.ADMIN, UserRole.TECHNICIAN])

def can_modify_user(current_user: User, target_user_id: str) -> bool:
    """Check if user can modify another user"""
    return (current_user.id == target_user_id or 
            current_user.role == UserRole.ADMIN)

def can_view_analytics(user: User) -> bool:
    """Check if user can view analytics"""
    return user.role in [UserRole.ADMIN, UserRole.TECHNICIAN]

def can_manage_system(user: User) -> bool:
    """Check if user can manage system settings"""
    return user.role == UserRole.ADMIN

# Rate limiting functions
def check_rate_limit(request: Request, limit: int = 60, window: int = 60) -> bool:
    """Check if request is within rate limit"""
    client_ip = request.client.host
    user_id = getattr(request.state, 'user_id', None)
    
    # Use user_id if available, otherwise use IP
    key = f"rate_limit:{user_id or client_ip}"
    current_time = int(time.time())
    
    # Get current count from cache
    cached_data = cache_manager.get(key)
    if cached_data:
        count, window_start_time = cached_data
        if current_time - window_start_time < window:
            if count >= limit:
                return False
            # Increment count
            cache_manager.set(key, (count + 1, window_start_time), window)
        else:
            # Reset window
            cache_manager.set(key, (1, current_time), window)
    else:
        # First request in window
        cache_manager.set(key, (1, current_time), window)
    
    return True

def rate_limit_dependency(limit: int = 60, window: int = 60):
    """Rate limiting dependency for FastAPI"""
    def check_limit(request: Request):
        if not check_rate_limit(request, limit, window):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {limit} requests per {window} seconds"
            )
        return True
    return check_limit