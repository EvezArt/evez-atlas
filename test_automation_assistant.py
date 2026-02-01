"""
Tests for the Device Automation Assistant Helper System
"""

import pytest
import time
from automation_assistant import (
    AutomationAssistantManager,
    AutomationHelper,
    BackendType,
    HelperConfig,
    HelperStatus,
    ChatGPTBackend,
    CometBackend,
    LocalBackend,
    create_chatgpt_helper,
    create_comet_helper,
    create_local_helper,
)


class TestBackends:
    """Tests for AI backend implementations."""
    
    @pytest.mark.asyncio
    async def test_chatgpt_backend_process(self):
        """Test ChatGPT backend can process prompts."""
        backend = ChatGPTBackend(model="gpt-3.5-turbo")
        result = await backend.process("Test prompt")
        
        assert result is not None
        assert "ChatGPT Response" in result
        assert "gpt-3.5-turbo" in result
    
    @pytest.mark.asyncio
    async def test_comet_backend_process(self):
        """Test Comet backend can process prompts."""
        backend = CometBackend(model="comet-v1")
        result = await backend.process("Test prompt")
        
        assert result is not None
        assert "Comet Response" in result
        assert "comet-v1" in result
    
    @pytest.mark.asyncio
    async def test_local_backend_process(self):
        """Test Local backend can process prompts."""
        backend = LocalBackend()
        result = await backend.process("Test prompt")
        
        assert result is not None
        assert "Local Response" in result
    
    @pytest.mark.asyncio
    async def test_backend_with_context(self):
        """Test backend processing with context."""
        backend = LocalBackend()
        context = {"key": "value", "priority": "high"}
        result = await backend.process("Test prompt", context)
        
        assert result is not None
        assert "Context provided" in result
    
    def test_backend_names(self):
        """Test backend name methods."""
        chatgpt = ChatGPTBackend(model="gpt-4")
        comet = CometBackend(model="comet-v2")
        local = LocalBackend(model="local-test")
        
        assert "gpt-4" in chatgpt.get_name()
        assert "comet-v2" in comet.get_name()
        assert "local-test" in local.get_name()


class TestAutomationHelper:
    """Tests for AutomationHelper class."""
    
    def test_helper_initialization(self):
        """Test helper can be initialized with configuration."""
        config = HelperConfig(
            backend_type=BackendType.LOCAL,
            name="TestHelper"
        )
        helper = AutomationHelper(config)
        
        assert helper.name == "TestHelper"
        assert helper.status == HelperStatus.INITIALIZING
        assert helper.backend is not None
    
    def test_helper_start_stop(self):
        """Test helper can be started and stopped."""
        config = HelperConfig(backend_type=BackendType.LOCAL)
        helper = AutomationHelper(config)
        
        helper.start()
        time.sleep(0.1)  # Give worker thread time to start
        assert helper.status in [HelperStatus.READY, HelperStatus.IDLE]
        assert helper._running is True
        
        helper.stop()
        # After stop, status may be set before or during thread cleanup
        # The important check is that _running is False
        assert helper._running is False
    
    def test_helper_submit_task(self):
        """Test submitting a task to helper."""
        config = HelperConfig(backend_type=BackendType.LOCAL)
        helper = AutomationHelper(config)
        helper.start()
        
        task_id = helper.submit_task("Test prompt")
        assert task_id is not None
        assert len(task_id) > 0
        
        helper.stop()
    
    def test_helper_process_task(self):
        """Test helper can process a task and return result."""
        config = HelperConfig(backend_type=BackendType.LOCAL)
        helper = AutomationHelper(config)
        helper.start()
        
        task_id = helper.submit_task("Test prompt")
        
        # Wait for processing
        time.sleep(1)
        
        result = helper.get_task_result(task_id)
        assert result is not None
        assert result.result is not None
        assert "Local Response" in result.result
        
        helper.stop()
    
    def test_helper_status(self):
        """Test helper status reporting."""
        config = HelperConfig(
            backend_type=BackendType.LOCAL,
            name="StatusTest"
        )
        helper = AutomationHelper(config)
        helper.start()
        
        status = helper.get_status()
        assert status["name"] == "StatusTest"
        assert status["status"] in [s.value for s in HelperStatus]
        assert "backend" in status
        assert "queued_tasks" in status
        
        helper.stop()
    
    def test_helper_multiple_tasks(self):
        """Test helper can process multiple tasks."""
        config = HelperConfig(backend_type=BackendType.LOCAL)
        helper = AutomationHelper(config)
        helper.start()
        
        task_ids = []
        for i in range(3):
            task_id = helper.submit_task(f"Test prompt {i}")
            task_ids.append(task_id)
        
        # Wait for all tasks to complete
        time.sleep(2)
        
        # Check all tasks completed
        for task_id in task_ids:
            result = helper.get_task_result(task_id)
            assert result is not None
            assert result.result is not None
        
        helper.stop()


class TestAutomationAssistantManager:
    """Tests for AutomationAssistantManager class."""
    
    def test_manager_initialization(self):
        """Test manager can be initialized."""
        manager = AutomationAssistantManager(max_helpers=5)
        assert manager.max_helpers == 5
        assert len(manager.helpers) == 0
    
    def test_spawn_helper(self):
        """Test spawning a new helper."""
        manager = AutomationAssistantManager()
        
        config = HelperConfig(
            backend_type=BackendType.LOCAL,
            name="TestHelper"
        )
        helper_id = manager.spawn_helper(config)
        
        assert helper_id is not None
        assert len(manager.helpers) == 1
        
        manager.terminate_all()
    
    def test_spawn_multiple_helpers(self):
        """Test spawning multiple helpers."""
        manager = AutomationAssistantManager()
        
        helper_ids = []
        for i in range(3):
            config = HelperConfig(
                backend_type=BackendType.LOCAL,
                name=f"Helper{i}"
            )
            helper_id = manager.spawn_helper(config)
            helper_ids.append(helper_id)
        
        assert len(manager.helpers) == 3
        assert len(set(helper_ids)) == 3  # All IDs are unique
        
        manager.terminate_all()
    
    def test_max_helpers_limit(self):
        """Test max helpers limit is enforced."""
        manager = AutomationAssistantManager(max_helpers=2)
        
        config = HelperConfig(backend_type=BackendType.LOCAL)
        
        # Spawn max helpers
        manager.spawn_helper(config)
        manager.spawn_helper(config)
        
        # Try to spawn one more
        with pytest.raises(RuntimeError, match="Maximum number of helpers"):
            manager.spawn_helper(config)
        
        manager.terminate_all()
    
    def test_terminate_helper(self):
        """Test terminating a specific helper."""
        manager = AutomationAssistantManager()
        
        config = HelperConfig(backend_type=BackendType.LOCAL)
        helper_id = manager.spawn_helper(config)
        
        assert len(manager.helpers) == 1
        
        manager.terminate_helper(helper_id)
        
        assert len(manager.helpers) == 0
    
    def test_get_helper(self):
        """Test retrieving a helper by ID."""
        manager = AutomationAssistantManager()
        
        config = HelperConfig(backend_type=BackendType.LOCAL)
        helper_id = manager.spawn_helper(config)
        
        helper = manager.get_helper(helper_id)
        assert helper is not None
        assert helper.helper_id == helper_id
        
        manager.terminate_all()
    
    def test_submit_task_via_manager(self):
        """Test submitting a task through the manager."""
        manager = AutomationAssistantManager()
        
        config = HelperConfig(backend_type=BackendType.LOCAL)
        helper_id = manager.spawn_helper(config)
        
        task_id = manager.submit_task(helper_id, "Test prompt")
        assert task_id is not None
        
        # Wait for processing
        time.sleep(1)
        
        result = manager.get_task_result(helper_id, task_id)
        assert result is not None
        assert result.result is not None
        
        manager.terminate_all()
    
    def test_get_all_helpers_status(self):
        """Test getting status of all helpers."""
        manager = AutomationAssistantManager()
        
        # Spawn multiple helpers
        for i in range(3):
            config = HelperConfig(
                backend_type=BackendType.LOCAL,
                name=f"Helper{i}"
            )
            manager.spawn_helper(config)
        
        statuses = manager.get_all_helpers_status()
        assert len(statuses) == 3
        
        for status in statuses:
            assert "name" in status
            assert "status" in status
            assert "backend" in status
        
        manager.terminate_all()
    
    def test_terminate_all(self):
        """Test terminating all helpers."""
        manager = AutomationAssistantManager()
        
        # Spawn multiple helpers
        for i in range(3):
            config = HelperConfig(backend_type=BackendType.LOCAL)
            manager.spawn_helper(config)
        
        assert len(manager.helpers) == 3
        
        manager.terminate_all()
        
        assert len(manager.helpers) == 0


class TestConvenienceFunctions:
    """Tests for convenience helper creation functions."""
    
    def test_create_chatgpt_helper(self):
        """Test creating a ChatGPT helper."""
        manager = AutomationAssistantManager()
        
        helper_id = create_chatgpt_helper(
            manager,
            name="ChatGPT-Test",
            model="gpt-4"
        )
        
        assert helper_id is not None
        helper = manager.get_helper(helper_id)
        assert helper.name == "ChatGPT-Test"
        assert "gpt-4" in helper.backend.get_name()
        
        manager.terminate_all()
    
    def test_create_comet_helper(self):
        """Test creating a Comet helper."""
        manager = AutomationAssistantManager()
        
        helper_id = create_comet_helper(
            manager,
            name="Comet-Test",
            model="comet-v2"
        )
        
        assert helper_id is not None
        helper = manager.get_helper(helper_id)
        assert helper.name == "Comet-Test"
        assert "comet-v2" in helper.backend.get_name()
        
        manager.terminate_all()
    
    def test_create_local_helper(self):
        """Test creating a Local helper."""
        manager = AutomationAssistantManager()
        
        helper_id = create_local_helper(
            manager,
            name="Local-Test"
        )
        
        assert helper_id is not None
        helper = manager.get_helper(helper_id)
        assert helper.name == "Local-Test"
        assert "Local" in helper.backend.get_name()
        
        manager.terminate_all()


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_multi_backend_parallel_processing(self):
        """Test parallel processing with multiple backends."""
        manager = AutomationAssistantManager()
        
        # Create helpers for each backend type
        chatgpt_id = create_chatgpt_helper(manager, name="ChatGPT")
        comet_id = create_comet_helper(manager, name="Comet")
        local_id = create_local_helper(manager, name="Local")
        
        # Submit tasks to all helpers
        task1 = manager.submit_task(chatgpt_id, "Task 1")
        task2 = manager.submit_task(comet_id, "Task 2")
        task3 = manager.submit_task(local_id, "Task 3")
        
        # Wait for processing
        time.sleep(2)
        
        # Verify all tasks completed
        result1 = manager.get_task_result(chatgpt_id, task1)
        result2 = manager.get_task_result(comet_id, task2)
        result3 = manager.get_task_result(local_id, task3)
        
        assert result1 is not None and result1.result is not None
        assert result2 is not None and result2.result is not None
        assert result3 is not None and result3.result is not None
        
        manager.terminate_all()
    
    def test_helper_lifecycle(self):
        """Test complete lifecycle of spawning, using, and terminating helpers."""
        manager = AutomationAssistantManager(max_helpers=3)
        
        # Spawn helpers
        helper_ids = []
        for i in range(3):
            config = HelperConfig(
                backend_type=BackendType.LOCAL,
                name=f"Lifecycle-{i}"
            )
            helper_id = manager.spawn_helper(config)
            helper_ids.append(helper_id)
        
        # Use helpers
        for helper_id in helper_ids:
            manager.submit_task(helper_id, "Lifecycle test")
        
        # Wait for processing
        time.sleep(1.5)
        
        # Check status
        statuses = manager.get_all_helpers_status()
        assert len(statuses) == 3
        
        # Terminate individual helpers
        for helper_id in helper_ids[:2]:
            manager.terminate_helper(helper_id)
        
        assert len(manager.helpers) == 1
        
        # Terminate remaining
        manager.terminate_all()
        assert len(manager.helpers) == 0
