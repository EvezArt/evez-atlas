"""
Device Automation Assistant Helper System

This module provides an on-device automation assistant that can spawn
multiple helper instances for different AI backends (ChatGPT, Comet, etc.).
Designed for resource-constrained devices like Samsung Galaxy A16.
"""

import abc
import asyncio
import json
import logging
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from queue import Queue, Empty

from telemetry import get_telemetry


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class BackendType(Enum):
    """Supported AI backend types."""
    CHATGPT = "chatgpt"
    COMET = "comet"
    LOCAL = "local"
    CUSTOM = "custom"


class HelperStatus(Enum):
    """Status of a helper instance."""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    IDLE = "idle"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class HelperConfig:
    """Configuration for a helper instance."""
    backend_type: BackendType
    name: Optional[str] = None
    max_concurrent_tasks: int = 1
    timeout_seconds: int = 30
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    model: Optional[str] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Represents a task to be processed by a helper."""
    task_id: str
    prompt: str
    context: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class AIBackend(abc.ABC):
    """Abstract base class for AI backend implementations."""
    
    @abc.abstractmethod
    async def process(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a prompt and return a response."""
        pass
    
    @abc.abstractmethod
    def get_name(self) -> str:
        """Return the backend name."""
        pass


class ChatGPTBackend(AIBackend):
    """ChatGPT backend implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", 
                 api_endpoint: Optional[str] = None):
        self.api_key = api_key or "demo-key"
        self.model = model
        self.api_endpoint = api_endpoint or "https://api.openai.com/v1/chat/completions"
    
    async def process(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a prompt using ChatGPT API."""
        # Simulated response for demonstration (in production, make actual API call)
        logger.info(f"[ChatGPT] Processing prompt: {prompt[:50]}...")
        await asyncio.sleep(0.5)  # Simulate API latency
        
        response = f"ChatGPT Response (model: {self.model}): Processed '{prompt[:30]}...'"
        if context:
            response += f" with context keys: {list(context.keys())}"
        
        return response
    
    def get_name(self) -> str:
        return f"ChatGPT ({self.model})"


class CometBackend(AIBackend):
    """Comet backend implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "comet-v1",
                 api_endpoint: Optional[str] = None):
        self.api_key = api_key or "demo-key"
        self.model = model
        self.api_endpoint = api_endpoint or "https://api.comet.ml/v1/generate"
    
    async def process(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a prompt using Comet API."""
        # Simulated response for demonstration
        logger.info(f"[Comet] Processing prompt: {prompt[:50]}...")
        await asyncio.sleep(0.4)  # Simulate API latency
        
        response = f"Comet Response (model: {self.model}): Analyzed '{prompt[:30]}...'"
        if context:
            response += f" | Context size: {len(context)}"
        
        return response
    
    def get_name(self) -> str:
        return f"Comet ({self.model})"


class LocalBackend(AIBackend):
    """Local/mock backend for testing and offline use."""
    
    def __init__(self, model: str = "local-mock"):
        self.model = model
    
    async def process(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a prompt using local logic."""
        logger.info(f"[Local] Processing prompt: {prompt[:50]}...")
        await asyncio.sleep(0.1)  # Simulate minimal processing time
        
        response = f"Local Response: Echo of '{prompt}'"
        if context:
            response += f" [Context provided]"
        
        return response
    
    def get_name(self) -> str:
        return f"Local ({self.model})"


class AutomationHelper:
    """
    Individual automation helper instance that processes tasks using an AI backend.
    """
    
    def __init__(self, config: HelperConfig):
        self.helper_id = str(uuid.uuid4())[:8]
        self.config = config
        self.name = config.name or f"Helper-{self.helper_id}"
        self.status = HelperStatus.INITIALIZING
        
        # Track spawn latency
        spawn_start = time.time()
        try:
            self.backend = self._create_backend()
            spawn_latency_ms = (time.time() - spawn_start) * 1000
            
            # Log successful spawn
            get_telemetry().log_helper_spawn(
                helper_id=self.helper_id,
                backend=self.backend.get_name(),
                latency_ms=spawn_latency_ms,
                success=True
            )
        except Exception as e:
            spawn_latency_ms = (time.time() - spawn_start) * 1000
            get_telemetry().log_helper_spawn(
                helper_id=self.helper_id,
                backend=config.backend_type.value,
                latency_ms=spawn_latency_ms,
                success=False,
                error=str(e)
            )
            raise
        
        self.task_queue: Queue = Queue()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._executor = ThreadPoolExecutor(max_workers=config.max_concurrent_tasks)
        
        logger.info(f"[{self.name}] Initialized with backend: {self.backend.get_name()}")
    
    def _create_backend(self) -> AIBackend:
        """Create the appropriate AI backend based on configuration."""
        if self.config.backend_type == BackendType.CHATGPT:
            return ChatGPTBackend(
                api_key=self.config.api_key,
                model=self.config.model or "gpt-3.5-turbo",
                api_endpoint=self.config.api_endpoint
            )
        elif self.config.backend_type == BackendType.COMET:
            return CometBackend(
                api_key=self.config.api_key,
                model=self.config.model or "comet-v1",
                api_endpoint=self.config.api_endpoint
            )
        elif self.config.backend_type == BackendType.LOCAL:
            return LocalBackend(model=self.config.model or "local-mock")
        else:
            raise ValueError(f"Unsupported backend type: {self.config.backend_type}")
    
    def start(self):
        """Start the helper worker thread."""
        if self._running:
            logger.warning(f"[{self.name}] Already running")
            return
        
        self._running = True
        self.status = HelperStatus.READY
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        logger.info(f"[{self.name}] Started")
    
    def stop(self):
        """Stop the helper worker thread."""
        if not self._running:
            return
        
        self._running = False
        self.status = HelperStatus.TERMINATED
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        self._executor.shutdown(wait=True)
        logger.info(f"[{self.name}] Stopped")
    
    def submit_task(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Submit a task to this helper."""
        task = Task(
            task_id=str(uuid.uuid4()),
            prompt=prompt,
            context=context
        )
        self.task_queue.put(task)
        logger.info(f"[{self.name}] Task {task.task_id[:8]} submitted")
        return task.task_id
    
    def get_task_result(self, task_id: str) -> Optional[Task]:
        """Get the result of a completed task."""
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def _worker_loop(self):
        """Main worker loop that processes tasks."""
        logger.info(f"[{self.name}] Worker loop started")
        
        while self._running:
            try:
                # Get task from queue with timeout
                task = self.task_queue.get(timeout=1)
                self._process_task(task)
            except Empty:
                # No tasks available, set status to idle
                if self.status != HelperStatus.IDLE:
                    self.status = HelperStatus.IDLE
                continue
            except Exception as e:
                logger.error(f"[{self.name}] Worker loop error: {e}")
                self.status = HelperStatus.ERROR
        
        logger.info(f"[{self.name}] Worker loop ended")
    
    def _process_task(self, task: Task):
        """Process a single task."""
        task_start = time.time()
        try:
            self.status = HelperStatus.PROCESSING
            self.active_tasks[task.task_id] = task
            
            logger.info(f"[{self.name}] Processing task {task.task_id[:8]}")
            
            # Run async backend processing in executor
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                backend_call_start = time.time()
                result = loop.run_until_complete(
                    self.backend.process(task.prompt, task.context)
                )
                backend_latency_ms = (time.time() - backend_call_start) * 1000
                
                task.result = result
                task.completed_at = datetime.now()
                
                # Log successful backend call
                get_telemetry().log_backend_call(
                    helper_id=self.helper_id,
                    backend=self.backend.get_name(),
                    latency_ms=backend_latency_ms,
                    success=True
                )
                
                task_latency_ms = (time.time() - task_start) * 1000
                get_telemetry().log_task_complete(
                    helper_id=self.helper_id,
                    task_id=task.task_id,
                    backend=self.backend.get_name(),
                    latency_ms=task_latency_ms,
                    success=True
                )
                
                logger.info(f"[{self.name}] Task {task.task_id[:8]} completed")
            finally:
                loop.close()
            
        except Exception as e:
            logger.error(f"[{self.name}] Task {task.task_id[:8]} failed: {e}")
            task.error = str(e)
            task.completed_at = datetime.now()
            
            # Log failed task
            task_latency_ms = (time.time() - task_start) * 1000
            get_telemetry().log_task_complete(
                helper_id=self.helper_id,
                task_id=task.task_id,
                backend=self.backend.get_name(),
                latency_ms=task_latency_ms,
                success=False,
                error=str(e)
            )
        finally:
            # Move task from active to completed
            self.active_tasks.pop(task.task_id, None)
            self.completed_tasks.append(task)
            self.status = HelperStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of this helper."""
        return {
            "helper_id": self.helper_id,
            "name": self.name,
            "status": self.status.value,
            "backend": self.backend.get_name(),
            "queued_tasks": self.task_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks)
        }


class AutomationAssistantManager:
    """
    Manager for multiple automation helper instances.
    Handles spawning, lifecycle, and coordination of helpers.
    """
    
    def __init__(self, max_helpers: int = 10):
        self.max_helpers = max_helpers
        self.helpers: Dict[str, AutomationHelper] = {}
        self._lock = threading.Lock()
        logger.info(f"AutomationAssistantManager initialized (max_helpers={max_helpers})")
    
    def spawn_helper(self, config: HelperConfig) -> str:
        """Spawn a new helper instance."""
        with self._lock:
            if len(self.helpers) >= self.max_helpers:
                raise RuntimeError(f"Maximum number of helpers ({self.max_helpers}) reached")
            
            helper = AutomationHelper(config)
            helper.start()
            self.helpers[helper.helper_id] = helper
            
            logger.info(f"Spawned new helper: {helper.name} (ID: {helper.helper_id})")
            return helper.helper_id
    
    def terminate_helper(self, helper_id: str):
        """Terminate a specific helper."""
        with self._lock:
            if helper_id not in self.helpers:
                raise ValueError(f"Helper {helper_id} not found")
            
            helper = self.helpers[helper_id]
            helper.stop()
            del self.helpers[helper_id]
            
            logger.info(f"Terminated helper: {helper.name} (ID: {helper_id})")
    
    def get_helper(self, helper_id: str) -> Optional[AutomationHelper]:
        """Get a specific helper by ID."""
        return self.helpers.get(helper_id)
    
    def submit_task(self, helper_id: str, prompt: str, 
                   context: Optional[Dict[str, Any]] = None) -> str:
        """Submit a task to a specific helper."""
        helper = self.get_helper(helper_id)
        if not helper:
            raise ValueError(f"Helper {helper_id} not found")
        
        return helper.submit_task(prompt, context)
    
    def get_task_result(self, helper_id: str, task_id: str) -> Optional[Task]:
        """Get task result from a specific helper."""
        helper = self.get_helper(helper_id)
        if not helper:
            return None
        
        return helper.get_task_result(task_id)
    
    def get_all_helpers_status(self) -> List[Dict[str, Any]]:
        """Get status of all helpers."""
        return [helper.get_status() for helper in self.helpers.values()]
    
    def terminate_all(self):
        """Terminate all helpers."""
        with self._lock:
            for helper in list(self.helpers.values()):
                helper.stop()
            self.helpers.clear()
            logger.info("All helpers terminated")


# Convenience function for quick helper spawning
def create_chatgpt_helper(manager: AutomationAssistantManager, 
                         name: Optional[str] = None,
                         model: str = "gpt-3.5-turbo",
                         api_key: Optional[str] = None) -> str:
    """Convenience function to spawn a ChatGPT helper."""
    config = HelperConfig(
        backend_type=BackendType.CHATGPT,
        name=name,
        model=model,
        api_key=api_key
    )
    return manager.spawn_helper(config)


def create_comet_helper(manager: AutomationAssistantManager,
                       name: Optional[str] = None,
                       model: str = "comet-v1",
                       api_key: Optional[str] = None) -> str:
    """Convenience function to spawn a Comet helper."""
    config = HelperConfig(
        backend_type=BackendType.COMET,
        name=name,
        model=model,
        api_key=api_key
    )
    return manager.spawn_helper(config)


def create_local_helper(manager: AutomationAssistantManager,
                       name: Optional[str] = None) -> str:
    """Convenience function to spawn a Local helper."""
    config = HelperConfig(
        backend_type=BackendType.LOCAL,
        name=name
    )
    return manager.spawn_helper(config)
