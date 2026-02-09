"""
Engine module - Resource management, navigation mesh, caching, and entity lifecycle.

This module provides the core infrastructure for:
- Resource pool management with auto-scaling
- Threshold-based navigation mesh with gate logic
- Offline-first caching layer
- Entity lifecycle management
- Metrics and gauges
"""

from .resource_engine import ResourceEngine, ResourceType, TaskPriority, Task, ResourcePool
from .nav_mesh import NavigationMesh, ThresholdDomain, RouteType, NavigationToken, ThresholdGate
from .latent_cache import LatentCache, CacheEntry, OperationType
from .entity_manager import EntityManager, EntityState, EntityType, Entity
from .metrics import MetricsCollector, Gauge, Meter

__all__ = [
    'ResourceEngine',
    'ResourceType',
    'TaskPriority',
    'Task',
    'ResourcePool',
    'NavigationMesh',
    'ThresholdDomain',
    'RouteType',
    'NavigationToken',
    'ThresholdGate',
    'LatentCache',
    'CacheEntry',
    'OperationType',
    'EntityManager',
    'EntityState',
    'EntityType',
    'Entity',
    'MetricsCollector',
    'Gauge',
    'Meter',
]
