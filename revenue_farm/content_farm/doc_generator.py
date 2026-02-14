"""
Documentation Generator

Generates technical documentation from repository activity.
Automatically creates local documentation that can be packaged for sale.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import subprocess

logger = logging.getLogger('DocGenerator')


def scan_code_structure() -> Dict[str, Any]:
    """Scan repository structure for documentation opportunities"""
    
    structure = {
        'python_modules': [],
        'typescript_modules': [],
        'workflows': [],
        'configs': []
    }
    
    repo_root = Path('.')
    
    # Find Python modules
    for py_file in repo_root.rglob('*.py'):
        if '__pycache__' not in str(py_file) and 'venv' not in str(py_file):
            structure['python_modules'].append(str(py_file))
    
    # Find TypeScript modules
    for ts_file in repo_root.rglob('*.ts'):
        if 'node_modules' not in str(ts_file):
            structure['typescript_modules'].append(str(ts_file))
    
    # Find workflows
    workflow_dir = Path('.github/workflows')
    if workflow_dir.exists():
        structure['workflows'] = [str(f) for f in workflow_dir.glob('*.yml')]
    
    # Find configs
    for config_file in repo_root.rglob('*.yml'):
        if '.github' not in str(config_file) and 'node_modules' not in str(config_file):
            structure['configs'].append(str(config_file))
    
    return structure


def generate_api_reference_proposal(modules: List[str]) -> Dict[str, Any]:
    """Generate proposal for API reference documentation"""
    
    return {
        'type': 'documentation',
        'subtype': 'api_reference',
        'title': 'Complete API Reference Guide',
        'status': 'proposal',
        'created': datetime.now().isoformat(),
        'revenue_potential': 200,
        'risk_level': 'low',
        'description': 'Comprehensive API reference for all modules',
        'content': {
            'sections': [
                {
                    'title': 'Python API',
                    'modules': [m for m in modules if m.endswith('.py')],
                    'format': 'sphinx or pdoc3',
                },
                {
                    'title': 'TypeScript API',
                    'modules': [m for m in modules if m.endswith('.ts')],
                    'format': 'typedoc',
                }
            ],
            'output_formats': ['HTML', 'PDF', 'Markdown'],
            'estimated_pages': len(modules) * 3
        },
        'execution_steps': [
            '1. Install documentation tools (sphinx/typedoc)',
            '2. Configure docstring style guide',
            '3. Generate HTML documentation',
            '4. Convert to PDF for packaging',
            '5. Add examples and tutorials',
            '6. Review for completeness',
            '7. Package for Gumroad/Ko-fi'
        ],
        'tools_needed': [
            'sphinx',
            'typedoc',
            'wkhtmltopdf (for PDF generation)'
        ]
    }


def generate_architecture_guide_proposal(structure: Dict[str, Any]) -> Dict[str, Any]:
    """Generate proposal for architecture documentation"""
    
    return {
        'type': 'documentation',
        'subtype': 'architecture_guide',
        'title': 'System Architecture Deep Dive',
        'status': 'proposal',
        'created': datetime.now().isoformat(),
        'revenue_potential': 300,
        'risk_level': 'low',
        'description': 'Complete architectural overview and design patterns',
        'content': {
            'chapters': [
                'Overview and Design Philosophy',
                'Core Components',
                'Data Flow and Integration',
                'GitHub Actions Workflows',
                'Cognitive Engine Architecture',
                'Deployment and Operations',
                'Monitoring and Observability',
                'Security and Compliance',
                'Scaling Considerations',
                'Future Roadmap'
            ],
            'diagrams': [
                'System overview diagram',
                'Data flow diagram',
                'Component interaction diagram',
                'Deployment architecture',
                'CI/CD pipeline'
            ],
            'estimated_pages': 80
        },
        'execution_steps': [
            '1. Extract architecture from code and docs',
            '2. Create system diagrams (draw.io or mermaid)',
            '3. Document key design decisions',
            '4. Add code examples for each component',
            '5. Include deployment guides',
            '6. Review technical accuracy',
            '7. Format as PDF for sale'
        ],
        'tools_needed': [
            'draw.io or mermaid.js',
            'markdown-pdf',
            'pandoc'
        ]
    }


def generate_tutorial_series_proposal() -> Dict[str, Any]:
    """Generate proposal for tutorial series"""
    
    return {
        'type': 'documentation',
        'subtype': 'tutorial_series',
        'title': 'From Zero to Cognitive System - Tutorial Series',
        'status': 'proposal',
        'created': datetime.now().isoformat(),
        'revenue_potential': 400,
        'risk_level': 'low',
        'description': 'Step-by-step tutorial series for building cognitive systems',
        'content': {
            'tutorials': [
                {
                    'title': 'Tutorial 1: Setup and First Steps',
                    'topics': ['Environment setup', 'Basic concepts', 'Hello World'],
                    'duration': '30 minutes'
                },
                {
                    'title': 'Tutorial 2: LORD Protocol Integration',
                    'topics': ['Installing LORD', 'First metrics', 'Dashboard setup'],
                    'duration': '60 minutes'
                },
                {
                    'title': 'Tutorial 3: GitHub Actions Automation',
                    'topics': ['Workflow basics', 'Event handling', 'Automated monitoring'],
                    'duration': '45 minutes'
                },
                {
                    'title': 'Tutorial 4: EKF Fusion Loops',
                    'topics': ['Predictive systems', 'State estimation', 'Performance tuning'],
                    'duration': '90 minutes'
                },
                {
                    'title': 'Tutorial 5: Self-Modifying Systems',
                    'topics': ['Copilot integration', 'Autonomous PRs', 'Safety controls'],
                    'duration': '120 minutes'
                }
            ],
            'total_duration': '5-6 hours',
            'format': 'Interactive notebooks + video',
            'estimated_pages': 120
        },
        'execution_steps': [
            '1. Create Jupyter notebooks for each tutorial',
            '2. Record video walkthroughs',
            '3. Add exercises and solutions',
            '4. Create sample code repositories',
            '5. Test with beta users',
            '6. Package as course bundle',
            '7. List on Gumroad at premium price'
        ],
        'tools_needed': [
            'Jupyter',
            'Screen recording software',
            'Video editing software'
        ]
    }


def generate_integration_cookbook_proposal() -> Dict[str, Any]:
    """Generate proposal for integration cookbook"""
    
    return {
        'type': 'documentation',
        'subtype': 'integration_cookbook',
        'title': 'Cognitive Systems Integration Cookbook',
        'status': 'proposal',
        'created': datetime.now().isoformat(),
        'revenue_potential': 250,
        'risk_level': 'low',
        'description': 'Ready-to-use recipes for common integrations',
        'content': {
            'recipes': [
                'Integrating with Slack',
                'Discord bot with LORD metrics',
                'Notion automation',
                'Email notifications',
                'Custom dashboards with Grafana',
                'Prometheus metrics export',
                'Datadog integration',
                'PagerDuty alerting',
                'Webhook handlers',
                'API authentication patterns'
            ],
            'format': 'Copy-paste code snippets with explanations',
            'estimated_pages': 60
        },
        'execution_steps': [
            '1. Extract integration patterns from codebase',
            '2. Create standalone examples',
            '3. Add configuration templates',
            '4. Test each recipe',
            '5. Document prerequisites and setup',
            '6. Format as searchable PDF',
            '7. Sell as quick-reference guide'
        ]
    }


def generate_proposals(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate documentation proposals"""
    
    doc_config = config.get('revenue_streams', {}).get('content_farm', {}).get('documentation', {})
    
    if not doc_config.get('enabled'):
        logger.info("Documentation generation disabled")
        return []
    
    # Scan repository structure
    structure = scan_code_structure()
    
    all_modules = structure['python_modules'] + structure['typescript_modules']
    
    proposals = []
    
    # Generate different documentation proposals
    if len(all_modules) > 10:  # Only if significant codebase
        proposals.append(generate_api_reference_proposal(all_modules))
        logger.info("Generated API reference proposal")
    
    if len(structure['workflows']) > 2:  # If using GitHub Actions
        proposals.append(generate_architecture_guide_proposal(structure))
        logger.info("Generated architecture guide proposal")
    
    # Always suggest tutorial series (high value)
    proposals.append(generate_tutorial_series_proposal())
    logger.info("Generated tutorial series proposal")
    
    # Always suggest integration cookbook
    proposals.append(generate_integration_cookbook_proposal())
    logger.info("Generated integration cookbook proposal")
    
    return proposals


if __name__ == '__main__':
    # Test
    import yaml
    
    config_path = Path('revenue_farm/configs/revenue_config.yml')
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    proposals = generate_proposals(config)
    print(f"Generated {len(proposals)} documentation proposals")
    
    for p in proposals:
        print(f"  - {p['title']} (${p['revenue_potential']} potential)")
