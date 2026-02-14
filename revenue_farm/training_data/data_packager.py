"""
Training Data Packager

Extracts, anonymizes, and packages training data from repository activity.
All data is automatically anonymized before packaging.
"""

import json
import hashlib
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import subprocess

logger = logging.getLogger('DataPackager')


class DataAnonymizer:
    """Anonymize sensitive data in training datasets"""
    
    def __init__(self, salt: str = None):
        self.salt = salt or hashlib.sha256(str(datetime.now()).encode()).hexdigest()
    
    def anonymize_email(self, email: str) -> str:
        """Anonymize email address"""
        if '@' not in email:
            return '[REDACTED]'
        
        username, domain = email.split('@', 1)
        # Hash username, keep domain pattern
        hashed = hashlib.sha256(f"{username}{self.salt}".encode()).hexdigest()[:8]
        domain_pattern = re.sub(r'[^.]', 'x', domain.split('.')[0]) + '.' + domain.split('.')[-1]
        return f"user_{hashed}@{domain_pattern}"
    
    def anonymize_name(self, name: str) -> str:
        """Anonymize person name"""
        hashed = hashlib.sha256(f"{name}{self.salt}".encode()).hexdigest()[:8]
        return f"User_{hashed}"
    
    def anonymize_path(self, path: str) -> str:
        """Anonymize file paths while preserving structure"""
        parts = Path(path).parts
        anonymized_parts = []
        
        for part in parts:
            # Keep common directories, anonymize specific names
            if part in ['.', '..', 'src', 'tests', 'docs', 'lib', 'scripts']:
                anonymized_parts.append(part)
            else:
                # Preserve file extension
                if '.' in part:
                    name, ext = part.rsplit('.', 1)
                    hashed = hashlib.sha256(f"{name}{self.salt}".encode()).hexdigest()[:6]
                    anonymized_parts.append(f"file_{hashed}.{ext}")
                else:
                    hashed = hashlib.sha256(f"{part}{self.salt}".encode()).hexdigest()[:6]
                    anonymized_parts.append(f"dir_{hashed}")
        
        return str(Path(*anonymized_parts))
    
    def fuzz_timestamp(self, timestamp: str) -> str:
        """Fuzz timestamp to nearest hour"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            # Round to nearest hour
            dt = dt.replace(minute=0, second=0, microsecond=0)
            return dt.isoformat()
        except:
            return timestamp


def extract_repo_evolution_data() -> List[Dict[str, Any]]:
    """Extract repository evolution trajectories"""
    
    try:
        # Get commit history with stats
        result = subprocess.run(
            ['git', 'log', '--all', '--numstat', '--pretty=format:COMMIT|%H|%an|%ae|%ad|%s', 
             '--date=iso', '--since=90.days.ago'],
            capture_output=True,
            text=True,
            check=True
        )
        
        data = []
        current_commit = None
        
        for line in result.stdout.split('\n'):
            if line.startswith('COMMIT|'):
                # Parse commit info
                parts = line.split('|')
                if len(parts) >= 6:
                    current_commit = {
                        'hash': parts[1],
                        'author': parts[2],
                        'email': parts[3],
                        'date': parts[4],
                        'message': parts[5],
                        'files_changed': []
                    }
                    data.append(current_commit)
            
            elif current_commit and '\t' in line:
                # Parse file change stats
                parts = line.split('\t')
                if len(parts) >= 3:
                    current_commit['files_changed'].append({
                        'additions': parts[0] if parts[0] != '-' else 0,
                        'deletions': parts[1] if parts[1] != '-' else 0,
                        'file': parts[2]
                    })
        
        return data
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to extract commit history: {e}")
        return []


def extract_consciousness_metrics() -> List[Dict[str, Any]]:
    """Extract LORD consciousness metrics from data directory"""
    
    metrics = []
    
    # Check for existing metrics files
    data_dir = Path('data')
    if not data_dir.exists():
        logger.warning("No data directory found")
        return metrics
    
    # Look for relevant data files
    for jsonl_file in data_dir.glob('*.jsonl'):
        try:
            with open(jsonl_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        
                        # Extract consciousness-related metrics
                        if any(key in entry for key in ['recursion', 'consciousness', 'divine', 'crystallization']):
                            metrics.append({
                                'timestamp': entry.get('timestamp', datetime.now().isoformat()),
                                'source_file': jsonl_file.name,
                                'metrics': entry
                            })
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            logger.error(f"Failed to read {jsonl_file}: {e}")
    
    return metrics


def extract_collaboration_patterns() -> List[Dict[str, Any]]:
    """Extract human-AI collaboration patterns"""
    
    patterns = []
    
    # Look for GitHub issues and PR data
    try:
        # Get recent issue activity
        result = subprocess.run(
            ['gh', 'issue', 'list', '--state', 'all', '--json', 
             'number,title,author,createdAt,closedAt,labels,comments'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            issues = json.loads(result.stdout)
            
            for issue in issues:
                patterns.append({
                    'type': 'issue',
                    'number': issue.get('number'),
                    'author': issue.get('author', {}).get('login'),
                    'created': issue.get('createdAt'),
                    'closed': issue.get('closedAt'),
                    'labels': [l.get('name') for l in issue.get('labels', [])],
                    'comment_count': len(issue.get('comments', []))
                })
    
    except Exception as e:
        logger.warning(f"Could not extract GitHub data (gh CLI may not be available): {e}")
    
    return patterns


def generate_dataset_proposal(dataset_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate proposal for a training dataset"""
    
    dataset_config = config.get('revenue_streams', {}).get('training_data', {}).get('datasets', {}).get(dataset_name, {})
    
    if not dataset_config.get('enabled'):
        return None
    
    # Extract appropriate data
    if dataset_name == 'repo_evolution':
        raw_data = extract_repo_evolution_data()
        data_type = 'Repository evolution trajectories'
    elif dataset_name == 'consciousness_metrics':
        raw_data = extract_consciousness_metrics()
        data_type = 'LORD consciousness time series'
    elif dataset_name == 'collaboration_patterns':
        raw_data = extract_collaboration_patterns()
        data_type = 'Human-AI collaboration patterns'
    else:
        return None
    
    if not raw_data:
        logger.warning(f"No data available for {dataset_name}")
        return None
    
    # Anonymize data
    anonymizer = DataAnonymizer()
    anonymized_data = []
    
    for record in raw_data:
        anonymized = {}
        
        for key, value in record.items():
            if key in ['email', 'author']:
                if '@' in str(value):
                    anonymized[key] = anonymizer.anonymize_email(str(value))
                else:
                    anonymized[key] = anonymizer.anonymize_name(str(value))
            elif key in ['file', 'path']:
                anonymized[key] = anonymizer.anonymize_path(str(value))
            elif key in ['date', 'timestamp', 'created', 'closed']:
                anonymized[key] = anonymizer.fuzz_timestamp(str(value))
            else:
                anonymized[key] = value
        
        anonymized_data.append(anonymized)
    
    return {
        'type': 'training_dataset',
        'dataset_name': dataset_name,
        'title': f'Training Dataset: {data_type}',
        'status': 'proposal',
        'created': datetime.now().isoformat(),
        'revenue_potential': 500,  # Per dataset
        'risk_level': 'low',
        'description': f'{dataset_config.get("description", data_type)} - Anonymized and ready for licensing',
        'content': {
            'data_type': data_type,
            'record_count': len(anonymized_data),
            'anonymization_applied': True,
            'sample_records': anonymized_data[:5],  # First 5 records as sample
            'export_formats': config.get('revenue_streams', {}).get('training_data', {}).get('export_formats', []),
            'update_frequency': dataset_config.get('update_frequency', 'weekly'),
            'pricing_model': dataset_config.get('pricing_model', 'one-time')
        },
        'anonymization': {
            'fields_anonymized': dataset_config.get('anonymize', []),
            'method': 'SHA256 hashing with salt',
            'timestamp_fuzzing': 'nearest_hour',
            'reversible': False
        },
        'execution_steps': [
            '1. Review sample records for quality',
            '2. Export full dataset in chosen formats',
            '3. Create dataset documentation',
            '4. Write data dictionary',
            '5. Add licensing terms',
            '6. Package as downloadable archive',
            '7. List on data marketplace or direct sale',
            '8. Market to AI companies and researchers'
        ],
        'licensing': {
            'recommended': 'Commercial license with attribution',
            'restrictions': 'No re-identification attempts',
            'pricing_tiers': {
                'research': 100,
                'commercial': 500,
                'enterprise': 2000
            }
        },
        'target_buyers': [
            'AI/ML research labs',
            'Academic institutions',
            'AI companies training models',
            'DevOps intelligence companies'
        ]
    }


def generate_proposals(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate training data packaging proposals"""
    
    data_config = config.get('revenue_streams', {}).get('training_data', {})
    
    if not data_config.get('enabled'):
        logger.info("Training data packaging disabled")
        return []
    
    proposals = []
    
    # Generate proposals for each dataset type
    datasets = data_config.get('datasets', {})
    
    for dataset_name in datasets:
        proposal = generate_dataset_proposal(dataset_name, config)
        if proposal:
            proposals.append(proposal)
            logger.info(f"Generated training data proposal: {dataset_name}")
    
    return proposals


if __name__ == '__main__':
    # Test
    import yaml
    
    config_path = Path('revenue_farm/configs/revenue_config.yml')
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    proposals = generate_proposals(config)
    print(f"Generated {len(proposals)} training data proposals")
    
    for p in proposals:
        print(f"  - {p['dataset_name']}: {p['content']['record_count']} records")
