"""
Blog Post Generator (Proposal-Only Mode)

Generates blog post proposals based on repository activity.
Does NOT auto-publish - all content requires human review.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import subprocess

logger = logging.getLogger('BlogGenerator')


def get_recent_commits(days: int = 7) -> List[Dict[str, Any]]:
    """Get recent commits from git history"""
    
    try:
        # Get git log
        result = subprocess.run(
            ['git', 'log', f'--since={days}.days.ago', '--pretty=format:%H|%s|%an|%ad', '--date=iso'],
            capture_output=True,
            text=True,
            check=True
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('|')
            if len(parts) >= 4:
                commits.append({
                    'hash': parts[0],
                    'message': parts[1],
                    'author': parts[2],
                    'date': parts[3]
                })
        
        return commits
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get git commits: {e}")
        return []


def analyze_commit_themes(commits: List[Dict[str, Any]]) -> List[str]:
    """Analyze commits to identify blog-worthy themes"""
    
    themes = []
    
    # Simple keyword-based theme detection
    keywords = {
        'cognitive-systems': ['cognitive', 'consciousness', 'lord', 'awareness'],
        'automation': ['automate', 'autonomous', 'workflow', 'ci/cd'],
        'ai-development': ['ai', 'ml', 'machine learning', 'neural'],
        'github-copilot': ['copilot', 'github', 'automation'],
        'monetization': ['revenue', 'sponsor', 'payment', 'monetize'],
        'performance': ['optimize', 'performance', 'latency', 'speed'],
    }
    
    commit_text = ' '.join([c['message'].lower() for c in commits])
    
    for theme, words in keywords.items():
        if any(word in commit_text for word in words):
            themes.append(theme)
    
    return themes


def generate_blog_proposal(theme: str, commits: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a blog post proposal for a theme"""
    
    # Topic suggestions based on theme
    topics = {
        'cognitive-systems': {
            'title': 'Building Self-Aware Repositories with LORD Protocol',
            'subtitle': 'How we monitor consciousness metrics in GitHub',
            'outline': [
                'Introduction to cognitive systems',
                'LORD protocol fundamentals',
                'Implementation in GitHub Actions',
                'Real-world metrics and results',
                'Future directions'
            ]
        },
        'automation': {
            'title': 'From Manual to Autonomous: Our GitHub Automation Journey',
            'subtitle': 'Lessons from building self-modifying repositories',
            'outline': [
                'The problem with manual workflows',
                'Designing autonomous systems',
                'GitHub Actions as the execution layer',
                'Handling edge cases and failures',
                'Measuring success'
            ]
        },
        'ai-development': {
            'title': 'AI-Driven Development: Beyond Code Completion',
            'subtitle': 'Using AI agents for repository evolution',
            'outline': [
                'Evolution of AI in development',
                'Agent-based architecture',
                'Integration with GitHub Copilot',
                'Case study: Evez666 project',
                'Best practices and pitfalls'
            ]
        },
        'github-copilot': {
            'title': 'GitHub Copilot as a Co-Maintainer',
            'subtitle': 'Closing the loop between AI and execution',
            'outline': [
                'Traditional Copilot usage patterns',
                'Issue-driven development with Copilot',
                'Automated PR generation',
                'Quality control and review',
                'Results and metrics'
            ]
        },
        'monetization': {
            'title': 'Monetizing Open Source: Beyond GitHub Sponsors',
            'subtitle': 'Building sustainable revenue streams',
            'outline': [
                'The open source sustainability problem',
                'Multiple revenue stream strategy',
                'Automation and scaling',
                'Tools and infrastructure',
                'Lessons learned'
            ]
        },
        'performance': {
            'title': 'Achieving Negative Latency with Predictive Systems',
            'subtitle': 'How EKF fusion loops create instant experiences',
            'outline': [
                'The latency problem',
                'Predictive computation basics',
                'Extended Kalman Filter implementation',
                'Real-world performance gains',
                'Trade-offs and limitations'
            ]
        }
    }
    
    topic_data = topics.get(theme, {
        'title': f'Recent Developments in {theme.title()}',
        'subtitle': 'Insights from our latest work',
        'outline': ['Introduction', 'Implementation', 'Results', 'Conclusion']
    })
    
    # Get relevant commits for this theme
    relevant_commits = [c for c in commits if any(
        keyword in c['message'].lower() 
        for keyword in theme.split('-')
    )][:5]
    
    proposal = {
        'type': 'blog_post',
        'title': topic_data['title'],
        'theme': theme,
        'status': 'proposal',
        'created': datetime.now().isoformat(),
        'revenue_potential': 50,  # Conservative estimate per post
        'risk_level': 'low',
        'description': f"Blog post about {theme} based on recent commits",
        'content': {
            'title': topic_data['title'],
            'subtitle': topic_data['subtitle'],
            'outline': topic_data['outline'],
            'supporting_commits': [
                f"{c['hash'][:8]}: {c['message']}" 
                for c in relevant_commits
            ],
            'target_platforms': config.get('content_farm', {}).get('blog_posts', {}).get('platforms', []),
            'estimated_words': 1500,
            'estimated_reading_time': '8 minutes'
        },
        'execution_steps': [
            '1. Review outline and adjust as needed',
            '2. Write full blog post (1500-2000 words)',
            '3. Add code examples from supporting commits',
            '4. Create accompanying images/diagrams',
            '5. Review for technical accuracy',
            '6. Publish to dev.to (or chosen platform)',
            '7. Share on social media',
            '8. Add canonical link to GitHub repo'
        ],
        'metadata': {
            'tags': theme.split('-'),
            'category': 'technical',
            'target_audience': 'developers',
            'seo_keywords': theme.replace('-', ' '),
            'ai_generated_notice': 'This outline was generated by AI and requires human review and completion'
        }
    }
    
    return proposal


def generate_proposals(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate blog post proposals based on recent activity"""
    
    blog_config = config.get('revenue_streams', {}).get('content_farm', {}).get('blog_posts', {})
    
    if not blog_config.get('enabled'):
        logger.info("Blog post generation disabled")
        return []
    
    # Get recent commits
    min_commits = config.get('revenue_streams', {}).get('content_farm', {}).get('blog_posts', {}).get('min_commit_count', 5)
    commits = get_recent_commits(days=7)
    
    if len(commits) < min_commits:
        logger.info(f"Not enough commits ({len(commits)} < {min_commits}) for blog post")
        return []
    
    # Analyze themes
    themes = analyze_commit_themes(commits)
    
    if not themes:
        logger.info("No blog-worthy themes detected in recent commits")
        return []
    
    # Generate proposals for top themes
    proposals = []
    max_proposals = config.get('revenue_streams', {}).get('content_farm', {}).get('max_proposals_per_day', 5)
    
    for theme in themes[:max_proposals]:
        proposal = generate_blog_proposal(theme, commits, config)
        proposals.append(proposal)
        logger.info(f"Generated blog proposal: {proposal['title']}")
    
    return proposals


if __name__ == '__main__':
    # Test with sample config
    import yaml
    
    config_path = Path('revenue_farm/configs/revenue_config.yml')
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    proposals = generate_proposals(config)
    print(f"Generated {len(proposals)} blog proposals")
    
    for p in proposals:
        print(f"  - {p['title']}")
