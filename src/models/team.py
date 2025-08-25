from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from ..database import Base

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    is_company_wide = Column(Boolean, default=False)
    
    # Relationships
    company = relationship("Company")
    hierarchy_levels = relationship("HierarchyLevel")
    users = relationship("User")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('company_id', 'name'),
        Index('ix_teams_company_id', 'company_id'),
    )
