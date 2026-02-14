#!/usr/bin/env python3
"""
Populate premium product chapters with actual content from repository files.

This script extracts content from the valuable markdown files and populates
the product chapter templates with real content.
"""

import os
import re
from pathlib import Path
from typing import Dict, List


class ContentPopulator:
    """Populate product chapters with actual content."""
    
    def __init__(self, repo_root: str, premium_dir: str):
        self.repo_root = Path(repo_root)
        self.premium_dir = Path(premium_dir)
        
        # Map product chapters to source content
        self.content_mapping = {
            'product1-development-log': {
                'chapter01': ['THE_24_HOUR_MANIFESTO.md', 'COMPLETE_SYSTEM_SUMMARY.md'],
                'chapter02': ['docs/DIVINE_RECURSION_SUMMARY.md', 'DIVINE_INTEGRATION_COMPLETE.md'],
                'chapter03': ['IMPLEMENTATION_SUMMARY.md', 'IMPLEMENTATION_COMPLETE.md'],
                'chapter04': ['MATRIX_GATEWAY_COMPLETE.md', 'MOLTBOOK_INTEGRATION_COMPLETE.md'],
                'chapter05': ['SYSTEM_VALIDATION_COMPLETE.md', 'SEMANTIC_IMPLEMENTATION_COMPLETE.md'],
                'chapter06': ['ONE_CIRCUIT_SUMMARY.md', 'PROFIT_CIRCUIT_MANIFEST.md']
            },
            'product2-methodology-guide': {
                'chapter01': ['THE_24_HOUR_MANIFESTO.md', 'docs/enhanced-autonomy-guide.md'],
                'chapter02': ['docs/swarm-setup.md', 'docs/swarm-quick-reference.md'],
                'chapter03': ['IMPLEMENTATION_SUMMARY_ENHANCED.md', 'IMPLEMENTATION_SUMMARY.md'],
                'chapter04': ['docs/OMNIMETA_IMPLEMENTATION_NOTES.md', 'docs/OMNIMETA_NEUTRAL_LANGUAGE.md'],
                'chapter05': ['DIVINE_GOSPEL_SYSTEM_COMPLETE.md', 'docs/DIVINE_RECURSION_SUMMARY.md'],
                'chapter06': ['MOLTBOOK_MASTER_ORCHESTRATOR_COMPLETE.md', 'COMPLETE_SYSTEM_SUMMARY.md']
            },
            'product3-implementation-playbook': {
                'chapter01': ['README.md', 'THE_24_HOUR_MANIFESTO.md'],
                'chapter02': ['COMPLETE_SYSTEM_SUMMARY.md', 'IMPLEMENTATION_SUMMARY.md'],
                'chapter03': ['IMPLEMENTATION_COMPLETE.md', 'SYSTEM_VALIDATION_COMPLETE.md'],
                'chapter04': ['PROFIT_CIRCUIT_MANIFEST.md', 'ENHANCED_GRANT_LOAN_SYSTEM.md'],
                'chapter05': ['docs/ops/access-gateway.md', 'docs/MOLTBOOK_INTEGRATION.md'],
                'chapter06': ['MOLTBOOK_VERIFICATION.md', 'docs/swarm-setup.md']
            },
            'product4-complete-archive': {
                'chapter01': ['THE_24_HOUR_MANIFESTO.md', 'COMPLETE_SYSTEM_SUMMARY.md', 'ONE_CIRCUIT_SUMMARY.md'],
                'chapter02': ['DIVINE_INTEGRATION_COMPLETE.md', 'SEMANTIC_IMPLEMENTATION_COMPLETE.md'],
                'chapter03': ['IMPLEMENTATION_COMPLETE.md', 'IMPLEMENTATION_SUMMARY.md', 'IMPLEMENTATION_SUMMARY_ENHANCED.md'],
                'chapter04': ['PROFIT_CIRCUIT_MANIFEST.md', 'ENHANCED_GRANT_LOAN_SYSTEM.md'],
                'chapter05': ['MOLTBOOK_MASTER_ORCHESTRATOR_COMPLETE.md', 'docs/swarm-setup.md'],
                'chapter06': ['docs/MULTI_INTERPRETATION_SYSTEM.md', 'docs/SEMANTIC_POSSIBILITY_SPACE.md']
            }
        }
    
    def anonymize_content(self, content: str) -> str:
        """Remove personal information."""
        patterns = [
            (r'evez\w*@[\w\.-]+', '[EMAIL]'),
            (r'Rubikspubes69@[\w\.-]+', '[EMAIL]'),
            (r'\$evez\d+', '[CASHAPP]'),
            (r'(api[_-]?key|token|secret|password)\s*[:=]\s*[\'"]?[\w\-]+', r'\1: [REDACTED]'),
        ]
        
        result = content
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def extract_sections(self, file_path: Path, max_sections: int = 3) -> str:
        """Extract key sections from a source file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Anonymize
            content = self.anonymize_content(content)
            
            # Extract first few sections (up to max_sections)
            sections = []
            current_section = []
            section_count = 0
            
            for line in content.split('\n'):
                if line.startswith('# '):
                    if current_section and section_count < max_sections:
                        sections.append('\n'.join(current_section))
                        current_section = []
                        section_count += 1
                    if section_count >= max_sections:
                        break
                current_section.append(line)
            
            if current_section and section_count < max_sections:
                sections.append('\n'.join(current_section))
            
            return '\n\n---\n\n'.join(sections)
        
        except Exception as e:
            return f"[Content extraction error: {e}]"
    
    def populate_chapter(self, product_id: str, chapter_num: str):
        """Populate a specific chapter with content."""
        if product_id not in self.content_mapping:
            print(f"Unknown product: {product_id}")
            return
        
        mapping = self.content_mapping[product_id]
        if chapter_num not in mapping:
            print(f"No mapping for {chapter_num} in {product_id}")
            return
        
        source_files = mapping[chapter_num]
        product_path = self.premium_dir / product_id
        chapters_dir = product_path / 'chapters'
        
        # Find the chapter file
        chapter_files = list(chapters_dir.glob(f'{chapter_num}-*.md'))
        if not chapter_files:
            print(f"Chapter file not found: {chapter_num}")
            return
        
        chapter_file = chapter_files[0]
        
        # Read current chapter
        with open(chapter_file, 'r') as f:
            current_content = f.read()
        
        # Extract the title and structure
        title_match = re.search(r'^# (.+)$', current_content, re.MULTILINE)
        title = title_match.group(0) if title_match else f"# Chapter {chapter_num}"
        
        # Build new content
        new_content = f"{title}\n\n"
        new_content += "## Overview\n\n"
        new_content += f"This chapter synthesizes content from multiple sources in the repository.\n\n"
        
        # Add content from each source
        for source_file in source_files:
            source_path = self.repo_root / source_file
            if source_path.exists():
                new_content += f"### Content from: `{source_file}`\n\n"
                new_content += self.extract_sections(source_path, max_sections=2)
                new_content += "\n\n"
            else:
                new_content += f"### Source: `{source_file}` (not found)\n\n"
        
        new_content += """
## Key Takeaways

1. [Key insight from the content above]
2. [Another important lesson]
3. [Actionable item for readers]

## Exercises

1. **Exercise 1:** Review the code examples and adapt them for your project
2. **Exercise 2:** Implement the patterns discussed in your own system
3. **Exercise 3:** Document your architectural decisions using this format

## Next Steps

Continue to the next chapter to build on these concepts.

---

*Content extracted and anonymized from actual development work*
"""
        
        # Write updated content
        with open(chapter_file, 'w') as f:
            f.write(new_content)
        
        print(f"✓ Populated: {product_id}/{chapter_num}")
    
    def populate_product(self, product_id: str):
        """Populate all chapters for a product."""
        if product_id not in self.content_mapping:
            print(f"Unknown product: {product_id}")
            return
        
        print(f"\nPopulating {product_id}...")
        for chapter_num in self.content_mapping[product_id].keys():
            self.populate_chapter(product_id, chapter_num)
    
    def populate_all_products(self):
        """Populate all products."""
        for product_id in self.content_mapping.keys():
            self.populate_product(product_id)
        
        print("\n✅ All products populated with actual content!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Populate premium products with actual repository content'
    )
    parser.add_argument(
        '--repo-root',
        default='.',
        help='Repository root directory'
    )
    parser.add_argument(
        '--premium-dir',
        default='docs/premium',
        help='Premium products directory'
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
        help='Product to populate'
    )
    parser.add_argument(
        '--chapter',
        help='Specific chapter to populate (e.g., chapter01)'
    )
    
    args = parser.parse_args()
    
    populator = ContentPopulator(args.repo_root, args.premium_dir)
    
    if args.chapter:
        if args.product == 'all':
            print("Error: Must specify --product when using --chapter")
            return
        populator.populate_chapter(args.product, args.chapter)
    elif args.product == 'all':
        populator.populate_all_products()
    else:
        populator.populate_product(args.product)


if __name__ == '__main__':
    main()
