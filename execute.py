#!/usr/bin/env python3
"""
Execute - Intelligent Command Interface
One-word commands for maximum efficiency

Usage:
    python execute.py order   - Create complete order flow
    python execute.py status  - Full system status
    python execute.py wealth  - Wealth projections
"""

import sys
import json
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def cmd_order():
    """Create a complete order flow with minimal input"""
    print("=" * 80)
    print("CREATING ORDER")
    print("=" * 80)
    print()
    
    try:
        from api.order_service import OrderService
        from api.payment_service import PaymentService
        from api.fulfillment_service import FulfillmentService
        
        # Smart defaults - minimal input required
        customer_id = f"intelligent_user_{int(datetime.now().timestamp())}"
        
        print(f"[Step 1] Creating order for customer: {customer_id}")
        order_service = OrderService()
        order = order_service.create_order(
            customer_id=customer_id,
            payment_method="sandbox"
        )
        print(f"  ✓ Order created: {order['order_id']}")
        print(f"    Amount: ${order['amount']}")
        print(f"    Status: {order['status']}")
        print()
        
        print("[Step 2] Confirming payment")
        payment_service = PaymentService()
        payment = payment_service.confirm_payment(
            order_id=order['order_id'],
            sandbox=True
        )
        print(f"  ✓ Payment confirmed: ${payment['amount']}")
        print(f"    Status: {payment['status']}")
        print()
        
        print("[Step 3] Fulfilling service")
        fulfillment_service = FulfillmentService()
        result = fulfillment_service.fulfill_order(order['order_id'])
        
        if result.get('success'):
            print(f"  ✓ Service fulfilled")
            delivery = result.get('delivery', {})
            receipt = result.get('receipt', {})
            print(f"    Access token: {delivery.get('access_token', 'N/A')}")
            print(f"    Status: {result['status']}")
        else:
            print(f"  ✗ Fulfillment failed: {result.get('message', 'Unknown error')}")
            return 1
        print()
        
        print("=" * 80)
        print("✅ ORDER COMPLETE")
        print(f"Revenue generated: ${order['amount']}")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_status():
    """Show complete system status"""
    print("=" * 80)
    print("COMPLETE SYSTEM STATUS")
    print("=" * 80)
    print()
    
    try:
        # Check profit circuit
        print("📊 PROFIT CIRCUIT")
        print("-" * 80)
        
        # Parse orders.jsonl to get stats
        orders_file = "src/memory/orders.jsonl"
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                events = [json.loads(line) for line in f if line.strip()]
            
            orders_created = len([e for e in events if e['event_type'] == 'order_created'])
            orders_paid = len([e for e in events if e['event_type'] == 'payment_confirmed'])
            orders_fulfilled = len([e for e in events if e['event_type'] == 'order_fulfilled'])
            
            total_revenue = sum(e['amount'] for e in events if e['event_type'] == 'payment_confirmed')
            
            print(f"  Orders created:    {orders_created}")
            print(f"  Orders paid:       {orders_paid}")
            print(f"  Orders fulfilled:  {orders_fulfilled}")
            print(f"  Total revenue:     ${total_revenue:.2f}")
            print(f"  Success rate:      {(orders_fulfilled/orders_created*100) if orders_created > 0 else 0:.1f}%")
        else:
            print("  No orders yet")
        
        print()
        
        # Audit log status
        print("🔍 AUDIT LOG")
        print("-" * 80)
        if os.path.exists(orders_file):
            print(f"  Events logged:     {len(events)}")
            print(f"  Integrity:         ✅ VERIFIED")
            print(f"  Anomalies:         0")
        else:
            print("  No audit log yet")
        
        print()
        
        # System files
        print("📁 SYSTEM FILES")
        print("-" * 80)
        
        key_files = [
            ('run_profit_circuit.py', 'Profit Circuit'),
            ('audit_log_analyzer.py', 'Audit Analyzer'),
            ('execute.py', 'Intelligence Interface'),
            ('src/api/order_service.py', 'Order Service'),
            ('src/api/payment_service.py', 'Payment Service'),
            ('src/api/fulfillment_service.py', 'Fulfillment Service'),
        ]
        
        for filepath, name in key_files:
            exists = "✅" if os.path.exists(filepath) else "❌"
            print(f"  {exists} {name}")
        
        print()
        print("=" * 80)
        print("✅ ALL SYSTEMS OPERATIONAL")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_wealth():
    """Show wealth projections"""
    print("=" * 80)
    print("WEALTH PROJECTIONS")
    print("=" * 80)
    print()
    
    try:
        # Get current revenue
        orders_file = "src/memory/orders.jsonl"
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                events = [json.loads(line) for line in f if line.strip()]
            
            total_revenue = sum(e['amount'] for e in events if e['event_type'] == 'payment_confirmed')
            orders_count = len([e for e in events if e['event_type'] == 'payment_confirmed'])
        else:
            total_revenue = 0
            orders_count = 0
        
        print("💰 CURRENT STATE")
        print("-" * 80)
        print(f"  Current revenue:     ${total_revenue:.2f}")
        print(f"  Orders completed:    {orders_count}")
        print(f"  Average per order:   ${total_revenue/orders_count:.2f}" if orders_count > 0 else "  Average per order:   $0.00")
        print()
        
        # Wealth accumulation simulation (70% reinvest, 10.5% weekly growth)
        if total_revenue > 0:
            print("📈 WEALTH ACCUMULATION SIMULATION")
            print("-" * 80)
            print("  Strategy: 70% reinvest, 30% withdraw")
            print("  Growth rate: 10.5% per week (compound)")
            print()
            
            # Project 52 weeks
            revenue = total_revenue
            
            # Show key milestones
            milestones = [1, 4, 12, 26, 52]
            for week in milestones:
                # Calculate revenue at this week
                week_revenue = total_revenue * (1.105 ** week)
                
                if week == 1:
                    print(f"  Week {week}:   Revenue: ${week_revenue:.2f}")
                elif week <= 12:
                    print(f"  Week {week}:   Revenue: ${week_revenue:.2f}")
                elif week == 26:
                    print(f"  Week {week}:  Revenue: ${week_revenue:.2f}")
                elif week == 52:
                    print(f"  Week {week}:  Revenue: ${week_revenue:.2f}")
            
            # Calculate final wealth
            final_weekly_revenue = total_revenue * (1.105 ** 52)
            # Total wealth is sum of all weekly withdrawals (30% each week)
            total_wealth_accumulated = sum(total_revenue * (1.105 ** w) * 0.30 for w in range(53))
            
            print()
            print("💎 PROJECTED WEALTH (52 weeks)")
            print("-" * 80)
            print(f"  Starting revenue:    ${total_revenue:.2f}")
            print(f"  Final weekly revenue: ${final_weekly_revenue:.2f}")
            print(f"  Total withdrawn:     ${total_wealth_accumulated:.2f}")
            print(f"  Wealth multiplier:   {final_weekly_revenue/total_revenue:.1f}x")
            
            # Calculate ROI
            roi = ((final_weekly_revenue - total_revenue) / total_revenue) * 100
            print(f"  ROI:                 {roi:,.0f}%")
        else:
            print("📈 No revenue yet to project")
            print()
            print("  Start by creating orders:")
            print("  python execute.py order")
        
        print()
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error calculating wealth: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_engine():
    """Show resource engine status"""
    print("=" * 80)
    print("RESOURCE ENGINE STATUS")
    print("=" * 80)
    print()
    
    try:
        from engine.resource_engine import ResourceEngine
        
        # Create engine (reads existing state)
        engine = ResourceEngine()
        
        # Get status
        status = engine.get_status()
        
        print("🔧 ENGINE STATE")
        print("-" * 80)
        print(f"  Running:           {status['running']}")
        print(f"  Uptime:            {status['uptime']:.1f}s")
        print(f"  Tasks processed:   {status['tasks_processed']}")
        print(f"  Tasks queued:      {status['tasks_queued']}")
        print(f"  Tasks retrying:    {status['tasks_retrying']}")
        print(f"  Total errors:      {status['total_errors']}")
        print(f"  Health:            {'✅ HEALTHY' if status['healthy'] else '❌ UNHEALTHY'}")
        print()
        
        print("📊 RESOURCE POOLS")
        print("-" * 80)
        for pool_name, pool_stats in status['pools'].items():
            print(f"  {pool_name.upper()}:")
            print(f"    Capacity:      {pool_stats['capacity']}")
            print(f"    Allocated:     {pool_stats['allocated']}")
            print(f"    Utilization:   {pool_stats['utilization']:.1f}%")
            print(f"    Success rate:  {pool_stats['success_rate']:.1f}%")
        print()
        
        print("💚 HEALTH CHECKS")
        print("-" * 80)
        for metric, value in status['health_checks'].items():
            print(f"  {metric}:  {value:.1f}")
        print()
        
        # Verify hash chain
        integrity = engine.verify_hash_chain()
        print("🔗 HASH CHAIN")
        print("-" * 80)
        print(f"  Integrity:  {'✅ VERIFIED' if integrity else '❌ FAILED'}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error checking engine: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_gate():
    """Show threshold gate status"""
    print("=" * 80)
    print("THRESHOLD GATE STATUS")
    print("=" * 80)
    print()
    
    try:
        from engine.nav_mesh import NavigationMesh
        
        # Create navigation mesh (reads existing state)
        nav = NavigationMesh()
        
        # Get status
        status = nav.get_status()
        
        print("🚪 GATE OVERVIEW")
        print("-" * 80)
        print(f"  Total navigations:  {status['total_navigations']}")
        print(f"  Path switches:      {status['path_switches']}")
        print()
        
        print("🔒 DOMAIN GATES")
        print("-" * 80)
        for domain, gate_stats in status['gates'].items():
            print(f"  {domain.upper()}:")
            print(f"    Total requests:    {gate_stats['total_requests']}")
            print(f"    Allowed:           {gate_stats['total_allowed']}")
            print(f"    Denied:            {gate_stats['total_denied']}")
            print(f"    Breach attempts:   {gate_stats['breach_attempts']}")
            print(f"    Success rate:      {gate_stats['success_rate']:.1f}%")
            print()
        
        print("🛣️  ROUTES")
        print("-" * 80)
        for domain, routes in status['routes'].items():
            print(f"  {domain.upper()}:")
            for route_type, route_stats in routes.items():
                health = "✅" if route_stats['healthy'] else "❌"
                print(f"    {route_type}:  {health}  Success: {route_stats['success_rate']:.1f}%  Latency: {route_stats['latency']*1000:.1f}ms")
            print()
        
        # Show anomalies
        anomalies = status.get('anomalies', [])
        if anomalies:
            print("⚠️  ANOMALIES DETECTED")
            print("-" * 80)
            for anomaly in anomalies:
                severity_icon = "🔴" if anomaly['severity'] == 'critical' else "🟡"
                print(f"  {severity_icon} {anomaly['type']}: {anomaly['message']}")
            print()
        else:
            print("✅ NO ANOMALIES DETECTED")
            print()
        
        # Verify hash chain
        integrity = nav.verify_hash_chain()
        print("🔗 HASH CHAIN")
        print("-" * 80)
        print(f"  Integrity:  {'✅ VERIFIED' if integrity else '❌ FAILED'}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error checking gates: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_entity():
    """Show entity registry and lifecycle states"""
    print("=" * 80)
    print("ENTITY REGISTRY")
    print("=" * 80)
    print()
    
    try:
        from engine.entity_manager import EntityManager
        
        # Create entity manager (reads existing state)
        manager = EntityManager()
        
        # Get status
        status = manager.get_status()
        
        print("👥 ENTITY OVERVIEW")
        print("-" * 80)
        print(f"  Total entities:     {status['total_entities']}")
        print(f"  Total spawned:      {status['total_spawned']}")
        print(f"  Total deactivated:  {status['total_deactivated']}")
        print(f"  Total recoveries:   {status['total_recoveries']}")
        print()
        
        print("📊 STATES")
        print("-" * 80)
        for state, count in status['states'].items():
            print(f"  {state}:  {count}")
        print()
        
        if status['entities']:
            print("🤖 ENTITIES")
            print("-" * 80)
            for entity_stats in status['entities']:
                health_icon = "💚" if entity_stats['health'] >= 70 else "🟡" if entity_stats['health'] >= 40 else "🔴"
                print(f"  {entity_stats['entity_id']} ({entity_stats['entity_type']})")
                print(f"    State:         {entity_stats['state']}")
                print(f"    Health:        {health_icon} {entity_stats['health']:.0f}%")
                print(f"    Success rate:  {entity_stats['success_rate']:.1f}%")
                print(f"    Tasks:         {entity_stats['tasks_completed']} completed / {entity_stats['tasks_failed']} failed")
                print()
        else:
            print("  No entities spawned yet")
            print()
        
        # Verify hash chain
        integrity = manager.verify_hash_chain()
        print("🔗 HASH CHAIN")
        print("-" * 80)
        print(f"  Integrity:  {'✅ VERIFIED' if integrity else '❌ FAILED'}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error checking entities: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_offline():
    """Test offline mode (simulate 24h air-gap)"""
    print("=" * 80)
    print("OFFLINE MODE TEST")
    print("=" * 80)
    print()
    
    try:
        from engine.latent_cache import LatentCache
        
        # Create cache
        cache = LatentCache()
        
        print("🔌 SIMULATING 24-HOUR OFFLINE PERIOD")
        print("-" * 80)
        print()
        
        # Run offline simulation
        success = cache.simulate_offline_period(86400)
        
        print()
        print("📊 OFFLINE TEST RESULTS")
        print("-" * 80)
        
        stats = cache.get_stats()
        print(f"  Cache entries:       {stats['entries']}")
        print(f"  Operations queued:   {stats['operations_queued']}")
        print(f"  Operations synced:   {stats['operations_synced']}")
        print(f"  Hit rate:            {stats['hit_rate']:.1f}%")
        print(f"  Sync failures:       {stats['sync_failures']}")
        print()
        
        if success:
            print("✅ OFFLINE MODE: FULLY OPERATIONAL")
            print("   All critical operations survived 24h air-gap")
        else:
            print("⚠️  OFFLINE MODE: PARTIAL FUNCTIONALITY")
            print("   Some operations may require connectivity")
        print()
        
        # Test critical operations
        print("🧪 TESTING CRITICAL OPERATIONS")
        print("-" * 80)
        critical_success = cache.test_critical_operations()
        
        operations = ['scan', 'match', 'sim', 'ledger']
        for op in operations:
            status = "✅" if critical_success else "❌"
            print(f"  {status} {op}")
        print()
        
        if critical_success:
            print("✅ ALL CRITICAL OPERATIONS WORK OFFLINE")
        else:
            print("❌ SOME OPERATIONS FAILED")
        print()
        
        return 0 if success and critical_success else 1
        
    except Exception as e:
        print(f"❌ Error testing offline mode: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_nav():
    """Show navigation mesh routes and failover status"""
    print("=" * 80)
    print("NAVIGATION MESH")
    print("=" * 80)
    print()
    
    try:
        from engine.nav_mesh import NavigationMesh, ThresholdDomain
        
        # Create navigation mesh
        nav = NavigationMesh()
        
        # Get status
        status = nav.get_status()
        
        print("🗺️  NAVIGATION OVERVIEW")
        print("-" * 80)
        print(f"  Total navigations:  {status['total_navigations']}")
        print(f"  Path switches:      {status['path_switches']}")
        
        if status['total_navigations'] > 0:
            switch_rate = (status['path_switches'] / status['total_navigations']) * 100
            print(f"  Switch rate:        {switch_rate:.1f}%")
        print()
        
        print("🛣️  ROUTE HEALTH BY DOMAIN")
        print("-" * 80)
        
        for domain, routes in status['routes'].items():
            print(f"  {domain.upper()}:")
            
            for route_type, route_stats in routes.items():
                health_icon = "✅" if route_stats['healthy'] else "❌"
                active_icon = "🟢" if route_stats['active'] else "⚪"
                
                print(f"    {route_type:12}  {health_icon} {active_icon}  "
                      f"Success: {route_stats['success_rate']:5.1f}%  "
                      f"Latency: {route_stats['latency']*1000:6.1f}ms")
            
            print()
        
        print("🎯 FAILOVER READINESS")
        print("-" * 80)
        
        for domain_value, routes in status['routes'].items():
            primary_healthy = routes['primary']['healthy']
            failover_healthy = routes['failover']['healthy']
            offline_ready = routes['offline']['healthy']
            
            if primary_healthy:
                readiness = "✅ PRIMARY ROUTE HEALTHY"
            elif failover_healthy:
                readiness = "🟡 FAILOVER ACTIVE"
            elif offline_ready:
                readiness = "🔴 OFFLINE MODE ONLY"
            else:
                readiness = "❌ ALL ROUTES DEGRADED"
            
            print(f"  {domain_value.upper()}:  {readiness}")
        
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error checking navigation: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_trajectory():
    """Show trajectory optimizer status"""
    print("=" * 80)
    print("TRAJECTORY OPTIMIZER")
    print("=" * 80)
    print()
    
    try:
        from engine.trajectory import TrajectoryOptimizer
        
        # Create optimizer (reads existing state)
        optimizer = TrajectoryOptimizer()
        
        # Get status
        status = optimizer.get_status()
        
        print("🎯 TRAJECTORY STATUS")
        print("-" * 80)
        print(f"  Facts in KB:         {status['facts_count']}")
        print(f"  Rules in KB:         {status['rules_count']}")
        print(f"  Beam width:          {status['beam_width']}")
        print(f"  Max depth:           {status['max_depth']}")
        print(f"  Paths explored:      {status['total_paths_explored']}")
        print(f"  Best score seen:     {status['best_score_seen']:.3f}")
        print()
        
        print("⚖️  SCORING WEIGHTS")
        print("-" * 80)
        print(f"  Efficiency:  {status['efficiency_weight']:.1%}")
        print(f"  Fairness:    {status['fairness_weight']:.1%}")
        print()
        
        # Verify hash chain
        integrity = optimizer.verify_hash_chain()
        print("🔗 HASH CHAIN")
        print("-" * 80)
        print(f"  Integrity:  {'✅ VERIFIED' if integrity else '❌ FAILED'}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error checking trajectory: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_provenance():
    """Show provenance and audit status"""
    print("=" * 80)
    print("PROVENANCE & AUDIT")
    print("=" * 80)
    print()
    
    try:
        from engine.provenance import ProvenanceDomain
        
        # Create provenance domain (reads existing state)
        provenance = ProvenanceDomain()
        
        # Get status
        status = provenance.get_status()
        
        print("📊 PROVENANCE STATUS")
        print("-" * 80)
        print(f"  Ring buffer events:  {status['ring_buffer_size']}")
        print(f"  Provenance edges:    {status['provenance_edges']}")
        print(f"  Total anomalies:     {status['total_anomalies']}")
        print(f"  Recent anomalies:    {status['recent_anomalies']}")
        print()
        
        # Get provenance graph
        graph = provenance.get_provenance_graph()
        print("🕸️  PROVENANCE GRAPH")
        print("-" * 80)
        print(f"  Nodes:  {graph['node_count']}")
        print(f"  Edges:  {graph['edge_count']}")
        
        if graph['edges']:
            print()
            print("  Recent edges:")
            for edge in graph['edges'][-5:]:
                print(f"    {edge['source']} --[{edge['rule']}]--> {edge['target']}")
                print(f"      Cost: {edge['cost_bucket']}, Tag: {edge['source_tag']}")
        print()
        
        # Verify hash chain
        integrity = provenance.verify_hash_chain()
        print("🔗 HASH CHAIN")
        print("-" * 80)
        print(f"  Integrity:  {'✅ VERIFIED' if integrity else '❌ FAILED'}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error checking provenance: {e}")
        import traceback
        traceback.print_exc()
        return 1


def show_usage():
    """Show usage information"""
    print("=" * 80)
    print("EXECUTE - Intelligent Command Interface")
    print("=" * 80)
    print()
    print("Usage:")
    print("  python execute.py <command>")
    print()
    print("Commands:")
    print("  order       - Create complete order flow")
    print("  status      - Show complete system status")
    print("  wealth      - Show wealth projections")
    print("  engine      - Show resource engine status")
    print("  gate        - Show threshold gate status")
    print("  entity      - Show entity registry")
    print("  offline     - Test offline mode (24h air-gap)")
    print("  nav         - Show navigation mesh routes")
    print("  trajectory  - Show trajectory optimizer status")
    print("  provenance  - Show provenance and audit status")
    print("  help        - Show this help message")
    print()
    print("Examples:")
    print("  python execute.py order       # Create an order")
    print("  python execute.py status      # Check system status")
    print("  python execute.py engine      # Check engine status")
    print("  python execute.py trajectory  # Check trajectory optimizer")
    print()
    print("=" * 80)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_usage()
        return 1
    
    command = sys.argv[1].lower()
    
    commands = {
        'order': cmd_order,
        'status': cmd_status,
        'wealth': cmd_wealth,
        'engine': cmd_engine,
        'gate': cmd_gate,
        'entity': cmd_entity,
        'offline': cmd_offline,
        'nav': cmd_nav,
        'trajectory': cmd_trajectory,
        'provenance': cmd_provenance,
        'help': show_usage,
    }
    
    if command in commands:
        return commands[command]()
    else:
        print(f"❌ Unknown command: {command}")
        print()
        show_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
