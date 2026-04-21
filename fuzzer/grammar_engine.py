import random
import re

class CUDASIMDGrammarFuzzer:
    def __init__(self):
        # Grammar rules for valid SIMD/Warp intrinsics and memory accesses
        self.variables = ['valA', 'valB', 'valC', 'valD']
        self.intrinsics = [
            "__byte_perm({0}, {1}, 0x3210)",          # SIMD byte permutation
            "__vadd2({0}, {1})",                      # SIMD 16-bit vector add
            "__vabsdiffu4({0}, {1})",                 # SIMD 8-bit absolute difference
            "__shfl_sync(0xFFFFFFFF, {0}, {1}, 32)",  # Warp shuffle
            "__popc({0} ^ {1})"                       # Population count (XOR)
        ]
        self.memory_ops = [
            "data_out[tid] = {0};",
            "data_out[(tid + {offset}) % N] = {0};",  # Edge-case memory generation
            "data_out[tid] = {0} + data_in[tid];"
        ]

    def generate_variable_init(self):
        """Generates random 32-bit integer initializations"""
        lines = []
        for var in self.variables:
            val = hex(random.getrandbits(32))
            lines.append(f"    unsigned int {var} = {val};")
        return "\n".join(lines)

    def generate_instruction_block(self, num_instructions=5):
        """Injects randomized SIMD operations based on the grammar"""
        lines = []
        for _ in range(num_instructions):
            instr = random.choice(self.intrinsics)
            v1, v2 = random.sample(self.variables, 2)
            dest = random.choice(self.variables)
            lines.append(f"    {dest} = {instr.format(v1, v2)};")
        return "\n".join(lines)

    def generate_memory_write(self):
        """Generates memory writes, sometimes with intentional out-of-bounds risks to trigger faults"""
        op = random.choice(self.memory_ops)
        source_var = random.choice(self.variables)
        offset = random.randint(0, 1024) # Potential edge case offset
        return f"    {op.format(source_var, offset=offset)}"

    def generate_payload(self):
        """Combines grammar rules into a syntactically valid CUDA payload"""
        payload = "// --- AUTO-GENERATED FUZZ PAYLOAD ---\n"
        payload += self.generate_variable_init() + "\n\n"
        payload += self.generate_instruction_block(random.randint(5, 15)) + "\n\n"
        payload += self.generate_memory_write() + "\n"
        payload += "    // -----------------------------------\n"
        return payload

if __name__ == "__main__":
    fuzzer = CUDASIMDGrammarFuzzer()
    print(fuzzer.generate_payload())
