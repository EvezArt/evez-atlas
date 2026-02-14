#!/usr/bin/env python3
"""
Extract valuable technical content from conversation history and repository docs.

Filters for technical, architecture, and implementation content while anonymizing
personal information. Generates structured content for premium products.
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime


class ContentExtractor:
    """Extract and filter technical content from markdown files."""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.content_filters = {
            'technical': [
                r'system', r'architecture', r'implementation', r'code',
                r'function', r'class', r'module', r'api', r'integration',
                r'algorithm', r'data structure', r'optimization'
            ],
            'architecture': [
                r'design', r'pattern', r'structure', r'component',
                r'layer', r'service', r'interface', r'protocol',
                r'framework', r'orchestrat', r'workflow'
            ],
            'implementation': [
                r'build', r'deploy', r'install', r'configure',
                r'setup', r'test', r'run', r'execute', r'command',
                r'script', r'pipeline', r'automation'
            ],
            'monetization': [
                r'revenue', r'price', r'payment', r'sponsor',
                r'product', r'marketplace', r'sale', r'bundle',
                r'tier', r'subscription', r'profit'
            ]
        }
        
        # Personal information patterns to anonymize
        self.anonymize_patterns = [
            (r'evez\w*@[\w\.-]+', '[EMAIL]'),
            (r'Rubikspubes69@[\w\.-]+', '[EMAIL]'),
            (r'\$evez\d+', '[CASHAPP]'),
            (r'evez666', '[USER]'),
            (r'EvezArt', '[OWNER]'),
            (r'Evez666', '[REPO]'),
            (r'(api[_-]?key|token|secret|password)\s*[:=]\s*[\'"]?[\w\-]+', r'\1: [REDACTED]'),
        ]
    
    def scan_repository(self) -> List[Path]:
        """Scan repository for valuable markdown files."""
        valuable_files = []
        
        # High-value files to extract
        priority_patterns = [
            '*MANIFEST*.md',
            '*SUMMARY*.md',
            '*COMPLETE*.md',
            'THE_*.md',
            'PROFIT_*.md',
            'IMPLEMENTATION_*.md',
            'docs/**/*.md',
            'README.md'
        ]
        
        for pattern in priority_patterns:
            for file_path in self.repo_root.glob(pattern):
                if self._is_valuable_file(file_path):
                    valuable_files.append(file_path)
        
        return list(set(valuable_files))  # Remove duplicates
    
    def _is_valuable_file(self, file_path: Path) -> bool:
        """Check if file contains valuable technical content."""
        # Exclude certain directories
        exclude_dirs = {'.git', 'node_modules', '.roo', 'third_party'}
        if any(excl in file_path.parts for excl in exclude_dirs):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                
                # Must contain technical keywords
                keyword_count = sum(
                    1 for keywords in self.content_filters.values()
                    for keyword in keywords
                    if re.search(keyword, content)
                )
                
                return keyword_count >= 5  # Threshold for valuable content
        except:
            return False
    
    def extract_content(self, file_path: Path, filters: List[str] = None) -> Dict:
        """Extract and categorize content from a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply filters if specified
        if filters:
            relevant = False
            for filter_name in filters:
                if filter_name in self.content_filters:
                    for keyword in self.content_filters[filter_name]:
                        if re.search(keyword, content, re.IGNORECASE):
                            relevant = True
                            break
            if not relevant:
                return None
        
        # Extract structured information
        extracted = {
            'source_file': str(file_path.relative_to(self.repo_root)),
            'title': self._extract_title(content),
            'sections': self._extract_sections(content),
            'code_blocks': self._extract_code_blocks(content),
            'keywords': self._extract_keywords(content),
            'word_count': len(content.split()),
            'extracted_at': datetime.now().isoformat()
        }
        
        return extracted
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content."""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else 'Untitled'
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract sections with headers."""
        sections = []
        pattern = r'^(#{1,6})\s+(.+)$'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2)
            sections.append({'level': level, 'title': title})
        
        return sections
    
    def _extract_code_blocks(self, content: str) -> List[Dict]:
        """Extract code blocks with language hints."""
        code_blocks = []
        pattern = r'```(\w*)\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            code_blocks.append({'language': language, 'code': code})
        
        return code_blocks
    
    def _extract_keywords(self, content: str) -> Dict[str, int]:
        """Extract and count relevant keywords by category."""
        keywords = {}
        
        for category, patterns in self.content_filters.items():
            count = sum(
                len(re.findall(pattern, content, re.IGNORECASE))
                for pattern in patterns
            )
            if count > 0:
                keywords[category] = count
        
        return keywords
    
    def anonymize_content(self, content: str) -> str:
        """Remove personal and sensitive information."""
        anonymized = content
        
        for pattern, replacement in self.anonymize_patterns:
            anonymized = re.sub(pattern, replacement, anonymized, flags=re.IGNORECASE)
        
        return anonymized
    
    def generate_product_content(self, product_type: str, output_format: str = 'markdown') -> str:
        """Generate content for a specific product type."""
        files = self.scan_repository()
        
        product_configs = {
            'development-log': {
                'title': 'Cognitive Engine Development Log',
                'filters': ['technical', 'architecture', 'implementation'],
                'priority_files': ['*MANIFEST*.md', '*SUMMARY*.md', '*COMPLETE*.md'],
                'description': 'Complete conversation flow showing evolution from concept to implementation'
            },
            'methodology-guide': {
                'title': 'AI-Assisted Repository Evolution',
                'filters': ['architecture', 'implementation', 'monetization'],
                'priority_files': ['THE_24_HOUR_MANIFESTO.md', 'IMPLEMENTATION_*.md'],
                'description': 'Methodology for using AI assistants for architectural planning'
            },
            'implementation-playbook': {
                'title': 'Zero-to-Production in 24 Hours',
                'filters': ['implementation', 'technical', 'monetization'],
                'priority_files': ['PROFIT_*.md', '*ORCHESTRATOR*.md', 'README.md'],
                'description': 'Step-by-step from empty repo to monetized cognitive engine'
            },
            'complete-archive': {
                'title': 'The Complete Archive',
                'filters': ['technical', 'architecture', 'implementation', 'monetization'],
                'priority_files': ['*.md'],
                'description': 'Everything from our conversations - full archive'
            }
        }
        
        if product_type not in product_configs:
            raise ValueError(f"Unknown product type: {product_type}")
        
        config = product_configs[product_type]
        extracted_content = []
        
        # Extract content from relevant files
        for file_path in files:
            for pattern in config['priority_files']:
                if file_path.match(pattern):
                    content = self.extract_content(file_path, config['filters'])
                    if content:
                        extracted_content.append(content)
                    break
        
        # Generate output
        if output_format == 'markdown':
            return self._format_as_markdown(config, extracted_content)
        elif output_format == 'json':
            return json.dumps({
                'product': product_type,
                'config': config,
                'content': extracted_content
            }, indent=2)
        else:
            raise ValueError(f"Unknown format: {output_format}")
    
    def _format_as_markdown(self, config: Dict, content: List[Dict]) -> str:
        """Format extracted content as markdown."""
        lines = []
        lines.append(f"# {config['title']}\n")
        lines.append(f"> {config['description']}\n")
        lines.append(f"\n**Extracted:** {datetime.now().strftime('%Y-%m-%d')}\n")
        lines.append(f"**Sources:** {len(content)} documents\n")
        lines.append("\n---\n")
        
        for item in content:
            lines.append(f"\n## {item['title']}")
            lines.append(f"\n**Source:** `{item['source_file']}`")
            lines.append(f"\n**Keywords:** {', '.join(item['keywords'].keys())}")
            lines.append(f"\n**Code Examples:** {len(item['code_blocks'])}\n")
            
            if item['sections']:
                lines.append("\n### Sections\n")
                for section in item['sections'][:10]:  # Limit to top 10
                    indent = '  ' * (section['level'] - 1)
                    lines.append(f"{indent}- {section['title']}")
            
            lines.append("\n")
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Extract valuable content from conversation history'
    )
    parser.add_argument(
        '--repo-root',
        default='.',
        help='Repository root directory'
    )
    parser.add_argument(
        '--filter',
        help='Comma-separated filters: technical,architecture,implementation,monetization'
    )
    parser.add_argument(
        '--anonymize',
        action='store_true',
        help='Anonymize personal information'
    )
    parser.add_argument(
        '--format',
        default='markdown',
        choices=['markdown', 'json', 'pdf'],
        help='Output format'
    )
    parser.add_argument(
        '--product',
        choices=['development-log', 'methodology-guide', 'implementation-playbook', 'complete-archive'],
        help='Generate content for specific product'
    )
    parser.add_argument(
        '--output',
        help='Output file path'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Scan repository and list valuable files'
    )
    
    args = parser.parse_args()
    
    extractor = ContentExtractor(args.repo_root)
    
    if args.scan:
        # Scan and list valuable files
        files = extractor.scan_repository()
        print(f"Found {len(files)} valuable files:\n")
        for f in sorted(files):
            print(f"  - {f.relative_to(args.repo_root)}")
        return
    
    if args.product:
        # Generate product content
        filters = args.filter.split(',') if args.filter else None
        content = extractor.generate_product_content(args.product, args.format)
        
        if args.anonymize:
            content = extractor.anonymize_content(content)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(content)
            print(f"Content written to: {args.output}")
        else:
            print(content)
    else:
        print("Please specify --scan or --product")


if __name__ == '__main__':
    main()
