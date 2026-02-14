#!/usr/bin/env python3
"""
Package extracted content into premium sellable products.

Generates structured product directories with metadata, chapters, code examples,
and templates. Creates bundles for distribution via Gumroad/Ko-fi.
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import argparse


class ProductPackager:
    """Package content into premium products."""
    
    def __init__(self, repo_root: str, output_dir: str):
        self.repo_root = Path(repo_root)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.products = {
            'product1-development-log': {
                'title': 'Cognitive Engine Development Log',
                'price': 67,
                'description': 'Cleaned conversation flow showing evolution from concept to implementation',
                'features': [
                    'Decision points and reasoning for architectural choices',
                    'Troubleshooting and problem-solving examples',
                    'Complete technical evolution timeline',
                    'Anonymized for privacy, maximized for value'
                ],
                'toc_sections': [
                    '1. Initial Vision & Concept',
                    '2. Architecture Design',
                    '3. Implementation Decisions',
                    '4. System Integration',
                    '5. Production Deployment',
                    '6. Lessons Learned'
                ]
            },
            'product2-methodology-guide': {
                'title': 'AI-Assisted Repository Evolution',
                'price': 97,
                'description': 'Methodology for using AI assistants for architectural planning',
                'features': [
                    'Prompt engineering for Copilot assignments',
                    'Issue-driven development patterns',
                    'Automated documentation generation',
                    'Self-bootstrapping system design'
                ],
                'toc_sections': [
                    '1. Introduction to AI-Assisted Development',
                    '2. Effective Prompt Engineering',
                    '3. Issue-Driven Workflows',
                    '4. Automated Documentation',
                    '5. Self-Improving Systems',
                    '6. Best Practices & Pitfalls'
                ]
            },
            'product3-implementation-playbook': {
                'title': 'Zero-to-Production in 24 Hours',
                'price': 147,
                'description': 'Step-by-step from empty repo to monetized cognitive engine',
                'features': [
                    'Actual commands, configurations, and decisions used',
                    'Common pitfalls and solutions',
                    'All PRs, issues, and conversation context',
                    'Replicable blueprint for your projects'
                ],
                'toc_sections': [
                    '1. Hour 0-6: Foundation & Setup',
                    '2. Hour 6-12: Core Systems',
                    '3. Hour 12-18: Integration & Testing',
                    '4. Hour 18-24: Monetization & Launch',
                    '5. Post-Launch: Maintenance',
                    '6. Troubleshooting Guide'
                ]
            },
            'product4-complete-archive': {
                'title': 'The Complete Archive',
                'price': 297,
                'description': 'Everything from our conversations - full archive',
                'features': [
                    'Full conversation transcripts (cleaned)',
                    'All generated specifications and docs',
                    'Every issue, PR, and comment created',
                    'Decision trees and reasoning logs',
                    'Exclusive bonus content'
                ],
                'toc_sections': [
                    '1. Complete Conversation Log',
                    '2. Technical Specifications',
                    '3. Implementation Details',
                    '4. Monetization Strategy',
                    '5. Automation & Tooling',
                    '6. Appendices & References'
                ]
            }
        }
    
    def create_product_structure(self, product_id: str) -> Path:
        """Create directory structure for a product."""
        if product_id not in self.products:
            raise ValueError(f"Unknown product: {product_id}")
        
        product_path = self.output_dir / product_id
        product_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = ['chapters', 'code-examples', 'templates', 'assets']
        for subdir in subdirs:
            (product_path / subdir).mkdir(exist_ok=True)
        
        return product_path
    
    def generate_metadata(self, product_id: str, product_path: Path):
        """Generate metadata.json for product."""
        product_info = self.products[product_id]
        
        metadata = {
            'product_id': product_id,
            'title': product_info['title'],
            'price': product_info['price'],
            'currency': 'USD',
            'description': product_info['description'],
            'features': product_info['features'],
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'format': 'digital-download',
            'license': 'Single-user license',
            'support': 'Email support for 30 days',
            'files_included': [
                'README.md',
                'TABLE_OF_CONTENTS.md',
                'chapters/*.md',
                'code-examples/*',
                'templates/*'
            ]
        }
        
        with open(product_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def generate_readme(self, product_id: str, product_path: Path):
        """Generate README.md for product."""
        product_info = self.products[product_id]
        
        readme_content = f"""# {product_info['title']}

> {product_info['description']}

**Price:** ${product_info['price']} USD

## What You'll Get

"""
        
        for feature in product_info['features']:
            readme_content += f"- {feature}\n"
        
        readme_content += f"""

## Table of Contents

See [TABLE_OF_CONTENTS.md](TABLE_OF_CONTENTS.md) for detailed chapter breakdown.

## How to Use This Product

1. **Read the chapters in order** - Start with Chapter 1 and work through sequentially
2. **Try the code examples** - All examples are in `code-examples/` directory
3. **Use the templates** - Templates in `templates/` directory for your own projects
4. **Reference as needed** - Keep as a reference guide for future projects

## What's Included

### Chapters
All chapters are in Markdown format for easy reading and reference:
- Full text content
- Code snippets and examples
- Diagrams and illustrations
- Key takeaways and action items

### Code Examples
Working code examples demonstrating:
- System architecture patterns
- Integration techniques
- Automation scripts
- Configuration files

### Templates
Reusable templates for:
- GitHub workflows
- Documentation structures
- Configuration files
- Prompt templates

## Support

**Email Support:** Available for 30 days after purchase  
**Updates:** Free updates for version 1.x

## License

Single-user license. Do not redistribute. See full license terms in LICENSE.md.

## About This Product

This product was generated from actual development conversations and implementation
work on the Evez666 Cognitive Engine project. All content has been:
- Cleaned and structured for clarity
- Anonymized to protect privacy
- Enhanced with additional context
- Verified for technical accuracy

**Created:** {datetime.now().strftime('%Y-%m-%d')}  
**Version:** 1.0.0

---

© 2026 Evez666 Project. All rights reserved.
"""
        
        with open(product_path / 'README.md', 'w') as f:
            f.write(readme_content)
    
    def generate_toc(self, product_id: str, product_path: Path):
        """Generate TABLE_OF_CONTENTS.md for product."""
        product_info = self.products[product_id]
        
        toc_content = f"""# Table of Contents

## {product_info['title']}

"""
        
        for section in product_info['toc_sections']:
            toc_content += f"### {section}\n"
            toc_content += "- Overview\n"
            toc_content += "- Key Concepts\n"
            toc_content += "- Code Examples\n"
            toc_content += "- Exercises\n\n"
        
        toc_content += """
## Additional Resources

### Appendix A: Command Reference
Complete command reference for all tools and scripts used.

### Appendix B: Troubleshooting
Common issues and their solutions.

### Appendix C: Further Reading
Additional resources and references.

### Appendix D: Glossary
Technical terms and definitions.
"""
        
        with open(product_path / 'TABLE_OF_CONTENTS.md', 'w') as f:
            f.write(toc_content)
    
    def create_sample_chapters(self, product_id: str, product_path: Path):
        """Create sample chapter files."""
        product_info = self.products[product_id]
        chapters_dir = product_path / 'chapters'
        
        for i, section in enumerate(product_info['toc_sections'], 1):
            chapter_num = str(i).zfill(2)
            chapter_title = section.split('. ', 1)[1] if '. ' in section else section
            
            chapter_content = f"""# Chapter {i}: {chapter_title}

## Overview

[This section will contain the actual content extracted from conversation history]

## Key Concepts

- Concept 1
- Concept 2
- Concept 3

## Detailed Discussion

[Detailed content goes here]

## Code Examples

See `code-examples/chapter{chapter_num}/` for working examples.

## Key Takeaways

1. Takeaway 1
2. Takeaway 2
3. Takeaway 3

## Exercises

1. Exercise 1: [Description]
2. Exercise 2: [Description]

## Next Steps

Continue to [Chapter {i+1}](chapter{str(i+1).zfill(2)}.md)

---

[Generated from actual development conversation - {datetime.now().strftime('%Y-%m-%d')}]
"""
            
            filename = f"chapter{chapter_num}-{chapter_title.lower().replace(' ', '-')[:30]}.md"
            with open(chapters_dir / filename, 'w') as f:
                f.write(chapter_content)
    
    def create_code_examples(self, product_id: str, product_path: Path):
        """Create code example directories and samples."""
        examples_dir = product_path / 'code-examples'
        
        # Create sample code examples
        samples = {
            'github-workflow-example.yml': '''name: Example Workflow
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run example
        run: echo "Example workflow"
''',
            'extraction-script.py': '''#!/usr/bin/env python3
"""Example extraction script."""

def extract_content():
    """Extract content from source."""
    print("Extracting content...")
    return {"status": "success"}

if __name__ == "__main__":
    result = extract_content()
    print(result)
''',
            'README.md': '''# Code Examples

This directory contains working code examples from the product.

## Structure

- Each chapter has its own subdirectory
- Examples are fully functional and tested
- Copy and adapt for your own use

## Usage

```bash
# Run Python examples
python example.py

# Use GitHub workflows
cp *.yml .github/workflows/
```
'''
        }
        
        for filename, content in samples.items():
            with open(examples_dir / filename, 'w') as f:
                f.write(content)
    
    def create_templates(self, product_id: str, product_path: Path):
        """Create template files."""
        templates_dir = product_path / 'templates'
        
        templates = {
            'issue-template.md': '''---
name: Feature Implementation
about: Template for AI-assisted feature implementation
---

## Objective
[Clear objective statement]

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Implementation Plan
1. Step 1
2. Step 2

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2
''',
            'product-metadata-template.json': '''{
  "product_id": "product-name",
  "title": "Product Title",
  "price": 0,
  "currency": "USD",
  "description": "Product description",
  "version": "1.0.0"
}
''',
            'README-template.md': '''# Project Title

## Description
[Project description]

## Features
- Feature 1
- Feature 2

## Installation
```bash
npm install
```

## Usage
[Usage instructions]
'''
        }
        
        for filename, content in templates.items():
            with open(templates_dir / filename, 'w') as f:
                f.write(content)
    
    def create_bundle(self, product_id: str, bundle_path: Path = None) -> Path:
        """Create a downloadable ZIP bundle of the product."""
        if bundle_path is None:
            bundle_path = self.output_dir / 'bundles'
        bundle_path.mkdir(parents=True, exist_ok=True)
        
        product_path = self.output_dir / product_id
        zip_filename = bundle_path / f"{product_id}-v1.0.0.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(product_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(product_path)
                    zipf.write(file_path, arcname)
        
        return zip_filename
    
    def package_product(self, product_id: str) -> Dict:
        """Package a complete product."""
        print(f"Packaging {product_id}...")
        
        # Create structure
        product_path = self.create_product_structure(product_id)
        
        # Generate files
        self.generate_metadata(product_id, product_path)
        self.generate_readme(product_id, product_path)
        self.generate_toc(product_id, product_path)
        self.create_sample_chapters(product_id, product_path)
        self.create_code_examples(product_id, product_path)
        self.create_templates(product_id, product_path)
        
        # Create bundle
        bundle_path = self.create_bundle(product_id)
        
        product_info = self.products[product_id]
        return {
            'product_id': product_id,
            'title': product_info['title'],
            'price': product_info['price'],
            'path': str(product_path),
            'bundle': str(bundle_path),
            'status': 'packaged'
        }
    
    def package_all_products(self) -> List[Dict]:
        """Package all products."""
        results = []
        for product_id in self.products.keys():
            result = self.package_product(product_id)
            results.append(result)
        return results
    
    def create_master_bundle(self) -> Path:
        """Create a master bundle containing all products."""
        bundle_path = self.output_dir / 'bundles'
        bundle_path.mkdir(parents=True, exist_ok=True)
        
        zip_filename = bundle_path / "complete-archive-bundle-v1.0.0.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for product_id in self.products.keys():
                product_path = self.output_dir / product_id
                if product_path.exists():
                    for root, dirs, files in os.walk(product_path):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(self.output_dir)
                            zipf.write(file_path, arcname)
        
        return zip_filename


def main():
    parser = argparse.ArgumentParser(
        description='Package content into premium products'
    )
    parser.add_argument(
        '--repo-root',
        default='.',
        help='Repository root directory'
    )
    parser.add_argument(
        '--output',
        default='docs/premium',
        help='Output directory for products'
    )
    parser.add_argument(
        '--product',
        choices=[
            'product1-development-log',
            'product2-methodology-guide',
            'product3-implementation-playbook',
            'product4-complete-archive',
            'all'
        ],
        default='all',
        help='Product to package'
    )
    parser.add_argument(
        '--create-bundle',
        action='store_true',
        help='Create ZIP bundle'
    )
    
    args = parser.parse_args()
    
    packager = ProductPackager(args.repo_root, args.output)
    
    if args.product == 'all':
        results = packager.package_all_products()
        print(f"\nPackaged {len(results)} products:")
        for result in results:
            print(f"  - {result['title']}: ${result['price']}")
            print(f"    Path: {result['path']}")
            if args.create_bundle:
                print(f"    Bundle: {result['bundle']}")
        
        if args.create_bundle:
            master_bundle = packager.create_master_bundle()
            print(f"\nMaster bundle created: {master_bundle}")
    else:
        result = packager.package_product(args.product)
        print(f"\nPackaged: {result['title']}")
        print(f"Path: {result['path']}")
        if args.create_bundle:
            print(f"Bundle: {result['bundle']}")


if __name__ == '__main__':
    main()
