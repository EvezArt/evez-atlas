from quantum import (
    evaluate_navigation_sequence,
    manifold_projection,
    predict_navigation_probabilities,
)


def test_manifold_projection_normalizes():
    features = [0.1, 0.2, 0.3]
    anchors = [
        [0.1, 0.2, 0.3],
        [0.9, 0.8, 0.7],
        [0.4, 0.4, 0.4],
    ]
    projection = manifold_projection(features, anchors, feature_dimension=3, reps=1)
    assert len(projection) == len(anchors)
    assert abs(sum(projection) - 1.0) < 1e-6


def test_predict_navigation_probabilities_prefers_recent_match():
    sequence = [
        [0.0, 0.0, 0.0],
        [0.2, 0.2, 0.2],
        [0.9, 0.9, 0.9],
    ]
    candidates = [
        [0.1, 0.1, 0.1],
        [0.9, 0.9, 0.9],
    ]
    probabilities = predict_navigation_probabilities(
        sequence,
        candidates,
        decay=0.5,
        feature_dimension=3,
        reps=1,
    )
    assert len(probabilities) == len(candidates)
    assert probabilities[1] > probabilities[0]


def test_evaluate_navigation_sequence_ranks_candidates():
    sequence = [
        [0.3, 0.3, 0.3],
        [0.7, 0.7, 0.7],
    ]
    candidates = [
        [0.2, 0.2, 0.2],
        [0.7, 0.7, 0.7],
    ]
    anchors = [
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
    ]
    evaluation = evaluate_navigation_sequence(
        sequence,
        candidates,
        anchors,
        decay=0.8,
        feature_dimension=3,
        reps=1,
    )
    assert evaluation["ranked_candidates"][0] == 1
