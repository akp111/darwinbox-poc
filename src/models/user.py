from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    email = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    hierarchy_level_id = Column(Integer, ForeignKey("hierarchy_levels.id"), nullable=False)
    active = Column(Boolean, default=True)
    
    # Relationships
    company = relationship("Company")
    team = relationship("Team")
    hierarchy_level = relationship("HierarchyLevel")
    expenses = relationship("Expense")
    approvals = relationship("Approval", foreign_keys="Approval.approver_id")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('company_id', 'email'),
        Index('ix_users_company_team', 'company_id', 'team_id'),
        Index('ix_users_hierarchy_level', 'hierarchy_level_id'),
        Index('ix_users_team_hierarchy', 'team_id', 'hierarchy_level_id'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
