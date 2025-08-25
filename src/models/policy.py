from sqlalchemy import Column, String, Integer, Text, DECIMAL, Boolean, ForeignKey, TIMESTAMP, UniqueConstraint, Index, CheckConstraint, text
from sqlalchemy.orm import relationship
from ..database import Base

class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    category = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Amount thresholds (merged from policy_rules)
    min_amount = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    max_amount = Column(DECIMAL(12, 2), nullable=False, default=999999999.99)
    
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    active = Column(Boolean, default=True)
    
    # Relationships
    company = relationship("Company")
    approval_steps = relationship("ApprovalStep")
    expenses = relationship("Expense")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('company_id', 'category', 'min_amount'),  # Allow multiple ranges per category
        Index('ix_policies_company_category', 'company_id', 'category'),
        Index('ix_policies_amount_range', 'company_id', 'min_amount', 'max_amount'),
        CheckConstraint('min_amount <= max_amount', name='check_amount_range'),
    )
    
    def __repr__(self):
        return f"<Policy(id={self.id}, category='{self.category}', name='{self.name}')>"
