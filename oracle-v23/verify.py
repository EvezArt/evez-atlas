#!/usr/bin/env python3
"""
Oracle v2.3 Audit Log Verification Tool
Verifies the integrity of hash-chained audit logs
"""
import json
import hashlib
import sys
from pathlib import Path

def verify_log_chain(log_file):
    """Verify the cryptographic integrity of the audit log chain"""

    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return False

    if not logs:
        print("⚠️  Log file is empty")
        return True

    print(f"\n{'='*60}")
    print(f"Oracle v2.3 Log Verification")
    print(f"{'='*60}")
    print(f"Total entries: {len(logs)}")
    print(f"{'='*60}\n")

    errors = []

    for i, entry in enumerate(logs):
        # Check required fields
        required = ['timestamp', 'type', 'agent', 'payload', 'hash', 'prevHash']
        missing = [f for f in required if f not in entry]
        if missing:
            errors.append(f"Entry {i}: Missing fields {missing}")
            continue

        # Verify prevHash linkage
        if i == 0:
            if entry['prevHash'] != "0" * 64:
                errors.append(f"Entry {i}: Invalid genesis prevHash")
        else:
            if entry['prevHash'] != logs[i-1]['hash']:
                errors.append(f"Entry {i}: Chain broken - prevHash mismatch")

        # Verify hash
        data = f"{entry['timestamp']}|{entry['type']}|{entry['agent']}|{json.dumps(entry['payload'])}|{entry['prevHash']}"
        computed_hash = hashlib.sha256(data.encode()).hexdigest()

        if computed_hash != entry['hash']:
            errors.append(f"Entry {i}: Hash verification failed")
            print(f"  Expected: {entry['hash']}")
            print(f"  Computed: {computed_hash}")

    # Report results
    if errors:
        print("❌ VERIFICATION FAILED\n")
        for error in errors:
            print(f"  • {error}")
        print(f"\n{len(errors)} error(s) found")
        return False
    else:
        print("✅ VERIFICATION PASSED")
        print(f"\n  • All {len(logs)} entries verified")
        print(f"  • Chain integrity: INTACT")
        print(f"  • Hash linkage: VALID")
        print(f"\nLog is cryptographically sound.\n")
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python verify.py <audit_log.json>")
        print("\nExample:")
        print("  python verify.py oracle_audit_SESS-ABC123.json")
        sys.exit(1)

    log_file = Path(sys.argv[1])

    if not log_file.exists():
        print(f"❌ File not found: {log_file}")
        sys.exit(1)

    success = verify_log_chain(log_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
