"""
Test Objects - First-class tests linked to hypotheses

Tests are first-class objects that can be:
- Explicitly linked to hypotheses
- Executed to gather evidence
- Tracked for reproducibility
- Analyzed for patterns

Design Principles:
- Tests drive knowability
- Explicit hypothesis links
- Auditable execution history
- User-driven test creation
"""

import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional, Callable


class TestStatus(Enum):
    """Status of a test"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestType(Enum):
    """Type of test"""
    USER_DRIVEN = "user_driven"  # Explicit user test
    AUTOMATED = "automated"  # Automated test
    OBSERVATIONAL = "observational"  # Passive observation
    EXPERIMENTAL = "experimental"  # Active experiment


@dataclass
class TestResult:
    """
    Result of a test execution.
    
    Captures outcome, evidence gathered, and links to events.
    """
    
    # Core identifiers
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str = ""
    execution_timestamp: float = field(default_factory=time.time)
    
    # Outcome
    status: TestStatus = TestStatus.PENDING
    passed: bool = False
    
    # Evidence gathered
    observations: List[str] = field(default_factory=list)
    measurements: Dict[str, Any] = field(default_factory=dict)
    
    # Events generated during test
    generated_events: List[str] = field(default_factory=list)
    
    # Execution details
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """Create from dictionary"""
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TestStatus(data['status'])
        return cls(**data)


@dataclass
class TestObject:
    """
    First-class test object linked to hypotheses.
    
    Represents a test that can be executed to gather evidence about
    one or more hypotheses. Tests drive knowability in HandshakeOS-E.
    """
    
    # Core identifiers
    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    
    # Test definition
    name: str = ""
    description: str = ""
    test_type: TestType = TestType.USER_DRIVEN
    
    # Hypothesis links
    hypothesis_ids: List[str] = field(default_factory=list)
    
    # Test procedure
    procedure: str = ""
    procedure_details: Dict[str, Any] = field(default_factory=dict)
    
    # Expected outcomes (for validation)
    expected_outcomes: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Execution history
    results: List[TestResult] = field(default_factory=list)
    
    # Current status
    status: TestStatus = TestStatus.PENDING
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def link_hypothesis(self, hypothesis_id: str) -> None:
        """Link this test to a hypothesis"""
        if hypothesis_id not in self.hypothesis_ids:
            self.hypothesis_ids.append(hypothesis_id)
    
    def execute(
        self,
        test_function: Optional[Callable] = None,
        **kwargs
    ) -> TestResult:
        """
        Execute this test.
        
        Args:
            test_function: Optional callable to execute the test
            **kwargs: Additional arguments for test execution
            
        Returns:
            TestResult object with execution outcome
        """
        start_time = time.time()
        self.status = TestStatus.RUNNING
        
        result = TestResult(
            test_id=self.test_id,
            execution_timestamp=start_time
        )
        
        try:
            if test_function:
                # Execute provided test function
                outcome = test_function(**kwargs)
                
                if isinstance(outcome, dict):
                    result.measurements = outcome.get('measurements', {})
                    result.observations = outcome.get('observations', [])
                    result.passed = outcome.get('passed', False)
                    result.generated_events = outcome.get('generated_events', [])
                else:
                    # Simple boolean return
                    result.passed = bool(outcome)
                
                result.status = TestStatus.PASSED if result.passed else TestStatus.FAILED
            else:
                # No test function - mark as skipped
                result.status = TestStatus.SKIPPED
                
        except Exception as e:
            result.status = TestStatus.ERROR
            result.error_message = str(e)
            result.passed = False
        
        result.duration_seconds = time.time() - start_time
        
        # Store result
        self.results.append(result)
        self.status = result.status
        
        return result
    
    def get_last_result(self) -> Optional[TestResult]:
        """Get most recent test result"""
        return self.results[-1] if self.results else None
    
    def get_success_rate(self) -> float:
        """Calculate success rate from execution history"""
        if not self.results:
            return 0.0
        
        passed_count = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        return passed_count / len(self.results)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['test_type'] = self.test_type.value
        data['status'] = self.status.value
        data['results'] = [r.to_dict() for r in self.results]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestObject':
        """Create from dictionary"""
        # Handle enums
        if 'test_type' in data and isinstance(data['test_type'], str):
            data['test_type'] = TestType(data['test_type'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TestStatus(data['status'])
        
        # Handle results
        if 'results' in data:
            data['results'] = [
                TestResult.from_dict(r) if isinstance(r, dict) else r
                for r in data['results']
            ]
        
        return cls(**data)


class TestRegistry:
    """
    Registry for tracking test objects.
    
    Enables test management, execution tracking, and hypothesis linking.
    """
    
    def __init__(self):
        """Initialize test registry"""
        self.tests: Dict[str, TestObject] = {}
    
    def register(self, test: TestObject) -> None:
        """Register a new test"""
        self.tests[test.test_id] = test
    
    def get(self, test_id: str) -> Optional[TestObject]:
        """Get test by ID"""
        return self.tests.get(test_id)
    
    def query_by_hypothesis(self, hypothesis_id: str) -> List[TestObject]:
        """Get all tests linked to a hypothesis"""
        return [
            test for test in self.tests.values()
            if hypothesis_id in test.hypothesis_ids
        ]
    
    def query_by_status(self, status: TestStatus) -> List[TestObject]:
        """Get tests by status"""
        return [
            test for test in self.tests.values()
            if test.status == status
        ]
    
    def query_by_type(self, test_type: TestType) -> List[TestObject]:
        """Get tests by type"""
        return [
            test for test in self.tests.values()
            if test.test_type == test_type
        ]
    
    def get_pending_tests(self) -> List[TestObject]:
        """Get all tests that haven't been executed"""
        return self.query_by_status(TestStatus.PENDING)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get overall test metrics"""
        total = len(self.tests)
        by_status = {}
        by_type = {}
        
        for status in TestStatus:
            count = len(self.query_by_status(status))
            by_status[status.value] = count
        
        for test_type in TestType:
            count = len(self.query_by_type(test_type))
            by_type[test_type.value] = count
        
        # Calculate overall success rate
        total_results = sum(len(t.results) for t in self.tests.values())
        passed_results = sum(
            sum(1 for r in t.results if r.status == TestStatus.PASSED)
            for t in self.tests.values()
        )
        success_rate = passed_results / total_results if total_results > 0 else 0.0
        
        return {
            'total_tests': total,
            'by_status': by_status,
            'by_type': by_type,
            'total_executions': total_results,
            'overall_success_rate': success_rate
        }
