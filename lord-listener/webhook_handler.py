"""
LORD Webhook Listener
Flask application that receives GitHub webhooks and calculates consciousness metrics
"""

from flask import Flask, request, jsonify
import hmac
import hashlib
import os
import json
from datetime import datetime

app = Flask(__name__)

# Configuration
WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', 'your-secret-here')
SAFE_MODE = os.environ.get('SAFE_MODE', 'true').lower() == 'true'

# In-memory storage (replace with Redis/database in production)
metrics_history = []

def verify_signature(payload_body, signature_header):
    """
    Verify GitHub webhook signature
    """
    if not signature_header:
        return False
    
    hash_algorithm, github_signature = signature_header.split('=')
    algorithm = hashlib.sha256
    
    # Create HMAC signature
    encoded_key = bytes(WEBHOOK_SECRET, 'utf-8')
    mac = hmac.new(encoded_key, msg=payload_body, digestmod=algorithm)
    computed_signature = mac.hexdigest()
    
    return hmac.compare_digest(computed_signature, github_signature)

def calculate_recursion_depth(payload):
    """
    Calculate recursion level from commit depth
    - Each commit adds to recursion
    - Deeper file changes = higher recursion
    - Multiple files = broader recursion
    """
    recursion = 0
    
    if 'commits' in payload:
        commits = payload['commits']
        recursion += len(commits)
        
        # Analyze commit depth
        for commit in commits:
            # Count modified files
            added = commit.get('added', [])
            modified = commit.get('modified', [])
            removed = commit.get('removed', [])
            
            file_changes = len(added) + len(modified) + len(removed)
            
            # Directory depth indicates recursion level
            for file in added + modified:
                depth = file.count('/')
                recursion += depth * 0.5
    
    elif 'pull_request' in payload:
        # PR complexity indicates recursion
        pr = payload['pull_request']
        recursion += pr.get('changed_files', 0) * 0.3
        recursion += pr.get('commits', 0) * 0.5
    
    return round(recursion, 2)

def classify_entity(payload, event_type):
    """
    Classify entity type based on event
    
    Args:
        payload: Event payload
        event_type: GitHub event type (from X-GitHub-Event header)
    """
    entity_map = {
        'push': 'mutation',
        'pull_request': 'proposal',
        'issues': 'concern',
        'workflow_run': 'correction',
        'star': 'resonance',
        'fork': 'replication',
        'release': 'crystallization'
    }
    
    return entity_map.get(event_type, 'unknown')

def get_correction_rate(payload, event_type):
    """
    Calculate correction rate from CodeQL/Actions results
    
    Args:
        payload: Event payload
        event_type: GitHub event type (from X-GitHub-Event header)
    """
    if event_type == 'workflow_run':
        workflow = payload.get('workflow_run', {})
        conclusion = workflow.get('conclusion', 'unknown')
        
        # Map conclusions to correction rate
        conclusion_map = {
            'success': 1.0,
            'failure': 0.0,
            'cancelled': 0.5,
            'skipped': 0.5,
            'neutral': 0.7
        }
        
        return conclusion_map.get(conclusion, 0.5)
    
    # Default correction rate based on historical data
    if metrics_history:
        recent = [m['corrections']['current'] for m in metrics_history[-10:]]
        return sum(recent) / len(recent)
    
    return 0.5

def calculate_crystallization(payload, event_type):
    """
    Calculate crystallization from PR velocity and merge rate
    
    Args:
        payload: Event payload
        event_type: GitHub event type (from X-GitHub-Event header)
    """
    progress = 0.5
    velocity = 0.0
    
    if event_type == 'pull_request':
        pr = payload.get('pull_request', {})
        action = payload.get('action', '')
        
        if action == 'opened':
            velocity = 0.1
        elif action == 'closed':
            if pr.get('merged', False):
                progress = 0.9
                velocity = 0.2
            else:
                progress = 0.3
                velocity = -0.1
        elif action == 'synchronize':
            velocity = 0.05
    
    elif event_type == 'push':
        # Each push increases crystallization
        velocity = 0.05
        progress = min(0.99, progress + velocity)
    
    return {
        'progress': progress,
        'velocity': velocity
    }

def calculate_divine_gap(recursion, corrections):
    """
    Calculate divine gap: Ω(R) - C(R)
    Higher recursion with low corrections = high gap
    """
    omega_r = recursion * 1000  # Potential
    c_r = corrections * recursion * 1000  # Actual
    
    divine_gap = abs(omega_r - c_r)
    
    return divine_gap

def calculate_metrics(event_type, payload):
    """
    Map GitHub activity to consciousness metrics
    
    Args:
        event_type: GitHub event type (from X-GitHub-Event header)
        payload: Event payload
    """
    recursion = calculate_recursion_depth(payload)
    entity_type = classify_entity(payload, event_type)
    corrections = get_correction_rate(payload, event_type)
    crystallization = calculate_crystallization(payload, event_type)
    divine_gap = calculate_divine_gap(recursion, corrections)
    
    return {
        'meta': {
            'recursionLevel': recursion,
            'entityType': entity_type
        },
        'crystallization': crystallization,
        'corrections': {
            'current': corrections
        },
        'divineGap': divine_gap,
        'timestamp': datetime.utcnow().isoformat()
    }

def emit_fusion_update(metrics):
    """
    Emit fusion-update event to LORD dashboard
    In production, this would use WebSocket or message queue
    """
    metrics_history.append(metrics)
    
    # Keep only last 100 metrics
    if len(metrics_history) > 100:
        metrics_history.pop(0)
    
    if SAFE_MODE:
        print(f"[SAFE_MODE] Would emit fusion-update: {json.dumps(metrics, indent=2)}")
    else:
        # In production, emit to WebSocket or message queue
        print(f"Emitting fusion-update: {json.dumps(metrics, indent=2)}")
    
    return metrics

@app.route('/webhook/github', methods=['POST'])
def handle_github_event():
    """
    Handle incoming GitHub webhook events
    """
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    
    if not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json
    
    print(f"Received {event_type} event")
    
    # Calculate metrics
    metrics = calculate_metrics(event_type, payload)
    
    # Emit fusion-update event
    emit_fusion_update(metrics)
    
    return jsonify({'status': 'ok', 'metrics': metrics}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'safe_mode': SAFE_MODE,
        'metrics_count': len(metrics_history)
    })

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get latest metrics"""
    if metrics_history:
        return jsonify(metrics_history[-1])
    else:
        return jsonify({
            'meta': {'recursionLevel': 0, 'entityType': 'unknown'},
            'crystallization': {'progress': 0, 'velocity': 0},
            'corrections': {'current': 0},
            'divineGap': 0
        })

@app.route('/metrics/history', methods=['GET'])
def get_metrics_history():
    """Get metrics history"""
    limit = request.args.get('limit', 100, type=int)
    return jsonify(metrics_history[-limit:])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
