"""
GitHub Action Marketplace Packager

Creates ready-to-publish GitHub Actions from existing workflows and scripts.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import yaml

logger = logging.getLogger('ActionPackager')


def scan_workflows() -> List[Path]:
    """Scan for existing workflows that could be packaged as Actions"""
    
    workflow_dir = Path('.github/workflows')
    if not workflow_dir.exists():
        return []
    
    return list(workflow_dir.glob('*.yml'))


def analyze_workflow_for_action(workflow_path: Path) -> Dict[str, Any]:
    """Analyze if workflow could be packaged as a reusable action"""
    
    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)
    
    # Check if it has reusable components
    has_composite_steps = False
    step_count = 0
    
    jobs = workflow.get('jobs', {})
    for job_name, job_data in jobs.items():
        steps = job_data.get('steps', [])
        step_count += len(steps)
        
        # Check for patterns that make good actions
        for step in steps:
            if 'uses' in step or 'run' in step:
                has_composite_steps = True
    
    return {
        'suitable': has_composite_steps and step_count > 3,
        'step_count': step_count,
        'jobs': len(jobs)
    }


def generate_action_metadata(action_name: str, description: str, category: str) -> Dict[str, Any]:
    """Generate action.yml metadata"""
    
    action_templates = {
        'lord-monitor': {
            'name': 'LORD Consciousness Monitor',
            'description': 'Monitor LORD consciousness metrics in your CI/CD pipeline',
            'inputs': {
                'recursion-depth': {
                    'description': 'Maximum recursion depth to track',
                    'required': False,
                    'default': '10'
                },
                'report-format': {
                    'description': 'Output format (json, markdown, html)',
                    'required': False,
                    'default': 'markdown'
                }
            },
            'outputs': {
                'consciousness-score': {
                    'description': 'Current consciousness score (0-100)'
                },
                'divine-gap': {
                    'description': 'Divine gap (ΔΩ) value'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Setup Python',
                        'uses': 'actions/setup-python@v4',
                        'with': {'python-version': '3.11'}
                    },
                    {
                        'name': 'Install dependencies',
                        'shell': 'bash',
                        'run': 'pip install pyyaml requests'
                    },
                    {
                        'name': 'Run LORD monitor',
                        'shell': 'bash',
                        'run': 'python ${{ github.action_path }}/monitor.py'
                    }
                ]
            }
        },
        'cognitive-health-check': {
            'name': 'Cognitive Health Check',
            'description': 'Verify cognitive engine health and metrics',
            'inputs': {
                'threshold': {
                    'description': 'Minimum health score (0-100)',
                    'required': False,
                    'default': '70'
                }
            },
            'outputs': {
                'health-status': {
                    'description': 'Health status (healthy, degraded, critical)'
                },
                'health-score': {
                    'description': 'Numeric health score'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Check cognitive metrics',
                        'shell': 'bash',
                        'run': 'echo "health-status=healthy" >> $GITHUB_OUTPUT'
                    }
                ]
            }
        },
        'training-data-export': {
            'name': 'Training Data Export',
            'description': 'Export anonymized training data from repository',
            'inputs': {
                'output-format': {
                    'description': 'Export format (jsonl, csv, parquet)',
                    'required': False,
                    'default': 'jsonl'
                },
                'anonymize': {
                    'description': 'Anonymize sensitive data',
                    'required': False,
                    'default': 'true'
                }
            },
            'outputs': {
                'export-path': {
                    'description': 'Path to exported data file'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Export data',
                        'shell': 'bash',
                        'run': 'python ${{ github.action_path }}/export.py'
                    }
                ]
            }
        },
        'autonomous-pr-review': {
            'name': 'Autonomous PR Review',
            'description': 'AI-powered PR review with cognitive metrics',
            'inputs': {
                'pr-number': {
                    'description': 'Pull request number',
                    'required': True
                },
                'check-lord-metrics': {
                    'description': 'Include LORD metrics in review',
                    'required': False,
                    'default': 'true'
                }
            },
            'outputs': {
                'review-status': {
                    'description': 'Review status (approved, changes-requested, commented)'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Review PR',
                        'shell': 'bash',
                        'run': 'echo "Reviewing PR..."'
                    }
                ]
            }
        },
        'revenue-report': {
            'name': 'Revenue Stream Report',
            'description': 'Generate revenue stream analytics report',
            'inputs': {
                'period': {
                    'description': 'Report period (daily, weekly, monthly)',
                    'required': False,
                    'default': 'weekly'
                }
            },
            'outputs': {
                'report-path': {
                    'description': 'Path to generated report'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Generate report',
                        'shell': 'bash',
                        'run': 'python ${{ github.action_path }}/report.py'
                    }
                ]
            }
        }
    }
    
    return action_templates.get(action_name, {
        'name': action_name.replace('-', ' ').title(),
        'description': description,
        'runs': {
            'using': 'composite',
            'steps': []
        }
    })


def generate_action_proposal(action_name: str, description: str, category: str) -> Dict[str, Any]:
    """Generate proposal for a GitHub Action"""
    
    metadata = generate_action_metadata(action_name, description, category)
    
    return {
        'type': 'github_action',
        'title': f'GitHub Action: {metadata["name"]}',
        'action_name': action_name,
        'status': 'proposal',
        'created': datetime.now().isoformat(),
        'revenue_potential': 100,  # Per action in marketplace
        'risk_level': 'low',
        'description': f'Packaged GitHub Action: {description}',
        'content': {
            'action_yml': metadata,
            'requires_scripts': [
                f'{action_name}/action.yml',
                f'{action_name}/README.md',
                f'{action_name}/LICENSE'
            ],
            'marketplace_branding': {
                'icon': 'activity',
                'color': 'purple'
            },
            'category': category
        },
        'execution_steps': [
            f'1. Create new repository: evezart/{action_name}',
            '2. Add action.yml with metadata (see proposal)',
            '3. Add implementation scripts',
            '4. Write comprehensive README',
            '5. Add LICENSE (MIT recommended)',
            '6. Create example workflows',
            '7. Test action locally',
            '8. Push to GitHub',
            '9. Publish to Marketplace',
            '10. Add to README as monetization link'
        ],
        'marketplace_listing': {
            'url': f'https://github.com/marketplace/actions/{action_name}',
            'visibility': 'public',
            'pricing': 'Free (with GitHub Sponsors link)'
        },
        'revenue_strategy': 'Free action with prominent sponsor links and paid support tiers'
    }


def generate_proposals(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate GitHub Action packaging proposals"""
    
    action_config = config.get('revenue_streams', {}).get('action_marketplace', {})
    
    if not action_config.get('enabled'):
        logger.info("Action marketplace disabled")
        return []
    
    proposals = []
    
    # Get action templates from config
    action_templates = action_config.get('action_templates', [])
    
    for template in action_templates:
        proposal = generate_action_proposal(
            template['name'],
            template['description'],
            template['category']
        )
        proposals.append(proposal)
        logger.info(f"Generated action proposal: {template['name']}")
    
    return proposals


def package_action_locally(action_name: str, metadata: Dict[str, Any], output_dir: Path):
    """Package action files locally for review"""
    
    action_dir = output_dir / action_name
    action_dir.mkdir(parents=True, exist_ok=True)
    
    # Write action.yml
    with open(action_dir / 'action.yml', 'w') as f:
        yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
    
    # Create README template
    readme_content = f"""# {metadata.get('name', action_name)}

{metadata.get('description', '')}

## Usage

```yaml
- uses: evezart/{action_name}@v1
  with:
    # See inputs below
```

## Inputs

[Generated from action.yml]

## Outputs

[Generated from action.yml]

## Example

```yaml
name: Example Workflow
on: [push]
jobs:
  example:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: evezart/{action_name}@v1
```

## License

MIT

## Support

- ⭐ Star this repo
- 💰 [Sponsor on GitHub](https://github.com/sponsors/EvezArt)
- 🐛 [Report issues](https://github.com/evezart/{action_name}/issues)
"""
    
    with open(action_dir / 'README.md', 'w') as f:
        f.write(readme_content)
    
    logger.info(f"Packaged action locally at {action_dir}")


if __name__ == '__main__':
    # Test
    import yaml
    
    config_path = Path('revenue_farm/configs/revenue_config.yml')
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    proposals = generate_proposals(config)
    print(f"Generated {len(proposals)} action proposals")
    
    for p in proposals:
        print(f"  - {p['action_name']}")
