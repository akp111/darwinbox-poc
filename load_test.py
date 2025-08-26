#!/usr/bin/env python3
"""
Enhanced Load Testing Script for DarwinBox POC - B2B Expense Tracker
Uses actual data structure from populate_data.py for realistic testing scenarios.
"""

import asyncio
import aiohttp
import time
import json
import random
import statistics
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import argparse


@dataclass
class TestResult:
    """Store individual test result"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: str = ""


@dataclass
class LoadTestConfig:
    """Load test configuration"""
    base_url: str = "http://127.0.0.1:4000"
    total_requests: int = 100
    concurrent_users: int = 10
    ramp_up_time: int = 5  # seconds
    test_duration: int = 60  # seconds
    request_delay: float = 0.1  # seconds between requests per user


class ExpenseLoadTester:
    """Enhanced load testing class using actual populate_data.py structure"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: List[TestResult] = []
        
        # Real data structure from populate_data.py
        self.company = {"id": 1, "name": "TechCorp Solutions"}
        self.team = {"id": 1, "name": "Technology", "company_id": 1}
        
        # Exact hierarchy levels from populate_data.py
        self.hierarchy_levels = [
            {"id": 1, "level_number": 1, "level_name": "CTO"},
            {"id": 2, "level_number": 2, "level_name": "VP"},
            {"id": 3, "level_number": 3, "level_name": "Director"},
            {"id": 4, "level_number": 4, "level_name": "AD"},      # Associate Director
            {"id": 5, "level_number": 5, "level_name": "SEM"},     # Senior Engineering Manager
            {"id": 6, "level_number": 6, "level_name": "Manager"},
            {"id": 7, "level_number": 7, "level_name": "SDE3"},    # Senior Software Engineer
        ]
        
        # Exact users from populate_data.py
        self.users = [
            {"id": 1, "name": "Alice Chen", "email": "cto@techcorp.com", "hierarchy_level_id": 1, "level": 1, "role": "CTO"},
            {"id": 2, "name": "Bob Smith", "email": "vp@techcorp.com", "hierarchy_level_id": 2, "level": 2, "role": "VP"},
            {"id": 3, "name": "Carol Johnson", "email": "director@techcorp.com", "hierarchy_level_id": 3, "level": 3, "role": "Director"},
            {"id": 4, "name": "David Wilson", "email": "ad@techcorp.com", "hierarchy_level_id": 4, "level": 4, "role": "AD"},
            {"id": 5, "name": "Eve Davis", "email": "sem@techcorp.com", "hierarchy_level_id": 5, "level": 5, "role": "SEM"},
            {"id": 6, "name": "Frank Miller", "email": "manager@techcorp.com", "hierarchy_level_id": 6, "level": 6, "role": "Manager"},
            {"id": 7, "name": "Grace Taylor", "email": "sde3@techcorp.com", "hierarchy_level_id": 7, "level": 7, "role": "SDE3"},
        ]
        
        # Exact policies from populate_data.py with their approval workflows
        self.policies = [
            {
                "id": 1, 
                "name": "Small Equipment", 
                "category": "equipment",
                "description": "Laptops, monitors under $2000",
                "min_amount": 0.00, 
                "max_amount": 1999.99,
                "approval_steps": [
                    {"step_order": 1, "required_level": 6, "team_scope": "submitter", "description": "Manager approval required"}
                ]
            },
            {
                "id": 2, 
                "name": "Large Equipment", 
                "category": "equipment",
                "description": "Servers, high-end equipment over $2000",
                "min_amount": 2000.00, 
                "max_amount": 999999999.99,
                "approval_steps": [
                    {"step_order": 1, "required_level": 6, "team_scope": "submitter", "description": "Manager approval required"},
                    {"step_order": 2, "required_level": 5, "team_scope": "submitter", "description": "SEM approval required"},
                    {"step_order": 3, "required_level": 4, "team_scope": "submitter", "description": "AD approval required"}
                ]
            },
            {
                "id": 3, 
                "name": "Business Travel", 
                "category": "travel",
                "description": "All business travel expenses",
                "min_amount": 0.00, 
                "max_amount": 999999999.99,
                "approval_steps": [
                    {"step_order": 1, "required_level": 6, "team_scope": "submitter", "description": "Manager approval required"},
                    {"step_order": 2, "required_level": 5, "team_scope": "submitter", "description": "SEM approval required"}
                ]
            },
        ]
        
        # Realistic expense descriptions by category
        self.expense_descriptions = {
            "equipment": {
                "small": [
                    "MacBook Pro M2 for development",
                    "Dell 32-inch 4K monitor",
                    "Logitech MX Master 3 mouse",
                    "Mechanical keyboard for coding",
                    "USB-C dock for MacBook",
                    "Webcam for video calls",
                    "Noise-cancelling headphones",
                    "External SSD for backups",
                    "iPad for wireframing",
                    "Standing desk converter"
                ],
                "large": [
                    "High-end workstation for ML training",
                    "Server rack for development environment",
                    "GPU cluster for AI research",
                    "Enterprise storage system",
                    "Network equipment upgrade",
                    "3D printer for prototyping",
                    "Testing lab equipment setup",
                    "Video conferencing system",
                    "Enterprise software licenses",
                    "Backup server infrastructure"
                ]
            },
            "travel": [
                "Flight to AWS re:Invent conference",
                "Hotel accommodation for client meeting",
                "Ground transportation for site visit",
                "Conference registration fees",
                "Team building retreat expenses",
                "Training workshop in Silicon Valley",
                "International business trip",
                "Customer onsite support visit",
                "Industry conference attendance",
                "Vendor meeting travel costs"
            ]
        }
        
        # Track created expenses for realistic approval testing
        self.created_expenses: List[Dict] = []
        self.pending_approvals: List[Dict] = []

    async def refresh_pending_approvals(self, session: aiohttp.ClientSession):
        """Refresh pending approvals by checking actual expense status"""
        if not self.created_expenses:
            return
        
        # Check a few recent expenses for their current approval status
        recent_expenses = self.created_expenses[-5:] if len(self.created_expenses) > 5 else self.created_expenses
        
        for expense_record in recent_expenses:
            try:
                async with session.get(
                    f"{self.config.base_url}/api/expenses/{expense_record['id']}/status",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        status_data = await response.json()
                        
                        # Find pending approvals from the status
                        for approval in status_data.get("approvals", []):
                            if approval["status"] == "pending":
                                # Find the approver user object
                                approver = None
                                for user in self.users:
                                    if user["name"] == approval["approver_name"]:
                                        approver = user
                                        break
                                
                                if approver:
                                    # Check if this approval is already in our pending list
                                    already_pending = any(
                                        pa["expense_id"] == expense_record["id"] and 
                                        pa["approver"]["id"] == approver["id"] and
                                        pa["step"] == approval["step_number"]
                                        for pa in self.pending_approvals
                                    )
                                    
                                    if not already_pending:
                                        self.pending_approvals.append({
                                            "expense_id": expense_record["id"],
                                            "expense_record": expense_record,
                                            "approver": approver,
                                            "step": approval["step_number"],
                                            "level": approval["approver_level"]
                                        })
            except Exception:
                # Ignore errors in status checking
                pass

    def get_realistic_approver_for_step(self, submitter_id: int, policy: Dict, step_order: int) -> Optional[Dict]:
        """Find realistic approver based on actual approval workflow"""
        
        # Find the approval step
        approval_step = None
        for step in policy["approval_steps"]:
            if step["step_order"] == step_order:
                approval_step = step
                break
        
        if not approval_step:
            return None
        
        required_level = approval_step["required_level"]
        
        # Find users with sufficient authority (level <= required_level)
        # Exclude the submitter (can't self-approve)
        potential_approvers = [
            user for user in self.users 
            if user["level"] <= required_level and user["id"] != submitter_id
        ]
        
        if not potential_approvers:
            return None
        
        # Return the most senior person available (lowest level number)
        return min(potential_approvers, key=lambda u: u["level"])

    def generate_realistic_expense_data(self) -> Dict:
        """Generate realistic expense data based on actual policies"""
        
        # Use lower-level employees as typical submitters (Manager, SDE3)
        submitters = [user for user in self.users if user["level"] >= 6]
        submitter = random.choice(submitters)
        
        # Select policy and generate appropriate amount
        policy = random.choice(self.policies)
        
        if policy["id"] == 1:  # Small Equipment
            amount = round(random.uniform(100, 1900), 2)
            description = random.choice(self.expense_descriptions["equipment"]["small"])
        elif policy["id"] == 2:  # Large Equipment  
            amount = round(random.uniform(2100, 15000), 2)
            description = random.choice(self.expense_descriptions["equipment"]["large"])
        else:  # Business Travel
            amount = round(random.uniform(200, 5000), 2)
            description = random.choice(self.expense_descriptions["travel"])
        
        return {
            "user_id": submitter["id"],
            "policy_id": policy["id"],
            "amount": amount,
            "description": description,
            "submitter": submitter,
            "policy": policy
        }

    async def create_expense_request(self, session: aiohttp.ClientSession) -> TestResult:
        """Test create expense endpoint with realistic data"""
        start_time = time.time()
        
        expense_data = self.generate_realistic_expense_data()
        
        payload = {
            "user_id": expense_data["user_id"],
            "policy_id": expense_data["policy_id"],
            "amount": expense_data["amount"],
            "description": expense_data["description"]
        }
        
        try:
            async with session.post(
                f"{self.config.base_url}/api/expenses",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                response_data = await response.json()
                
                success = response.status == 201
                if success and "expense_id" in response_data:
                    expense_id = response_data["expense_id"]
                    
                    # Store expense with its approval workflow
                    expense_record = {
                        "id": expense_id,
                        "submitter": expense_data["submitter"],
                        "policy": expense_data["policy"],
                        "amount": expense_data["amount"],
                        "description": expense_data["description"],
                        "current_step": 1,
                        "total_steps": len(expense_data["policy"]["approval_steps"])
                    }
                    
                    self.created_expenses.append(expense_record)
                    
                    # Extract actual approvers from API response instead of guessing
                    if "approvals_required" in response_data:
                        for approval_info in response_data["approvals_required"]:
                            # Find the user ID for this approver name
                            approver = None
                            for user in self.users:
                                if user["name"] == approval_info["approver"]:
                                    approver = user
                                    break
                            
                            if approver:
                                self.pending_approvals.append({
                                    "expense_id": expense_id,
                                    "expense_record": expense_record,
                                    "approver": approver,
                                    "step": approval_info["step"],
                                    "level": approval_info["level"]
                                })
                
                return TestResult(
                    endpoint="/api/expenses",
                    method="POST",
                    status_code=response.status,
                    response_time=response_time,
                    success=success,
                    error_message="" if success else str(response_data)
                )
                
        except Exception as e:
            return TestResult(
                endpoint="/api/expenses",
                method="POST",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

    async def approve_expense_request(self, session: aiohttp.ClientSession) -> TestResult:
        """Test approve expense endpoint with realistic approval workflow"""
        start_time = time.time()
        
        if not self.pending_approvals:
            # Return a skipped result if no expenses to approve
            return TestResult(
                endpoint="/api/expenses/approve",
                method="POST",
                status_code=200,
                response_time=0.001,
                success=True,
                error_message="No pending approvals available"
            )
        
        # Get a random pending approval (these are actual approvals assigned by the API)
        approval = random.choice(self.pending_approvals)
        
        # Generate realistic approval comments
        approval_comments = [
            f"Approved by {approval['approver']['name']} - Load test approval",
            f"Equipment justified for team productivity - {approval['approver']['role']}",
            f"Budget approved for {approval['expense_record']['policy']['category']} expense",
            f"Standard approval from {approval['approver']['role']} level",
            f"Business case validated by {approval['approver']['name']}",
        ]
        
        payload = {
            "expense_id": approval["expense_id"],
            "approver_id": approval["approver"]["id"],
            "comments": random.choice(approval_comments)
        }
        
        try:
            async with session.post(
                f"{self.config.base_url}/api/expenses/approve",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                response_data = await response.json()
                success = response.status == 200
                
                if success:
                    # Remove current approval from pending (it's been processed)
                    try:
                        self.pending_approvals.remove(approval)
                    except ValueError:
                        # Approval was already removed, ignore
                        pass
                    
                    # Note: We don't need to manually add next approval steps
                    # because the API doesn't tell us about subsequent steps
                    # Real subsequent approvals would be handled by the actual system
                
                return TestResult(
                    endpoint="/api/expenses/approve",
                    method="POST",
                    status_code=response.status,
                    response_time=response_time,
                    success=success,
                    error_message="" if success else str(response_data)
                )
                
        except Exception as e:
            return TestResult(
                endpoint="/api/expenses/approve",
                method="POST",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

    async def get_expense_status_request(self, session: aiohttp.ClientSession) -> TestResult:
        """Test get expense status endpoint"""
        start_time = time.time()
        
        if not self.created_expenses:
            # Use a default expense ID if none created yet
            expense_id = 1
        else:
            expense_record = random.choice(self.created_expenses)
            expense_id = expense_record["id"]
        
        try:
            async with session.get(
                f"{self.config.base_url}/api/expenses/{expense_id}/status",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                response_data = await response.json()
                success = response.status == 200
                
                return TestResult(
                    endpoint=f"/api/expenses/{expense_id}/status",
                    method="GET",
                    status_code=response.status,
                    response_time=response_time,
                    success=success,
                    error_message="" if success else str(response_data)
                )
                
        except Exception as e:
            return TestResult(
                endpoint=f"/api/expenses/status",
                method="GET",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

    async def user_simulation(self, user_id: int, session: aiohttp.ClientSession):
        """Simulate realistic user behavior based on role hierarchy"""
        await asyncio.sleep(user_id * (self.config.ramp_up_time / self.config.concurrent_users))
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < self.config.test_duration:
            
            # Periodically refresh pending approvals from API (every 10 requests)
            if request_count % 10 == 0:
                await self.refresh_pending_approvals(session)
            
            # Simulate realistic user behavior patterns
            # Lower-level employees (SDE3, Manager) create more expenses
            # Higher-level employees (SEM, AD, Director, VP, CTO) approve more
            user_level = (user_id % 7) + 1  # Cycle through user levels
            
            if user_level >= 6:  # Manager and SDE3 - create more expenses
                action = random.choices(
                    ['create', 'approve', 'status'],
                    weights=[0.6, 0.2, 0.2],  # 60% create, 20% approve, 20% status
                    k=1
                )[0]
            else:  # Senior roles - approve more, create less
                action = random.choices(
                    ['create', 'approve', 'status'],
                    weights=[0.2, 0.6, 0.2],  # 20% create, 60% approve, 20% status
                    k=1
                )[0]
            
            # If no pending approvals available, don't try to approve
            if action == 'approve' and not self.pending_approvals:
                action = random.choice(['create', 'status'])
            
            if action == 'create':
                result = await self.create_expense_request(session)
            elif action == 'approve':
                result = await self.approve_expense_request(session)
            else:
                result = await self.get_expense_status_request(session)
            
            self.results.append(result)
            request_count += 1
            
            # Realistic delays based on action complexity
            if action == 'create':
                await asyncio.sleep(self.config.request_delay * 1.5)  # Creating takes longer
            elif action == 'approve':
                await asyncio.sleep(self.config.request_delay * 1.2)  # Approving takes some thought
            else:
                await asyncio.sleep(self.config.request_delay)  # Status check is quick

    async def run_load_test(self):
        """Run the comprehensive load test with enhanced reporting"""
        print("🚀 Starting Enhanced Load Test for DarwinBox POC")
        print(f"📊 Configuration:")
        print(f"   - Base URL: {self.config.base_url}")
        print(f"   - Concurrent Users: {self.config.concurrent_users}")
        print(f"   - Test Duration: {self.config.test_duration}s")
        print(f"   - Ramp-up Time: {self.config.ramp_up_time}s")
        print(f"   - Request Delay: {self.config.request_delay}s")
        print()
        print("📋 Test Data Structure:")
        print(f"   - Company: {self.company['name']}")
        print(f"   - Team: {self.team['name']}")
        print(f"   - Users: {len(self.users)} (from {self.users[0]['role']} to {self.users[-1]['role']})")
        print(f"   - Policies: {len(self.policies)} with realistic approval workflows")
        print()
        
        # Test API connectivity first
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/") as response:
                    if response.status != 200:
                        print("❌ API server not responding. Please start the server first.")
                        return
        except Exception as e:
            print(f"❌ Cannot connect to API server: {e}")
            print("Please ensure the server is running on http://127.0.0.1:4000")
            return
        
        print("✅ API server connectivity confirmed")
        print("🏃 Starting realistic load test simulation...")
        
        start_time = time.time()
        
        # Create connector with appropriate limits
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Create user simulation tasks
            tasks = [
                self.user_simulation(i, session)
                for i in range(self.config.concurrent_users)
            ]
            
            # Run all simulations concurrently
            await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        print(f"\n✅ Load test completed in {total_time:.2f}s")
        
        # Generate enhanced report
        self.generate_enhanced_report()

    def generate_enhanced_report(self):
        """Generate comprehensive test results report with workflow analysis"""
        if not self.results:
            print("❌ No test results to report")
            return
        
        print("\n" + "="*70)
        print("📊 ENHANCED LOAD TEST RESULTS REPORT")
        print("="*70)
        
        # Overall statistics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests) * 100
        
        response_times = [r.response_time for r in self.results if r.success]
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Requests: {total_requests}")
        print(f"   Successful: {successful_requests} ({success_rate:.2f}%)")
        print(f"   Failed: {failed_requests}")
        
        if response_times:
            print(f"   Average Response Time: {statistics.mean(response_times):.3f}s")
            print(f"   Median Response Time: {statistics.median(response_times):.3f}s")
            print(f"   95th Percentile: {statistics.quantiles(response_times, n=20)[18]:.3f}s")
            print(f"   Max Response Time: {max(response_times):.3f}s")
            print(f"   Min Response Time: {min(response_times):.3f}s")
        
        # Enhanced per-endpoint statistics
        endpoints = {}
        for result in self.results:
            if result.endpoint.startswith('/api/expenses') and result.method == 'GET':
                endpoint_key = "GET expense-status"
            else:
                endpoint_key = f"{result.method} {result.endpoint.split('/')[-1]}"
            
            if endpoint_key not in endpoints:
                endpoints[endpoint_key] = []
            endpoints[endpoint_key].append(result)
        
        print(f"\n🎯 Per-Endpoint Statistics:")
        for endpoint, results in endpoints.items():
            successful = sum(1 for r in results if r.success)
            total = len(results)
            success_rate = (successful / total) * 100
            
            successful_times = [r.response_time for r in results if r.success]
            if successful_times:
                avg_time = statistics.mean(successful_times)
                print(f"   {endpoint}:")
                print(f"     Requests: {total} | Success: {successful} ({success_rate:.1f}%) | Avg Time: {avg_time:.3f}s")
        
        # Workflow analysis
        print(f"\n🔄 Workflow Analysis:")
        print(f"   Expenses Created: {len(self.created_expenses)}")
        print(f"   Pending Approvals: {len(self.pending_approvals)}")
        
        # Policy breakdown
        if self.created_expenses:
            policy_usage = {}
            for expense in self.created_expenses:
                policy_name = expense["policy"]["name"]
                policy_usage[policy_name] = policy_usage.get(policy_name, 0) + 1
            
            print(f"\n📋 Policy Usage Distribution:")
            for policy_name, count in policy_usage.items():
                percentage = (count / len(self.created_expenses)) * 100
                print(f"   {policy_name}: {count} expenses ({percentage:.1f}%)")
        
        # Approval workflow status
        if self.pending_approvals:
            print(f"\n✅ Approval Workflow Status:")
            step_distribution = {}
            for approval in self.pending_approvals:
                step = approval["step"]
                approver_role = approval["approver"]["role"]
                key = f"Step {step} ({approver_role})"
                step_distribution[key] = step_distribution.get(key, 0) + 1
            
            for step_info, count in step_distribution.items():
                print(f"   {step_info}: {count} pending")
        
        # Error analysis with enhanced context
        errors = [r for r in self.results if not r.success]
        if errors:
            print(f"\n❌ Error Analysis:")
            error_types = {}
            for error in errors:
                error_key = f"{error.status_code}: {error.error_message[:60]}"
                error_types[error_key] = error_types.get(error_key, 0) + 1
            
            for error_type, count in error_types.items():
                print(f"   {error_type}: {count} occurrences")
        
        # Performance thresholds with realistic benchmarks
        print(f"\n⚡ Performance Analysis:")
        slow_requests = [r for r in self.results if r.response_time > 1.0]
        very_slow_requests = [r for r in self.results if r.response_time > 2.0]
        
        print(f"   Requests > 1s: {len(slow_requests)} ({len(slow_requests)/total_requests*100:.1f}%)")
        print(f"   Requests > 2s: {len(very_slow_requests)} ({len(very_slow_requests)/total_requests*100:.1f}%)")
        
        # Enhanced recommendations based on actual workflow performance
        print(f"\n💡 Enhanced Recommendations:")
        if success_rate < 90:
            print("   ⚠️  Success rate below 90% - check approval workflow logic")
        elif success_rate < 95:
            print("   ⚠️  Success rate below 95% - investigate error causes")
        
        if response_times and statistics.mean(response_times) > 0.8:
            print("   ⚠️  Average response time > 800ms - consider database optimization")
        elif response_times and statistics.mean(response_times) > 0.5:
            print("   ⚠️  Average response time > 500ms - monitor database performance")
        
        if len(very_slow_requests) > total_requests * 0.05:  # More than 5%
            print("   ⚠️  Too many slow requests (>2s) - check database query performance")
        
        # Workflow-specific recommendations
        if len(self.pending_approvals) > len(self.created_expenses) * 0.8:
            print("   ⚠️  High pending approval ratio - approval bottleneck detected")
        
        if success_rate >= 95 and response_times and statistics.mean(response_times) <= 0.5:
            print("   ✅ Excellent performance! System handles the load well")
            print("   💡 Consider testing with higher concurrent users")
        
        print("\n" + "="*70)


def main():
    """Main function with enhanced command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Enhanced load test for DarwinBox POC API with realistic workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python load_test.py --users 10 --duration 60    # Standard load test
  python load_test.py --users 25 --duration 120   # Heavy load test  
  python load_test.py --users 5 --duration 30     # Quick validation test
        """
    )
    
    parser.add_argument("--url", default="http://127.0.0.1:4000", 
                       help="Base URL of the API (default: %(default)s)")
    parser.add_argument("--users", type=int, default=10, 
                       help="Number of concurrent users (default: %(default)s)")
    parser.add_argument("--duration", type=int, default=60, 
                       help="Test duration in seconds (default: %(default)s)")
    parser.add_argument("--rampup", type=int, default=5, 
                       help="Ramp-up time in seconds (default: %(default)s)")
    parser.add_argument("--delay", type=float, default=0.1, 
                       help="Delay between requests per user (default: %(default)s)")
    
    args = parser.parse_args()
    
    config = LoadTestConfig(
        base_url=args.url,
        concurrent_users=args.users,
        test_duration=args.duration,
        ramp_up_time=args.rampup,
        request_delay=args.delay
    )
    
    tester = ExpenseLoadTester(config)
    
    try:
        asyncio.run(tester.run_load_test())
    except KeyboardInterrupt:
        print("\n⏹️  Load test interrupted by user")
        if tester.results:
            tester.generate_enhanced_report()


if __name__ == "__main__":
    main()
