#!/bin/bash
set -euo pipefail

echo "════════════════════════════════════════════════════════════"
echo "  EVEZ666 DEVCONTAINER SETUP"
echo "  Installing Canonical Hashing Libraries for Golden Hash Testing"
echo "════════════════════════════════════════════════════════════"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get workspace root
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(pwd)}"
cd "$WORKSPACE_ROOT"

# 1. Install Node.js dependencies (including json-canonicalize)
echo -e "\n${YELLOW}📦 Installing Node.js dependencies...${NC}"
npm install
npm install --save-dev json-canonicalize
echo -e "${GREEN}✅ Node.js dependencies installed (including json-canonicalize)${NC}"

# 2. Install Python dependencies (including rfc8785)
echo -e "\n${YELLOW}🐍 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install rfc8785
echo -e "${GREEN}✅ Python dependencies installed (including rfc8785)${NC}"

# 3. Install Go dependencies (including webpki/jcs)
echo -e "\n${YELLOW}🐹 Installing Go dependencies...${NC}"
if [ ! -f "go.mod" ]; then
    echo "Initializing Go module..."
    go mod init github.com/EvezArt/Evez666 || true
fi
go get github.com/cyberphone/json-canonicalization/go/src/webpki.org/jsoncanonicalizer || true
echo -e "${GREEN}✅ Go dependencies configured (webpki/jcs available)${NC}"

# 4. Setup Rust project for serde_jcs
echo -e "\n${YELLOW}🦀 Setting up Rust environment...${NC}"
if [ ! -f "Cargo.toml" ]; then
    echo "Creating Rust project structure for canonical hashing..."
    mkdir -p rust-canonicalize
    cd rust-canonicalize
    cat > Cargo.toml << 'EOF'
[package]
name = "evez666-canonicalize"
version = "0.1.0"
edition = "2021"

[dependencies]
serde_jcs = "0.1"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
EOF
    mkdir -p src
    cat > src/lib.rs << 'EOF'
use serde::{Deserialize, Serialize};
use serde_jcs;

#[derive(Serialize, Deserialize)]
pub struct TestData {
    pub message: String,
    pub timestamp: u64,
}

pub fn canonicalize_json(json_str: &str) -> Result<String, Box<dyn std::error::Error>> {
    let value: serde_json::Value = serde_json::from_str(json_str)?;
    let canonical = serde_jcs::to_string(&value)?;
    Ok(canonical)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_canonicalization() {
        let json = r#"{"b": 2, "a": 1}"#;
        let result = canonicalize_json(json).unwrap();
        assert_eq!(result, r#"{"a":1,"b":2}"#);
    }
}
EOF
    cargo build
    cd ..
    echo -e "${GREEN}✅ Rust project created with serde_jcs${NC}"
else
    echo -e "${GREEN}✅ Rust environment ready${NC}"
fi

# 5. Setup Java/Maven for WebPKI
echo -e "\n${YELLOW}☕ Setting up Java environment...${NC}"
if [ ! -f "pom.xml" ]; then
    echo "Creating Maven project for canonical hashing..."
    mkdir -p java-canonicalize/src/main/java/org/evez666
    cd java-canonicalize
    cat > pom.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>org.evez666</groupId>
    <artifactId>evez666-canonicalize</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <name>Evez666 Canonical JSON</name>
    <description>JSON Canonical Serialization for Evez666</description>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.webpki.json</groupId>
            <artifactId>webpki.org.json</artifactId>
            <version>1.1.8</version>
        </dependency>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
EOF

    cat > src/main/java/org/evez666/CanonicalJson.java << 'EOF'
package org.evez666;

import org.webpki.json.JSONObjectReader;
import org.webpki.json.JSONParser;

public class CanonicalJson {
    public static String canonicalize(String json) throws Exception {
        JSONObjectReader reader = JSONParser.parse(json);
        return reader.serializeToString(org.webpki.json.JSONOutputFormats.CANONICALIZED);
    }

    public static void main(String[] args) {
        try {
            String json = "{\"b\": 2, \"a\": 1}";
            String canonical = canonicalize(json);
            System.out.println("Canonical: " + canonical);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
EOF
    
    # Try to compile but don't fail if Maven repo is unavailable
    mvn clean compile || echo "⚠️  Maven compile skipped (may require internet)"
    cd ..
    echo -e "${GREEN}✅ Java Maven project created with WebPKI${NC}"
else
    echo -e "${GREEN}✅ Java environment ready${NC}"
fi

# 6. Create golden hash test utilities directory
echo -e "\n${YELLOW}🔐 Setting up golden hash testing utilities...${NC}"
mkdir -p tests/golden-hash
cat > tests/golden-hash/README.md << 'EOF'
# Golden Hash Testing

This directory contains utilities and test data for canonical JSON hashing across multiple languages.

## Supported Libraries

- **Node.js**: `json-canonicalize` (npm)
- **Python**: `rfc8785` (pip)
- **Go**: `webpki/jcs` (go get)
- **Rust**: `serde_jcs` (cargo)
- **Java**: WebPKI JSON library (maven)

## Usage

Run tests to verify consistent canonical JSON serialization across all languages:

```bash
# Node.js
npm test -- tests/golden-hash

# Python
pytest tests/golden-hash/

# Go
go test ./tests/golden-hash/...

# Rust
cd rust-canonicalize && cargo test

# Java
cd java-canonicalize && mvn test
```

## Golden Hash Test Data

All implementations should produce identical canonical JSON output for the same input data,
enabling cross-language hash verification.
EOF

# Create a sample test data file
cat > tests/golden-hash/test-data.json << 'EOF'
{
  "name": "Evez666",
  "type": "quantum-threat-detection",
  "features": ["canonical-hashing", "multi-language-support"],
  "version": 1.0,
  "modules": {
    "market-intelligence": true,
    "notifications": true,
    "automation": true,
    "monetization": true,
    "ai-engine": true
  }
}
EOF

echo -e "${GREEN}✅ Golden hash testing utilities created${NC}"

# 7. Final verification
echo -e "\n${YELLOW}🔍 Verifying installation...${NC}"

# Check Node.js
if npm list json-canonicalize &> /dev/null; then
    echo -e "${GREEN}✅ json-canonicalize (npm) - installed${NC}"
else
    echo -e "${YELLOW}⚠️  json-canonicalize (npm) - not found${NC}"
fi

# Check Python
if python3 -c "import rfc8785" &> /dev/null; then
    echo -e "${GREEN}✅ rfc8785 (python) - installed${NC}"
else
    echo -e "${YELLOW}⚠️  rfc8785 (python) - not found${NC}"
fi

# Check Go
if [ -f "go.mod" ] && grep -q "jsoncanonicalizer" go.mod 2>/dev/null; then
    echo -e "${GREEN}✅ webpki/jcs (go) - configured${NC}"
else
    echo -e "${YELLOW}⚠️  webpki/jcs (go) - not configured${NC}"
fi

# Check Rust
if [ -d "rust-canonicalize" ] && [ -f "rust-canonicalize/Cargo.toml" ]; then
    echo -e "${GREEN}✅ serde_jcs (rust) - configured${NC}"
else
    echo -e "${YELLOW}⚠️  serde_jcs (rust) - not configured${NC}"
fi

# Check Java
if [ -d "java-canonicalize" ] && [ -f "java-canonicalize/pom.xml" ]; then
    echo -e "${GREEN}✅ WebPKI (java) - configured${NC}"
else
    echo -e "${YELLOW}⚠️  WebPKI (java) - not configured${NC}"
fi

echo -e "\n${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  DEVCONTAINER SETUP COMPLETE${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Available canonical hashing libraries:"
echo "  • json-canonicalize (Node.js/npm)"
echo "  • rfc8785 (Python/pip)"
echo "  • webpki/jcs (Go)"
echo "  • serde_jcs (Rust)"
echo "  • WebPKI (Java/Maven)"
echo ""
echo "Run golden hash tests:"
echo "  npm test -- tests/golden-hash"
echo ""
echo "Deploy ops stack:"
echo "  ./scripts/deploy-ops-stack.sh"
echo ""
