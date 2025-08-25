from sqlalchemy import Column, String, Integer, Boolean, Text, TIMESTAMP, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from ..database import Base

class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver_level_id = Column(Integer, ForeignKey("hierarchy_levels.id"), nullable=False)
    
    required = Column(Boolean, default=True)
    status = Column(String(20), default='pending')
    approved_at = Column(TIMESTAMP, nullable=True)
    comments = Column(Text)
    
    # Relationships
    expense = relationship("Expense")
    approver = relationship("User", foreign_keys=[approver_id], overlaps="approvals")
    approver_level = relationship("HierarchyLevel")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('expense_id', 'step_number', 'approver_id'),
        Index('ix_approvals_approver_status', 'approver_id', 'status'),
        Index('ix_approvals_expense_step', 'expense_id', 'step_number'),
    )
    
    def __repr__(self):
        return f"<Approval(id={self.id}, expense_id={self.expense_id}, step_number={self.step_number}, status='{self.status}')>"
