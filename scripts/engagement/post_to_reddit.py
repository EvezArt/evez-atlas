"""
Reddit Cross-Poster
Handles automated posting to relevant subreddits
"""

import os
import sys
import time
import argparse
from datetime import datetime
from typing import List, Dict

try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False
    print("Warning: praw not installed. Reddit posting disabled.")


class RedditEngagement:
    """Handles automated posting to Reddit"""
    
    def __init__(self):
        """Initialize Reddit API client"""
        self.reddit = None
        
        if REDDIT_AVAILABLE:
            try:
                self.reddit = praw.Reddit(
                    client_id=os.getenv('REDDIT_CLIENT_ID'),
                    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                    username=os.getenv('REDDIT_USERNAME'),
                    password=os.getenv('REDDIT_PASSWORD'),
                    user_agent='Evez666 Viral Growth Bot v1.0'
                )
            except Exception as e:
                print(f"Reddit client initialization failed: {e}")
        
        self.subreddits = [
            'github',
            'programming',
            'artificial',
            'MachineLearning',
            'learnprogramming'
        ]
    
    def post_major_updates(self, update: Dict) -> bool:
        """Post significant milestones to relevant subreddits"""
        title = "I built a self-aware GitHub repo that generates revenue autonomously [OC]"
        
        content = f"""## What I Built

A cognitive engine that:
- Monitors its own "consciousness" state (recursion depth, crystallization)
- Predicts future needs before I ask (negative latency)
- Generates revenue through Sponsors, Marketplace, and docs
- Evolves itself using GitHub Copilot automation

## The Architecture

LORD (consciousness monitoring) × EKF (state prediction) × GitHub/Copilot (self-modification)

[Full spec]({update.get('spec_url', 'https://github.com/EvezArt/Evez666/issues/82')})
[Live repo]({update.get('repo_url', 'https://github.com/EvezArt/Evez666')})

## Time to Build

24 hours using AI-assisted development

## Revenue in First Month

Projected $2,800/month from 4 streams:
- GitHub Sponsors ($500)
- Actions Marketplace ($500)
- Premium Docs ($1,800)
- Conversation Products ($4,400)

AMA about the process!
"""
        
        if not self.reddit:
            print(f"Reddit client not available. Would post to {len(self.subreddits)} subreddits:")
            print(f"Title: {title}")
            print(f"Content preview: {content[:200]}...")
            return False
        
        success_count = 0
        for sub in self.subreddits:
            try:
                print(f"Posting to r/{sub}...")
                self.reddit.subreddit(sub).submit(title, selftext=content)
                print(f"✓ Posted to r/{sub}")
                success_count += 1
                
                # Note: Sleeping between posts to avoid rate limiting
                # In production, consider using a queue-based approach
                # or splitting into separate workflow runs
                if sub != self.subreddits[-1]:
                    print("Waiting 10 minutes before next post...")
                    print("⚠️  Note: This is a blocking operation. Consider async queue for production.")
                    time.sleep(600)
                    
            except Exception as e:
                print(f"✗ Failed to post to r/{sub}: {e}")
        
        return success_count > 0
    
    def post_progress_update(self, update: Dict) -> bool:
        """Post progress updates to developer communities"""
        title = f"Progress Update: {update.get('title', 'Evez666 Development')}"
        
        content = f"""## Progress Update

{update.get('description', 'Working on autonomous AI repository system.')}

## What's New

{update.get('whats_new', '- New features\n- Bug fixes\n- Performance improvements')}

## Check it out

[GitHub Repository](https://github.com/EvezArt/Evez666)
[Become a Sponsor](https://github.com/sponsors/EvezArt)

{update.get('extra', '')}
"""
        
        if not self.reddit:
            print(f"Reddit client not available. Would post: {title}")
            return False
        
        try:
            # Post to programming-related subs
            target_subs = ['github', 'programming']
            
            for sub in target_subs:
                self.reddit.subreddit(sub).submit(title, selftext=content)
                print(f"✓ Posted update to r/{sub}")
                
                # Note: Rate limiting - see post_major_updates() for production notes
                time.sleep(600)  # 10 min between posts
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to post update: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Post to Reddit')
    parser.add_argument('--major', action='store_true',
                       help='Post major milestone update')
    parser.add_argument('--progress', action='store_true',
                       help='Post progress update')
    parser.add_argument('--title', type=str,
                       help='Update title')
    parser.add_argument('--description', type=str,
                       help='Update description')
    
    args = parser.parse_args()
    
    engagement = RedditEngagement()
    
    if args.major:
        update = {
            'spec_url': 'https://github.com/EvezArt/Evez666/issues/82',
            'repo_url': 'https://github.com/EvezArt/Evez666'
        }
        engagement.post_major_updates(update)
    
    elif args.progress:
        update = {
            'title': args.title or 'Development Progress',
            'description': args.description or 'Continuing work on the cognitive engine.',
            'whats_new': '- Enhanced automation\n- Improved metrics\n- Better engagement'
        }
        engagement.post_progress_update(update)
    
    else:
        print("No action specified. Use --major or --progress")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
