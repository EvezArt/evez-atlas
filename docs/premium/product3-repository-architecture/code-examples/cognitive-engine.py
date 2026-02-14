"""
GitHub Cognitive Engine - Self-Modifying Repository Controller
Self-Modifying Repository Architecture - Chapter 11

Implements closed-loop GitHub → LORD → GitHub automation
with self-modification capabilities and safety validation.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class RepositoryState:
    """Current state of the repository"""
    commit_sha: str
    branch: str
    file_count: int
    last_modified: str
    health_score: float
    pending_modifications: List[str]


@dataclass
class ModificationProposal:
    """Proposed modification to repository"""
    id: str
    type: str  # 'add', 'modify', 'delete'
    file_path: str
    content: Optional[str]
    reason: str
    safety_score: float
    timestamp: str


class CognitiveEngine:
    """
    Self-modifying repository cognitive engine
    
    Monitors repository state, proposes modifications,
    validates safety, and executes changes autonomously.
    """
    
    def __init__(self, repo_path: str, config: Dict[str, Any]):
        """
        Initialize cognitive engine
        
        Args:
            repo_path: Path to repository
            config: Configuration dictionary
        """
        self.repo_path = repo_path
        self.config = config
        self.state = None
        self.modification_history = []
        self.safety_threshold = config.get('safety_threshold', 0.8)
        
    def scan_repository(self) -> RepositoryState:
        """
        Scan current repository state
        
        Returns:
            Current repository state
        """
        import subprocess
        
        # Get current commit
        commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=self.repo_path
        ).decode().strip()
        
        # Get current branch
        branch = subprocess.check_output(
            ['git', 'branch', '--show-current'],
            cwd=self.repo_path
        ).decode().strip()
        
        # Count files
        file_count = sum(1 for _ in self._walk_files())
        
        # Calculate health score
        health_score = self._calculate_health_score()
        
        state = RepositoryState(
            commit_sha=commit,
            branch=branch,
            file_count=file_count,
            last_modified=datetime.now().isoformat(),
            health_score=health_score,
            pending_modifications=[]
        )
        
        self.state = state
        return state
    
    def propose_modification(self, 
                           mod_type: str,
                           file_path: str,
                           content: Optional[str],
                           reason: str) -> ModificationProposal:
        """
        Propose a modification to the repository
        
        Args:
            mod_type: Type of modification
            file_path: Path to file
            content: New content (for add/modify)
            reason: Reason for modification
            
        Returns:
            Modification proposal
        """
        # Generate unique ID
        mod_id = hashlib.sha256(
            f"{mod_type}:{file_path}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Calculate safety score
        safety_score = self._evaluate_safety(mod_type, file_path, content)
        
        proposal = ModificationProposal(
            id=mod_id,
            type=mod_type,
            file_path=file_path,
            content=content,
            reason=reason,
            safety_score=safety_score,
            timestamp=datetime.now().isoformat()
        )
        
        return proposal
    
    def validate_modification(self, proposal: ModificationProposal) -> bool:
        """
        Validate modification against safety constraints
        
        Args:
            proposal: Modification proposal
            
        Returns:
            True if safe to execute
        """
        # Check safety score
        if proposal.safety_score < self.safety_threshold:
            print(f"❌ Modification {proposal.id} rejected: "
                  f"safety score {proposal.safety_score:.2f} < {self.safety_threshold}")
            return False
        
        # Check file path constraints
        restricted_paths = self.config.get('restricted_paths', [])
        for restricted in restricted_paths:
            if proposal.file_path.startswith(restricted):
                print(f"❌ Modification {proposal.id} rejected: "
                      f"path {proposal.file_path} is restricted")
                return False
        
        # Check modification type
        if proposal.type == 'delete':
            critical_files = self.config.get('critical_files', [])
            if proposal.file_path in critical_files:
                print(f"❌ Modification {proposal.id} rejected: "
                      f"cannot delete critical file")
                return False
        
        return True
    
    def execute_modification(self, proposal: ModificationProposal) -> bool:
        """
        Execute validated modification
        
        Args:
            proposal: Modification proposal
            
        Returns:
            True if successful
        """
        if not self.validate_modification(proposal):
            return False
        
        try:
            file_path = os.path.join(self.repo_path, proposal.file_path)
            
            if proposal.type == 'add' or proposal.type == 'modify':
                # Create directories if needed
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Write content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(proposal.content)
                
                print(f"✅ {proposal.type.capitalize()}ed: {proposal.file_path}")
                
            elif proposal.type == 'delete':
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"✅ Deleted: {proposal.file_path}")
            
            # Record in history
            self.modification_history.append({
                'proposal': asdict(proposal),
                'executed_at': datetime.now().isoformat(),
                'success': True
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to execute modification: {e}")
            self.modification_history.append({
                'proposal': asdict(proposal),
                'executed_at': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            })
            return False
    
    def commit_changes(self, message: str) -> bool:
        """
        Commit modifications to repository
        
        Args:
            message: Commit message
            
        Returns:
            True if successful
        """
        import subprocess
        
        try:
            # Stage all changes
            subprocess.run(
                ['git', 'add', '.'],
                cwd=self.repo_path,
                check=True
            )
            
            # Commit
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.repo_path,
                check=True
            )
            
            print(f"✅ Committed: {message}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Commit failed: {e}")
            return False
    
    def _walk_files(self):
        """Walk repository files"""
        for root, dirs, files in os.walk(self.repo_path):
            # Skip .git directory
            if '.git' in root:
                continue
            for file in files:
                yield os.path.join(root, file)
    
    def _calculate_health_score(self) -> float:
        """
        Calculate repository health score
        
        Returns:
            Health score (0.0 - 1.0)
        """
        score = 1.0
        
        # Check for required files
        required_files = ['README.md', '.gitignore']
        for req_file in required_files:
            if not os.path.exists(os.path.join(self.repo_path, req_file)):
                score -= 0.1
        
        # Check for documentation
        docs_dir = os.path.join(self.repo_path, 'docs')
        if not os.path.exists(docs_dir):
            score -= 0.1
        
        return max(0.0, score)
    
    def _evaluate_safety(self, 
                        mod_type: str,
                        file_path: str,
                        content: Optional[str]) -> float:
        """
        Evaluate safety of modification
        
        Returns:
            Safety score (0.0 - 1.0)
        """
        score = 1.0
        
        # Check file extension
        dangerous_extensions = ['.sh', '.exe', '.bat']
        if any(file_path.endswith(ext) for ext in dangerous_extensions):
            score -= 0.2
        
        # Check for sensitive content
        if content:
            sensitive_patterns = ['password', 'secret', 'api_key', 'token']
            for pattern in sensitive_patterns:
                if pattern in content.lower():
                    score -= 0.3
        
        # Check modification type
        if mod_type == 'delete':
            score -= 0.1  # Deletions are slightly riskier
        
        return max(0.0, score)
    
    def save_state(self, output_path: str):
        """Save engine state to file"""
        state_data = {
            'state': asdict(self.state) if self.state else None,
            'modification_history': self.modification_history,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2)


# Example usage
if __name__ == "__main__":
    print("🧠 Cognitive Engine Demo")
    print("=" * 60)
    
    # Configuration
    config = {
        'safety_threshold': 0.7,
        'restricted_paths': ['.git/', '.github/workflows/'],
        'critical_files': ['README.md', 'LICENSE']
    }
    
    # Initialize engine
    engine = CognitiveEngine('/tmp/demo-repo', config)
    
    # Scan repository
    print("\n📊 Scanning repository...")
    state = engine.scan_repository()
    print(f"   Branch: {state.branch}")
    print(f"   Files: {state.file_count}")
    print(f"   Health: {state.health_score:.2f}")
    
    # Propose modification
    print("\n💡 Proposing modification...")
    proposal = engine.propose_modification(
        mod_type='add',
        file_path='docs/auto-generated.md',
        content='# Auto-Generated Documentation\n\nThis file was created by the cognitive engine.',
        reason='Create documentation for new feature'
    )
    print(f"   ID: {proposal.id}")
    print(f"   Safety: {proposal.safety_score:.2f}")
    
    # Execute if safe
    print("\n⚙️  Executing modification...")
    if engine.execute_modification(proposal):
        print("   ✅ Modification successful")
    
    # Save state
    print("\n💾 Saving state...")
    engine.save_state('/tmp/engine-state.json')
    print("   ✅ State saved")
    
    print("\n" + "=" * 60)
    print("✨ Cognitive engine demo complete!")
