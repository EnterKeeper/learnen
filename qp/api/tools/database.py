from ..database import db_session
from ..models.users import User, OwnerGroup


def create_owner_user():
    """Create default owner user on database first initialization"""
    session = db_session.create_session()

    users = session.query(User).first()
    if not users:
        owner = User(email="admin@change.email", username="admin", group=OwnerGroup.id)
        owner.set_password("admin")

        session.add(owner)
        session.commit()
