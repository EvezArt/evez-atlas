# Samsung Galaxy A16 Deployment Guide

This guide shows how to deploy and use the Device Automation Assistant Helper on a Samsung Galaxy A16.

## Prerequisites

### Option 1: Termux (Recommended)
Termux is a terminal emulator for Android that provides a Linux environment.

1. Install Termux from [F-Droid](https://f-droid.org/) or Google Play Store
2. Open Termux and run:
   ```bash
   pkg update
   pkg install python git
   ```

### Option 2: Pydroid 3
Pydroid 3 is a Python 3 IDE for Android.

1. Install Pydroid 3 from Google Play Store
2. Open the app and ensure Python is installed

## Installation

### Via Termux

```bash
# Clone the repository
git clone https://github.com/EvezArt/Evez666.git
cd Evez666

# Install dependencies
pip install -r requirements.txt

# Run the demo
python automation_assistant_demo.py
```

### Via Pydroid 3

1. Clone or download the repository to your device
2. Open Pydroid 3
3. Navigate to the `Evez666` folder
4. Install dependencies: Menu → Pip → Install from requirements.txt
5. Open `automation_assistant_demo.py` and run it

## Basic Usage on Device

### Example 1: Local Processing (Offline)

```python
from automation_assistant import (
    AutomationAssistantManager,
    create_local_helper,
)

# Create manager with device-friendly limits
manager = AutomationAssistantManager(max_helpers=2)

# Create local helper (works offline)
helper_id = create_local_helper(manager, name="Device-Helper")

# Submit a task
task_id = manager.submit_task(
    helper_id,
    "Check device battery status and optimize settings"
)

# Wait and get result
import time
time.sleep(1)

result = manager.get_task_result(helper_id, task_id)
print(result.result)

# Cleanup
manager.terminate_all()
```

### Example 2: Cloud Processing (Online)

```python
from automation_assistant import (
    AutomationAssistantManager,
    create_chatgpt_helper,
)
import os

# Set your OpenAI API key
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

# Create manager
manager = AutomationAssistantManager(max_helpers=2)

# Create ChatGPT helper
helper_id = create_chatgpt_helper(
    manager,
    name="Cloud-Helper",
    model="gpt-3.5-turbo",  # More efficient for mobile
    api_key=os.environ['OPENAI_API_KEY']
)

# Submit a task
task_id = manager.submit_task(
    helper_id,
    "Analyze my app usage and suggest optimizations",
    context={"device": "Samsung Galaxy A16"}
)

# Wait and get result
import time
time.sleep(2)

result = manager.get_task_result(helper_id, task_id)
print(result.result)

# Cleanup
manager.terminate_all()
```

### Example 3: Hybrid Approach (Offline + Online)

```python
from automation_assistant import (
    AutomationAssistantManager,
    create_local_helper,
    create_chatgpt_helper,
)

# Create manager with limited resources
manager = AutomationAssistantManager(max_helpers=3)

# Local helper for quick, offline tasks
local_id = create_local_helper(manager, name="Quick-Helper")

# Cloud helper for complex tasks (when online)
cloud_id = create_chatgpt_helper(
    manager,
    name="Smart-Helper",
    model="gpt-3.5-turbo"
)

# Use local helper for simple tasks
task1 = manager.submit_task(
    local_id,
    "List installed apps"
)

# Use cloud helper for analysis (when online)
task2 = manager.submit_task(
    cloud_id,
    "Suggest productivity improvements based on usage"
)

# Process results
import time
time.sleep(2)

result1 = manager.get_task_result(local_id, task1)
result2 = manager.get_task_result(cloud_id, task2)

print("Local result:", result1.result)
print("Cloud result:", result2.result)

# Cleanup
manager.terminate_all()
```

## Performance Tips for Samsung Galaxy A16

### 1. Limit Helper Count
The A16 has 4-6GB RAM. Recommended settings:
```python
# Conservative: 2 helpers
manager = AutomationAssistantManager(max_helpers=2)

# Moderate: 3 helpers
manager = AutomationAssistantManager(max_helpers=3)

# Maximum: 5 helpers (only if needed)
manager = AutomationAssistantManager(max_helpers=5)
```

### 2. Use Local Backend When Possible
```python
# Saves battery and works offline
local_helper = create_local_helper(manager)
```

### 3. Optimize Task Processing
```python
# Process one task at a time per helper
config = HelperConfig(
    backend_type=BackendType.CHATGPT,
    max_concurrent_tasks=1,  # Default, safest
    timeout_seconds=30
)
```

### 4. Clean Up Resources
```python
# Terminate helpers when done
manager.terminate_helper(helper_id)

# Or terminate all
manager.terminate_all()
```

## Battery Optimization

### 1. Disable Battery Optimization for Termux
Go to: Settings → Apps → Termux → Battery → Select "Unrestricted"

### 2. Keep Screen On (During Processing)
In Termux:
```bash
termux-wake-lock
# When done:
termux-wake-unlock
```

### 3. Use WiFi Instead of Mobile Data
Cloud-based helpers will work better on WiFi.

## Troubleshooting

### Issue: Out of Memory

**Solution:**
```python
# Reduce helper count
manager = AutomationAssistantManager(max_helpers=2)

# Use local backend
local_helper = create_local_helper(manager)
```

### Issue: Slow Performance

**Solution:**
```python
# Close other apps
# Use local backend
# Reduce concurrent tasks
config = HelperConfig(
    backend_type=BackendType.LOCAL,
    max_concurrent_tasks=1
)
```

### Issue: Network Timeout

**Solution:**
```python
# Increase timeout
config = HelperConfig(
    backend_type=BackendType.CHATGPT,
    timeout_seconds=60  # Increase from default 30
)
```

### Issue: API Key Not Working

**Solution:**
```python
# Set API key explicitly
helper_id = create_chatgpt_helper(
    manager,
    api_key="sk-your-actual-api-key"
)
```

## Example Automation Scripts

### Script 1: Device Health Check
```python
# Save as: device_health.py
from automation_assistant import *

manager = AutomationAssistantManager(max_helpers=1)
helper = create_local_helper(manager, name="Health-Check")

tasks = [
    "Check device temperature",
    "Monitor memory usage",
    "Analyze battery drain",
    "Review running processes"
]

for task in tasks:
    task_id = manager.submit_task(helper, task)
    time.sleep(1)
    result = manager.get_task_result(helper, task_id)
    print(f"✓ {task}: {result.result}")

manager.terminate_all()
```

### Script 2: Smart Notifications
```python
# Save as: smart_notifications.py
from automation_assistant import *

manager = AutomationAssistantManager(max_helpers=1)
helper = create_chatgpt_helper(
    manager,
    name="Notifier",
    model="gpt-3.5-turbo"
)

# Analyze and summarize notifications
task_id = manager.submit_task(
    helper,
    "Summarize and prioritize my notifications",
    context={"count": 50, "timeframe": "today"}
)

time.sleep(2)
result = manager.get_task_result(helper, task_id)
print(result.result)

manager.terminate_all()
```

## Running in Background

### Termux Method
```bash
# Install tmux for background sessions
pkg install tmux

# Start a new session
tmux new -s automation

# Run your script
python your_script.py

# Detach: Press Ctrl+B, then D
# Reattach later: tmux attach -t automation
```

### Service Method (Advanced)
Create a Termux boot service for persistent operation.

## Security Notes

1. **API Keys**: Never commit API keys to code. Use environment variables:
   ```python
   import os
   api_key = os.environ.get('OPENAI_API_KEY')
   ```

2. **Network Security**: Always use HTTPS endpoints (default in the system)

3. **Resource Limits**: Set appropriate limits to prevent DoS:
   ```python
   manager = AutomationAssistantManager(max_helpers=3)
   ```

4. **Data Privacy**: Local backend processes data on-device only

## Next Steps

1. Review the [full documentation](AUTOMATION_ASSISTANT_README.md)
2. Run the demo: `python automation_assistant_demo.py`
3. Explore the test suite: `pytest test_automation_assistant.py -v`
4. Create your own automation scripts
5. Join the community and share your use cases

## Support

For issues specific to Samsung Galaxy A16:
- Check Termux wiki: https://wiki.termux.com/
- Review Android-specific Python issues
- Test with smaller workloads first

For automation assistant issues:
- Check the main [README](AUTOMATION_ASSISTANT_README.md)
- Review test cases for examples
- Open an issue on GitHub

## Community Examples

Share your Samsung Galaxy A16 automation scripts in the discussions!

Example use cases:
- Battery life optimization
- App usage analysis
- Smart notifications
- Device maintenance
- Security monitoring
- Performance tuning

Happy automating! 🤖📱
