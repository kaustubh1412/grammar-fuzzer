import os
import subprocess
import time
import shutil

# To run this script from the root of the repository
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fuzzer.grammar_engine import CUDASIMDGrammarFuzzer

TEMPLATE_PATH = "templates/harness.cu.template"
WORKSPACE_DIR = "workspace"
CRASH_LOGS_DIR = "crash_reports"

def setup_directories():
    for d in [WORKSPACE_DIR, CRASH_LOGS_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)

def create_test_case(fuzzer, test_id):
    """Injects fuzz payload into the template."""
    with open(TEMPLATE_PATH, "r") as f:
        template = f.read()
    
    payload = fuzzer.generate_payload()
    test_code = template.replace("<<<INJECT_PAYLOAD_HERE>>>", payload)
    
    file_path = os.path.join(WORKSPACE_DIR, f"test_{test_id}.cu")
    with open(file_path, "w") as f:
        f.write(test_code)
    
    return file_path

def compile_cuda(src_file, bin_file):
    """Compiles the injected CUDA code."""
    cmd = ["nvcc", src_file, "-o", bin_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr

def run_with_valgrind(bin_file, test_id):
    """Executes the binary wrapped in Valgrind to catch mem leaks & segfaults."""
    log_file = os.path.join(WORKSPACE_DIR, f"valgrind_{test_id}.log")
    cmd = [
        "valgrind", 
        "--tool=memcheck", 
        "--leak-check=full", 
        "--error-exitcode=1", 
        f"--log-file={log_file}",
        f"./{bin_file}"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # If Valgrind caught an error or the program segfaulted
    if result.returncode != 0:
        return False, log_file
    return True, log_file

def main():
    print("=== Starting Automated SIMD Fuzzing Pipeline ===")
    setup_directories()
    fuzzer = CUDASIMDGrammarFuzzer()
    
    iterations = 50 # Set higher for massive test coverage
    faults_caught = 0

    for i in range(iterations):
        print(f"\n[Iteration {i+1}/{iterations}] Generating test case...")
        
        # 1. Generate & Inject
        src_file = create_test_case(fuzzer, i)
        bin_file = os.path.join(WORKSPACE_DIR, f"test_{i}.out")
        
        # 2. Compile
        success, err_log = compile_cuda(src_file, bin_file)
        if not success:
            print(f"[-] Compilation failed (Syntax/Grammar error). Skipping.\n{err_log}")
            continue
            
        # 3. Memory Debugging via Valgrind
        print(f"[*] Running hardware-software memory interface validation...")
        passed, valgrind_log = run_with_valgrind(bin_file, i)
        
        if not passed:
            print(f"[!] FAULT DETECTED: Segmentation Fault / Memory Leak captured.")
            faults_caught += 1
            
            # Archive the faulting code and the Valgrind log
            fault_dir = os.path.join(CRASH_LOGS_DIR, f"fault_{i}")
            os.makedirs(fault_dir, exist_ok=True)
            shutil.copy(src_file, fault_dir)
            shutil.copy(valgrind_log, fault_dir)
            print(f"[*] Fault isolated and logged to {fault_dir}")
        else:
            print(f"[+] Clean execution. No faults detected.")
            
    print(f"\n=== Pipeline Complete ===")
    print(f"Total Iterations: {iterations}")
    print(f"Total Faults Isolated: {faults_caught}")

if __name__ == "__main__":
    main()
