from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    species = Column(String, nullable=False)   # e.g., dog, cat
    breed = Column(String, nullable=True)
    age = Column(Integer, nullable=True)        # years
    gender = Column(String, nullable=True)
    weight = Column(Float, nullable=True)       # kg

    # Relationship back to User
    user = relationship("User", back_populates="pets")
