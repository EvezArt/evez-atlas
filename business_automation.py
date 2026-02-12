#!/usr/bin/env python3
"""
Business Automation System - Customer Onboarding & Service Delivery

Automates the entire customer lifecycle from signup to service delivery.
Integrates with consciousness orchestrator to provide services.
"""

import sys
import json
import uuid
import time
import smtplib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.mastra.core import (
    UniversalEventRecord, create_event, DomainSignature,
    IntentToken, PreAction,
    BoundedIdentity, PermissionScope,
    AuditLogger
)
from consciousness_orchestrator import ConsciousnessOrchestrator


class ServiceTier(Enum):
    """Service tier levels"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class CustomerStatus(Enum):
    """Customer lifecycle status"""
    LEAD = "lead"
    TRIAL = "trial"
    ACTIVE = "active"
    CHURNED = "churned"
    SUSPENDED = "suspended"


@dataclass
class Pricing:
    """Pricing configuration"""
    starter_monthly: float = 297.00
    professional_monthly: float = 997.00
    enterprise_monthly: float = 4997.00

    quantum_analysis: float = 497.00
    quantum_integration: float = 2497.00
    quantum_consulting_hourly: float = 397.00

    consciousness_workshop: float = 4997.00
    consciousness_implementation: float = 14997.00
    consciousness_audit: float = 1997.00

    automation_quickstart: float = 2497.00
    automation_full: float = 9997.00
    automation_managed_monthly: float = 1997.00

    certification: float = 1497.00
    masterclass: float = 497.00
    team_training: float = 4997.00

    api_base_monthly: float = 497.00
    white_label_setup: float = 9997.00
    white_label_monthly: float = 997.00
    component_license: float = 2997.00


@dataclass
class Customer:
    """Customer entity"""
    customer_id: str
    name: str
    email: str
    company: str
    tier: ServiceTier
    status: CustomerStatus
    created_at: datetime = field(default_factory=datetime.now)

    # Service configuration
    max_helpers: int = 3
    max_events_per_month: int = 10000
    data_retention_days: int = 30

    # Billing
    monthly_recurring_revenue: float = 0.0
    billing_cycle_start: Optional[datetime] = None
    last_payment_date: Optional[datetime] = None

    # Service instance
    orchestrator_id: Optional[str] = None
    api_key: Optional[str] = None

    # Metrics
    total_events: int = 0
    total_intents: int = 0
    total_hypotheses: int = 0

    # Notes
    notes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class ServiceOrder:
    """Service order/purchase"""
    order_id: str
    customer_id: str
    service_type: str
    service_name: str
    price: float
    status: str  # pending, processing, completed, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    details: Dict[str, Any] = field(default_factory=dict)


class BusinessAutomation:
    """
    Complete business automation system for HandshakeOS services.

    Handles:
    - Customer onboarding
    - Service provisioning
    - Billing and payments
    - Usage tracking
    - Support ticket management
    - Analytics and reporting
    """

    def __init__(self, data_dir: str = "data/business"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        for subdir in ["customers", "orders", "instances", "analytics"]:
            (self.data_dir / subdir).mkdir(exist_ok=True)

        # Pricing
        self.pricing = Pricing()

        # Audit logging
        self.audit_logger = AuditLogger(
            log_path=str(self.data_dir / "business_audit.jsonl")
        )

        # Business identity
        self.business_identity = BoundedIdentity(
            entity_name="handshakeos_business",
            entity_type="business_system",
            permission_scope=PermissionScope(
                tier_level=5,
                bounded_actions=[
                    "create_customer", "provision_service",
                    "process_payment", "access_analytics"
                ]
            )
        )

        # Active customer instances
        self.customer_instances: Dict[str, ConsciousnessOrchestrator] = {}

        print("BusinessAutomation system initialized")

    # ===== CUSTOMER MANAGEMENT =====

    def create_customer(self,
                       name: str,
                       email: str,
                       company: str,
                       tier: ServiceTier = ServiceTier.STARTER) -> Customer:
        """Create a new customer account."""
        customer_id = str(uuid.uuid4())

        # Determine tier configuration
        tier_config = self._get_tier_config(tier)

        customer = Customer(
            customer_id=customer_id,
            name=name,
            email=email,
            company=company,
            tier=tier,
            status=CustomerStatus.TRIAL,
            max_helpers=tier_config["max_helpers"],
            max_events_per_month=tier_config["max_events"],
            data_retention_days=tier_config["retention_days"],
            monthly_recurring_revenue=tier_config["price"],
            api_key=self._generate_api_key()
        )

        # Save customer
        self._save_customer(customer)

        # Log event
        event = create_event(
            event_type="customer_created",
            attributed_to=self.business_identity.entity_name,
            state_before={"customers": "count_before"},
            state_after={"customer_id": customer_id, "tier": tier.value},
            domain_signature=DomainSignature(
                technical=0.6, social=0.8, financial=0.9
            )
        )
        event.save_to_log(str(self.data_dir / "events.jsonl"))

        self.audit_logger.log_action(
            "customer_created",
            self.business_identity.entity_name,
            {
                "customer_id": customer_id,
                "tier": tier.value,
                "email": email
            }
        )

        # Send welcome email
        self._send_welcome_email(customer)

        print(f"✓ Customer created: {customer.name} ({tier.value})")
        return customer

    def _get_tier_config(self, tier: ServiceTier) -> Dict[str, Any]:
        """Get configuration for a service tier."""
        configs = {
            ServiceTier.STARTER: {
                "max_helpers": 3,
                "max_events": 10000,
                "retention_days": 30,
                "price": self.pricing.starter_monthly
            },
            ServiceTier.PROFESSIONAL: {
                "max_helpers": 10,
                "max_events": 100000,
                "retention_days": 90,
                "price": self.pricing.professional_monthly
            },
            ServiceTier.ENTERPRISE: {
                "max_helpers": 999,
                "max_events": 9999999,
                "retention_days": 365,
                "price": self.pricing.enterprise_monthly
            }
        }
        return configs.get(tier, configs[ServiceTier.STARTER])

    def _generate_api_key(self) -> str:
        """Generate a unique API key."""
        return f"hsos_{uuid.uuid4().hex}"

    # ===== SERVICE PROVISIONING =====

    def provision_consciousness_service(self, customer_id: str) -> str:
        """Provision a consciousness orchestrator instance for a customer."""
        customer = self._load_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Create dedicated data directory for customer
        customer_data_dir = self.data_dir / "instances" / customer_id
        customer_data_dir.mkdir(exist_ok=True)

        # Create consciousness orchestrator instance
        orchestrator = ConsciousnessOrchestrator(
            data_dir=str(customer_data_dir),
            max_helpers=customer.max_helpers,
            consciousness_loop_interval=10.0
        )

        # Start the instance
        orchestrator.ignite()

        # Store instance ID
        customer.orchestrator_id = orchestrator.system_identity.entity_name
        customer.status = CustomerStatus.ACTIVE
        customer.billing_cycle_start = datetime.now()
        self._save_customer(customer)

        # Store active instance
        self.customer_instances[customer_id] = orchestrator

        # Log provisioning
        self.audit_logger.log_action(
            "service_provisioned",
            self.business_identity.entity_name,
            {
                "customer_id": customer_id,
                "orchestrator_id": customer.orchestrator_id,
                "tier": customer.tier.value
            }
        )

        # Send setup complete email
        self._send_service_ready_email(customer)

        print(f"✓ Service provisioned for {customer.name}")
        return customer.orchestrator_id

    # ===== ORDER PROCESSING =====

    def create_order(self,
                    customer_id: str,
                    service_type: str,
                    service_name: str,
                    price: float,
                    details: Optional[Dict] = None) -> ServiceOrder:
        """Create a new service order."""
        order = ServiceOrder(
            order_id=str(uuid.uuid4()),
            customer_id=customer_id,
            service_type=service_type,
            service_name=service_name,
            price=price,
            status="pending",
            details=details or {}
        )

        # Save order
        self._save_order(order)

        # Log order
        self.audit_logger.log_action(
            "order_created",
            self.business_identity.entity_name,
            {
                "order_id": order.order_id,
                "customer_id": customer_id,
                "service_type": service_type,
                "price": price
            }
        )

        print(f"✓ Order created: {order.order_id} - {service_name} (${price})")
        return order

    def process_order(self, order_id: str) -> bool:
        """Process a service order."""
        order = self._load_order(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.status = "processing"
        self._save_order(order)

        # Execute order based on service type
        success = False

        if order.service_type == "consciousness_workshop":
            success = self._deliver_workshop(order)
        elif order.service_type == "quantum_analysis":
            success = self._deliver_quantum_analysis(order)
        elif order.service_type == "automation_implementation":
            success = self._deliver_automation_implementation(order)
        elif order.service_type == "certification":
            success = self._deliver_certification(order)
        else:
            print(f"Unknown service type: {order.service_type}")
            success = True  # Default to success for unknown types

        if success:
            order.status = "completed"
            order.completed_at = datetime.now()
        else:
            order.status = "failed"

        self._save_order(order)

        # Log completion
        self.audit_logger.log_action(
            "order_processed",
            self.business_identity.entity_name,
            {
                "order_id": order_id,
                "status": order.status,
                "service_type": order.service_type
            }
        )

        return success

    # ===== SERVICE DELIVERY =====

    def _deliver_workshop(self, order: ServiceOrder) -> bool:
        """Deliver consciousness workshop."""
        customer = self._load_customer(order.customer_id)

        # Create workshop materials directory
        workshop_dir = self.data_dir / "workshops" / order.order_id
        workshop_dir.mkdir(parents=True, exist_ok=True)

        # Generate workshop materials (placeholder)
        materials = {
            "agenda": "Day 1: Consciousness Fundamentals\nDay 2: Implementation",
            "slides": "slides_url",
            "exercises": "exercises_url",
            "resources": [
                "CONSCIOUSNESS_SYSTEM_README.md",
                "docs/HANDSHAKEOS_E_ARCHITECTURE.md"
            ]
        }

        with open(workshop_dir / "materials.json", 'w') as f:
            json.dump(materials, f, indent=2)

        # Send workshop details email
        self._send_workshop_email(customer, materials)

        print(f"✓ Workshop delivered for order {order.order_id}")
        return True

    def _deliver_quantum_analysis(self, order: ServiceOrder) -> bool:
        """Deliver quantum analysis service."""
        # Run quantum analysis (placeholder)
        analysis_results = {
            "feature_map": "Generated quantum feature map",
            "kernel_similarities": "Computed similarity matrix",
            "fingerprints": "Security fingerprints generated",
            "recommendations": [
                "Optimize qubit count to 8 for best performance",
                "Use statepreparation feature map for this use case"
            ]
        }

        # Save results
        results_file = self.data_dir / "analytics" / f"{order.order_id}_analysis.json"
        with open(results_file, 'w') as f:
            json.dump(analysis_results, f, indent=2)

        customer = self._load_customer(order.customer_id)
        self._send_analysis_complete_email(customer, str(results_file))

        print(f"✓ Quantum analysis delivered for order {order.order_id}")
        return True

    def _deliver_automation_implementation(self, order: ServiceOrder) -> bool:
        """Deliver automation implementation."""
        # Provision consciousness service if not already done
        customer = self._load_customer(order.customer_id)

        if not customer.orchestrator_id:
            self.provision_consciousness_service(order.customer_id)

        # Create implementation guide
        guide = f"""
# Automation Implementation Complete

Your consciousness orchestrator is now live!

## Access Details:
- API Key: {customer.api_key}
- Orchestrator ID: {customer.orchestrator_id}
- Max Helpers: {customer.max_helpers}

## Quick Start:
1. Review documentation: CONSCIOUSNESS_SYSTEM_README.md
2. Access your dashboard: [URL]
3. Deploy your first helper
4. Monitor consciousness cycles

## Support:
- Email: support@handshakeos.com
- Documentation: docs/
- Community: [Discord/Forum link]
"""

        impl_file = self.data_dir / "implementations" / f"{order.order_id}_guide.md"
        impl_file.parent.mkdir(exist_ok=True)
        impl_file.write_text(guide)

        self._send_implementation_complete_email(customer, guide)

        print(f"✓ Automation implementation delivered for order {order.order_id}")
        return True

    def _deliver_certification(self, order: ServiceOrder) -> bool:
        """Deliver certification program."""
        customer = self._load_customer(order.customer_id)

        # Generate certification enrollment
        enrollment = {
            "program": "HandshakeOS-E Developer Certification",
            "customer": customer.name,
            "start_date": datetime.now().isoformat(),
            "duration_days": 90,
            "access_link": f"https://training.handshakeos.com/cert/{order.order_id}",
            "curriculum": [
                "Module 1: UniversalEventRecord",
                "Module 2: IntentToken",
                "Module 3: ParallelHypotheses",
                "Module 4: TestObject",
                "Module 5: BoundedIdentity",
                "Module 6: AuditLogger",
                "Module 7: ReversibilityManager",
                "Final Project: Build Your Consciousness System"
            ]
        }

        cert_file = self.data_dir / "certifications" / f"{order.order_id}_enrollment.json"
        cert_file.parent.mkdir(exist_ok=True)
        with open(cert_file, 'w') as f:
            json.dump(enrollment, f, indent=2)

        self._send_certification_email(customer, enrollment)

        print(f"✓ Certification enrollment delivered for order {order.order_id}")
        return True

    # ===== ANALYTICS & REPORTING =====

    def generate_revenue_report(self) -> Dict[str, Any]:
        """Generate revenue analytics report."""
        all_customers = self._load_all_customers()
        all_orders = self._load_all_orders()

        # Calculate metrics
        total_mrr = sum(c.monthly_recurring_revenue for c in all_customers if c.status == CustomerStatus.ACTIVE)
        total_arr = total_mrr * 12

        active_customers = len([c for c in all_customers if c.status == CustomerStatus.ACTIVE])
        trial_customers = len([c for c in all_customers if c.status == CustomerStatus.TRIAL])

        completed_orders = [o for o in all_orders if o.status == "completed"]
        total_one_time_revenue = sum(o.price for o in completed_orders)

        # By tier
        tier_breakdown = {}
        for tier in ServiceTier:
            tier_customers = [c for c in all_customers if c.tier == tier and c.status == CustomerStatus.ACTIVE]
            tier_breakdown[tier.value] = {
                "customers": len(tier_customers),
                "mrr": sum(c.monthly_recurring_revenue for c in tier_customers)
            }

        report = {
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "total_customers": len(all_customers),
                "active_customers": active_customers,
                "trial_customers": trial_customers,
                "total_mrr": round(total_mrr, 2),
                "total_arr": round(total_arr, 2),
                "total_one_time_revenue": round(total_one_time_revenue, 2),
                "average_customer_value": round(total_mrr / max(active_customers, 1), 2)
            },
            "tier_breakdown": tier_breakdown,
            "recent_orders": [
                {
                    "order_id": o.order_id,
                    "service": o.service_name,
                    "price": o.price,
                    "status": o.status,
                    "date": o.created_at.isoformat()
                }
                for o in sorted(all_orders, key=lambda x: x.created_at, reverse=True)[:10]
            ]
        }

        # Save report
        report_file = self.data_dir / "analytics" / f"revenue_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        return report

    def get_customer_health_score(self, customer_id: str) -> float:
        """Calculate customer health score (0-100)."""
        customer = self._load_customer(customer_id)
        if not customer:
            return 0.0

        score = 0.0

        # Active status
        if customer.status == CustomerStatus.ACTIVE:
            score += 40

        # Usage (based on events)
        expected_events_per_day = customer.max_events_per_month / 30
        if  customer.total_events > 0:
            days_active = (datetime.now() - customer.created_at).days or 1
            actual_events_per_day = customer.total_events / days_active
            usage_ratio = min(actual_events_per_day / expected_events_per_day, 1.0)
            score += usage_ratio * 30

        # Payment history
        if customer.last_payment_date:
            days_since_payment = (datetime.now() - customer.last_payment_date).days
            if days_since_payment < 35:  # Within billing cycle
                score += 20

        # Engagement
        if len(customer.notes) > 0:
            score += 10

        return min(round(score, 2), 100.0)

    # ===== EMAIL AUTOMATION =====

    def _send_welcome_email(self, customer: Customer):
        """Send welcome email to new customer."""
        subject = f"Welcome to HandshakeOS, {customer.name}!"
        body = f"""
Hi {customer.name},

Welcome to HandshakeOS Consciousness Systems! We're excited to have {customer.company} on board.

Your {customer.tier.value} tier account has been created. Here's what happens next:

1. We'll provision your consciousness orchestrator instance
2. You'll receive access credentials and documentation
3. Our team will reach out to schedule your onboarding call

In the meantime, check out our documentation:
- CONSCIOUSNESS_SYSTEM_README.md
- docs/HANDSHAKEOS_E_ARCHITECTURE.md

Questions? Reply to this email or reach out to support@handshakeos.com

Best regards,
The HandshakeOS Team
"""
        self._send_email(customer.email, subject, body)

    def _send_service_ready_email(self, customer: Customer):
        """Send service ready notification."""
        subject = "Your Consciousness System is Ready!"
        body = f"""
Hi {customer.name},

Great news! Your consciousness orchestrator instance is now live and ready to use.

Access Details:
- API Key: {customer.api_key}
- Orchestrator ID: {customer.orchestrator_id}
- Max Helpers: {customer.max_helpers}
- Dashboard: [URL here]

Quick Start Guide:
1. Review the docs at docs/
2. Try the demo: python consciousness_orchestrator.py
3. Deploy your first automation helper
4. Monitor your consciousness cycles

Let us know if you need any help getting started!

Best regards,
The HandshakeOS Team
"""
        self._send_email(customer.email, subject, body)

    def _send_workshop_email(self, customer: Customer, materials: Dict):
        """Send workshop details."""
        subject = "Your Consciousness Discovery Workshop - Starting Soon!"
        body = f"""
Hi {customer.name},

Your Consciousness Discovery Workshop is confirmed!

Workshop Details:
- Format: 2-day intensive
- Materials: Attached
- Prerequisites: None (we'll cover everything)

Day 1: Consciousness Fundamentals
- Multi-perspective evaluation
- Event recording & attribution
- Intent tracking

Day 2: Implementation
- Hands-on lab: Build your system
- Integration planning
- Strategy session

See you soon!

The HandshakeOS Team
"""
        self._send_email(customer.email, subject, body)

    def _send_analysis_complete_email(self, customer: Customer, results_file: str):
        """Send quantum analysis results."""
        subject = "Your Quantum Analysis Results Are Ready"
        body = f"""
Hi {customer.name},

Your quantum kernel analysis is complete!

Results available at: {results_file}

Key Findings:
- Quantum feature map generated
- Kernel similarities computed
- Performance recommendations included

Our team will follow up to discuss the results and next steps.

Best regards,
The HandshakeOS Team
"""
        self._send_email(customer.email, subject, body)

    def _send_implementation_complete_email(self, customer: Customer, guide: str):
        """Send implementation complete notification."""
        subject = "Automation Implementation Complete!"
        body = f"""
Hi {customer.name},

Your automation implementation is complete and ready to go!

{guide}

Need help? We're here:
- Email: support@handshakeos.com
- Documentation: docs/
- Emergency: [phone]

Let's schedule a training call - reply to this email with your availability.

Best regards,
The HandshakeOS Team
"""
        self._send_email(customer.email, subject, body)

    def _send_certification_email(self, customer: Customer, enrollment: Dict):
        """Send certification enrollment details."""
        subject = "Welcome to HandshakeOS-E Developer Certification!"
        body = f"""
Hi {customer.name},

You're enrolled in the HandshakeOS-E Developer Certification program!

Access your course: {enrollment['access_link']}

Program Details:
- Duration: 90 days
- 8 modules covering all 7 core components
- Final project: Build your own consciousness system
- Certificate upon completion

Start Date: {enrollment['start_date']}

Let's build conscious systems together!

The HandshakeOS Team
"""
        self._send_email(customer.email, subject, body)

    def _send_email(self, to_email: str, subject: str, body: str):
        """Send email (placeholder - integrate with actual email service)."""
        print(f"\n📧 EMAIL TO: {to_email}")
        print(f"   SUBJECT: {subject}")
        print(f"   BODY: {body[:100]}...")
        print()
        # TODO: Integrate with SendGrid, AWS SES, or similar

    # ===== PERSISTENCE =====

    def _save_customer(self, customer: Customer):
        """Save customer to disk."""
        file_path = self.data_dir / "customers" / f"{customer.customer_id}.json"
        data = asdict(customer)
        # Convert enums to their values
        data['tier'] = customer.tier.value
        data['status'] = customer.status.value
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _load_customer(self, customer_id: str) -> Optional[Customer]:
        """Load customer from disk."""
        file_path = self.data_dir / "customers" / f"{customer_id}.json"
        if not file_path.exists():
            return None

        with open(file_path) as f:
            data = json.load(f)
            # Convert strings back to enums and datetime
            data['tier'] = ServiceTier(data['tier'])
            data['status'] = CustomerStatus(data['status'])
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            if data.get('billing_cycle_start'):
                data['billing_cycle_start'] = datetime.fromisoformat(data['billing_cycle_start'])
            if data.get('last_payment_date'):
                data['last_payment_date'] = datetime.fromisoformat(data['last_payment_date'])
            return Customer(**data)

    def _load_all_customers(self) -> List[Customer]:
        """Load all customers."""
        customers = []
        customer_dir = self.data_dir / "customers"
        for file_path in customer_dir.glob("*.json"):
            customer_id = file_path.stem
            customer = self._load_customer(customer_id)
            if customer:
                customers.append(customer)
        return customers

    def _save_order(self, order: ServiceOrder):
        """Save order to disk."""
        file_path = self.data_dir / "orders" / f"{order.order_id}.json"
        with open(file_path, 'w') as f:
            json.dump(asdict(order), f, indent=2, default=str)

    def _load_order(self, order_id: str) -> Optional[ServiceOrder]:
        """Load order from disk."""
        file_path = self.data_dir / "orders" / f"{order_id}.json"
        if not file_path.exists():
            return None

        with open(file_path) as f:
            data = json.load(f)
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            if data.get('completed_at'):
                data['completed_at'] = datetime.fromisoformat(data['completed_at'])
            return ServiceOrder(**data)

    def _load_all_orders(self) -> List[ServiceOrder]:
        """Load all orders."""
        orders = []
        order_dir = self.data_dir / "orders"
        for file_path in order_dir.glob("*.json"):
            order_id = file_path.stem
            order = self._load_order(order_id)
            if order:
                orders.append(order)
        return orders


# ===== DEMO USAGE =====

def demo_business_automation():
    """Demonstrate the business automation system."""
    print("=" * 70)
    print("  HANDSHAKEOS BUSINESS AUTOMATION DEMO")
    print("=" * 70)

    business = BusinessAutomation()

    # Create customers
    print("\n[1] Creating customers...")

    customer1 = business.create_customer(
        name="Alice Johnson",
        email="alice@techcorp.com",
        company="TechCorp",
        tier=ServiceTier.PROFESSIONAL
    )

    customer2 = business.create_customer(
        name="Bob Smith",
        email="bob@startupinc.com",
        company="Startup Inc",
        tier=ServiceTier.STARTER
    )

    # Provision services
    print("\n[2] Provisioning services...")
    business.provision_consciousness_service(customer1.customer_id)

    # Create orders
    print("\n[3] Creating service orders...")

    order1 = business.create_order(
        customer_id=customer1.customer_id,
        service_type="quantum_analysis",
        service_name="Quantum Kernel Analysis",
        price=business.pricing.quantum_analysis
    )

    order2 = business.create_order(
        customer_id=customer2.customer_id,
        service_type="consciousness_workshop",
        service_name="2-Day Consciousness Discovery Workshop",
        price=business.pricing.consciousness_workshop
    )

    # Process orders
    print("\n[4] Processing orders...")
    business.process_order(order1.order_id)
    business.process_order(order2.order_id)

    # Generate analytics
    print("\n[5] Generating revenue report...")
    report = business.generate_revenue_report()

    print("\n📊 REVENUE REPORT")
    print(f"   Total Customers: {report['metrics']['total_customers']}")
    print(f"   Active Customers: {report['metrics']['active_customers']}")
    print(f"   Total MRR: ${report['metrics']['total_mrr']}")
    print(f"   Total ARR: ${report['metrics']['total_arr']}")
    print(f"   One-Time Revenue: ${report['metrics']['total_one_time_revenue']}")

    # Customer health scores
    print("\n[6] Customer Health Scores:")
    for customer in [customer1, customer2]:
        score = business.get_customer_health_score(customer.customer_id)
        print(f"   {customer.name}: {score}/100")

    print("\n" + "=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_business_automation()
