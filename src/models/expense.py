from sqlalchemy import Column, String, Integer, Text, DECIMAL, TIMESTAMP, ForeignKey, Index, text
from sqlalchemy.orm import relationship
from ..database import Base

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    description = Column(Text)
    
    status = Column(String(20), default='pending')
    submitted_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    completed_at = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    company = relationship("Company")
    user = relationship("User")
    policy = relationship("Policy")
    approvals = relationship("Approval")
    
    # Constraints
    __table_args__ = (
        Index('ix_expenses_company_user_submitted', 'company_id', 'user_id', 'submitted_at'),
        Index('ix_expenses_company_status', 'company_id', 'status'),
    )
    
    def __repr__(self):
        return f"<Expense(id={self.id}, amount={self.amount}, status='{self.status}')>"
