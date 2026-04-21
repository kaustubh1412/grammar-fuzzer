# Automated Grammar-Based Fuzzer for SIMD Intrinsics

A testing framework that uses context-free grammar constraints to autonomously generate syntactically valid CUDA code, designed to stress-test compiler optimizations and Instruction Set Architecture (ISA) execution.

## Core Features
* **Grammar-Based Fuzzing:** Autonomously generates complex sequences of CUDA SIMD intrinsics (e.g., PTX vector operations, warp shuffles).
* **Automated Injection:** Injects generated test cases into standardized execution harnesses.
* **Memory Safety Validation:** Seamlessly integrates with Valgrind (`memcheck`) to capture, isolate, and log segmentation faults, out-of-bounds accesses, and memory leaks before they hit expensive hardware simulators.
* **Fault Archiving:** Automatically archives failing CUDA files alongside their corresponding memory-fault logs for rapid root-cause analysis.

## Setup and Execution

### Prerequisites
* NVIDIA CUDA Toolkit (`nvcc`)
* Python 3.8+
* Valgrind

### Running the Pipeline
Navigate to the root directory and execute the runner script. The orchestrator will handle generation, compilation, execution, and memory debugging autonomously.

```bash
python3 runner/debug_pipeline.py
