"""
Performance Benchmarking Suite for Negative Latency Systems
Negative Latency Implementation Blueprint - Chapter 21

Comprehensive benchmarking tools for measuring EKF performance,
latency characteristics, and system throughput.
"""

import time
import numpy as np
from typing import Dict, List, Callable, Any
import json
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_time: float
    throughput: float
    
    
class PerformanceBenchmark:
    """
    Comprehensive performance benchmarking suite
    """
    
    def __init__(self):
        self.results = []
        self.metrics = defaultdict(list)
        
    def benchmark(self, 
                 func: Callable,
                 iterations: int = 1000,
                 warmup: int = 10,
                 name: str = None) -> BenchmarkResult:
        """
        Benchmark a function
        
        Args:
            func: Function to benchmark
            iterations: Number of iterations
            warmup: Number of warmup iterations
            name: Benchmark name
            
        Returns:
            Benchmark result
        """
        if name is None:
            name = func.__name__
            
        # Warmup
        for _ in range(warmup):
            func()
        
        # Benchmark
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)
        
        # Calculate statistics
        times_array = np.array(times)
        total_time = np.sum(times_array)
        avg_time = np.mean(times_array)
        min_time = np.min(times_array)
        max_time = np.max(times_array)
        std_time = np.std(times_array)
        throughput = iterations / total_time
        
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_time=std_time,
            throughput=throughput
        )
        
        self.results.append(result)
        return result
    
    def benchmark_latency(self,
                         predict_func: Callable,
                         update_func: Callable,
                         iterations: int = 1000) -> Dict[str, float]:
        """
        Benchmark latency characteristics
        
        Args:
            predict_func: Prediction function
            update_func: Update function
            iterations: Number of iterations
            
        Returns:
            Latency metrics
        """
        predict_times = []
        update_times = []
        total_times = []
        
        for _ in range(iterations):
            # Predict latency
            start = time.perf_counter()
            predict_func()
            predict_end = time.perf_counter()
            predict_times.append(predict_end - start)
            
            # Update latency
            update_func()
            update_end = time.perf_counter()
            update_times.append(update_end - predict_end)
            
            # Total latency
            total_times.append(update_end - start)
        
        metrics = {
            'predict_mean': np.mean(predict_times) * 1000,  # ms
            'predict_std': np.std(predict_times) * 1000,
            'update_mean': np.mean(update_times) * 1000,
            'update_std': np.std(update_times) * 1000,
            'total_mean': np.mean(total_times) * 1000,
            'total_std': np.std(total_times) * 1000,
            'predict_p99': np.percentile(predict_times, 99) * 1000,
            'update_p99': np.percentile(update_times, 99) * 1000,
            'total_p99': np.percentile(total_times, 99) * 1000
        }
        
        self.metrics['latency'] = metrics
        return metrics
    
    def benchmark_throughput(self,
                           func: Callable,
                           duration: float = 10.0) -> Dict[str, float]:
        """
        Benchmark throughput over time
        
        Args:
            func: Function to benchmark
            duration: Duration in seconds
            
        Returns:
            Throughput metrics
        """
        start_time = time.perf_counter()
        count = 0
        samples = []
        
        while time.perf_counter() - start_time < duration:
            sample_start = time.perf_counter()
            func()
            count += 1
            
            # Record throughput every second
            if count % 100 == 0:
                elapsed = time.perf_counter() - start_time
                throughput = count / elapsed
                samples.append(throughput)
        
        elapsed = time.perf_counter() - start_time
        
        metrics = {
            'total_operations': count,
            'duration': elapsed,
            'avg_throughput': count / elapsed,
            'min_throughput': np.min(samples) if samples else 0,
            'max_throughput': np.max(samples) if samples else 0,
            'std_throughput': np.std(samples) if samples else 0
        }
        
        self.metrics['throughput'] = metrics
        return metrics
    
    def benchmark_memory(self,
                        func: Callable,
                        iterations: int = 100) -> Dict[str, int]:
        """
        Benchmark memory usage
        
        Args:
            func: Function to benchmark
            iterations: Number of iterations
            
        Returns:
            Memory metrics
        """
        import tracemalloc
        
        tracemalloc.start()
        
        # Baseline
        baseline = tracemalloc.get_traced_memory()[0]
        
        # Run function
        for _ in range(iterations):
            func()
        
        # Measure
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        metrics = {
            'baseline_bytes': baseline,
            'current_bytes': current,
            'peak_bytes': peak,
            'allocated_bytes': current - baseline,
            'allocated_mb': (current - baseline) / 1024 / 1024
        }
        
        self.metrics['memory'] = metrics
        return metrics
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "=" * 70)
        print("📊 PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 70)
        
        # Function benchmarks
        if self.results:
            print("\n🔧 Function Benchmarks:")
            print("-" * 70)
            for result in self.results:
                print(f"\n{result.name}:")
                print(f"  Iterations:  {result.iterations:,}")
                print(f"  Avg Time:    {result.avg_time*1000:.3f} ms")
                print(f"  Min Time:    {result.min_time*1000:.3f} ms")
                print(f"  Max Time:    {result.max_time*1000:.3f} ms")
                print(f"  Std Dev:     {result.std_time*1000:.3f} ms")
                print(f"  Throughput:  {result.throughput:,.0f} ops/sec")
        
        # Latency metrics
        if 'latency' in self.metrics:
            print("\n⏱️  Latency Metrics:")
            print("-" * 70)
            latency = self.metrics['latency']
            print(f"  Predict:  {latency['predict_mean']:.3f} ± {latency['predict_std']:.3f} ms (p99: {latency['predict_p99']:.3f} ms)")
            print(f"  Update:   {latency['update_mean']:.3f} ± {latency['update_std']:.3f} ms (p99: {latency['update_p99']:.3f} ms)")
            print(f"  Total:    {latency['total_mean']:.3f} ± {latency['total_std']:.3f} ms (p99: {latency['total_p99']:.3f} ms)")
        
        # Throughput metrics
        if 'throughput' in self.metrics:
            print("\n📈 Throughput Metrics:")
            print("-" * 70)
            tp = self.metrics['throughput']
            print(f"  Total Ops:    {tp['total_operations']:,}")
            print(f"  Duration:     {tp['duration']:.2f} sec")
            print(f"  Avg:          {tp['avg_throughput']:,.0f} ops/sec")
            print(f"  Min:          {tp['min_throughput']:,.0f} ops/sec")
            print(f"  Max:          {tp['max_throughput']:,.0f} ops/sec")
        
        # Memory metrics
        if 'memory' in self.metrics:
            print("\n💾 Memory Metrics:")
            print("-" * 70)
            mem = self.metrics['memory']
            print(f"  Baseline:     {mem['baseline_bytes']:,} bytes")
            print(f"  Current:      {mem['current_bytes']:,} bytes")
            print(f"  Peak:         {mem['peak_bytes']:,} bytes")
            print(f"  Allocated:    {mem['allocated_mb']:.2f} MB")
        
        print("\n" + "=" * 70)
    
    def export_json(self, filename: str):
        """Export results to JSON"""
        data = {
            'timestamp': time.time(),
            'results': [asdict(r) for r in self.results],
            'metrics': dict(self.metrics)
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Exported results to {filename}")


# Example usage
if __name__ == "__main__":
    from ekf_implementation import ExtendedKalmanFilter
    
    print("🚀 Starting EKF Performance Benchmark")
    
    # Initialize benchmark suite
    bench = PerformanceBenchmark()
    
    # Setup EKF
    ekf = ExtendedKalmanFilter(state_dim=4, measurement_dim=2)
    ekf.x = np.array([0, 0, 1, 1])
    
    def f(x):
        dt = 0.1
        F = np.eye(4)
        F[0, 2] = dt
        F[1, 3] = dt
        return F @ x
    
    def F_jac(x):
        dt = 0.1
        F = np.eye(4)
        F[0, 2] = dt
        F[1, 3] = dt
        return F
    
    def h(x):
        return x[:2]
    
    def H_jac(x):
        H = np.zeros((2, 4))
        H[0, 0] = 1
        H[1, 1] = 1
        return H
    
    # Benchmark predict
    bench.benchmark(
        lambda: ekf.predict(f, F_jac, 0.1),
        iterations=10000,
        name="EKF Predict"
    )
    
    # Benchmark update
    z = np.array([1.0, 1.0])
    bench.benchmark(
        lambda: ekf.update(z, h, H_jac),
        iterations=10000,
        name="EKF Update"
    )
    
    # Benchmark latency
    bench.benchmark_latency(
        lambda: ekf.predict(f, F_jac, 0.1),
        lambda: ekf.update(z, h, H_jac),
        iterations=1000
    )
    
    # Benchmark throughput
    bench.benchmark_throughput(
        lambda: (ekf.predict(f, F_jac, 0.1), ekf.update(z, h, H_jac)),
        duration=5.0
    )
    
    # Print summary
    bench.print_summary()
    
    # Export results
    bench.export_json('ekf_benchmark_results.json')
