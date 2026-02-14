#!/usr/bin/env node

/**
 * Health Check Script
 * Verifies system components and reports status
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

const STATUS = {
  OK: `${colors.green}✓${colors.reset}`,
  FAIL: `${colors.red}✗${colors.reset}`,
  WARN: `${colors.yellow}⚠${colors.reset}`,
  INFO: `${colors.blue}ℹ${colors.reset}`
};

class HealthChecker {
  constructor() {
    this.results = {
      timestamp: new Date().toISOString(),
      checks: [],
      summary: {
        total: 0,
        passed: 0,
        failed: 0,
        warnings: 0
      }
    };
  }

  log(message) {
    console.log(message);
  }

  check(name, fn) {
    this.results.summary.total++;
    try {
      const result = fn();
      if (result.status === 'ok') {
        this.results.summary.passed++;
        this.log(`${STATUS.OK} ${name}`);
        if (result.message) {
          this.log(`  ${colors.cyan}${result.message}${colors.reset}`);
        }
      } else if (result.status === 'warn') {
        this.results.summary.warnings++;
        this.log(`${STATUS.WARN} ${name}`);
        this.log(`  ${colors.yellow}${result.message}${colors.reset}`);
      } else {
        this.results.summary.failed++;
        this.log(`${STATUS.FAIL} ${name}`);
        this.log(`  ${colors.red}${result.message}${colors.reset}`);
      }
      this.results.checks.push({ name, ...result });
    } catch (error) {
      this.results.summary.failed++;
      this.log(`${STATUS.FAIL} ${name}`);
      this.log(`  ${colors.red}Error: ${error.message}${colors.reset}`);
      this.results.checks.push({
        name,
        status: 'fail',
        message: error.message
      });
    }
  }

  // Check if directory exists
  checkDirectory(dirPath) {
    return fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory();
  }

  // Check if file exists
  checkFile(filePath) {
    return fs.existsSync(filePath) && fs.statSync(filePath).isFile();
  }

  // Execute command and capture output
  execCommand(command) {
    try {
      return execSync(command, { encoding: 'utf8', stdio: 'pipe' }).trim();
    } catch (error) {
      throw new Error(`Command failed: ${error.message}`);
    }
  }

  runChecks() {
    this.log(`\n${colors.cyan}=== Evez666 Health Check ===${colors.reset}\n`);

    // 1. Core directories
    this.log(`${colors.blue}Checking core directories...${colors.reset}`);
    this.check('Core directories', () => {
      const dirs = ['.github/workflows', '.openclaw/skills', 'docs', 'scripts'];
      const missing = dirs.filter(d => !this.checkDirectory(path.join(process.cwd(), d)));
      
      if (missing.length === 0) {
        return { status: 'ok', message: 'All core directories present' };
      } else {
        return { status: 'fail', message: `Missing: ${missing.join(', ')}` };
      }
    });

    // 2. Package.json dependencies
    this.log(`\n${colors.blue}Checking Node.js dependencies...${colors.reset}`);
    this.check('package.json', () => {
      const pkgPath = path.join(process.cwd(), 'package.json');
      if (!this.checkFile(pkgPath)) {
        return { status: 'fail', message: 'package.json not found' };
      }
      
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const requiredDeps = ['openai', '@octokit/rest', 'node-fetch'];
      const missing = requiredDeps.filter(dep => 
        !pkg.dependencies || !pkg.dependencies[dep]
      );
      
      if (missing.length === 0) {
        return { status: 'ok', message: 'Required dependencies configured' };
      } else {
        return { status: 'warn', message: `Missing dependencies: ${missing.join(', ')}` };
      }
    });

    this.check('node_modules', () => {
      if (this.checkDirectory(path.join(process.cwd(), 'node_modules'))) {
        return { status: 'ok', message: 'Dependencies installed' };
      } else {
        return { status: 'warn', message: 'Run npm install to install dependencies' };
      }
    });

    // 3. GitHub workflows
    this.log(`\n${colors.blue}Checking GitHub workflows...${colors.reset}`);
    this.check('Workflows', () => {
      const workflows = [
        'auto-ready-prs.yml',
        'metrics-dashboard.yml',
        'secret-scan.yml',
        'policy-check.yml'
      ];
      const workflowDir = path.join(process.cwd(), '.github/workflows');
      const missing = workflows.filter(w => !this.checkFile(path.join(workflowDir, w)));
      
      if (missing.length === 0) {
        return { status: 'ok', message: `${workflows.length} workflows configured` };
      } else {
        return { status: 'warn', message: `Missing: ${missing.join(', ')}` };
      }
    });

    this.check('Dependabot', () => {
      if (this.checkFile(path.join(process.cwd(), '.github/dependabot.yml'))) {
        return { status: 'ok', message: 'Dependabot configured' };
      } else {
        return { status: 'warn', message: 'Dependabot not configured' };
      }
    });

    // 4. OpenClaw skills
    this.log(`\n${colors.blue}Checking OpenClaw skills...${colors.reset}`);
    this.check('Skills', () => {
      const skills = [
        'self-awareness.js',
        'deepclaw-integration.js',
        'chatgpt-integration.js',
        'perplexity-integration.js',
        'github-autonomous.js',
        'autonomous-orchestrator.js'
      ];
      const skillsDir = path.join(process.cwd(), '.openclaw/skills');
      const existing = skills.filter(s => this.checkFile(path.join(skillsDir, s)));
      
      if (existing.length === skills.length) {
        return { status: 'ok', message: `All ${skills.length} skills present` };
      } else {
        return { status: 'warn', message: `${existing.length}/${skills.length} skills present` };
      }
    });

    // 5. Environment variables
    this.log(`\n${colors.blue}Checking environment variables...${colors.reset}`);
    this.check('SAFE_MODE', () => {
      const safeMode = process.env.SAFE_MODE;
      if (safeMode === undefined || safeMode === 'true') {
        return { status: 'ok', message: 'SAFE_MODE enabled (recommended)' };
      } else {
        return { status: 'warn', message: 'SAFE_MODE disabled (use with caution)' };
      }
    });

    const apiKeys = [
      { name: 'OPENAI_API_KEY', optional: false },
      { name: 'PERPLEXITY_API_KEY', optional: false },
      { name: 'ANTHROPIC_API_KEY', optional: false },
      { name: 'GITHUB_TOKEN', optional: true }
    ];

    apiKeys.forEach(({ name, optional }) => {
      this.check(name, () => {
        if (process.env[name]) {
          return { status: 'ok', message: 'Configured' };
        } else if (optional) {
          return { status: 'warn', message: 'Not set (optional)' };
        } else {
          return { status: 'warn', message: 'Not set (required for full functionality)' };
        }
      });
    });

    // 6. Documentation
    this.log(`\n${colors.blue}Checking documentation...${colors.reset}`);
    this.check('Documentation', () => {
      const docs = ['TROUBLESHOOTING.md', 'SAFETY.md'];
      const docsDir = path.join(process.cwd(), 'docs');
      const existing = docs.filter(d => this.checkFile(path.join(docsDir, d)));
      
      if (existing.length === docs.length) {
        return { status: 'ok', message: 'All essential docs present' };
      } else {
        return { status: 'warn', message: `Missing: ${docs.filter(d => !existing.includes(d)).join(', ')}` };
      }
    });

    // 7. Git status
    this.log(`\n${colors.blue}Checking Git status...${colors.reset}`);
    this.check('Git repository', () => {
      try {
        const status = this.execCommand('git status --porcelain');
        if (status === '') {
          return { status: 'ok', message: 'Working tree clean' };
        } else {
          const lines = status.split('\n').length;
          return { status: 'info', message: `${lines} uncommitted changes` };
        }
      } catch (error) {
        return { status: 'warn', message: 'Not a git repository or git not available' };
      }
    });

    // Summary
    this.log(`\n${colors.cyan}=== Summary ===${colors.reset}`);
    this.log(`Total checks: ${this.results.summary.total}`);
    this.log(`${STATUS.OK} Passed: ${this.results.summary.passed}`);
    this.log(`${STATUS.FAIL} Failed: ${this.results.summary.failed}`);
    this.log(`${STATUS.WARN} Warnings: ${this.results.summary.warnings}`);

    // Overall status
    if (this.results.summary.failed === 0) {
      this.log(`\n${colors.green}✓ System health: GOOD${colors.reset}`);
      return 0;
    } else if (this.results.summary.failed <= 2) {
      this.log(`\n${colors.yellow}⚠ System health: FAIR (some issues detected)${colors.reset}`);
      return 0;
    } else {
      this.log(`\n${colors.red}✗ System health: POOR (multiple issues detected)${colors.reset}`);
      return 1;
    }
  }
}

// Run health check
const checker = new HealthChecker();
const exitCode = checker.runChecks();

// Save results to file if requested
if (process.argv.includes('--output')) {
  const outputPath = path.join(process.cwd(), 'health-check-results.json');
  fs.writeFileSync(outputPath, JSON.stringify(checker.results, null, 2));
  console.log(`\nResults saved to: ${outputPath}`);
}

process.exit(exitCode);
