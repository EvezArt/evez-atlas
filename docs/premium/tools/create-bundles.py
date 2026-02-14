#!/usr/bin/env python3
"""
Premium Documentation Bundle Generator
Creates downloadable ZIP bundles for Gumroad/Ko-fi distribution
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List


PREMIUM_DIR = Path(__file__).parent.parent
BUNDLES_DIR = PREMIUM_DIR / "bundles"

PRODUCTS = {
    "product1": {
        "id": "lord-guide",
        "name": "Complete LORD Integration Guide",
        "price": 47,
        "includes": [
            "README.md",
            "TABLE_OF_CONTENTS.md",
            "metadata.json",
            "code-examples/audio-visualizer.js",
            "code-examples/webhook-server.js",
            "templates/deploy-lord-docker.sh"
        ]
    },
    "product2": {
        "id": "latency-blueprint",
        "name": "Negative Latency Implementation Blueprint",
        "price": 97,
        "includes": [
            "README.md",
            "TABLE_OF_CONTENTS.md",
            "metadata.json",
            "code-examples/ekf_implementation.py",
            "code-examples/performance_benchmark.py"
        ]
    },
    "product3": {
        "id": "repository-architecture",
        "name": "Self-Modifying Repository Architecture",
        "price": 197,
        "includes": [
            "README.md",
            "TABLE_OF_CONTENTS.md",
            "metadata.json",
            "code-examples/cognitive-engine.py",
            "templates/cognitive-engine-pipeline.yml",
            "templates/docker-compose-full-stack.yml"
        ]
    },
    "product4": {
        "id": "quantum-dev-kit",
        "name": "Quantum Entity Development Kit",
        "price": 497,
        "includes": "all"  # Include everything
    }
}


def create_readme_txt(product_id: str) -> str:
    """Create README.txt for bundle"""
    product = PRODUCTS[product_id]
    
    content = f"""{'=' * 70}
{product['name']}
{'=' * 70}

Thank you for your purchase!

CONTENTS
--------
This bundle contains:
- Complete documentation (Markdown format)
- Working code examples
- Deployment templates
- Configuration files

GETTING STARTED
---------------
1. Extract all files to your project directory
2. Read the README.md for detailed instructions
3. Review TABLE_OF_CONTENTS.md for chapter listings
4. Explore code-examples/ directory for working code
5. Use templates/ for deployment configurations

SUPPORT
-------
Email: support@evezart.dev
Discord: https://discord.gg/evezart
GitHub: https://github.com/EvezArt/Evez666

Updates: You'll receive free updates for 1 year
License: See LICENSE.txt for terms

QUICK LINKS
-----------
Documentation: https://github.com/EvezArt/Evez666/tree/main/docs/premium
Community: https://discord.gg/evezart
More Products: https://gumroad.com/evezart

{'=' * 70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: 1.0.0
{'=' * 70}
"""
    return content


def create_license_txt() -> str:
    """Create LICENSE.txt for bundle"""
    return """MIT License

Copyright (c) 2024 EvezArt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

DOCUMENTATION LICENSE
---------------------
The documentation content is © 2024 EvezArt. All rights reserved.
Personal and commercial use is permitted for purchasers.
Redistribution of documentation is prohibited.
"""


def create_bundle(product_id: str, product_key: str):
    """Create a downloadable bundle for a product"""
    product = PRODUCTS[product_key]
    product_dir = PREMIUM_DIR / f"{product_id}-{product['id']}"
    
    if not product_dir.exists():
        print(f"⚠️  Product directory not found: {product_dir}")
        return
    
    # Create bundle filename
    bundle_name = f"{product['id']}-v1.0.0.zip"
    bundle_path = BUNDLES_DIR / bundle_name
    
    print(f"\n📦 Creating bundle: {bundle_name}")
    
    # Create ZIP file
    with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add README.txt
        readme_content = create_readme_txt(product_key)
        zipf.writestr('README.txt', readme_content)
        
        # Add LICENSE.txt
        license_content = create_license_txt()
        zipf.writestr('LICENSE.txt', license_content)
        
        if product['includes'] == 'all':
            # Include all products for bundle
            for other_key in ['product1', 'product2', 'product3']:
                other_id = PRODUCTS[other_key]['id']
                other_dir = PREMIUM_DIR / f"{other_key}-{other_id}"
                if other_dir.exists():
                    add_product_to_zip(zipf, other_dir, other_id)
        else:
            # Add specific files
            for file_path in product['includes']:
                full_path = product_dir / file_path
                if full_path.exists():
                    arcname = f"{product['id']}/{file_path}"
                    zipf.write(full_path, arcname)
                    print(f"  ✅ Added: {file_path}")
                else:
                    print(f"  ⚠️  Missing: {file_path}")
    
    # Get bundle size
    size_mb = bundle_path.stat().st_size / 1024 / 1024
    
    print(f"  ✨ Bundle created: {bundle_path}")
    print(f"  📊 Size: {size_mb:.2f} MB")


def add_product_to_zip(zipf: zipfile.ZipFile, product_dir: Path, product_id: str):
    """Add all files from a product directory to ZIP"""
    for root, dirs, files in os.walk(product_dir):
        # Skip empty directories
        if root.endswith('chapters') and not files:
            continue
            
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(product_dir)
            arcname = f"{product_id}/{rel_path}"
            zipf.write(file_path, arcname)


def generate_download_manifest():
    """Generate manifest for all bundles"""
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "version": "1.0.0",
        "bundles": []
    }
    
    for product_key, product in PRODUCTS.items():
        bundle_name = f"{product['id']}-v1.0.0.zip"
        bundle_path = BUNDLES_DIR / bundle_name
        
        if bundle_path.exists():
            size = bundle_path.stat().st_size
            manifest["bundles"].append({
                "id": product['id'],
                "name": product['name'],
                "price": product['price'],
                "filename": bundle_name,
                "size_bytes": size,
                "size_mb": round(size / 1024 / 1024, 2),
                "download_url": f"https://gumroad.com/l/{product['id']}"
            })
    
    manifest_file = BUNDLES_DIR / "download-manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Generated download manifest: {manifest_file}")


def main():
    """Main function"""
    print("🚀 Premium Documentation Bundle Generator")
    print("=" * 70)
    
    # Ensure bundles directory exists
    BUNDLES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create bundles for each product
    for product_key in PRODUCTS.keys():
        create_bundle(product_key, product_key)
    
    # Generate download manifest
    generate_download_manifest()
    
    print("\n" + "=" * 70)
    print("✨ Bundle generation complete!")
    print(f"📁 Bundles saved to: {BUNDLES_DIR}")
    
    # List all bundles
    print("\n📦 Available Bundles:")
    for bundle_file in sorted(BUNDLES_DIR.glob("*.zip")):
        size_mb = bundle_file.stat().st_size / 1024 / 1024
        print(f"  - {bundle_file.name} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
