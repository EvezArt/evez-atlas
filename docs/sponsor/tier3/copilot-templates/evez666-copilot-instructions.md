# Custom Copilot Instructions Template

**Access Level:** Tier 3 - Quantum Developer ($100/month)

This template provides custom GitHub Copilot instructions optimized for working with the Evez666 cognitive engine and quantum-inspired systems.

## Installation

1. Open your repository settings in GitHub
2. Navigate to Copilot settings
3. Add the instructions below to your custom instructions file (`.github/copilot-instructions.md`)

---

## Evez666 Cognitive Engine Copilot Instructions

### Project Context

You are working on the Evez666 cognitive engine - an advanced quantum-inspired threat detection and autonomous agent system. The codebase combines Python machine learning, TypeScript service orchestration, and quantum computing concepts.

### Architecture Overview

- **Quantum Module** (`quantum.py`): Core threat detection using quantum-inspired algorithms
- **LORD Dashboard**: Real-time monitoring and resource management system
- **Hazard Formulas**: Advanced risk calculation and threat assessment
- **OpenClaw Swarm**: Multi-agent orchestration and coordination
- **EKF Fusion Loop**: Extended Kalman Filter for state estimation

### Code Style & Conventions

#### Python Code
- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Prefer `dataclasses` for structured data
- Use numpy for numerical computations
- Document with docstrings (Google style)

Example:
```python
from typing import Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class ThreatMetrics:
    """Container for threat detection metrics."""
    threat_level: float
    confidence: float
    timestamp: int

def calculate_threat(
    vector: np.ndarray,
    threshold: float = 0.5
) -> Optional[ThreatMetrics]:
    """
    Calculate threat level from feature vector.
    
    Args:
        vector: Feature vector from quantum detector
        threshold: Classification threshold
        
    Returns:
        ThreatMetrics if threat detected, None otherwise
    """
    pass
```

#### TypeScript Code
- Use strict TypeScript with explicit types
- Prefer interfaces over type aliases for objects
- Use async/await for asynchronous operations
- Follow functional programming patterns where possible

Example:
```typescript
interface ResourceMetrics {
  cpuUsage: number;
  memoryUsage: number;
  activeQueries: number;
  quantumDepth: number;
}

async function fetchMetrics(): Promise<ResourceMetrics> {
  const response = await fetch('/api/metrics');
  return await response.json();
}
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `QuantumThreatDetector`, `HazardFormulaEngine`)
- **Functions**: snake_case in Python, camelCase in TypeScript
- **Constants**: UPPER_SNAKE_CASE
- **Private methods**: Prefix with underscore `_method_name`
- **Async functions**: No special prefix, rely on type system

### Quantum Computing Patterns

When working with quantum-inspired features:

1. **State Vectors**: Always normalize quantum state vectors
```python
def normalize_state(state: np.ndarray) -> np.ndarray:
    """Normalize quantum state vector to unit length."""
    norm = np.linalg.norm(state)
    return state / norm if norm > 0 else state
```

2. **Entanglement**: Use correlation matrices for entanglement representation
```python
def calculate_entanglement(
    state1: np.ndarray,
    state2: np.ndarray
) -> float:
    """Calculate entanglement measure between two states."""
    correlation = np.corrcoef(state1, state2)[0, 1]
    return abs(correlation)
```

3. **Measurement**: Simulate measurements probabilistically
```python
def measure_state(state: np.ndarray) -> int:
    """Perform probabilistic measurement of quantum state."""
    probabilities = np.abs(state) ** 2
    probabilities /= np.sum(probabilities)
    return np.random.choice(len(state), p=probabilities)
```

### Error Handling

- Use custom exception classes for domain-specific errors
- Always log errors with context
- Implement graceful degradation for non-critical failures

```python
class QuantumEngineError(Exception):
    """Base exception for quantum engine errors."""
    pass

class StateVectorError(QuantumEngineError):
    """Raised when state vector is invalid."""
    pass

def process_state(state: np.ndarray) -> None:
    """Process quantum state with error handling."""
    try:
        if len(state) == 0:
            raise StateVectorError("Empty state vector")
        # Process state...
    except StateVectorError as e:
        logger.error(f"State vector error: {e}")
        # Fallback to classical processing
        process_classical(state)
```

### Testing Patterns

- Write unit tests for all hazard formulas
- Use parameterized tests for multiple scenarios
- Mock external dependencies (APIs, quantum backends)

```python
import pytest
from hazard_formulas import HazardFormulaEngine

class TestHazardFormulas:
    @pytest.fixture
    def engine(self):
        return HazardFormulaEngine()
    
    @pytest.mark.parametrize("threat,baseline,expected", [
        (np.array([0.8, 0.6]), np.array([0.5, 0.5]), 0.3),
        (np.array([1.0, 1.0]), np.array([0.5, 0.5]), 0.7),
    ])
    def test_primary_hazard(self, engine, threat, baseline, expected):
        result = engine.calculate_primary_hazard(threat, baseline)
        assert abs(result - expected) < 0.1
```

### Performance Considerations

- Cache expensive computations (quantum state calculations)
- Use numpy vectorization instead of loops
- Profile before optimizing
- Consider memory usage for large state vectors

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_eigenvalues(matrix_tuple: tuple) -> np.ndarray:
    """Calculate eigenvalues with caching."""
    matrix = np.array(matrix_tuple)
    return np.linalg.eigvals(matrix)
```

### Security Best Practices

- Never commit secrets or API keys
- Validate all user inputs
- Use environment variables for configuration
- Implement rate limiting on API endpoints
- Sanitize data before logging

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Good: Use environment variables
API_KEY = os.getenv('QUANTUM_API_KEY')

# Bad: Hardcoded secrets
# API_KEY = "sk-1234567890"  # DON'T DO THIS
```

### Documentation Standards

- Add docstrings to all public functions and classes
- Include examples in docstrings for complex functions
- Keep README.md updated with new features
- Document hazard formula derivations with mathematical notation

```python
def calculate_composite_risk(
    metrics: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate composite risk score from multiple hazard metrics.
    
    The composite risk is calculated as:
        R_composite = Σ(w_i * H_i) + interaction_term
    
    where:
        w_i = weight for metric i
        H_i = hazard score for metric i
        interaction_term = non-linear interaction effects
    
    Args:
        metrics: Dictionary mapping metric names to hazard scores
        weights: Optional custom weights (defaults to equal weighting)
        
    Returns:
        Composite risk score in range [0, 1]
        
    Example:
        >>> metrics = {'primary': 0.5, 'quantum': 0.6, 'temporal': 0.4}
        >>> weights = {'primary': 0.4, 'quantum': 0.4, 'temporal': 0.2}
        >>> risk = calculate_composite_risk(metrics, weights)
        >>> print(f"Risk: {risk:.2f}")
        Risk: 0.52
    """
    pass
```

### Integration Patterns

#### LORD Dashboard Integration
```typescript
// Connect to LORD dashboard WebSocket
const ws = new WebSocket('ws://localhost:8080');

ws.onopen = () => {
  ws.send(JSON.stringify({ 
    type: 'subscribe',
    channels: ['metrics', 'alerts']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleMetricsUpdate(data);
};
```

#### Quantum Engine Integration
```python
from quantum import QuantumThreatDetector

# Initialize detector
detector = QuantumThreatDetector()

# Process data through quantum pipeline
result = detector.process({
    'features': feature_vector,
    'quantum_depth': 3,
    'use_ekf': True
})
```

### Common Pitfalls to Avoid

1. **Don't** use global state for quantum calculations
2. **Don't** ignore numerical precision issues
3. **Don't** forget to normalize probability distributions
4. **Don't** block the event loop in async operations
5. **Don't** mix classical and quantum operations without proper bridging

### Helpful Commands

```bash
# Run Python tests with coverage
pytest --cov=src --cov-report=html

# Build TypeScript
npm run build

# Lint Python code
pylint src/**/*.py

# Lint TypeScript code
npm run lint

# Run hazard formula validation
python docs/sponsor/tier3/hazard-formulas.py

# Start LORD dashboard
node src/lord-dashboard.js
```

### When Suggesting Code

- Prioritize security and correctness over performance
- Suggest numpy-based solutions for numerical work
- Consider quantum-classical hybrid approaches
- Think about error propagation in hazard calculations
- Remember that this is research code - clarity matters

### Project-Specific Patterns

#### Hazard Calculation Pipeline
```python
# Standard pattern for hazard assessment
def assess_threat(data: Dict) -> HazardMetrics:
    # 1. Extract features
    features = extract_features(data)
    
    # 2. Calculate individual hazards
    primary = calculate_primary_hazard(features['threat'], features['baseline'])
    quantum = calculate_quantum_hazard(features['state'], features['entanglement'])
    temporal = calculate_temporal_hazard(features['time_series'])
    
    # 3. Combine into composite risk
    composite = calculate_composite_risk({
        'primary': primary,
        'quantum': quantum,
        'temporal': temporal
    })
    
    # 4. Classify and return
    return HazardMetrics(
        primary_hazard=primary,
        quantum_hazard=quantum,
        composite_risk=composite,
        threat_level=assess_threat_level(composite),
        confidence=calculate_confidence([primary, quantum, temporal])
    )
```

---

## Usage Notes

These instructions will help Copilot provide more relevant suggestions when working on the Evez666 cognitive engine. The instructions emphasize:

- Quantum-inspired computing patterns
- Hazard calculation methodologies
- Security best practices
- Type safety and documentation
- Testing and validation

For questions or suggestions about these instructions, contact support via your Tier 3 sponsor dashboard.
