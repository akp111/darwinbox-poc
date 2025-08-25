# API Testing Guide

This document provides test cases and examples for the three main expense management APIs.

## Prerequisites

1. Start the server: `python -m src.main`
2. Populate sample data: `python populate_data.py`
3. Server should be running on: `http://127.0.0.1:4000`

## Sample Data Overview

After running `populate_data.py`, you'll have:

**Users:**
- User ID 1: Alice Chen (CTO, Level 1)
- User ID 2: Bob Smith (VP, Level 2)  
- User ID 3: Carol Johnson (Director, Level 3)
- User ID 4: David Wilson (AD, Level 4)
- User ID 5: Eve Davis (SEM, Level 5)
- User ID 6: Frank Miller (Manager, Level 6)
- User ID 7: Grace Taylor (SDE3, Level 7)

**Policies:**
- Policy ID 1: Small Equipment (under $2000) → Manager approval
- Policy ID 2: Large Equipment (over $2000) → Manager → SEM → AD approval  
- Policy ID 3: Business Travel → Manager → SEM approval

---

## 1. Create Expense API

**Endpoint:** `POST /api/expenses`

### Test Case 1: Small Equipment Purchase (Single Approval)

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

**Expected Response:**
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

### Test Case 2: Large Equipment Purchase (Multi-step Approval)

```bash
curl -X POST "http://127.0.0.1:4000/api/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 7,
    "policy_id": 2,
    "amount": 3500.00,
    "description": "High-end workstation for ML projects"
  }'
```

**Expected Response:**
```json
{
  "message": "Expense created successfully",
  "expense_id": 2,
  "status": "pending",
  "amount": 3500.0,
  "approvals_required": [
    {
      "step": 1,
      "approver": "Frank Miller",
      "level": "Manager"
    },
    {
      "step": 2,
      "approver": "Eve Davis",
      "level": "SEM"
    },
    {
      "step": 3,
      "approver": "David Wilson",
      "level": "AD"
    }
  ]
}
```

### Test Case 3: Business Travel

```bash
curl -X POST "http://127.0.0.1:4000/api/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 6,
    "policy_id": 3,
    "amount": 850.00,
    "description": "Flight to tech conference"
  }'
```

### Error Test Cases

**Amount Outside Policy Range:**
```bash
curl -X POST "http://127.0.0.1:4000/api/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 7,
    "policy_id": 1,
    "amount": 2500.00,
    "description": "Expensive laptop"
  }'
```

**Invalid User:**
```bash
curl -X POST "http://127.0.0.1:4000/api/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 999,
    "policy_id": 1,
    "amount": 1200.00,
    "description": "Invalid user test"
  }'
```

---

## 2. Approve Expense API

**Endpoint:** `POST /api/expenses/approve`

### Test Case 1: Manager Approves Small Equipment

```bash
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 1,
    "approver_id": 6,
    "comments": "Approved for team productivity"
  }'
```

**Expected Response:**
```json
{
  "message": "Approval submitted successfully",
  "expense_id": 1,
  "step_approved": 1,
  "expense_status": "approved",
  "pending_approvals": 0
}
```

### Test Case 2: Multi-step Approval (Step 1)

```bash
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 2,
    "approver_id": 6,
    "comments": "Justified for ML work"
  }'
```

**Expected Response:**
```json
{
  "message": "Approval submitted successfully",
  "expense_id": 2,
  "step_approved": 1,
  "expense_status": "pending",
  "pending_approvals": 2
}
```

### Test Case 3: Multi-step Approval (Step 2)

```bash
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 2,
    "approver_id": 5,
    "comments": "Good investment for the team"
  }'
```

### Test Case 4: Multi-step Approval (Final Step)

```bash
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 2,
    "approver_id": 4,
    "comments": "Approved after budget review"
  }'
```

### Error Test Cases

**Unauthorized Approver:**
```bash
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 1,
    "approver_id": 7,
    "comments": "Trying to approve own expense"
  }'
```

**Invalid Expense ID:**
```bash
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 999,
    "approver_id": 6,
    "comments": "Invalid expense"
  }'
```

---

## 3. Get Expense Status API

**Endpoint:** `GET /api/expenses/{expense_id}/status`

### Test Case 1: Check Small Equipment Status

```bash
curl -X GET "http://127.0.0.1:4000/api/expenses/1/status"
```

**Expected Response (after approval):**
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

### Test Case 2: Check Large Equipment Status (Multi-step)

```bash
curl -X GET "http://127.0.0.1:4000/api/expenses/2/status"
```

**Expected Response (partial approval):**
```json
{
  "id": 2,
  "amount": 3500.0,
  "description": "High-end workstation for ML projects",
  "status": "pending",
  "submitted_at": "2025-08-25T10:35:00.000Z",
  "completed_at": null,
  "user_name": "Grace Taylor",
  "policy_name": "Large Equipment",
  "approvals": [
    {
      "step_number": 1,
      "approver_name": "Frank Miller",
      "approver_level": "Manager",
      "status": "approved",
      "approved_at": "2025-08-25T10:50:00.000Z",
      "comments": "Justified for ML work",
      "required": true
    },
    {
      "step_number": 2,
      "approver_name": "Eve Davis",
      "approver_level": "SEM",
      "status": "pending",
      "approved_at": null,
      "comments": null,
      "required": true
    },
    {
      "step_number": 3,
      "approver_name": "David Wilson",
      "approver_level": "AD",
      "status": "pending",
      "approved_at": null,
      "comments": null,
      "required": true
    }
  ]
}
```

### Error Test Case

**Invalid Expense ID:**
```bash
curl -X GET "http://127.0.0.1:4000/api/expenses/999/status"
```

**Expected Response:**
```json
{
  "detail": "Expense with id 999 not found"
}
```

---

## Testing Workflow

### Complete End-to-End Test

1. **Create an expense:**
```bash
curl -X POST "http://127.0.0.1:4000/api/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 7,
    "policy_id": 2,
    "amount": 4000.00,
    "description": "Powerful development workstation"
  }'
```

2. **Check initial status:**
```bash
curl -X GET "http://127.0.0.1:4000/api/expenses/3/status"
```

3. **Manager approval (Step 1):**
```bash
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 3,
    "approver_id": 6,
    "comments": "Required for new project"
  }'
```

4. **Check status after step 1:**
```bash
curl -X GET "http://127.0.0.1:4000/api/expenses/3/status"
```

5. **SEM approval (Step 2):**
```bash
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 3,
    "approver_id": 5,
    "comments": "Supports team goals"
  }'
```

6. **AD approval (Final Step):**
```bash
curl -X POST "http://127.0.0.1:4000/api/expenses/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "expense_id": 3,
    "approver_id": 4,
    "comments": "Final approval granted"
  }'
```

7. **Check final status:**
```bash
curl -X GET "http://127.0.0.1:4000/api/expenses/3/status"
```

---

## API Documentation

You can also view the interactive API documentation at:
- **Swagger UI:** http://127.0.0.1:4000/docs
- **ReDoc:** http://127.0.0.1:4000/redoc

These provide a user-friendly interface to test the APIs directly from your browser.

---

## Expected Status Codes

- **200 OK:** Successful GET requests
- **201 Created:** Successful expense creation
- **400 Bad Request:** Invalid data (amount out of range, etc.)
- **403 Forbidden:** Unauthorized action
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server error

---

## Tips

1. Always start by populating sample data with `python populate_data.py`
2. Use the status API to track approval progress
3. Remember that users cannot approve their own expenses
4. Approval steps must be completed in order
5. Check the server logs for detailed error information
