#!/usr/bin/env python3
"""
Hazard Formula Implementations
Access Level: Tier 3 - Quantum Developer ($100/month)

This module contains the complete hazard formula implementations for the
Evez666 cognitive engine. These formulas are used for threat assessment,
risk calculation, and quantum state evaluation.

References: EVEZ-Hazard-Formulas.pdf
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class HazardMetrics:
    """Container for hazard calculation results"""
    primary_hazard: float
    quantum_hazard: float
    composite_risk: float
    threat_level: str
    confidence: float


class HazardFormulaEngine:
    """
    Core engine for calculating various hazard metrics in the cognitive system.
    
    The hazard formulas combine classical threat detection with quantum-inspired
    feature analysis to provide comprehensive risk assessment.
    """
    
    def __init__(self, threshold_params: Optional[Dict] = None):
        """
        Initialize the hazard formula engine.
        
        Args:
            threshold_params: Custom threshold parameters for risk classification
        """
        self.thresholds = threshold_params or {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.85,
            'critical': 0.95
        }
        
        # Quantum entanglement factors
        self.entanglement_weights = {
            'temporal': 0.25,
            'spatial': 0.25,
            'causal': 0.30,
            'contextual': 0.20
        }
    
    def calculate_primary_hazard(self, 
                                 threat_vector: np.ndarray,
                                 baseline: np.ndarray) -> float:
        """
        Calculate primary hazard score using Euclidean distance.
        
        Formula: H₁ = ||V_threat - V_baseline|| / ||V_baseline||
        
        Args:
            threat_vector: Current threat feature vector
            baseline: Baseline normal behavior vector
            
        Returns:
            Normalized hazard score [0, 1]
        """
        diff = threat_vector - baseline
        distance = np.linalg.norm(diff)
        baseline_norm = np.linalg.norm(baseline)
        
        if baseline_norm < 1e-10:
            # Zero baseline indicates misconfiguration or invalid data
            import warnings
            warnings.warn(
                "Baseline vector has zero norm. This may indicate invalid "
                "baseline data. Returning 0.0 hazard score.",
                RuntimeWarning
            )
            return 0.0  # Return zero as we can't calculate meaningful hazard
        
        hazard = distance / baseline_norm
        return min(hazard, 1.0)  # Cap at 1.0
    
    def calculate_quantum_hazard(self,
                                state_vector: np.ndarray,
                                entanglement_matrix: np.ndarray) -> float:
        """
        Calculate quantum hazard using entanglement entropy.
        
        Formula: H_q = -Σ(p_i * log(p_i)) * E_factor
        where E_factor is derived from entanglement matrix
        
        Args:
            state_vector: Quantum state representation
            entanglement_matrix: Matrix of entanglement coefficients
            
        Returns:
            Quantum hazard score [0, 1]
        """
        # Normalize state vector to probability distribution
        probabilities = np.abs(state_vector) ** 2
        probabilities = probabilities / np.sum(probabilities)
        
        # Calculate Shannon entropy
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * np.log2(p)
        
        # Calculate entanglement factor from matrix
        eigenvalues = np.linalg.eigvals(entanglement_matrix)
        entanglement_factor = np.sum(np.abs(eigenvalues)) / len(eigenvalues)
        
        # Combine entropy and entanglement
        max_entropy = np.log2(len(probabilities))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        quantum_hazard = normalized_entropy * entanglement_factor
        return min(quantum_hazard, 1.0)
    
    def calculate_temporal_hazard(self,
                                  time_series: List[float],
                                  window_size: int = 10) -> float:
        """
        Calculate temporal hazard based on time-series anomalies.
        
        Formula: H_t = σ(Δv) / μ(v) * trend_factor
        
        Args:
            time_series: Time-series data points
            window_size: Size of moving window
            
        Returns:
            Temporal hazard score [0, 1]
        """
        if len(time_series) < window_size:
            return 0.0
        
        # Calculate velocity (first derivative)
        velocities = np.diff(time_series)
        
        # Get recent window
        recent_velocities = velocities[-window_size:]
        
        # Calculate statistics
        mean_velocity = np.mean(recent_velocities)
        std_velocity = np.std(recent_velocities)
        
        if abs(mean_velocity) < 1e-6:
            return 0.0
        
        # Detect acceleration (second derivative)
        accelerations = np.diff(velocities)
        trend_factor = np.abs(np.mean(accelerations[-window_size:]))
        
        # Combine volatility and trend
        hazard = (std_velocity / abs(mean_velocity)) * (1 + trend_factor)
        return min(hazard, 1.0)
    
    def calculate_composite_risk(self,
                                metrics: Dict[str, float],
                                weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate composite risk score from multiple hazard metrics.
        
        Formula: R_composite = Σ(w_i * H_i) + interaction_term
        
        Args:
            metrics: Dictionary of individual hazard metrics
            weights: Custom weights for each metric (optional)
            
        Returns:
            Composite risk score [0, 1]
        """
        if weights is None:
            weights = {k: 1.0 / len(metrics) for k in metrics.keys()}
        
        # Calculate weighted sum
        composite = sum(weights.get(k, 0) * v for k, v in metrics.items())
        
        # Add interaction term (non-linear effects)
        metric_values = list(metrics.values())
        if len(metric_values) >= 2:
            interaction = np.std(metric_values) * np.mean(metric_values)
            composite += interaction * 0.1  # Small interaction weight
        
        return min(composite, 1.0)
    
    def calculate_ekf_hazard(self,
                            predicted: np.ndarray,
                            observed: np.ndarray,
                            covariance: np.ndarray) -> float:
        """
        Calculate hazard using Extended Kalman Filter residuals.
        
        Formula: H_ekf = (y - ŷ)ᵀ * P⁻¹ * (y - ŷ)
        
        Args:
            predicted: Predicted state from EKF
            observed: Observed measurements
            covariance: Error covariance matrix
            
        Returns:
            EKF-based hazard score [0, 1]
        """
        # Calculate innovation (residual)
        innovation = observed - predicted
        
        # Mahalanobis distance using covariance
        try:
            inv_covariance = np.linalg.inv(covariance)
            mahalanobis = np.sqrt(
                innovation.T @ inv_covariance @ innovation
            )
        except np.linalg.LinAlgError:
            # If covariance is singular, use Euclidean distance
            mahalanobis = np.linalg.norm(innovation)
        
        # Normalize to [0, 1] using sigmoid
        normalized = 1 / (1 + np.exp(-mahalanobis + 3))
        return normalized
    
    def assess_threat_level(self, composite_risk: float) -> str:
        """
        Classify threat level based on composite risk score.
        
        Args:
            composite_risk: Composite risk score [0, 1]
            
        Returns:
            Threat level classification string
        """
        if composite_risk >= self.thresholds['critical']:
            return 'CRITICAL'
        elif composite_risk >= self.thresholds['high']:
            return 'HIGH'
        elif composite_risk >= self.thresholds['medium']:
            return 'MEDIUM'
        elif composite_risk >= self.thresholds['low']:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def calculate_confidence(self,
                           hazard_scores: List[float],
                           variance: float) -> float:
        """
        Calculate confidence in hazard assessment.
        
        Formula: C = (1 - σ²) * consistency_factor
        
        Args:
            hazard_scores: List of individual hazard scores
            variance: Variance in measurements
            
        Returns:
            Confidence score [0, 1]
        """
        if len(hazard_scores) == 0:
            return 0.0
        
        # Calculate consistency (how close scores are to each other)
        score_std = np.std(hazard_scores)
        consistency = 1 / (1 + score_std)
        
        # Factor in measurement variance
        variance_factor = 1 / (1 + variance)
        
        confidence = consistency * variance_factor
        return confidence
    
    def full_hazard_analysis(self,
                           threat_vector: np.ndarray,
                           baseline: np.ndarray,
                           state_vector: np.ndarray,
                           entanglement_matrix: np.ndarray,
                           time_series: List[float]) -> HazardMetrics:
        """
        Perform complete hazard analysis using all available metrics.
        
        Args:
            threat_vector: Current threat feature vector
            baseline: Baseline normal behavior vector
            state_vector: Quantum state representation
            entanglement_matrix: Entanglement coefficients
            time_series: Historical time-series data
            
        Returns:
            HazardMetrics object with complete analysis
        """
        # Calculate individual hazards
        primary = self.calculate_primary_hazard(threat_vector, baseline)
        quantum = self.calculate_quantum_hazard(state_vector, entanglement_matrix)
        temporal = self.calculate_temporal_hazard(time_series)
        
        # Calculate composite risk
        metrics = {
            'primary': primary,
            'quantum': quantum,
            'temporal': temporal
        }
        composite = self.calculate_composite_risk(metrics, self.entanglement_weights)
        
        # Assess threat level
        threat_level = self.assess_threat_level(composite)
        
        # Calculate confidence
        confidence = self.calculate_confidence(
            [primary, quantum, temporal],
            np.var([primary, quantum, temporal])
        )
        
        return HazardMetrics(
            primary_hazard=primary,
            quantum_hazard=quantum,
            composite_risk=composite,
            threat_level=threat_level,
            confidence=confidence
        )


# Example usage and testing
if __name__ == '__main__':
    # Initialize engine
    engine = HazardFormulaEngine()
    
    # Create sample data
    threat_vector = np.array([0.8, 0.6, 0.9, 0.7])
    baseline = np.array([0.5, 0.5, 0.5, 0.5])
    
    state_vector = np.array([0.5, 0.5, 0.5, 0.5])
    entanglement_matrix = np.random.rand(4, 4)
    
    time_series = [0.5, 0.52, 0.51, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
    
    # Perform analysis
    results = engine.full_hazard_analysis(
        threat_vector,
        baseline,
        state_vector,
        entanglement_matrix,
        time_series
    )
    
    print(f"Hazard Analysis Results:")
    print(f"  Primary Hazard: {results.primary_hazard:.3f}")
    print(f"  Quantum Hazard: {results.quantum_hazard:.3f}")
    print(f"  Composite Risk: {results.composite_risk:.3f}")
    print(f"  Threat Level: {results.threat_level}")
    print(f"  Confidence: {results.confidence:.3f}")
