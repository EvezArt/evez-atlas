# DevContainer Configuration for Evez666

This devcontainer configuration provides a comprehensive development environment for the Evez666 project with support for multiple programming languages and canonical JSON hashing libraries.

## Features

### Multi-Language Support
- **Node.js 20** - TypeScript/JavaScript development
- **Python 3.11** - Python-based services and APIs
- **Go 1.21** - Go modules and services
- **Rust** - Systems programming with Cargo
- **Java 17** - JVM-based applications with Maven

### Canonical Hashing Libraries

The devcontainer includes support for canonical JSON serialization (RFC 8785) across all supported languages:

| Language | Library | Package Manager |
|----------|---------|-----------------|
| Node.js | json-canonicalize | npm |
| Python | rfc8785 | pip |
| Go | webpki/jcs | go get |
| Rust | serde_jcs | cargo |
| Java | WebPKI JSON | maven |

These libraries enable consistent JSON canonicalization for golden hash testing and cross-language verification.

## Getting Started

### 1. Open in GitHub Codespaces

Click the "Code" button on the repository page and select "Open with Codespaces" → "New codespace".

### 2. Automatic Setup

The devcontainer will automatically:
- Install all language runtimes
- Configure VS Code with recommended extensions
- Run the setup script to install canonical hashing libraries
- Create test data and utilities for golden hash testing

### 3. Verify Installation

After the devcontainer starts, verify the installation:

```bash
# Check Node.js
node --version
npm list json-canonicalize

# Check Python
python3 --version
pip list | grep rfc8785

# Check Go
go version

# Check Rust
rustc --version
cargo --version

# Check Java
java --version
mvn --version
```

## Ops Stack

The devcontainer is configured to support the Evez666 Ops Stack, which includes:

- **Market Intelligence** - Market analysis and trend detection
- **Notifications** - Multi-channel notification system
- **Automation** - Task and workflow automation engine
- **Monetization** - Revenue tracking and financial metrics
- **AI Engine** - ML model management and predictions

### Deploy the Ops Stack

```bash
# Build and deploy the ops stack
./scripts/deploy-ops-stack.sh

# Or manually:
npm install
npm run build
node dist/ops-stack.js
```

## Golden Hash Testing

The devcontainer includes utilities for golden hash testing to verify consistent canonical JSON serialization across languages.

### Test Data Location

```
tests/golden-hash/
├── README.md          # Golden hash testing documentation
└── test-data.json     # Sample test data
```

### Running Golden Hash Tests

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

## Port Forwarding

The following ports are automatically forwarded:

- **8000** - Jubilee API
- **3000** - Development Server
- **8080** - Ops Stack

## Development Workflow

### 1. Build TypeScript

```bash
npm run build
```

### 2. Run Tests

```bash
npm test
```

### 3. Lint Code

```bash
npm run lint
```

### 4. Run Existing Services

```bash
# Start Jubilee service
./scripts/jubilee_up.sh

# Deploy all services
./scripts/deploy-all.sh

# Stop all services
./scripts/stop-all.sh
```

## VS Code Extensions

The devcontainer includes the following pre-installed extensions:

- ESLint - JavaScript/TypeScript linting
- Pylance - Python language support
- Go - Go language support
- Rust Analyzer - Rust language support
- Java Extension Pack - Java development tools
- Prettier - Code formatting
- GitHub Copilot - AI pair programming
- Docker - Container management

## Environment Variables

Default environment variables:

```bash
JUBILEE_MODE=qsvc-ibm
NODE_ENV=development
OPS_STACK_PORT=8080
```

Override these in your `.env` file or Codespace settings.

## Troubleshooting

### Setup Script Fails

If the setup script fails, you can run it manually:

```bash
bash .devcontainer/setup.sh
```

### Missing Dependencies

Install missing dependencies manually:

```bash
# Node.js
npm install

# Python
pip install -r requirements.txt

# Go
go mod download

# Rust
cd rust-canonicalize && cargo build

# Java
cd java-canonicalize && mvn install
```

### Port Conflicts

If ports are already in use, update the port configuration in `.devcontainer/devcontainer.json` or use different ports in your service configuration.

## Additional Resources

- [Evez666 README](../README.md)
- [Ops Stack Documentation](../src/ops-stack.ts)
- [Golden Hash Testing](../tests/golden-hash/README.md)
- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)

## Contributing

When making changes to the devcontainer:

1. Test changes locally with the Dev Containers extension
2. Verify all languages and tools are properly configured
3. Update this README if adding new features
4. Ensure the setup script is idempotent
