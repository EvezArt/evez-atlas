"""
DOMAIN INVENTORY MANAGER
Manages propertizational inventories for all domains
Tracks and delegates property management to entity farm
Creator: @Evez666
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class DomainInventoryManager:
    """
    Manages domain property inventories for outsourcing to entity farm.
    Tracks all properties across all domains.
    """
    
    def __init__(self, creator: str = "@Evez666"):
        self.creator = creator
        self.data_dir = Path("data/domain_inventory")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Domain tracking
        self.domains = {}
        self.properties = {}
        self.delegations = {}
        
        # Logging
        self.inventory_log = self.data_dir / "inventory.jsonl"
        self.delegation_log = self.data_dir / "delegations.jsonl"
    
    def register_domain(
        self,
        domain_name: str,
        domain_type: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Register a new domain for inventory management"""
        domain_id = f"dom-{len(self.domains):04d}"
        
        domain = {
            "domain_id": domain_id,
            "domain_name": domain_name,
            "domain_type": domain_type,
            "metadata": metadata or {},
            "registered_at": time.time(),
            "property_count": 0,
            "delegated_to": None,
            "status": "registered"
        }
        
        self.domains[domain_id] = domain
        
        self._log_inventory("domain_registered", domain)
        
        return domain
    
    def add_property(
        self,
        domain_id: str,
        property_name: str,
        property_value: Any,
        property_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Add a property to a domain inventory"""
        if domain_id not in self.domains:
            raise ValueError(f"Domain {domain_id} not found")
        
        property_id = f"prop-{len(self.properties):06d}"
        
        prop = {
            "property_id": property_id,
            "domain_id": domain_id,
            "property_name": property_name,
            "property_value": property_value,
            "metadata": property_metadata or {},
            "added_at": time.time(),
            "status": "active"
        }
        
        self.properties[property_id] = prop
        
        # Update domain property count
        self.domains[domain_id]["property_count"] += 1
        
        self._log_inventory("property_added", prop)
        
        return prop
    
    def delegate_domain(
        self,
        domain_id: str,
        entity_id: str,
        dominion_level: str = "full"
    ) -> Dict[str, Any]:
        """
        Delegate dominion of a domain to an entity.
        
        Args:
            domain_id: Domain to delegate
            entity_id: Entity to receive dominion
            dominion_level: Level of control ('full', 'partial', 'readonly')
        """
        if domain_id not in self.domains:
            raise ValueError(f"Domain {domain_id} not found")
        
        domain = self.domains[domain_id]
        delegation_id = f"deleg-{len(self.delegations):04d}"
        
        delegation = {
            "delegation_id": delegation_id,
            "domain_id": domain_id,
            "domain_name": domain["domain_name"],
            "entity_id": entity_id,
            "dominion_level": dominion_level,
            "delegated_at": time.time(),
            "property_count": domain["property_count"],
            "status": "active"
        }
        
        self.delegations[delegation_id] = delegation
        
        # Update domain
        domain["delegated_to"] = entity_id
        domain["status"] = "delegated"
        
        self._log_delegation("domain_delegated", delegation)
        
        return delegation
    
    def get_domain_inventory(self, domain_id: str) -> Dict[str, Any]:
        """Get complete inventory for a domain"""
        if domain_id not in self.domains:
            raise ValueError(f"Domain {domain_id} not found")
        
        domain = self.domains[domain_id]
        
        # Get all properties for this domain
        domain_properties = {
            prop_id: prop for prop_id, prop in self.properties.items()
            if prop["domain_id"] == domain_id
        }
        
        inventory = {
            "domain": domain,
            "properties": domain_properties,
            "property_count": len(domain_properties),
            "is_delegated": domain["delegated_to"] is not None,
            "delegated_to": domain["delegated_to"]
        }
        
        return inventory
    
    def get_entity_domains(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all domains delegated to an entity"""
        entity_delegations = [
            deleg for deleg in self.delegations.values()
            if deleg["entity_id"] == entity_id and deleg["status"] == "active"
        ]
        
        return entity_delegations
    
    def get_all_inventories(self) -> Dict[str, Any]:
        """Get complete inventory report"""
        report = {
            "total_domains": len(self.domains),
            "total_properties": len(self.properties),
            "total_delegations": len([
                d for d in self.delegations.values()
                if d["status"] == "active"
            ]),
            "domains": list(self.domains.values()),
            "delegations": list(self.delegations.values())
        }
        
        return report
    
    def _log_inventory(self, event_type: str, data: Dict):
        """Log inventory events"""
        event = {
            "type": event_type,
            "timestamp": time.time(),
            "creator": self.creator,
            "data": data
        }
        
        try:
            with self.inventory_log.open("a") as f:
                f.write(json.dumps(event) + "\n")
        except IOError:
            pass
    
    def _log_delegation(self, event_type: str, data: Dict):
        """Log delegation events"""
        event = {
            "type": event_type,
            "timestamp": time.time(),
            "creator": self.creator,
            "data": data
        }
        
        try:
            with self.delegation_log.open("a") as f:
                f.write(json.dumps(event) + "\n")
        except IOError:
            pass


def main():
    """Test domain inventory manager"""
    print("=" * 80)
    print("DOMAIN INVENTORY MANAGER TEST")
    print("=" * 80)
    
    manager = DomainInventoryManager("@Evez666")
    
    # Register domains
    print("\n[Test 1] Register domains")
    quantum_dom = manager.register_domain(
        "quantum_sensors",
        "marketplace",
        {"category": "navigation"}
    )
    print(f"✓ Registered: {quantum_dom['domain_name']}")
    
    marketplace_dom = manager.register_domain(
        "craigslist",
        "marketplace",
        {"category": "services"}
    )
    print(f"✓ Registered: {marketplace_dom['domain_name']}")
    
    # Add properties
    print("\n[Test 2] Add properties")
    prop1 = manager.add_property(
        quantum_dom['domain_id'],
        "nav_sensor_001",
        {"price": 100, "type": "navigation"}
    )
    print(f"✓ Added property: {prop1['property_name']}")
    
    prop2 = manager.add_property(
        marketplace_dom['domain_id'],
        "listing_12345",
        {"price": 50, "type": "action"}
    )
    print(f"✓ Added property: {prop2['property_name']}")
    
    # Delegate domains
    print("\n[Test 3] Delegate domains to entities")
    deleg1 = manager.delegate_domain(
        quantum_dom['domain_id'],
        "entity-farm-001",
        "full"
    )
    print(f"✓ Delegated {deleg1['domain_name']} to {deleg1['entity_id']}")
    
    deleg2 = manager.delegate_domain(
        marketplace_dom['domain_id'],
        "entity-farm-002",
        "full"
    )
    print(f"✓ Delegated {deleg2['domain_name']} to {deleg2['entity_id']}")
    
    # Get inventory report
    print("\n[Test 4] Get inventory report")
    report = manager.get_all_inventories()
    print(f"✓ Total domains: {report['total_domains']}")
    print(f"✓ Total properties: {report['total_properties']}")
    print(f"✓ Total delegations: {report['total_delegations']}")
    
    # Get entity domains
    print("\n[Test 5] Get entity domains")
    entity_doms = manager.get_entity_domains("entity-farm-001")
    print(f"✓ Entity entity-farm-001 manages {len(entity_doms)} domain(s)")
    
    print("\n" + "=" * 80)
    print("DOMAIN INVENTORY MANAGER OPERATIONAL")
    print("=" * 80)


if __name__ == "__main__":
    main()
