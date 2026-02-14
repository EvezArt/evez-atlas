#!/usr/bin/env python3
"""
Autonomous Revenue Farm Orchestrator (Level-1 Safe Implementation)

This orchestrator manages multiple revenue streams while maintaining
strict safety guardrails. All high-risk actions require human approval.

Usage:
    python revenue_farm/orchestrator.py --mode=proposal
    python revenue_farm/orchestrator.py --status
    python revenue_farm/orchestrator.py --report
    python revenue_farm/orchestrator.py --emergency-stop
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('revenue_farm/audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('RevenueOrchestrator')


class SafetyGuard:
    """Enforces safety constraints on all operations"""
    
    def __init__(self, safety_config: Dict[str, Any]):
        self.config = safety_config
        self.violations = []
    
    def check_operation(self, operation: str) -> bool:
        """Check if operation is allowed"""
        
        # Check if operation requires approval
        always_require = self.config.get('human_approval', {}).get('always_require_approval', [])
        if operation in always_require:
            logger.warning(f"Operation '{operation}' requires human approval")
            return False
        
        # Check if operation can be automated
        can_automate = self.config.get('human_approval', {}).get('can_automate', [])
        if operation in can_automate:
            return True
        
        # Default: require approval
        logger.warning(f"Operation '{operation}' not in approved list")
        return False
    
    def check_financial(self, amount: float) -> bool:
        """Check if financial transaction is allowed"""
        
        if self.config.get('financial', {}).get('auto_spend', False) is False:
            logger.error(f"AUTO-SPEND BLOCKED: Attempted to spend ${amount}")
            self.violations.append({
                'type': 'financial',
                'operation': 'auto_spend',
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            })
            return False
        
        return False  # Level-1: Always block
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive data"""
        
        anonymize_fields = self.config.get('data_privacy', {}).get('anonymize_always', [])
        anonymized = data.copy()
        
        for field in anonymize_fields:
            if field in anonymized:
                anonymized[field] = '[REDACTED]'
        
        return anonymized


class RevenueOrchestrator:
    """Main orchestrator for revenue streams"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.revenue_config = self._load_config('revenue_config.yml')
        self.safety_config = self._load_config('safety_config.yml')
        self.safety_guard = SafetyGuard(self.safety_config)
        self.proposals_dir = Path('revenue_farm/proposals')
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Revenue Orchestrator initialized in Level-1 Safe Mode")
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration"""
        config_path = self.config_dir / filename
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def generate_proposals(self) -> List[Dict[str, Any]]:
        """Generate proposals for all enabled revenue streams"""
        
        proposals = []
        streams = self.revenue_config.get('revenue_streams', {})
        
        # Import revenue stream modules with path adjustment
        import sys
        from pathlib import Path
        
        # Add parent directory to path
        repo_root = Path(__file__).parent.parent
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        
        # Generate content farm proposals
        if streams.get('content_farm', {}).get('enabled'):
            logger.info("Generating content farm proposals...")
            try:
                from revenue_farm.content_farm import blog_generator, doc_generator
                
                blog_proposals = blog_generator.generate_proposals(self.revenue_config)
                proposals.extend(blog_proposals)
                
                doc_proposals = doc_generator.generate_proposals(self.revenue_config)
                proposals.extend(doc_proposals)
            except Exception as e:
                logger.warning(f"Content farm error: {e}")
        
        # Generate action marketplace proposals
        if streams.get('action_marketplace', {}).get('enabled'):
            logger.info("Generating action marketplace proposals...")
            try:
                from revenue_farm.action_marketplace import action_packager
                
                action_proposals = action_packager.generate_proposals(self.revenue_config)
                proposals.extend(action_proposals)
            except Exception as e:
                logger.warning(f"Action marketplace error: {e}")
        
        # Generate training data proposals
        if streams.get('training_data', {}).get('enabled'):
            logger.info("Generating training data proposals...")
            try:
                from revenue_farm.training_data import data_packager
                
                data_proposals = data_packager.generate_proposals(self.revenue_config)
                proposals.extend(data_proposals)
            except Exception as e:
                logger.warning(f"Training data error: {e}")
        
        # Generate product wiring proposals
        if streams.get('product_wiring', {}).get('enabled'):
            logger.info("Generating product wiring proposals...")
            try:
                from revenue_farm.product_wiring import product_meta
                
                product_proposals = product_meta.generate_proposals(self.revenue_config)
                proposals.extend(product_proposals)
            except Exception as e:
                logger.warning(f"Product wiring error: {e}")
        
        # Save proposals
        self._save_proposals(proposals)
        
        return proposals
    
    def _save_proposals(self, proposals: List[Dict[str, Any]]):
        """Save proposals to disk for human review"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        proposal_file = self.proposals_dir / f'proposals_{timestamp}.json'
        
        with open(proposal_file, 'w') as f:
            json.dump(proposals, f, indent=2)
        
        logger.info(f"Saved {len(proposals)} proposals to {proposal_file}")
        
        # Generate human-readable summary
        summary_file = self.proposals_dir / f'summary_{timestamp}.md'
        self._generate_summary(proposals, summary_file)
    
    def _generate_summary(self, proposals: List[Dict[str, Any]], output_file: Path):
        """Generate human-readable summary of proposals"""
        
        with open(output_file, 'w') as f:
            f.write("# Revenue Farm Proposals\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(f"Total Proposals: {len(proposals)}\n\n")
            f.write("---\n\n")
            
            for i, proposal in enumerate(proposals, 1):
                f.write(f"## Proposal {i}: {proposal.get('title', 'Untitled')}\n\n")
                f.write(f"**Type**: {proposal.get('type', 'Unknown')}\n\n")
                f.write(f"**Revenue Potential**: ${proposal.get('revenue_potential', 0)}\n\n")
                f.write(f"**Risk Level**: {proposal.get('risk_level', 'Unknown')}\n\n")
                f.write(f"**Description**:\n{proposal.get('description', 'No description')}\n\n")
                
                if 'execution_steps' in proposal:
                    f.write("**Execution Steps**:\n")
                    for step in proposal['execution_steps']:
                        f.write(f"- {step}\n")
                    f.write("\n")
                
                f.write("---\n\n")
        
        logger.info(f"Generated proposal summary: {output_file}")
    
    def show_status(self) -> Dict[str, Any]:
        """Show current status of all revenue streams"""
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'safety_level': self.safety_config.get('safety_level', 1),
            'streams': {},
            'proposals': {
                'total': len(list(self.proposals_dir.glob('proposals_*.json'))),
                'recent': []
            }
        }
        
        streams = self.revenue_config.get('revenue_streams', {})
        
        for stream_name, stream_config in streams.items():
            status['streams'][stream_name] = {
                'enabled': stream_config.get('enabled', False),
                'status': 'operational' if stream_config.get('enabled') else 'disabled'
            }
        
        # Get recent proposals
        recent_proposals = sorted(
            self.proposals_dir.glob('proposals_*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:5]
        
        for proposal_file in recent_proposals:
            status['proposals']['recent'].append({
                'file': proposal_file.name,
                'timestamp': datetime.fromtimestamp(proposal_file.stat().st_mtime).isoformat()
            })
        
        return status
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive revenue report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'period': 'all-time',
            'metrics': {
                'proposals_generated': len(list(self.proposals_dir.glob('proposals_*.json'))),
                'proposals_approved': 0,  # Would be tracked separately
                'revenue_actual': 0,  # Would be tracked separately
                'revenue_potential': 0
            },
            'streams': {}
        }
        
        # Calculate potential revenue from proposals
        for proposal_file in self.proposals_dir.glob('proposals_*.json'):
            with open(proposal_file, 'r') as f:
                proposals = json.load(f)
                for proposal in proposals:
                    report['metrics']['revenue_potential'] += proposal.get('revenue_potential', 0)
        
        return report
    
    def emergency_stop(self):
        """Emergency stop all operations"""
        
        logger.critical("EMERGENCY STOP ACTIVATED")
        
        # Create emergency stop flag
        stop_file = Path('revenue_farm/.emergency_stop')
        stop_file.touch()
        
        logger.info("All automated operations halted")
        logger.info("Remove revenue_farm/.emergency_stop to resume")


def main():
    parser = argparse.ArgumentParser(description='Revenue Farm Orchestrator')
    parser.add_argument('--mode', choices=['proposal', 'status', 'report'], 
                       default='proposal', help='Operation mode')
    parser.add_argument('--emergency-stop', action='store_true',
                       help='Emergency stop all operations')
    
    args = parser.parse_args()
    
    # Check for emergency stop flag
    stop_file = Path('revenue_farm/.emergency_stop')
    if stop_file.exists() and not args.emergency_stop:
        logger.error("EMERGENCY STOP FLAG DETECTED - Operations halted")
        logger.error("Remove revenue_farm/.emergency_stop to resume")
        sys.exit(1)
    
    # Initialize orchestrator
    config_dir = Path('revenue_farm/configs')
    orchestrator = RevenueOrchestrator(config_dir)
    
    # Execute requested operation
    if args.emergency_stop:
        orchestrator.emergency_stop()
    
    elif args.mode == 'proposal':
        logger.info("Generating revenue proposals...")
        proposals = orchestrator.generate_proposals()
        print(f"\n✅ Generated {len(proposals)} proposals")
        print(f"📁 Review at: revenue_farm/proposals/")
        print("\n⚠️  IMPORTANT: All proposals require human approval before execution")
    
    elif args.mode == 'status':
        status = orchestrator.show_status()
        print("\n=== Revenue Farm Status ===\n")
        print(json.dumps(status, indent=2))
    
    elif args.mode == 'report':
        report = orchestrator.generate_report()
        print("\n=== Revenue Report ===\n")
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
