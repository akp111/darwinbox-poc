# DarwinBox POC - B2B Expense Tracker

A proof-of-concept expense management system with hierarchical approval workflows built with FastAPI and PostgreSQL.

## 🏗️ Architecture

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0+
- **Container:** Docker Compose

## 📋 Features

- ✅ Hierarchical organizational structure (7-level hierarchy)
- ✅ Policy-based expense categorization with amount thresholds
- ✅ Multi-step approval workflows
- ✅ Role-based authorization
- ✅ RESTful API with automatic documentation
- ✅ Real-time expense tracking and status updates

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd darwin-box-poc

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Database

```bash
# Start PostgreSQL container
docker compose up -d

# Verify database is running
docker compose ps
```

### 3. Start Application

```bash
# Start the FastAPI server
python -m src.main
```

The server will start on `http://127.0.0.1:4000`

### 4. Populate Sample Data

```bash
# Run the data population script
python populate_data.py
```

This creates:
- 1 company (TechCorp Solutions)
- 1 team (Technology)
- 7 hierarchy levels (CTO → VP → Director → AD → SEM → Manager → SDE3)
- 7 users (one per level)
- 3 expense policies with approval workflows

## 📊 Sample Data Structure

### Users & Hierarchy
```
Level 1: Alice Chen (CTO)
Level 2: Bob Smith (VP)
Level 3: Carol Johnson (Director)
Level 4: David Wilson (AD - Associate Director)
Level 5: Eve Davis (SEM - Senior Engineering Manager)
Level 6: Frank Miller (Manager)
Level 7: Grace Taylor (SDE3 - Senior Software Engineer)
```

### Expense Policies
1. **Small Equipment** (under $2000) → Manager approval
2. **Large Equipment** (over $2000) → Manager → SEM → AD approval
3. **Business Travel** → Manager → SEM approval

## 🔧 API Endpoints

### Base URL: `http://127.0.0.1:4000`

#### 1. Create Expense
**POST** `/api/expenses`

Create a new expense against a policy.

```bash
curl -X POST "http://127.0.0.1:4000/api/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 7,
    "policy_id": 1,
    "amount": 1200.00,
    "description": "New MacBook Pro for development"
  }'
```

#### 2. Approve Expense
**POST** `/api/expenses/approve`

Approve an expense step (only authorized personnel).

```bash
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 1,
    "approver_id": 6,
    "comments": "Approved for team productivity"
  }'
```

#### 3. Get Expense Status
**GET** `/api/expenses/{expense_id}/status`

Get detailed status and approval progress.

```bash
curl -X GET "http://127.0.0.1:4000/api/expenses/1/status"
```

## 🧪 Testing Workflows

### Test Case 1: Single Approval (Small Equipment)

```bash
# 1. Create expense
curl -X POST "http://127.0.0.1:4000/api/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 7,
    "policy_id": 1,
    "amount": 800.00,
    "description": "Development laptop"
  }'

# 2. Manager approves (Frank Miller - User ID 6)
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 1,
    "approver_id": 6,
    "comments": "Standard equipment upgrade"
  }'

# 3. Check final status
curl -X GET "http://127.0.0.1:4000/api/expenses/1/status"
```

### Test Case 2: Multi-Step Approval (Large Equipment)

```bash
# 1. Create expensive equipment request
curl -X POST "http://127.0.0.1:4000/api/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 7,
    "policy_id": 2,
    "amount": 4000.00,
    "description": "High-end workstation for ML projects"
  }'

# 2. Manager approval (Step 1)
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 2,
    "approver_id": 6,
    "comments": "Justified for ML work"
  }'

# 3. SEM approval (Step 2)
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 2,
    "approver_id": 5,
    "comments": "Supports team goals"
  }'

# 4. AD approval (Final step)
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 2,
    "approver_id": 4,
    "comments": "Final approval granted"
  }'

# 5. Check final status
curl -X GET "http://127.0.0.1:4000/api/expenses/2/status"
```

## 📚 Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI:** http://127.0.0.1:4000/docs
- **ReDoc:** http://127.0.0.1:4000/redoc

## 🗂️ Project Structure

```
darwin-box-poc/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── api.py              # API endpoints
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── team.py
│   │   ├── hierarchy_level.py
│   │   ├── user.py
│   │   ├── policy.py
│   │   ├── approval_step.py
│   │   ├── expense.py
│   │   └── approval.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── log.py              # Logging configuration
│   ├── config.py               # Configuration
│   ├── database.py             # Database setup
│   └── main.py                 # FastAPI application
├── populate_data.py            # Sample data population
├── docker-compose.yml          # PostgreSQL container
├── requirements.txt            # Python dependencies
├── test.md                     # Detailed API testing guide
└── README.md                   # This file
```

## 🔒 Security Features

- **Authorization:** Only designated approvers can approve expenses
- **Company Isolation:** Users can only interact with expenses in their company
- **Step Validation:** Approval workflow follows configured steps
- **Self-Approval Prevention:** Users cannot approve their own expenses

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker compose ps

# View database logs
docker compose logs postgres

# Restart database
docker compose down -v && docker compose up -d
```

### API Not Responding
```bash
# Check if server is running
curl http://127.0.0.1:4000/

# Check server logs for errors
python -m src.main
```

### Reset Everything
```bash
# Stop all services and clear data
docker-compose down -v

# Restart database
docker-compose up -d

# Restart server
python -m src.main

# Repopulate data
python scripts/populate_data.py
```

## 📈 API Response Formats

### Success Response (Create Expense)
```json
{
  "message": "Expense created successfully",
  "expense_id": 1,
  "status": "pending",
  "amount": 1200.0,
  "approvals_required": [
    {
      "step": 1,
      "approver": "Frank Miller",
      "level": "Manager"
    }
  ]
}
```

### Success Response (Approve Expense)
```json
{
  "message": "Approval submitted successfully",
  "expense_id": 1,
  "step_approved": 1,
  "expense_status": "approved",
  "pending_approvals": 0
}
```

### Expense Status Response
```json
{
  "id": 1,
  "amount": 1200.0,
  "description": "New MacBook Pro for development",
  "status": "approved",
  "submitted_at": "2025-08-25T10:30:00.000Z",
  "completed_at": "2025-08-25T10:45:00.000Z",
  "user_name": "Grace Taylor",
  "policy_name": "Small Equipment",
  "approvals": [
    {
      "step_number": 1,
      "approver_name": "Frank Miller",
      "approver_level": "Manager",
      "status": "approved",
      "approved_at": "2025-08-25T10:45:00.000Z",
      "comments": "Approved for team productivity",
      "required": true
    }
  ]
}
```

## 🎯 Next Steps

- [ ] Add user authentication (JWT/OAuth)
- [ ] Implement expense rejection workflow
- [ ] Add email notifications for approvals
- [ ] Create dashboard UI
- [ ] Add expense reporting and analytics
- [ ] Implement file upload for receipts
- [ ] Add audit logging

## 📄 License

This project is a proof-of-concept for educational purposes.

---

**Happy Testing! 🚀**

For detailed API testing examples, see [test.md](test.md)
