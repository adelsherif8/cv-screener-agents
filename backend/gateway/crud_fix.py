def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user"""
    try:
        from .auth import verify_password
    except ImportError:
        from auth import verify_password
    
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
