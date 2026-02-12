# Copilot instructions for Evez666

## Project overview
- This is a small, single-module Python demo of a “quantum-inspired” threat detection system.
- Core logic lives in [quantum.py](../quantum.py) (feature map encoding, kernel estimation, and fingerprinting).
- Demo pipeline lives in [demo.py](../demo.py) (synthetic data generation, normalization, k-NN on kernel similarities, metrics).
- [run_all.py](../run_all.py) is a thin entrypoint that runs the demo and shows exported helpers fr⁷om `quantum.__all__`.

## How to run
- Python 3.8+ only, standard library only. No install required.
- Run the demo directly: `python demo.py`.
- Run the wrapper script: `python run_all.py`.

## Key patterns and conventions
- `quantum.py` defines the public surface in `__all__` and exports helpers like `quantum_kernel_estimation()` and `compute_fingerprint()`.
- The quantum feature map is a *classical simulation* capped at 10 qubits (`MAX_SIMULATION_QUBITS`), and this limit is intentional for performance.
- Demo data uses the first 10 NSL-KDD-style numeric features (`FEATURE_NAMES` in [demo.py](../demo.py)).
- Feature normalization is min-max scaling with train stats reused on test data (`normalize_features()` in [demo.py](../demo.py)).
- The “quantum classifier” is a simple k-NN on kernel similarity, not a trained model (`simple_quantum_classifier()` in [demo.py](../demo.py)).
- Fingerprinting uses supported secure hashes only (`SUPPORTED_ALGORITHMS` in [quantum.py](../quantum.py)); MD5 is intentionally excluded.

## Dependencies and integration points
- No external dependencies are required (see [requirements.txt](../requirements.txt)).
- Optional libraries (qiskit, pandas, numpy, scikit-learn, matplotlib) are listed as comments only; do not assume they exist.

## When editing or extending
- Keep changes small and consistent with the standard-library-only design.
- If you add new public helpers in [quantum.py](../quantum.py), update `__all__`.
- Prefer adding new demo behavior in [demo.py](../demo.py) rather than complicating the core module.
