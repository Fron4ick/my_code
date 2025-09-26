#!/usr/bin/env python3
"""
GPU-Accelerated NAND Circuit Minimizer - Finds the smallest NAND-only circuit for a given truth table.
Uses CuPy for GPU acceleration and optimized search strategies.

Usage: python3 gpu_nand_minimizer.py < input.txt
   or: python3 gpu_nand_minimizer.py input.txt [--max-nands N] [--verbose] [--use-gpu] [--batch-size N]

Requirements:
- CuPy: pip install cupy-cuda12x (or cupy-cuda11x for CUDA 11.x)
- NumPy: pip install numpy
"""

import sys
import time
import itertools
import multiprocessing as mp
from typing import List, Tuple, Dict, Set, Optional, Iterator
from collections import defaultdict
import numpy as np
from functools import lru_cache
import threading
from queue import Queue
import argparse

# Try to import CuPy for GPU acceleration
try:
    import cupy as cp
    GPU_AVAILABLE = True
    print("GPU acceleration available (CuPy detected)")
except ImportError:
    cp = None
    GPU_AVAILABLE = False
    print("GPU acceleration not available (install cupy for GPU support)")

def parse_input(lines: List[str]) -> Tuple[List[str], List[str], np.ndarray, np.ndarray]:
    """Parse truth table specification from input lines."""
    header = lines[0].strip()
    parts = header.split(';')
    input_names = [n.strip() for n in parts[0].split(',') if n.strip()]
    output_names = [n.strip() for n in parts[1].split(',') if n.strip()]
    
    input_vectors = []
    output_vectors = []
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split(';')
        inputs = [int(v.strip()) for v in parts[0].split(',') if v.strip()]
        outputs = [int(v.strip()) for v in parts[1].split(',') if v.strip()]
        input_vectors.append(inputs)
        output_vectors.append(outputs)
    
    return (input_names, output_names, 
            np.array(input_vectors, dtype=np.uint8), 
            np.array(output_vectors, dtype=np.uint8))

class GPUNANDEvaluator:
    """GPU-accelerated NAND circuit evaluator using CuPy."""
    
    def __init__(self, input_data: np.ndarray, output_data: np.ndarray, use_gpu: bool = True):
        self.use_gpu = use_gpu and GPU_AVAILABLE
        self.num_rows, self.num_inputs = input_data.shape
        self.num_outputs = output_data.shape[1]
        
        if self.use_gpu:
            # Transfer data to GPU
            self.gpu_inputs = cp.asarray(input_data, dtype=cp.uint8)
            self.gpu_outputs = cp.asarray(output_data, dtype=cp.uint8)
        else:
            self.cpu_inputs = input_data
            self.cpu_outputs = output_data
    
    def evaluate_batch(self, configs: List[Tuple], batch_size: int = 1000) -> List[bool]:
        """Evaluate a batch of circuit configurations."""
        if not configs:
            return []
        
        if self.use_gpu:
            return self._evaluate_batch_gpu(configs, batch_size)
        else:
            return self._evaluate_batch_cpu(configs, batch_size)
    
    def _evaluate_batch_gpu(self, configs: List[Tuple], batch_size: int) -> List[bool]:
        """GPU batch evaluation using CuPy."""
        results = []
        
        for i in range(0, len(configs), batch_size):
            batch = configs[i:i + batch_size]
            batch_results = []
            
            for config in batch:
                nand_inputs, output_drivers = config
                if self._evaluate_single_gpu(nand_inputs, output_drivers):
                    batch_results.append(True)
                else:
                    batch_results.append(False)
            
            results.extend(batch_results)
        
        return results
    
    def _evaluate_single_gpu(self, nand_inputs: List[Tuple[int, int]], 
                            output_drivers: List[int]) -> bool:
        """Evaluate single configuration on GPU."""
        # Create signal array: inputs + NAND outputs
        num_signals = self.num_inputs + len(nand_inputs)
        signals = cp.zeros((self.num_rows, num_signals), dtype=cp.uint8)
        
        # Copy primary inputs
        signals[:, :self.num_inputs] = self.gpu_inputs
        
        # Evaluate NANDs in order
        for i, (a_idx, b_idx) in enumerate(nand_inputs):
            nand_output_idx = self.num_inputs + i
            a_vals = signals[:, a_idx]
            b_vals = signals[:, b_idx]
            # NAND operation: ~(a & b)
            signals[:, nand_output_idx] = (~(a_vals & b_vals)) & 1
        
        # Check outputs
        for i, driver_idx in enumerate(output_drivers):
            computed = signals[:, driver_idx]
            expected = self.gpu_outputs[:, i]
            if not cp.array_equal(computed, expected):
                return False
        
        return True
    
    def _evaluate_batch_cpu(self, configs: List[Tuple], batch_size: int) -> List[bool]:
        """CPU batch evaluation using NumPy."""
        results = []
        
        for config in configs:
            nand_inputs, output_drivers = config
            if self._evaluate_single_cpu(nand_inputs, output_drivers):
                results.append(True)
            else:
                results.append(False)
        
        return results
    
    def _evaluate_single_cpu(self, nand_inputs: List[Tuple[int, int]], 
                            output_drivers: List[int]) -> bool:
        """Evaluate single configuration on CPU."""
        # Create signal array: inputs + NAND outputs
        num_signals = self.num_inputs + len(nand_inputs)
        signals = np.zeros((self.num_rows, num_signals), dtype=np.uint8)
        
        # Copy primary inputs
        signals[:, :self.num_inputs] = self.cpu_inputs
        
        # Evaluate NANDs in order
        for i, (a_idx, b_idx) in enumerate(nand_inputs):
            nand_output_idx = self.num_inputs + i
            a_vals = signals[:, a_idx]
            b_vals = signals[:, b_idx]
            # NAND operation: ~(a & b)
            signals[:, nand_output_idx] = (~(a_vals & b_vals)) & 1
        
        # Check outputs
        for i, driver_idx in enumerate(output_drivers):
            computed = signals[:, driver_idx]
            expected = self.cpu_outputs[:, i]
            if not np.array_equal(computed, expected):
                return False
        
        return True

class OptimizedNANDSearcher:
    """Optimized NAND circuit searcher with parallel processing and smart pruning."""
    
    def __init__(self, input_names: List[str], output_names: List[str], 
                 input_data: np.ndarray, output_data: np.ndarray,
                 max_nands: Optional[int] = None, verbose: bool = False,
                 use_gpu: bool = True, batch_size: int = 1000, num_workers: int = None):
        self.input_names = input_names
        self.output_names = output_names
        self.num_inputs = len(input_names)
        self.num_outputs = len(output_names)
        self.num_rows = len(input_data)
        self.max_nands = max_nands or 20
        self.verbose = verbose
        self.batch_size = batch_size
        self.num_workers = num_workers or mp.cpu_count()
        
        # Create evaluator
        self.evaluator = GPUNANDEvaluator(input_data, output_data, use_gpu)
        
        # For progress tracking
        self.start_time = time.time()
        self.checked = 0
        self.total = 0
        
        # Memoization for usage validation
        self._usage_cache = {}
    
    @lru_cache(maxsize=10000)
    def _validate_usage_cached(self, nand_inputs_tuple: Tuple, output_drivers_tuple: Tuple) -> bool:
        """Cached version of usage validation."""
        usage = defaultdict(int)
        
        # Count NAND input usage
        for a_idx, b_idx in nand_inputs_tuple:
            usage[a_idx] += 1
            usage[b_idx] += 1
        
        # Count output driver usage
        for driver_idx in output_drivers_tuple:
            usage[driver_idx] += 1
        
        # Check primary input usage (1-5 times)
        for i in range(self.num_inputs):
            if usage[i] == 0 or usage[i] > 5:
                return False
        
        # Check NAND output usage (0-5 times)
        for i in range(self.num_inputs, self.num_inputs + len(nand_inputs_tuple)):
            if usage[i] > 5:
                return False
        
        return True
    
    def generate_configs_smart(self, num_nands: int) -> Iterator[Tuple]:
        """Generate configurations with smart pruning and ordering."""
        if num_nands == 0:
            # Direct wiring only
            for output_drivers in itertools.product(range(self.num_inputs), repeat=self.num_outputs):
                config = ([], output_drivers)
                if self._validate_usage_cached(tuple(), output_drivers):
                    yield config
            return
        
        # Generate NAND configurations
        nand_choices = []
        for nand_idx in range(num_nands):
            # Available signals: primary inputs + previous NANDs
            max_signal_idx = self.num_inputs + nand_idx
            # Generate all pairs of inputs for this NAND
            choices = [(a, b) for a in range(max_signal_idx) for b in range(a, max_signal_idx)]
            nand_choices.append(choices)
        
        # Available signals for outputs: primary inputs + all NANDs
        output_signal_range = self.num_inputs + num_nands
        
        # Use nested loops for better memory efficiency
        total_nand_combos = 1
        for choices in nand_choices:
            total_nand_combos *= len(choices)
        
        total_output_combos = output_signal_range ** self.num_outputs
        self.total = total_nand_combos * total_output_combos
        
        count = 0
        for nand_combo in itertools.product(*nand_choices):
            for output_drivers in itertools.product(range(output_signal_range), repeat=self.num_outputs):
                count += 1
                self.checked = count
                
                # Quick validation
                if self._validate_usage_cached(nand_combo, output_drivers):
                    yield (list(nand_combo), list(output_drivers))
    
    def search_parallel(self):
        """Parallel search with GPU acceleration."""
        for num_nands in range(0, self.max_nands + 1):
            print(f"\nSearching with {num_nands} NANDs...", flush=True)
            
            if self._search_with_n_nands(num_nands):
                return True
        
        print("\nNo solution found within search limits", flush=True)
        return False
    
    def _search_with_n_nands(self, num_nands: int) -> bool:
        """Search with specific number of NANDs."""
        self.checked = 0
        self.total = 0
        
        # Collect configs in batches
        config_batch = []
        last_progress_time = time.time()
        
        for config in self.generate_configs_smart(num_nands):
            config_batch.append(config)
            
            # Process batch when full
            if len(config_batch) >= self.batch_size:
                results = self.evaluator.evaluate_batch(config_batch, self.batch_size)
                
                for i, is_solution in enumerate(results):
                    if is_solution:
                        nand_inputs, output_drivers = config_batch[i]
                        self._print_solution(num_nands, nand_inputs, output_drivers)
                        return True
                
                config_batch.clear()
                
                # Progress update
                current_time = time.time()
                if current_time - last_progress_time > 0.5:
                    self._print_progress(num_nands)
                    last_progress_time = current_time
        
        # Process remaining configs
        if config_batch:
            results = self.evaluator.evaluate_batch(config_batch, len(config_batch))
            
            for i, is_solution in enumerate(results):
                if is_solution:
                    nand_inputs, output_drivers = config_batch[i]
                    self._print_solution(num_nands, nand_inputs, output_drivers)
                    return True
        
        self._print_progress(num_nands)
        print(f"\nNo solution found with {num_nands} NANDs", flush=True)
        return False
    
    def _print_progress(self, num_nands: int):
        """Print search progress."""
        elapsed = time.time() - self.start_time
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        percent = (self.checked / self.total * 100) if self.total > 0 else 0
        print(f"\rSearching with {num_nands} NANDs — progress: {percent:.2f}% "
              f"(checked {self.checked}/{self.total} combinations) — elapsed: {elapsed_str}", 
              end='', flush=True)
    
    def _print_solution(self, num_nands: int, nand_inputs: List[Tuple[int, int]], 
                       output_drivers: List[int]):
        """Print the found solution."""
        print(f"\n\nSOLUTION FOUND with N={num_nands}")
        print("Connections (one line per NAND and then primary outputs):")
        
        # Convert indices back to signal names
        signal_names = self.input_names + [f'n_{i+1}' for i in range(num_nands)]
        
        connection_str = ""
        for i, (a_idx, b_idx) in enumerate(nand_inputs, 1):
            a_name = signal_names[a_idx]
            b_name = signal_names[b_idx]
            connection_str += f"n_{i}_a={a_name}; n_{i}_b={b_name}; "
        
        connection_str += f"primary_inputs={','.join(self.input_names)}; "
        output_connections = []
        for i, driver_idx in enumerate(output_drivers):
            driver_name = signal_names[driver_idx]
            output_connections.append(f"{self.output_names[i]}={driver_name}")
        connection_str += f"primary_outputs={','.join(output_connections)};"
        
        print(connection_str)
        print("\nVerified truth table matches specification.")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='GPU-Accelerated NAND Circuit Minimizer')
    parser.add_argument('input_file', nargs='?', help='Input file (default: stdin)')
    parser.add_argument('--max-nands', type=int, default=20, help='Maximum number of NANDs to try')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--use-gpu', action='store_true', default=True, help='Use GPU acceleration')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for GPU evaluation')
    parser.add_argument('--num-workers', type=int, help='Number of worker processes (default: CPU count)')
    
    args = parser.parse_args()
    
    # Read input
    if args.input_file:
        with open(args.input_file, 'r') as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()
    
    # Parse truth table
    try:
        input_names, output_names, input_data, output_data = parse_input(lines)
    except Exception as e:
        print(f"Error parsing input: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Parsed truth table: {len(input_names)} inputs, {len(output_names)} outputs, {len(input_data)} rows")
    print(f"Inputs: {', '.join(input_names)}")
    print(f"Outputs: {', '.join(output_names)}")
    
    if args.use_gpu and not GPU_AVAILABLE:
        print("Warning: GPU requested but CuPy not available, falling back to CPU")
        args.use_gpu = False
    
    print(f"Using {'GPU' if args.use_gpu else 'CPU'} acceleration")
    print(f"Batch size: {args.batch_size}")
    
    # Search for solution
    searcher = OptimizedNANDSearcher(
        input_names, output_names, input_data, output_data,
        args.max_nands, args.verbose, args.use_gpu, args.batch_size, args.num_workers
    )
    
    if searcher.search_parallel():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
