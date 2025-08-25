#!/usr/bin/env python3
"""
Minimal sample data population script for B2B Expense Tracker POC
Run this after the server has created the database tables
"""

from datetime import datetime, timedelta
from src.database import SessionLocal
from src.models import (
    Company, Team, HierarchyLevel, User, Policy, 
    ApprovalStep, Expense, Approval
)

def populate_sample_data():
    """Populate the database with minimal sample data"""
    
    db = SessionLocal()
    
    try:
        print("🌱 Starting minimal data population...")
        
        # Check if data already exists
        if db.query(Company).first():
            print("⚠️  Data already exists. Skipping population.")
            return
        
        # 1. Create Company
        print("📢 Creating company...")
        company = Company(name="TechCorp Solutions")
        db.add(company)
        db.commit()
        
        # 2. Create Tech Team
        print("👥 Creating tech team...")
        tech_team = Team(company_id=company.id, name="Technology", is_company_wide=False)
        db.add(tech_team)
        db.commit()
        
        # 3. Create Hierarchy Levels (7 levels)
        print("📊 Creating hierarchy levels...")
        hierarchy_levels = [
            HierarchyLevel(company_id=company.id, team_id=tech_team.id, level_number=1, level_name="CTO"),
            HierarchyLevel(company_id=company.id, team_id=tech_team.id, level_number=2, level_name="VP"),
            HierarchyLevel(company_id=company.id, team_id=tech_team.id, level_number=3, level_name="Director"),
            HierarchyLevel(company_id=company.id, team_id=tech_team.id, level_number=4, level_name="AD"),  # Associate Director
            HierarchyLevel(company_id=company.id, team_id=tech_team.id, level_number=5, level_name="SEM"),  # Senior Engineering Manager
            HierarchyLevel(company_id=company.id, team_id=tech_team.id, level_number=6, level_name="Manager"),
            HierarchyLevel(company_id=company.id, team_id=tech_team.id, level_number=7, level_name="SDE3"),  # Senior Software Engineer
        ]
        db.add_all(hierarchy_levels)
        db.commit()
        
        # 4. Create Users (one for each level)
        print("👤 Creating users...")
        users = [
            User(company_id=company.id, team_id=tech_team.id, email="cto@techcorp.com", 
                 name="Alice Chen", hierarchy_level_id=hierarchy_levels[0].id),  # CTO
            User(company_id=company.id, team_id=tech_team.id, email="vp@techcorp.com", 
                 name="Bob Smith", hierarchy_level_id=hierarchy_levels[1].id),  # VP
            User(company_id=company.id, team_id=tech_team.id, email="director@techcorp.com", 
                 name="Carol Johnson", hierarchy_level_id=hierarchy_levels[2].id),  # Director
            User(company_id=company.id, team_id=tech_team.id, email="ad@techcorp.com", 
                 name="David Wilson", hierarchy_level_id=hierarchy_levels[3].id),  # AD
            User(company_id=company.id, team_id=tech_team.id, email="sem@techcorp.com", 
                 name="Eve Davis", hierarchy_level_id=hierarchy_levels[4].id),  # SEM
            User(company_id=company.id, team_id=tech_team.id, email="manager@techcorp.com", 
                 name="Frank Miller", hierarchy_level_id=hierarchy_levels[5].id),  # Manager
            User(company_id=company.id, team_id=tech_team.id, email="sde3@techcorp.com", 
                 name="Grace Taylor", hierarchy_level_id=hierarchy_levels[6].id),  # SDE3
        ]
        db.add_all(users)
        db.commit()
        
        # 5. Create Simple Policies
        print("📋 Creating policies...")
        policies = [
            Policy(company_id=company.id, category="equipment", name="Small Equipment", 
                   description="Laptops, monitors under $2000", min_amount=0.00, max_amount=1999.99),
            Policy(company_id=company.id, category="equipment", name="Large Equipment", 
                   description="Servers, high-end equipment over $2000", min_amount=2000.00, max_amount=999999999.99),
            Policy(company_id=company.id, category="travel", name="Business Travel", 
                   description="All business travel expenses", min_amount=0.00, max_amount=999999999.99),
        ]
        db.add_all(policies)
        db.commit()
        
        # 6. Create Approval Steps
        print("✅ Creating approval steps...")
        approval_steps = [
            # Small Equipment (under $2000) - Manager approval only
            ApprovalStep(policy_id=policies[0].id, step_order=1, required_level=6, team_scope='submitter', 
                        description='Manager approval required'),
            
            # Large Equipment (over $2000) - Manager -> SEM -> AD
            ApprovalStep(policy_id=policies[1].id, step_order=1, required_level=6, team_scope='submitter', 
                        description='Manager approval required'),
            ApprovalStep(policy_id=policies[1].id, step_order=2, required_level=5, team_scope='submitter', 
                        description='SEM approval required'),
            ApprovalStep(policy_id=policies[1].id, step_order=3, required_level=4, team_scope='submitter', 
                        description='AD approval required'),
            
            # Business Travel - Manager -> SEM
            ApprovalStep(policy_id=policies[2].id, step_order=1, required_level=6, team_scope='submitter', 
                        description='Manager approval required'),
            ApprovalStep(policy_id=policies[2].id, step_order=2, required_level=5, team_scope='submitter', 
                        description='SEM approval required'),
        ]
        db.add_all(approval_steps)
        db.commit()
        
        print("✨ Minimal sample data population completed successfully!")
        print(f"📊 Created:")
        print(f"   • 1 company: {company.name}")
        print(f"   • 1 team: {tech_team.name}")
        print(f"   • {len(hierarchy_levels)} hierarchy levels (CTO -> VP -> Director -> AD -> SEM -> Manager -> SDE3)")
        print(f"   • {len(users)} users")
        print(f"   • {len(policies)} policies")
        print(f"   • {len(approval_steps)} approval steps")
        print("📝 Ready for expense creation via API!")
        
    except Exception as e:
        print(f"❌ Error populating data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_sample_data()
