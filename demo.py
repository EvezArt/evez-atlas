"""
Quantum Threat Detection System - Demo Module

This module provides a demonstration of the quantum threat detection
system using simulated network intrusion data.
"""

import logging
import random
from typing import Any, Dict, List, Tuple

from quantum import (
    evaluate_navigation_sequence,
    predict_navigation_probabilities,
    recursive_navigation_evaluation,
)

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

ENVIRONMENTAL_TASKS = [
    "terrain_scan",
    "atmospheric_drift",
    "thermal_gradient",
    "signal_refraction",
    "magnetic_flux",
    "subsurface_echo",
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
    feature_vectors = []
    class_labels = []
    
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
        feature_vectors.append(features[:n_features])
        class_labels.append(0)
    
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
        
        feature_vectors.append(features[:n_features])
        class_labels.append(1)
    
    # Shuffle data
    combined = list(zip(feature_vectors, class_labels))
    random.shuffle(combined)
    feature_vectors, class_labels = zip(*combined)
    
    return list(feature_vectors), list(class_labels)


def normalize_features(
    feature_vectors: List[List[float]], 
    mins: List[float] = None, 
    maxs: List[float] = None
) -> Tuple[List[List[float]], List[float], List[float]]:
    """
    Normalize features using min-max scaling.
    
    Args:
        feature_vectors: List of feature vectors
        mins: Pre-computed minimum values (from training data)
        maxs: Pre-computed maximum values (from training data)
        
    Returns:
        Tuple of (normalized_features, mins, maxs) for reuse with test data
    """
    if not feature_vectors:
        return feature_vectors, [], []
    
    n_features = len(feature_vectors[0])
    
    # Compute min and max for each feature if not provided
    if mins is None or maxs is None:
        mins = [float("inf")] * n_features
        maxs = [float("-inf")] * n_features
        
        for sample in feature_vectors:
            for feature_index, value in enumerate(sample):
                mins[feature_index] = min(mins[feature_index], value)
                maxs[feature_index] = max(maxs[feature_index], value)
    
    # Normalize using the provided or computed min/max values
    normalized_features = []
    for sample in feature_vectors:
        normalized = []
        for feature_index, value in enumerate(sample):
            range_val = maxs[feature_index] - mins[feature_index]
            if range_val > 0:
                normalized.append((value - mins[feature_index]) / range_val)
            else:
                normalized.append(0.0)
        normalized_features.append(normalized)
    
    return normalized_features, mins, maxs


def compute_metrics(true_labels: List[int], predicted_labels: List[int]) -> Dict[str, float]:
    """
    Compute classification metrics.
    
    Args:
        true_labels: True labels
        predicted_labels: Predicted labels
        
    Returns:
        Dictionary with accuracy, precision, recall, and f1
    """
    tp = sum(1 for true_label, predicted_label in zip(true_labels, predicted_labels) if true_label == 1 and predicted_label == 1)
    tn = sum(1 for true_label, predicted_label in zip(true_labels, predicted_labels) if true_label == 0 and predicted_label == 0)
    fp = sum(1 for true_label, predicted_label in zip(true_labels, predicted_labels) if true_label == 0 and predicted_label == 1)
    fn = sum(1 for true_label, predicted_label in zip(true_labels, predicted_labels) if true_label == 1 and predicted_label == 0)
    
    accuracy = (tp + tn) / len(true_labels) if true_labels else 0.0
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
    training_features: List[List[float]],
    training_labels: List[int],
    test_features: List[List[float]],
    k_neighbors: int = 3
) -> List[int]:
    """
    Simple quantum-inspired classifier using kernel distances.
    
    Uses quantum kernel estimation to compute similarities and
    classifies based on k-nearest neighbors in the quantum feature space.
    
    Args:
        training_features: Training features
        training_labels: Training labels
        test_features: Test features
        k_neighbors: Number of neighbors for classification
        
    Returns:
        Predicted labels for test samples
    """
    from quantum import quantum_kernel_estimation
    
    predictions = []
    
    # Handle edge case of empty training data
    if not training_features:
        return [0] * len(test_features)
    
    # Clamp k_neighbors to training set size
    effective_k = min(k_neighbors, len(training_features))
    
    for test_sample in test_features:
        # Compute kernel similarities to all training samples
        similarities = []
        for train_index, train_sample in enumerate(training_features):
            kernel_val = quantum_kernel_estimation(test_sample, train_sample)
            similarities.append((kernel_val, training_labels[train_index]))
        
        # Sort by similarity (descending) using only kernel value and take k nearest
        similarities.sort(key=lambda item: item[0], reverse=True)
        k_nearest = similarities[:effective_k]
        
        # Majority vote based on actual neighbor count
        votes = sum(label for _, label in k_nearest)
        prediction = 1 if votes > len(k_nearest) / 2 else 0
        predictions.append(prediction)
    
    return predictions


def run_navigation_demo() -> Dict[str, List[float]]:
    """Run a navigation evaluation demo using quantum-inspired sequencing."""
    sequence = [
        [0.1, 0.2, 0.15],
        [0.2, 0.4, 0.3],
        [0.8, 0.7, 0.9],
    ]
    candidates = [
        [0.2, 0.3, 0.2],
        [0.9, 0.8, 0.95],
        [0.4, 0.5, 0.45],
    ]
    anchors = [
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
        [0.5, 0.5, 0.5],
    ]
    evaluation = evaluate_navigation_sequence(
        sequence,
        candidates,
        anchors,
        decay=0.8,
        feature_dimension=3,
        reps=1,
    )
    probabilities = predict_navigation_probabilities(
        sequence,
        candidates,
        decay=0.8,
        feature_dimension=3,
        reps=1,
    )
    return {
        "projection": evaluation["manifold_projection"],
        "candidate_probabilities": probabilities,
    }


def _make_sensor_vector(
    random_generator: random.Random,
    baseline: float,
    jitter: float,
    feature_dimension: int,
) -> List[float]:
    return [
        max(0.0, min(1.0, baseline + random_generator.uniform(-jitter, jitter)))
        for _ in range(feature_dimension)
    ]


def build_navigation_ui_state(
    seed: int = 13,
    feature_dimension: int = 10,
    steps: int = 3,
    decay: float = 0.85,
    reps: int = 2,
) -> Dict[str, Any]:
    """Build a navigation UI state snapshot for environmental sensory tasks."""
    random_generator = random.Random(seed)
    sensor_tasks = [
        {
            "name": task,
            "vector": _make_sensor_vector(
                random_generator,
                baseline=0.2 + task_index * 0.1,
                jitter=0.08,
                feature_dimension=feature_dimension,
            ),
        }
        for task_index, task in enumerate(ENVIRONMENTAL_TASKS)
    ]
    sequence = [entry["vector"] for entry in sensor_tasks[:3]]
    candidates = [
        _make_sensor_vector(random_generator, baseline=0.6, jitter=0.15, feature_dimension=feature_dimension),
        _make_sensor_vector(random_generator, baseline=0.35, jitter=0.1, feature_dimension=feature_dimension),
        _make_sensor_vector(random_generator, baseline=0.75, jitter=0.12, feature_dimension=feature_dimension),
        _make_sensor_vector(random_generator, baseline=0.5, jitter=0.2, feature_dimension=feature_dimension),
    ]
    anchors = [
        _make_sensor_vector(random_generator, baseline=0.15, jitter=0.05, feature_dimension=feature_dimension),
        _make_sensor_vector(random_generator, baseline=0.5, jitter=0.05, feature_dimension=feature_dimension),
        _make_sensor_vector(random_generator, baseline=0.85, jitter=0.05, feature_dimension=feature_dimension),
    ]
    evaluation = evaluate_navigation_sequence(
        sequence,
        candidates,
        anchors,
        decay=decay,
        feature_dimension=feature_dimension,
        reps=reps,
    )
    recursive = recursive_navigation_evaluation(
        sequence,
        candidates,
        anchors,
        steps=steps,
        decay=decay,
        feature_dimension=feature_dimension,
        reps=reps,
    )
    return {
        "sensor_tasks": sensor_tasks,
        "sequence": sequence,
        "candidates": candidates,
        "anchors": anchors,
        "evaluation": evaluation,
        "recursive": recursive,
    }


def main():
    """Run the quantum threat detection demo."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    print("=" * 60)
    print("Quantum Threat Detection System Demo")
    print("=" * 60)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate synthetic data
    print("\n[1] Generating synthetic network traffic data...")
    training_features, training_labels = generate_sample_data(n_samples=50, attack_ratio=0.3)
    test_features, test_labels = generate_sample_data(n_samples=20, attack_ratio=0.3)
    
    print(f"    Training samples: {len(training_features)}")
    print(f"    Test samples: {len(test_features)}")
    print(f"    Features: {FEATURE_NAMES[:len(training_features[0])]}")
    
    # Normalize features (compute stats from training, apply to both)
    print("\n[2] Normalizing features...")
    train_normalized, mins, maxs = normalize_features(training_features)
    test_normalized, _, _ = normalize_features(test_features, mins, maxs)
    
    # Train and evaluate classifier
    print("\n[3] Running quantum-inspired classification...")
    predicted_labels = simple_quantum_classifier(train_normalized, training_labels, test_normalized, k_neighbors=3)
    
    # Compute metrics
    print("\n[4] Computing evaluation metrics...")
    metrics = compute_metrics(test_labels, predicted_labels)
    
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
    for sample_index in range(min(5, len(test_labels))):
        true_label = "ATTACK" if test_labels[sample_index] == 1 else "NORMAL"
        pred_label = "ATTACK" if predicted_labels[sample_index] == 1 else "NORMAL"
        status = "✓" if test_labels[sample_index] == predicted_labels[sample_index] else "✗"
        print(f"    Sample {sample_index+1}: True={true_label:6s}, Predicted={pred_label:6s} {status}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("Quantum Navigation Demo")
    print("=" * 60)
    navigation_results = run_navigation_demo()
    print("    Manifold projection:", [f"{p:.2f}" for p in navigation_results["projection"]])
    print(
        "    Candidate probabilities:",
        [f"{p:.2f}" for p in navigation_results["candidate_probabilities"]],
    )
    recursive_navigation_evaluation(
        sequence=[
            [0.1, 0.2, 0.15],
            [0.2, 0.4, 0.3],
        ],
        candidates=[
            [0.2, 0.3, 0.2],
            [0.9, 0.8, 0.95],
            [0.4, 0.5, 0.45],
        ],
        anchors=[
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0],
            [0.5, 0.5, 0.5],
        ],
        steps=2,
        decay=0.8,
        feature_dimension=3,
        reps=1,
        log=True,
    )
    
    return metrics


if __name__ == "__main__":
    main()
