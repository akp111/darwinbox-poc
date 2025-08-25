from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.orm import relationship
from ..database import Base

class ApprovalStep(Base):
    __tablename__ = "approval_steps"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    required_level = Column(Integer, nullable=False)  # hierarchy level number required
    team_scope = Column(
        Enum('submitter', 'finance', 'hr', 'legal', 'company_wide', name='team_scope_enum'),
        nullable=False,
        default='submitter'
    )
    is_required = Column(Boolean, default=True)
    description = Column(String(255))
    
    # Relationships
    policy = relationship("Policy")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('policy_id', 'step_order'),
        Index('ix_approval_steps_policy_order', 'policy_id', 'step_order'),
        Index('ix_approval_steps_level_scope', 'required_level', 'team_scope'),
        CheckConstraint('step_order > 0', name='check_step_order'),
        CheckConstraint('required_level BETWEEN 1 AND 10', name='check_required_level'),
    )
    
    def __repr__(self):
        return f"<ApprovalStep(id={self.id}, policy_id={self.policy_id}, step_order={self.step_order}, required_level={self.required_level})>"
