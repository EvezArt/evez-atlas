# Device Automation Assistant Helper System

A comprehensive on-device automation assistant system that can spawn multiple helper instances for different AI backends. Designed for resource-constrained devices like the Samsung Galaxy A16.

## Features

- **Multi-Backend Support**: Integration with ChatGPT, Comet, and Local backends
- **Dynamic Helper Spawning**: Create multiple helper instances on-demand
- **Parallel Task Processing**: Process multiple tasks concurrently across different helpers
- **Resource Management**: Optimized for device constraints with configurable limits
- **Inter-Helper Communication**: Coordinate multiple helpers working together
- **Device Optimization**: Special configurations for mobile devices

## Architecture

### Core Components

1. **AutomationAssistantManager**: Central manager for spawning and coordinating helper instances
2. **AutomationHelper**: Individual helper instance that processes tasks using an AI backend
3. **AIBackend**: Abstract interface for different AI service providers (ChatGPT, Comet, Local)
4. **Task Queue System**: Asynchronous task processing with result tracking

### Supported Backends

#### ChatGPT Backend
- Uses OpenAI's GPT models (gpt-3.5-turbo, gpt-4, etc.)
- Configurable API endpoints and authentication
- Best for: Complex reasoning, natural language tasks

#### Comet Backend
- Integration with Comet ML's generation capabilities
- Customizable model selection
- Best for: ML experiment tracking, data analysis

#### Local Backend
- Offline-capable mock backend for testing and development
- No external dependencies
- Best for: Testing, offline operation, prototyping

## Installation

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### For Samsung Galaxy A16 (via Termux)

```bash
# Install Termux from F-Droid or Google Play
# In Termux:
pkg install python
pip install fastapi httpx pydantic python-dotenv uvicorn
```

## Quick Start

### Basic Usage

```python
from automation_assistant import (
    AutomationAssistantManager,
    create_chatgpt_helper,
    create_local_helper,
)

# Create the manager
manager = AutomationAssistantManager(max_helpers=5)

# Spawn a ChatGPT helper
chatgpt_id = create_chatgpt_helper(
    manager,
    name="ChatGPT-Assistant",
    model="gpt-3.5-turbo",
    api_key="your-api-key"
)

# Spawn a local helper for offline use
local_id = create_local_helper(
    manager,
    name="Local-Assistant"
)

# Submit tasks
task_id = manager.submit_task(
    chatgpt_id,
    "Analyze network security patterns",
    context={"priority": "high"}
)

# Wait for processing
import time
time.sleep(2)

# Get results
result = manager.get_task_result(chatgpt_id, task_id)
print(result.result)

# Cleanup
manager.terminate_all()
```

### Running the Demo

```bash
# Run the comprehensive demo
python automation_assistant_demo.py

# Run the demo and generate telemetry debrief
python automation_assistant_demo.py --debrief
```

This will demonstrate:
- Multi-backend support
- Dynamic helper spawning
- Parallel task processing
- Device-optimized operation

## Telemetry & Debrief

The automation assistant includes built-in telemetry tracking to monitor performance and reliability.

### What is Tracked

- **Helper Spawn Latency**: Time taken to initialize each helper instance
- **Backend Call Success/Failure**: Success rate of backend API calls
- **Task Completion Metrics**: Task processing times and outcomes
- **Error Rates**: Frequency and types of errors encountered

### Telemetry Data Location

All telemetry is appended to `src/memory/audit.jsonl` in structured JSONL format:

```json
{
  "timestamp": 1769967212.25,
  "run_id": "20260205_165411",
  "event": "helper_spawn",
  "helper_id": "a1b2c3d4",
  "backend": "ChatGPT (gpt-3.5-turbo)",
  "latency_ms": 12.5,
  "success": true
}
```

### Generating a Debrief Report

To analyze telemetry and generate a health report:

```bash
# After running demos
python scripts/debrief.py
```

The debrief script will:
1. Read all telemetry entries from `audit.jsonl`
2. Compute aggregated statistics (p95 latency, failure rate, top errors)
3. Print a console summary
4. Save a detailed markdown report to `docs/debrief/latest.md`

### Debrief Metrics

The debrief report includes:

- **Overall Health**: 🟢 OK (< 5% failures), 🟡 Degraded (5-20%), or 🔴 Critical (> 20%)
- **Per-Backend Stats**: Success count, error count, failure rate
- **Latency Metrics**: Average, P50 (median), and P95 latency
- **Stability Score**: Computed as 1 - (errors / total events)

### Example Debrief Output

```
====================================================================
Automation Assistant Telemetry Debrief
====================================================================

Overall Health: 🟢 OK
Total Runs: 3
Total Events: 45
Success: 44
Errors: 1
Failure Rate: 2.22%

Per-Backend Stats:
  ChatGPT (gpt-3.5-turbo):
    Calls: 15, Errors: 0, Failure: 0.00%
    Latency: avg=520.5ms, p50=515.2ms, p95=548.1ms
  Local (local-mock):
    Calls: 15, Errors: 1, Failure: 6.67%
    Latency: avg=102.3ms, p50=101.5ms, p95=115.8ms

✅ Detailed report saved to: docs/debrief/latest.md
====================================================================
```

### Automated Debrief

Run the demo with the `--debrief` flag to automatically generate a debrief report after completion:

```bash
python automation_assistant_demo.py --debrief
```

This is useful for:
- Continuous monitoring of system health
- Performance regression testing
- Identifying problematic backends or patterns
- Tracking improvements over time

## Advanced Configuration

### Creating Custom Helper Configurations

```python
from automation_assistant import HelperConfig, BackendType

# Create a custom configuration
config = HelperConfig(
    backend_type=BackendType.CHATGPT,
    name="Custom-Helper",
    max_concurrent_tasks=3,
    timeout_seconds=60,
    api_key="your-api-key",
    model="gpt-4-turbo",
    custom_params={"temperature": 0.7}
)

# Spawn with custom config
helper_id = manager.spawn_helper(config)
```

### Device-Optimized Setup

For resource-constrained devices like Samsung Galaxy A16:

```python
# Limit total helpers
manager = AutomationAssistantManager(max_helpers=3)

# Use local backend for offline capability
local_id = create_local_helper(manager, name="Offline-Helper")

# Use efficient cloud model when needed
chatgpt_id = create_chatgpt_helper(
    manager,
    name="Cloud-Helper",
    model="gpt-3.5-turbo"  # More efficient than gpt-4
)
```

### Multiple Instances of Same Backend

```python
# Spawn multiple ChatGPT instances with different models
helpers = []

for model in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]:
    config = HelperConfig(
        backend_type=BackendType.CHATGPT,
        name=f"ChatGPT-{model}",
        model=model
    )
    helper_id = manager.spawn_helper(config)
    helpers.append(helper_id)

# Submit parallel tasks
for helper_id in helpers:
    manager.submit_task(helper_id, "Process this task")
```

## API Reference

### AutomationAssistantManager

#### Methods

- `spawn_helper(config: HelperConfig) -> str`: Spawn a new helper instance
- `terminate_helper(helper_id: str)`: Terminate a specific helper
- `get_helper(helper_id: str) -> AutomationHelper`: Get helper by ID
- `submit_task(helper_id: str, prompt: str, context: dict) -> str`: Submit a task
- `get_task_result(helper_id: str, task_id: str) -> Task`: Get task result
- `get_all_helpers_status() -> List[dict]`: Get status of all helpers
- `terminate_all()`: Terminate all helpers

### AutomationHelper

#### Properties

- `helper_id`: Unique identifier
- `name`: Human-readable name
- `status`: Current status (INITIALIZING, READY, PROCESSING, IDLE, ERROR, TERMINATED)
- `backend`: Associated AI backend

#### Methods

- `start()`: Start the helper worker thread
- `stop()`: Stop the helper worker thread
- `submit_task(prompt: str, context: dict) -> str`: Submit a task
- `get_task_result(task_id: str) -> Task`: Get task result
- `get_status() -> dict`: Get current status

### HelperConfig

Configuration for spawning helpers:

```python
@dataclass
class HelperConfig:
    backend_type: BackendType  # CHATGPT, COMET, LOCAL
    name: Optional[str] = None
    max_concurrent_tasks: int = 1
    timeout_seconds: int = 30
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    model: Optional[str] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)
```

### Task

Result object for completed tasks:

```python
@dataclass
class Task:
    task_id: str
    prompt: str
    context: Optional[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]
    result: Optional[Any]
    error: Optional[str]
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest test_automation_assistant.py -v

# Run specific test class
pytest test_automation_assistant.py::TestBackends -v

# Run with coverage
pytest test_automation_assistant.py --cov=automation_assistant
```

## Performance Considerations

### Samsung Galaxy A16 Optimization

The Samsung Galaxy A16 has:
- Octa-core processor
- 4-6GB RAM
- Limited background processing

Recommended settings:
```python
# Conservative settings for mobile devices
manager = AutomationAssistantManager(max_helpers=3)

# Use local backend when possible
local_id = create_local_helper(manager)

# Limit concurrent tasks per helper
config = HelperConfig(
    backend_type=BackendType.CHATGPT,
    max_concurrent_tasks=1,  # Process one at a time
    timeout_seconds=30
)
```

### Memory Management

- Each helper uses ~10-20MB of memory
- Task results are stored in memory until retrieved
- Use `terminate_helper()` to free resources when done
- Call `get_task_result()` and clear old tasks periodically

### Network Optimization

- Use Local backend when offline
- Batch tasks when possible
- Set appropriate timeout values
- Monitor network conditions before cloud tasks

## Use Cases

### Network Security Monitoring

```python
# Spawn security analysis helpers
security_helper = create_chatgpt_helper(
    manager,
    name="Security-Analyst",
    model="gpt-4"
)

# Analyze network patterns
task_id = manager.submit_task(
    security_helper,
    "Analyze this network log for security threats",
    context={"log_data": network_logs}
)
```

### Multi-Model Comparison

```python
# Spawn multiple models
models = ["gpt-3.5-turbo", "gpt-4"]
helpers = [create_chatgpt_helper(manager, model=m) for m in models]

# Submit same prompt to all
prompt = "Explain quantum computing"
tasks = [(h, manager.submit_task(h, prompt)) for h in helpers]

# Compare results
for helper_id, task_id in tasks:
    result = manager.get_task_result(helper_id, task_id)
    print(f"Model result: {result.result}")
```

### Automated Device Maintenance

```python
# Device optimization assistant
local_helper = create_local_helper(manager, name="Device-Optimizer")

tasks = [
    "Check battery health and suggest optimizations",
    "Analyze app usage and recommend cleanup",
    "Monitor system resources"
]

for task_prompt in tasks:
    manager.submit_task(local_helper, task_prompt)
```

## Troubleshooting

### Helper Not Starting

```python
# Check helper status
status = helper.get_status()
print(status)

# Common issues:
# - Backend initialization failure
# - Invalid configuration
# - Resource constraints
```

### Task Not Completing

```python
# Check if task is in queue
status = helper.get_status()
print(f"Queued tasks: {status['queued_tasks']}")

# Increase timeout if needed
config = HelperConfig(
    backend_type=BackendType.CHATGPT,
    timeout_seconds=60  # Increase from default 30
)
```

### Memory Issues on Device

```python
# Reduce helper count
manager = AutomationAssistantManager(max_helpers=2)

# Clear completed tasks
manager.terminate_helper(helper_id)  # Frees memory

# Use lightweight backends
local_id = create_local_helper(manager)
```

## Security Considerations

1. **API Keys**: Store API keys securely, use environment variables
2. **Input Validation**: Validate all task inputs before processing
3. **Rate Limiting**: Implement rate limiting for API calls
4. **Resource Limits**: Set max_helpers to prevent resource exhaustion
5. **Network Security**: Use HTTPS for all API communications

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code follows existing style
- New features include tests
- Documentation is updated

## License

See LICENSE file for details.

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review test cases for examples

## Changelog

### Version 1.0.0 (2026-02-01)

- Initial release
- Multi-backend support (ChatGPT, Comet, Local)
- Dynamic helper spawning
- Parallel task processing
- Device optimization for Samsung Galaxy A16
- Comprehensive test suite
- Full documentation
