from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from ..database import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    
    # Relationships
    teams = relationship("Team")
    hierarchy_levels = relationship("HierarchyLevel")
    users = relationship("User")
    policies = relationship("Policy")
    expenses = relationship("Expense")
