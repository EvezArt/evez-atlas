"""
GitHub Policy Executor
Executes control policies by creating GitHub resources
"""

from github import Github, GithubException
import os
import json
from datetime import datetime

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'EvezArt/Evez666')
SAFE_MODE = os.environ.get('SAFE_MODE', 'true').lower() == 'true'

class PolicyExecutor:
    """
    Execute control policies by creating GitHub resources
    """
    
    def __init__(self, github_token=None, repo_name=None):
        self.token = github_token or GITHUB_TOKEN
        self.repo_name = repo_name or GITHUB_REPO
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN is required")
        
        self.gh = Github(self.token)
        self.repo = self.gh.get_repo(self.repo_name)
        
        print(f"Initialized PolicyExecutor for {self.repo_name}")
        print(f"SAFE_MODE: {SAFE_MODE}")
    
    def execute_policy(self, control_policy):
        """
        Execute control policy by creating GitHub resources
        
        Args:
            control_policy: dict with action, labels, title, body, etc.
        
        Returns:
            Created resource or None
        """
        if not control_policy:
            print("No control policy to execute")
            return None
        
        action = control_policy.get('action')
        
        if action == 'create_issue':
            return self.create_issue(control_policy)
        elif action == 'create_pr':
            return self.create_pull_request(control_policy)
        elif action == 'add_comment':
            return self.add_comment(control_policy)
        else:
            print(f"Unknown action: {action}")
            return None
    
    def create_issue(self, policy):
        """
        Create a GitHub issue from policy
        
        Args:
            policy: dict with title, body, labels, assign_copilot
        
        Returns:
            Issue object or None
        """
        title = policy.get('title', 'LORD Autonomous Issue')
        body = policy.get('body', '')
        labels = policy.get('labels', [])
        assign_copilot = policy.get('assign_copilot', False)
        
        # Add SAFE_MODE disclaimer to body
        if SAFE_MODE:
            body += "\n\n---\n**🔒 SAFE_MODE**: This issue was created in safe mode. "
            body += "Review before taking action.\n"
        
        # Add metadata
        body += f"\n\n**Metadata:**\n"
        body += f"- Generated: {datetime.utcnow().isoformat()}Z\n"
        body += f"- Reason: {policy.get('reason', 'unknown')}\n"
        body += f"- SAFE_MODE: {SAFE_MODE}\n"
        
        if SAFE_MODE:
            # In SAFE_MODE, log what would be created
            print("\n" + "="*60)
            print("SAFE_MODE: Would create issue:")
            print("="*60)
            print(f"Title: {title}")
            print(f"Labels: {labels}")
            print(f"Body:\n{body}")
            print("="*60 + "\n")
            
            return {
                'safe_mode': True,
                'would_create': 'issue',
                'title': title,
                'labels': labels
            }
        
        try:
            # Create the issue
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels
            )
            
            print(f"✓ Created issue #{issue.number}: {title}")
            
            # Assign Copilot if requested
            if assign_copilot:
                self.assign_copilot_to_issue(issue.number)
            
            return issue
            
        except GithubException as e:
            print(f"✗ Failed to create issue: {e}")
            return None
    
    def create_pull_request(self, policy):
        """
        Create a pull request from policy
        
        Args:
            policy: dict with title, body, head, base
        
        Returns:
            PR object or None
        """
        title = policy.get('title', 'LORD Autonomous PR')
        body = policy.get('body', '')
        head = policy.get('head')  # Branch to merge from
        base = policy.get('base', 'main')  # Branch to merge into
        
        if not head:
            print("PR creation requires 'head' branch")
            return None
        
        if SAFE_MODE:
            print("\n" + "="*60)
            print("SAFE_MODE: Would create PR:")
            print("="*60)
            print(f"Title: {title}")
            print(f"Head: {head} -> Base: {base}")
            print(f"Body:\n{body}")
            print("="*60 + "\n")
            
            return {
                'safe_mode': True,
                'would_create': 'pull_request',
                'title': title
            }
        
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            
            print(f"✓ Created PR #{pr.number}: {title}")
            return pr
            
        except GithubException as e:
            print(f"✗ Failed to create PR: {e}")
            return None
    
    def add_comment(self, policy):
        """
        Add comment to existing issue or PR
        
        Args:
            policy: dict with issue_number, comment
        
        Returns:
            Comment object or None
        """
        issue_number = policy.get('issue_number')
        comment_body = policy.get('comment', '')
        
        if not issue_number:
            print("Comment requires 'issue_number'")
            return None
        
        if SAFE_MODE:
            print(f"SAFE_MODE: Would comment on issue #{issue_number}")
            return {'safe_mode': True, 'would_comment': True}
        
        try:
            issue = self.repo.get_issue(issue_number)
            comment = issue.create_comment(comment_body)
            
            print(f"✓ Added comment to issue #{issue_number}")
            return comment
            
        except GithubException as e:
            print(f"✗ Failed to add comment: {e}")
            return None
    
    def assign_copilot_to_issue(self, issue_number):
        """
        Assign Copilot to an issue
        
        Note: This is a placeholder. Actual Copilot assignment
        happens via labels and issue templates.
        
        Args:
            issue_number: Issue number to assign
        """
        if SAFE_MODE:
            print(f"SAFE_MODE: Would assign Copilot to issue #{issue_number}")
            return
        
        try:
            issue = self.repo.get_issue(issue_number)
            
            # Add label to trigger Copilot
            issue.add_to_labels('copilot:requested')
            
            # Add comment to invoke Copilot
            comment = (
                "@copilot Please analyze this issue and propose a solution. "
                "This is an autonomous request from the LORD cognitive loop."
            )
            issue.create_comment(comment)
            
            print(f"✓ Assigned Copilot to issue #{issue_number}")
            
        except GithubException as e:
            print(f"✗ Failed to assign Copilot: {e}")
    
    def get_recent_issues(self, labels=None, state='open', limit=10):
        """
        Get recent issues, optionally filtered by labels
        
        Args:
            labels: List of label names to filter
            state: 'open', 'closed', or 'all'
            limit: Maximum number of issues to return
        
        Returns:
            List of issue objects
        """
        try:
            issues = self.repo.get_issues(
                state=state,
                labels=labels or [],
                sort='created',
                direction='desc'
            )
            
            return list(issues[:limit])
            
        except GithubException as e:
            print(f"✗ Failed to get issues: {e}")
            return []
    
    def check_duplicate_issue(self, title_prefix, days=7):
        """
        Check if similar issue exists in last N days
        
        Args:
            title_prefix: Title prefix to match
            days: Number of days to look back
        
        Returns:
            True if duplicate found, False otherwise
        """
        try:
            issues = self.repo.get_issues(
                state='all',
                sort='created',
                direction='desc'
            )
            
            # Get current time as UTC
            now_utc = datetime.utcnow()
            
            for issue in issues[:50]:  # Check last 50 issues
                if issue.title.startswith(title_prefix):
                    # Check age - both times are UTC
                    issue_created_utc = issue.created_at.replace(tzinfo=None)
                    age = (now_utc - issue_created_utc).days
                    if age <= days:
                        print(f"Found duplicate issue #{issue.number}: {issue.title}")
                        return True
            
            return False
            
        except GithubException as e:
            print(f"✗ Failed to check duplicates: {e}")
            return False

def main():
    """Main function for testing"""
    executor = PolicyExecutor()
    
    # Test policy
    test_policy = {
        'action': 'create_issue',
        'labels': ['test', 'lord:autonomous'],
        'title': 'Test Issue from LORD',
        'body': 'This is a test issue created by the LORD policy executor.',
        'assign_copilot': False,
        'reason': 'test'
    }
    
    result = executor.execute_policy(test_policy)
    print(f"Result: {result}")

if __name__ == '__main__':
    main()
