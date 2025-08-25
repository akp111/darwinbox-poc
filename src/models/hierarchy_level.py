from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from ..database import Base

class HierarchyLevel(Base):
    __tablename__ = "hierarchy_levels"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    level_number = Column(Integer, nullable=False)  # 1=highest (CEO), 5=lowest (Employee)
    level_name = Column(String(100), nullable=False)
    
    # Relationships
    company = relationship("Company")
    team = relationship("Team")
    users = relationship("User")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('company_id', 'team_id', 'level_number'),
        Index('ix_hierarchy_levels_company_level', 'company_id', 'level_number'),
        Index('ix_hierarchy_levels_team_level', 'team_id', 'level_number'),
    )
