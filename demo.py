"""
Quantum Threat Detection System - Demo Module

This module provides a demonstration of the quantum threat detection
system using simulated network intrusion data.
"""

import random
from typing import Dict, List, Tuple

# Feature names from NSL-KDD dataset (first 10 numeric features)
FEATURE_NAMES = [
    "duration",
    "src_bytes", 
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
]


def generate_sample_data(
    n_samples: int = 100,
    n_features: int = 10,
    attack_ratio: float = 0.3
) -> Tuple[List[List[float]], List[int]]:
    """
    Generate synthetic network traffic data for demonstration.
    
    Args:
        n_samples: Number of samples to generate
        n_features: Number of features per sample
        attack_ratio: Proportion of attack samples (0-1)
        
    Returns:
        Tuple of (features, labels) where labels are 0=normal, 1=attack
    """
    X = []
    y = []
    
    n_attacks = int(n_samples * attack_ratio)
    n_normal = n_samples - n_attacks
    
    # Generate normal traffic patterns
    for _ in range(n_normal):
        features = [
            random.uniform(0, 100),      # duration
            random.uniform(100, 1000),   # src_bytes
            random.uniform(100, 1000),   # dst_bytes
            0.0,                         # land (normal)
            random.uniform(0, 1),        # wrong_fragment
            0.0,                         # urgent
            random.uniform(0, 3),        # hot
            0.0,                         # num_failed_logins
            1.0,                         # logged_in
            0.0,                         # num_compromised
        ]
        X.append(features[:n_features])
        y.append(0)
    
    # Generate attack patterns
    for _ in range(n_attacks):
        attack_type = random.choice(["dos", "probe", "r2l", "u2r"])
        
        if attack_type == "dos":
            # Denial of Service: high traffic, anomalous patterns
            features = [
                random.uniform(0, 10),       # short duration
                random.uniform(0, 100),      # low src_bytes
                random.uniform(5000, 50000), # high dst_bytes
                random.choice([0.0, 1.0]),   # land
                random.uniform(0, 3),        # wrong_fragment
                0.0,                         # urgent
                random.uniform(5, 20),       # high hot
                0.0,                         # num_failed_logins
                0.0,                         # not logged_in
                0.0,                         # num_compromised
            ]
        elif attack_type == "probe":
            # Probing: scanning behavior
            features = [
                random.uniform(0, 5),        # very short duration
                random.uniform(0, 50),       # low src_bytes
                random.uniform(0, 50),       # low dst_bytes
                0.0,                         # land
                0.0,                         # wrong_fragment
                0.0,                         # urgent
                0.0,                         # hot
                0.0,                         # num_failed_logins
                0.0,                         # not logged_in
                0.0,                         # num_compromised
            ]
        elif attack_type == "r2l":
            # Remote to Local: unauthorized access
            features = [
                random.uniform(100, 500),    # longer duration
                random.uniform(500, 2000),   # src_bytes
                random.uniform(500, 2000),   # dst_bytes
                0.0,                         # land
                0.0,                         # wrong_fragment
                0.0,                         # urgent
                random.uniform(1, 5),        # hot
                random.uniform(1, 10),       # failed logins!
                0.0,                         # not logged_in
                0.0,                         # num_compromised
            ]
        else:  # u2r
            # User to Root: privilege escalation
            features = [
                random.uniform(50, 200),     # medium duration
                random.uniform(200, 1000),   # src_bytes
                random.uniform(200, 1000),   # dst_bytes
                0.0,                         # land
                0.0,                         # wrong_fragment
                0.0,                         # urgent
                random.uniform(3, 10),       # hot
                0.0,                         # num_failed_logins
                1.0,                         # logged_in
                random.uniform(1, 5),        # compromised!
            ]
        
        X.append(features[:n_features])
        y.append(1)
    
    # Shuffle data
    combined = list(zip(X, y))
    random.shuffle(combined)
    X, y = zip(*combined)
    
    return list(X), list(y)


def normalize_features(
    X: List[List[float]], 
    mins: List[float] = None, 
    maxs: List[float] = None
) -> Tuple[List[List[float]], List[float], List[float]]:
    """
    Normalize features using min-max scaling.
    
    Args:
        X: List of feature vectors
        mins: Pre-computed minimum values (from training data)
        maxs: Pre-computed maximum values (from training data)
        
    Returns:
        Tuple of (normalized_features, mins, maxs) for reuse with test data
    """
    if not X:
        return X, [], []
    
    n_features = len(X[0])
    
    # Compute min and max for each feature if not provided
    if mins is None or maxs is None:
        mins = [float("inf")] * n_features
        maxs = [float("-inf")] * n_features
        
        for sample in X:
            for i, val in enumerate(sample):
                mins[i] = min(mins[i], val)
                maxs[i] = max(maxs[i], val)
    
    # Normalize using the provided or computed min/max values
    X_normalized = [
        [
            (val - mins[i]) / (maxs[i] - mins[i]) if maxs[i] > mins[i] else 0.0
            for i, val in enumerate(sample)
        ]
        for sample in X
    ]
    
    return X_normalized, mins, maxs


def compute_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
    """
    Compute classification metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        
    Returns:
        Dictionary with accuracy, precision, recall, and f1
    """
    # Single pass computation for better performance
    tp = tn = fp = fn = 0
    for t, p in zip(y_true, y_pred):
        if t == 1 and p == 1:
            tp += 1
        elif t == 0 and p == 0:
            tn += 1
        elif t == 0 and p == 1:
            fp += 1
        else:  # t == 1 and p == 0
            fn += 1
    
    accuracy = (tp + tn) / len(y_true) if y_true else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def simple_quantum_classifier(
    X_train: List[List[float]],
    y_train: List[int],
    X_test: List[List[float]],
    k_neighbors: int = 3
) -> List[int]:
    """
    Simple quantum-inspired classifier using kernel distances.
    
    Uses quantum kernel estimation to compute similarities and
    classifies based on k-nearest neighbors in the quantum feature space.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        k_neighbors: Number of neighbors for classification
        
    Returns:
        Predicted labels for test samples
    """
    from quantum import QuantumFeatureMap
    
    predictions = []
    
    # Handle edge case of empty training data
    if not X_train:
        return [0] * len(X_test)
    
    # Clamp k_neighbors to training set size
    effective_k = min(k_neighbors, len(X_train))
    
    # Create feature map once and reuse for better performance
    feature_map = QuantumFeatureMap(feature_dimension=10, reps=2)
    
    # Pre-compute encoded training samples for efficiency
    encoded_train = [feature_map.encode(x) for x in X_train]
    
    for x_test in X_test:
        # Encode test sample once
        encoded_test = feature_map.encode(x_test)
        
        # Compute kernel similarities to all training samples
        similarities = []
        for i, encoded_train_sample in enumerate(encoded_train):
            # Compute fidelity (inner product magnitude squared)
            inner_product = sum(
                s1.conjugate() * s2 
                for s1, s2 in zip(encoded_test, encoded_train_sample)
            )
            kernel_val = abs(inner_product) ** 2
            similarities.append((kernel_val, y_train[i]))
        
        # Sort by similarity (descending) using only kernel value and take k nearest
        similarities.sort(key=lambda item: item[0], reverse=True)
        k_nearest = similarities[:effective_k]
        
        # Majority vote based on actual neighbor count
        votes = sum(label for _, label in k_nearest)
        prediction = 1 if votes > len(k_nearest) / 2 else 0
        predictions.append(prediction)
    
    return predictions


def main():
    """Run the quantum threat detection demo."""
    print("=" * 60)
    print("Quantum Threat Detection System Demo")
    print("=" * 60)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate synthetic data
    print("\n[1] Generating synthetic network traffic data...")
    X_train, y_train = generate_sample_data(n_samples=50, attack_ratio=0.3)
    X_test, y_test = generate_sample_data(n_samples=20, attack_ratio=0.3)
    
    print(f"    Training samples: {len(X_train)}")
    print(f"    Test samples: {len(X_test)}")
    print(f"    Features: {FEATURE_NAMES[:len(X_train[0])]}")
    
    # Normalize features (compute stats from training, apply to both)
    print("\n[2] Normalizing features...")
    X_train_norm, mins, maxs = normalize_features(X_train)
    X_test_norm, _, _ = normalize_features(X_test, mins, maxs)
    
    # Train and evaluate classifier
    print("\n[3] Running quantum-inspired classification...")
    y_pred = simple_quantum_classifier(X_train_norm, y_train, X_test_norm, k_neighbors=3)
    
    # Compute metrics
    print("\n[4] Computing evaluation metrics...")
    metrics = compute_metrics(y_test, y_pred)
    
    print("\n" + "=" * 60)
    print("Results")
    print("=" * 60)
    print(f"    Accuracy:  {metrics['accuracy']:.2%}")
    print(f"    Precision: {metrics['precision']:.2%}")
    print(f"    Recall:    {metrics['recall']:.2%}")
    print(f"    F1-Score:  {metrics['f1']:.2%}")
    
    # Show some example predictions
    print("\n" + "=" * 60)
    print("Sample Predictions")
    print("=" * 60)
    for i in range(min(5, len(y_test))):
        true_label = "ATTACK" if y_test[i] == 1 else "NORMAL"
        pred_label = "ATTACK" if y_pred[i] == 1 else "NORMAL"
        status = "✓" if y_test[i] == y_pred[i] else "✗"
        print(f"    Sample {i+1}: True={true_label:6s}, Predicted={pred_label:6s} {status}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    
    return metrics


if __name__ == "__main__":
    main()
