"""
Test Object - HandshakeOS-E

First-class test objects that link to hypotheses and enable systematic testing
of system behaviors with full audit trails.

Design Philosophy:
- Tests as first-class objects: Not just code, but trackable entities
- Hypothesis-driven: Tests verify specific hypotheses
- Perspective-aware: Tests can filter by me/we/they/system perspectives
- Executable: Tests can run automatically or manually
- Measured: Complete tracking of pass/fail rates over time
- Auditable: Full history of test executions

For the stranger who wears your shell tomorrow:
TestObjects represent "executable questions about system behavior". Each test
links to one or more hypotheses and can be executed to verify expectations.
The test results feed back into hypothesis confidence scores, creating a
learning loop.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json
import subprocess


@dataclass
class TestResult:
    """
    Result from a single test execution.
    
    Captures outcomes, timing, and context for each test run.
    
    Attributes:
        result_id: Unique identifier for this result
        timestamp: When the test was executed
        passed: Whether the test passed (True/False/None for error)
        execution_time_ms: How long the test took
        output: Captured output from test execution
        error_message: Error message if test failed
        context: Additional context about test environment
    """
    result_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    passed: Optional[bool] = None
    execution_time_ms: float = 0.0
    output: str = ""
    error_message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'result_id': self.result_id,
            'timestamp': self.timestamp.isoformat(),
            'passed': self.passed,
            'execution_time_ms': self.execution_time_ms,
            'output': self.output,
            'error_message': self.error_message,
            'context': self.context,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """Create TestResult from dictionary."""
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class TestObject:
    """
    First-class Test Object for systematic behavior verification.
    
    TestObjects are hypothesis-driven tests that can be executed automatically
    or manually to verify system behaviors. They link to ParallelHypotheses and
    track pass/fail rates over time.
    
    Key Features:
    1. Hypothesis-driven: Tests verify specific hypotheses
    2. Perspective-aware: Filter by me/we/they/system
    3. Executable: Can run automatically with tracking
    4. Measured: Complete execution history
    5. Auditable: Full trail of who ran what when
    
    Example Usage:
        >>> from src.mastra.core import TestObject
        >>> 
        >>> # Create a test
        >>> test = TestObject(
        ...     test_name="Verify API response time",
        ...     test_description="API should respond within 100ms",
        ...     test_type="performance",
        ...     hypothesis_ids=["hyp_123"],
        ...     executable=True,
        ...     execution_command="python tests/test_api_speed.py",
        ...     expected_outcome="Pass if all responses < 100ms",
        ...     acceptance_criteria=["Mean response < 100ms", "No errors"]
        ... )
        >>> 
        >>> # Execute the test
        >>> result = test.execute()
        >>> print(f"Test passed: {result.passed}")
        >>> 
        >>> # Check pass rate
        >>> pass_rate = test.calculate_pass_rate()
        >>> print(f"Historical pass rate: {pass_rate:.1%}")
    """
    
    # Core identification
    test_id: str = field(default_factory=lambda: str(uuid4()))
    test_name: str = ""
    test_description: str = ""
    test_type: str = "functional"  # functional, performance, integration, unit, etc.
    
    # Hypothesis linkage
    hypothesis_ids: List[str] = field(default_factory=list)  # ParallelHypotheses IDs
    
    # Perspective filtering (HandshakeOS-E concept)
    perspective_filter: Optional[str] = None  # "me", "we", "they", "system", or None for all
    
    # Execution details
    executable: bool = False
    execution_command: Optional[str] = None
    last_run: Optional[datetime] = None
    last_result: Optional[TestResult] = None
    
    # Expected outcomes
    expected_outcome: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    
    # Execution history
    results_history: List[TestResult] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""  # Bounded identity ID
    tags: List[str] = field(default_factory=list)
    
    # Versioning
    version: str = "1.0.0"
    
    def execute(self, context: Optional[Dict[str, Any]] = None) -> TestResult:
        """
        Execute the test and record result.
        
        Args:
            context: Optional execution context
            
        Returns:
            TestResult with execution outcome
        """
        import time
        
        start_time = time.time()
        result = TestResult(context=context or {})
        
        if not self.executable or not self.execution_command:
            result.passed = None
            result.error_message = "Test is not executable or no command specified"
            result.execution_time_ms = 0
        else:
            try:
                # Execute command
                process = subprocess.run(
                    self.execution_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                result.output = process.stdout
                result.passed = (process.returncode == 0)
                
                if not result.passed:
                    result.error_message = process.stderr or "Non-zero exit code"
                    
            except subprocess.TimeoutExpired:
                result.passed = False
                result.error_message = "Test execution timed out"
            except Exception as e:
                result.passed = False
                result.error_message = f"Execution failed: {str(e)}"
        
        # Record timing
        result.execution_time_ms = (time.time() - start_time) * 1000
        
        # Update test object
        self.last_run = datetime.utcnow()
        self.last_result = result
        self.record_result(result)
        
        return result
    
    def record_result(self, result: TestResult):
        """
        Record a test result to history.
        
        Args:
            result: TestResult to record
        """
        self.results_history.append(result)
        self.last_result = result
        self.last_run = result.timestamp
    
    def calculate_pass_rate(self, last_n: Optional[int] = None) -> float:
        """
        Calculate pass rate from historical results.
        
        Args:
            last_n: Only consider last N results (None = all)
            
        Returns:
            Pass rate as float 0.0-1.0
        """
        if not self.results_history:
            return 0.0
        
        results = self.results_history[-last_n:] if last_n else self.results_history
        passed_tests = [r for r in results if r.passed is True]
        
        return len(passed_tests) / len(results)
    
    def calculate_average_execution_time(self) -> float:
        """
        Calculate average execution time across all runs.
        
        Returns:
            Average execution time in milliseconds
        """
        if not self.results_history:
            return 0.0
        
        total_time = sum(r.execution_time_ms for r in self.results_history)
        return total_time / len(self.results_history)
    
    def link_hypothesis(self, hypothesis_id: str):
        """
        Link this test to a hypothesis.
        
        Args:
            hypothesis_id: ID of ParallelHypotheses to link
        """
        if hypothesis_id not in self.hypothesis_ids:
            self.hypothesis_ids.append(hypothesis_id)
    
    def unlink_hypothesis(self, hypothesis_id: str):
        """
        Unlink this test from a hypothesis.
        
        Args:
            hypothesis_id: ID of ParallelHypotheses to unlink
        """
        if hypothesis_id in self.hypothesis_ids:
            self.hypothesis_ids.remove(hypothesis_id)
    
    def get_recent_failures(self, n: int = 5) -> List[TestResult]:
        """
        Get N most recent failures.
        
        Args:
            n: Number of recent failures to return
            
        Returns:
            List of recent TestResult failures
        """
        failures = [r for r in self.results_history if r.passed is False]
        return failures[-n:]
    
    def is_flaky(self, threshold: float = 0.2) -> bool:
        """
        Determine if test is flaky (inconsistent pass/fail).
        
        Args:
            threshold: Flakiness threshold (0.0-1.0)
            
        Returns:
            True if test appears flaky
        """
        if len(self.results_history) < 5:
            return False  # Not enough data
        
        pass_rate = self.calculate_pass_rate(last_n=10)
        
        # Flaky if pass rate is between threshold and (1-threshold)
        return threshold < pass_rate < (1 - threshold)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'test_description': self.test_description,
            'test_type': self.test_type,
            'hypothesis_ids': self.hypothesis_ids,
            'perspective_filter': self.perspective_filter,
            'executable': self.executable,
            'execution_command': self.execution_command,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'last_result': self.last_result.to_dict() if self.last_result else None,
            'expected_outcome': self.expected_outcome,
            'acceptance_criteria': self.acceptance_criteria,
            'results_history': [r.to_dict() for r in self.results_history],
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'tags': self.tags,
            'version': self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestObject':
        """Create TestObject from dictionary."""
        # Parse timestamps
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('last_run'), str):
            data['last_run'] = datetime.fromisoformat(data['last_run'])
        
        # Parse last_result
        if data.get('last_result') and isinstance(data['last_result'], dict):
            data['last_result'] = TestResult.from_dict(data['last_result'])
        
        # Parse results_history
        if data.get('results_history'):
            data['results_history'] = [
                TestResult.from_dict(r) if isinstance(r, dict) else r
                for r in data['results_history']
            ]
        
        return cls(**data)
    
    def save_to_log(self, log_path: str):
        """Append this test to a JSONL log file."""
        import os
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'a') as f:
            json.dump(self.to_dict(), f)
            f.write('\n')
    
    @staticmethod
    def load_from_log(log_path: str) -> List['TestObject']:
        """Load all tests from a JSONL log file."""
        tests = []
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        tests.append(TestObject.from_dict(data))
        except FileNotFoundError:
            pass
        
        return tests
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        status = "✓" if self.last_result and self.last_result.passed else "✗" if self.last_result else "○"
        return (
            f"TestObject({status} "
            f"id={self.test_id[:8]}..., "
            f"name='{self.test_name}', "
            f"type={self.test_type})"
        )


if __name__ == "__main__":
    # Demo: Create and execute tests
    print("🎯 TestObject Demo")
    print("=" * 50)
    
    # Create a simple test
    test1 = TestObject(
        test_name="API Health Check",
        test_description="Verify API endpoint is responding",
        test_type="integration",
        hypothesis_ids=["hyp_001"],
        perspective_filter="system",
        executable=True,
        execution_command="echo 'API OK' && exit 0",  # Simple passing test
        expected_outcome="API responds with 200 OK",
        acceptance_criteria=[
            "Response code is 200",
            "Response time < 100ms"
        ],
        created_by="agent_tester_001",
        tags=["api", "health", "critical"]
    )
    
    print(f"\n✅ Created: {test1}")
    print(f"   Name: {test1.test_name}")
    print(f"   Type: {test1.test_type}")
    print(f"   Hypotheses: {test1.hypothesis_ids}")
    print(f"   Perspective: {test1.perspective_filter}")
    
    # Execute test multiple times
    print(f"\n⚙️  Executing test 3 times...")
    for i in range(3):
        result = test1.execute(context={"run": i+1})
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"   Run {i+1}: {status} ({result.execution_time_ms:.2f}ms)")
    
    # Calculate statistics
    pass_rate = test1.calculate_pass_rate()
    avg_time = test1.calculate_average_execution_time()
    
    print(f"\n📊 Statistics:")
    print(f"   Pass Rate: {pass_rate:.1%}")
    print(f"   Avg Execution Time: {avg_time:.2f}ms")
    print(f"   Total Runs: {len(test1.results_history)}")
    print(f"   Is Flaky: {test1.is_flaky()}")
    
    # Create a test that fails
    test2 = TestObject(
        test_name="Database Connection",
        test_description="Verify database is accessible",
        test_type="integration",
        hypothesis_ids=["hyp_002"],
        executable=True,
        execution_command="exit 1",  # Failing test
        expected_outcome="Database connection succeeds",
        created_by="agent_tester_001",
        tags=["database", "critical"]
    )
    
    print(f"\n✅ Created: {test2}")
    result2 = test2.execute()
    print(f"   Execution Result: {'✓ PASS' if result2.passed else '✗ FAIL'}")
    
    if not result2.passed:
        print(f"   Error: {result2.error_message}")
    
    # Save to log
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "tests", "tests.jsonl")
        test1.save_to_log(log_path)
        test2.save_to_log(log_path)
        print(f"\n💾 Saved to: {log_path}")
        
        # Load back
        loaded = TestObject.load_from_log(log_path)
        print(f"✅ Loaded {len(loaded)} test(s) from log")
        
        for test in loaded:
            pass_rate = test.calculate_pass_rate()
            print(f"   - {test.test_name}: {pass_rate:.1%} pass rate")
    
    print("\n" + "=" * 50)
    print("✅ Demo complete!")
