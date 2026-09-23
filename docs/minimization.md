# DFA Minimization — Employee ID Validator

**Author:** Ken (Backend / Automata Core Lead)

## 1. Goal

Minimize the DFA without changing the language it recognizes.

## 2. Algorithm (`app/core/minimizer.py`)

1. Reachability pruning — remove states not reachable from q0.
2. Initial partition — P₀ = { F, Q \ F }.
3. Refinement — split blocks whose members transition to different blocks
   on the same symbol, until stable.
4. Merging — collapse each equivalence class into a single state.
5. Metadata — record which original states were merged.

## 3. Result for the Employee ID DFA

**The canonical DFA is already minimal.** No state is merged.

### Proof

1. **Length distinguishability.** From qᵢ (0 ≤ i ≤ 12), the shortest string
   reaching q13 has length 13 − i. All 13 values are distinct, so no two of
   q0…q12 are equivalent.
2. **Final vs non-final.** q13 ∈ F, all others ∉ F → split by P₀.
3. **Trap distinguishability.** No string from q_trap reaches q13; from every
   qᵢ some string does. Therefore q_trap is distinguishable.
4. **Conclusion.** All 15 states are pairwise distinguishable.
   |Q_min| = 15.

## 4. Implementation Notes

- `_reachable_states` treats `q_trap` as implicitly reachable even though its
  transition row is empty. Without this, `q_trap` would be wrongly pruned.
- Partition refinement uses signature comparison over every symbol in Σ.

## 5. Verification

`tests/core/test_minimization.py` proves:

- `minimize()` preserves acceptance on sample strings.
- The canonical DFA's state count does not shrink.
- An artificially-added unreachable state is pruned.

## 6. Why This Matters for the Defense

Minimization forces us to prove every state is *necessary*. If asked
"why couldn't you reduce it further?", cite the length-distinguishability
proof above.