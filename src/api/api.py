from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from ..database import get_db
from ..models import (
    Company, Team, HierarchyLevel, User, Policy, 
    ApprovalStep, Expense, Approval
)

# Pydantic models for request/response
from pydantic import BaseModel

class ExpenseCreateRequest(BaseModel):
    user_id: int
    policy_id: int
    amount: float
    description: Optional[str] = None

class ExpenseApprovalRequest(BaseModel):
    expense_id: int
    approver_id: int
    comments: Optional[str] = None

class ExpenseStatusResponse(BaseModel):
    id: int
    amount: float
    description: Optional[str]
    status: str
    submitted_at: datetime
    completed_at: Optional[datetime]
    user_name: str
    policy_name: str
    approvals: List[dict]

router = APIRouter(prefix="/api", tags=["expenses"])

@router.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(
    request: ExpenseCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new expense against a policy.
    Automatically creates required approval steps based on policy configuration.
    """
    
    # Validate user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {request.user_id} not found"
        )
    
    # Validate policy exists and amount is within range
    policy = db.query(Policy).filter(Policy.id == request.policy_id).first()
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy with id {request.policy_id} not found"
        )
    
    # Check if amount is within policy range
    if not (policy.min_amount <= request.amount <= policy.max_amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Amount ${request.amount} is outside policy range ${policy.min_amount} - ${policy.max_amount}"
        )
    
    # Ensure user belongs to same company as policy
    if user.company_id != policy.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User and policy must belong to the same company"
        )
    
    try:
        # Create the expense
        expense = Expense(
            company_id=user.company_id,
            user_id=request.user_id,
            policy_id=request.policy_id,
            amount=Decimal(str(request.amount)),
            description=request.description,
            status="pending"
        )
        db.add(expense)
        db.flush()  # Get the expense ID
        
        # Get approval steps for this policy
        approval_steps = db.query(ApprovalStep).filter(
            ApprovalStep.policy_id == request.policy_id
        ).order_by(ApprovalStep.step_order).all()
        
        if not approval_steps:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No approval steps configured for this policy"
            )
        
        # Create approval records for each step
        approvals_created = []
        for step in approval_steps:
            # Find appropriate approver based on step requirements
            approver = find_approver(db, user, step)
            if not approver:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No suitable approver found for step {step.step_order} (requires level {step.required_level})"
                )
            
            approval = Approval(
                expense_id=expense.id,
                step_number=step.step_order,
                approver_id=approver.id,
                approver_level_id=approver.hierarchy_level_id,
                required=step.is_required,
                status="pending"
            )
            db.add(approval)
            approvals_created.append({
                "step": step.step_order,
                "approver": approver.name,
                "level": approver.hierarchy_level.level_name
            })
        
        db.commit()
        
        return {
            "message": "Expense created successfully",
            "expense_id": expense.id,
            "status": expense.status,
            "amount": float(expense.amount),
            "approvals_required": approvals_created
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating expense: {str(e)}"
        )

@router.post("/expenses/approve")
def approve_expense(
    request: ExpenseApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Approve an expense step. Only authorized personnel can approve.
    Automatically advances to next step or completes expense.
    """
    
    # Validate expense exists
    expense = db.query(Expense).filter(Expense.id == request.expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id {request.expense_id} not found"
        )
    
    # Validate approver exists
    approver = db.query(User).filter(User.id == request.approver_id).first()
    if not approver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approver with id {request.approver_id} not found"
        )
    
    # Ensure approver belongs to same company
    if approver.company_id != expense.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Approver must belong to the same company as expense"
        )
    
    # Find the current pending approval for this approver
    approval = db.query(Approval).filter(
        and_(
            Approval.expense_id == request.expense_id,
            Approval.approver_id == request.approver_id,
            Approval.status == "pending"
        )
    ).first()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending approval found for this approver on this expense"
        )
    
    try:
        # Update the approval
        approval.status = "approved"
        approval.approved_at = datetime.now()
        approval.comments = request.comments
        
        # Flush the changes to make sure the status update is visible in the same transaction
        db.flush()
        
        # Check if all required approvals are complete
        pending_approvals = db.query(Approval).filter(
            and_(
                Approval.expense_id == request.expense_id,
                Approval.required == True,
                Approval.status == "pending"
            )
        ).count()
        
        # If no more pending required approvals, mark expense as approved
        if pending_approvals == 0:
            expense.status = "approved"
            expense.completed_at = datetime.now()
        
        db.commit()
        
        return {
            "message": "Approval submitted successfully",
            "expense_id": expense.id,
            "step_approved": approval.step_number,
            "expense_status": expense.status,
            "pending_approvals": pending_approvals
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing approval: {str(e)}"
        )

@router.get("/expenses/{expense_id}/status", response_model=ExpenseStatusResponse)
def get_expense_status(
    expense_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the current status and approval progress of an expense.
    """
    
    # Get expense with related data
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id {expense_id} not found"
        )
    
    # Get all approvals for this expense
    approvals = db.query(Approval).filter(
        Approval.expense_id == expense_id
    ).order_by(Approval.step_number).all()
    
    # Format approval data
    approval_data = []
    for approval in approvals:
        approval_data.append({
            "step_number": approval.step_number,
            "approver_name": approval.approver.name,
            "approver_level": approval.approver.hierarchy_level.level_name,
            "status": approval.status,
            "approved_at": approval.approved_at,
            "comments": approval.comments,
            "required": approval.required
        })
    
    return ExpenseStatusResponse(
        id=expense.id,
        amount=float(expense.amount),
        description=expense.description,
        status=expense.status,
        submitted_at=expense.submitted_at,
        completed_at=expense.completed_at,
        user_name=expense.user.name,
        policy_name=expense.policy.name,
        approvals=approval_data
    )

def find_approver(db: Session, submitter: User, step: ApprovalStep) -> Optional[User]:
    """
    Find an appropriate approver for a given approval step.
    """
    
    if step.team_scope == "submitter":
        # Find someone in the same team with the required level or higher
        approver = db.query(User).join(HierarchyLevel).filter(
            and_(
                User.company_id == submitter.company_id,
                User.team_id == submitter.team_id,
                HierarchyLevel.level_number <= step.required_level,
                User.id != submitter.id,  # Can't approve own expense
                User.active == True
            )
        ).order_by(HierarchyLevel.level_number.desc()).first()  # Get highest level person
        
        return approver
    
    elif step.team_scope == "company_wide":
        # Find someone company-wide with the required level or higher
        approver = db.query(User).join(HierarchyLevel).filter(
            and_(
                User.company_id == submitter.company_id,
                HierarchyLevel.level_number <= step.required_level,
                User.id != submitter.id,
                User.active == True
            )
        ).order_by(HierarchyLevel.level_number.desc()).first()
        
        return approver
    
    # For other team scopes (finance, hr, etc.), find in specific teams
    # This would require additional logic based on team names
    # For now, fall back to company-wide search
    return db.query(User).join(HierarchyLevel).filter(
        and_(
            User.company_id == submitter.company_id,
            HierarchyLevel.level_number <= step.required_level,
            User.id != submitter.id,
            User.active == True
        )
    ).order_by(HierarchyLevel.level_number.desc()).first()
