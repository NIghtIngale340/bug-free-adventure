# AUTOMATA THEORY BASELINE & CANONICAL SPECIFICATION
## Single Source of Truth: Mathematical Models, State Names, and Delta Function

**Audience:** All Team Members (Ken, Chester, Integrator)  
**Purpose:** Eliminates any ambiguity regarding state names, alphabet symbols, transition functions, and trap states.

---

## 1. Formal 5-Tuple Definition

The authoritative recognizer of the Employee ID language is the **Minimized Deterministic Finite Automaton (DFA)**:

$$M = (Q, \Sigma, \delta, q_0, F)$$

Where:
* **Alphabet ($\Sigma$):** Exactly 14 symbols:
  $$\Sigma = \{\text{'E'}, \text{'M'}, \text{'P'}, \text{'-'}, \text{'0'}, \text{'1'}, \text{'2'}, \text{'3'}, \text{'4'}, \text{'5'}, \text{'6'}, \text{'7'}, \text{'8'}, \text{'9'}\}$$
* **States ($Q$):** Exactly 15 states (14 sequential recognition states + 1 dead/trap state):
  $$Q = \{q_0, q_1, q_2, q_3, q_4, q_5, q_6, q_7, q_8, q_9, q_{10}, q_{11}, q_{12}, q_{13}, q_{\text{trap}}\}$$
* **Start State ($q_0$):** Initial state awaiting the first prefix character `'E'`.
* **Accepting States ($F$):** Exactly one accepting state:
  $$F = \{q_{13}\}$$
* **Input Length:** Valid strings have length $|w| = 13$.

---

## 2. Canonical State Meanings (The Frozen State Dictionary)

Both Ken (in backend code) and Chester (in GUI badges/labels) must use these **exact state identifiers**:

| State | Expected Next Input Symbol | Meaning / Structural Segment | Is Accepting? |
| :---: | :---: | :--- | :---: |
| **$q_0$** | `'E'` | Start of string; awaiting prefix character 1 | No |
| **$q_1$** | `'M'` | Prefix 'E' matched; awaiting prefix character 2 | No |
| **$q_2$** | `'P'` | Prefix 'EM' matched; awaiting prefix character 3 | No |
| **$q_3$** | `'-'` | Prefix 'EMP' matched; awaiting first hyphen separator | No |
| **$q_4$** | `'0'`–`'9'` | Separator matched; awaiting Year Digit 1 (millennium) | No |
| **$q_5$** | `'0'`–`'9'` | Year digit 1 matched; awaiting Year Digit 2 (century) | No |
| **$q_6$** | `'0'`–`'9'` | Year digit 2 matched; awaiting Year Digit 3 (decade) | No |
| **$q_7$** | `'0'`–`'9'` | Year digit 3 matched; awaiting Year Digit 4 (year) | No |
| **$q_8$** | `'-'` | Complete 4-digit year matched; awaiting second hyphen | No |
| **$q_9$** | `'0'`–`'9'` | Second hyphen matched; awaiting Sequence Digit 1 | No |
| **$q_{10}$** | `'0'`–`'9'` | Sequence digit 1 matched; awaiting Sequence Digit 2 | No |
| **$q_{11}$** | `'0'`–`'9'` | Sequence digit 2 matched; awaiting Sequence Digit 3 | No |
| **$q_{12}$** | `'0'`–`'9'` | Sequence digit 3 matched; awaiting Sequence Digit 4 | No |
| **$q_{13}$** | *End of String* | **Complete valid ID recognized; terminal accepting state** | **YES** |
| **$q_{\text{trap}}$** | *Any* | **Dead/sink state; reached upon any invalid transition** | No |

---

## 3. Transition Function $\delta(q, a)$ Table

For any state $q \in Q$ and input symbol $a \in \Sigma$, if no valid forward transition is listed, the automaton transitions to **$q_{\text{trap}}$**:

$$\forall a \in \Sigma, \quad \delta(q_{\text{trap}}, a) = q_{\text{trap}}$$

| Current State ($q$) | Condition on Input Symbol ($a$) | Next State ($\delta(q, a)$) | All Other Symbols in $\Sigma$ |
| :---: | :--- | :---: | :---: |
| **$q_0$** | $a = \text{'E'}$ | **$q_1$** | $q_{\text{trap}}$ |
| **$q_1$** | $a = \text{'M'}$ | **$q_2$** | $q_{\text{trap}}$ |
| **$q_2$** | $a = \text{'P'}$ | **$q_3$** | $q_{\text{trap}}$ |
| **$q_3$** | $a = \text{'-'}$ | **$q_4$** | $q_{\text{trap}}$ |
| **$q_4$** | $a \in \{\text{'0'}\dots\text{'9'}\}$ | **$q_5$** | $q_{\text{trap}}$ |
| **$q_5$** | $a \in \{\text{'0'}\dots\text{'9'}\}$ | **$q_6$** | $q_{\text{trap}}$ |
| **$q_6$** | $a \in \{\text{'0'}\dots\text{'9'}\}$ | **$q_7$** | $q_{\text{trap}}$ |
| **$q_7$** | $a \in \{\text{'0'}\dots\text{'9'}\}$ | **$q_8$** | $q_{\text{trap}}$ |
| **$q_8$** | $a = \text{'-'}$ | **$q_9$** | $q_{\text{trap}}$ |
| **$q_9$** | $a \in \{\text{'0'}\dots\text{'9'}\}$ | **$q_{10}$** | $q_{\text{trap}}$ |
| **$q_{10}$** | $a \in \{\text{'0'}\dots\text{'9'}\}$ | **$q_{11}$** | $q_{\text{trap}}$ |
| **$q_{11}$** | $a \in \{\text{'0'}\dots\text{'9'}\}$ | **$q_{12}$** | $q_{\text{trap}}$ |
| **$q_{12}$** | $a \in \{\text{'0'}\dots\text{'9'}\}$ | **$q_{13}$** | $q_{\text{trap}}$ |
| **$q_{13}$** | Any additional symbol $a \in \Sigma$ | **$q_{\text{trap}}$** | $q_{\text{trap}}$ |
| **$q_{\text{trap}}$** | Any symbol $a \in \Sigma$ | **$q_{\text{trap}}$** | $q_{\text{trap}}$ |

*Note on symbols outside $\Sigma$:* If an input character $c \notin \Sigma$ is encountered (e.g. `'A'`, `'!'`), it triggers immediate rejection with `SimulationStatus.REJECTED_INVALID_SYMBOL` and records an immediate trap transition to $q_{\text{trap}}$.

---

## 4. Why This DFA is Already Minimal

During the defense, professors often ask:  
*"Why couldn't you reduce the states further during DFA minimization?"*

**The Mathematical Proof:**
1. **Length Distinguishability:** Every state $q_i$ ($0 \le i \le 12$) requires a strictly distinct suffix length $13 - i$ to reach the accepting state $q_{13}$. For example, $q_4$ requires exactly 9 more symbols to accept, whereas $q_5$ requires 8 symbols. Therefore, no two states $q_i$ and $q_j$ ($i \neq j$) can be equivalent because their accepting strings have different lengths.
2. **Accepting vs Non-Accepting:** $q_{13} \in F$, while all other states $q_0 \dots q_{12}, q_{\text{trap}} \notin F$. By definition, partition refinement splits $F$ from $Q \setminus F$ at step $k=0$.
3. **Trap State Distinguishability:** For $q_{\text{trap}}$, no string $w \in \Sigma^*$ can ever reach $F$. For any $q_i$, there exists at least one valid suffix leading to $F$. Therefore, $q_{\text{trap}}$ cannot be merged with any $q_i$.
4. **Conclusion:** All 15 states are pairwise distinguishable. The Minimized DFA contains exactly **15 states**.

---

## 5. Ready-to-Use Python Dictionary Representation

Ken can directly embed this clean transition map into `app/data/id_rules.py` or `app/core/dfa.py`:

```python
"""
CANONICAL TRANSITION TABLE MAPPING
Owner: Ken / Integrator
"""

DIGITS = [str(d) for d in range(10)]  # '0' through '9'

CANONICAL_TRANSITIONS = {
    "q0": {"E": "q1"},
    "q1": {"M": "q2"},
    "q2": {"P": "q3"},
    "q3": {"-": "q4"},
    "q4": {d: "q5" for d in DIGITS},
    "q5": {d: "q6" for d in DIGITS},
    "q6": {d: "q7" for d in DIGITS},
    "q7": {d: "q8" for d in DIGITS},
    "q8": {"-": "q9"},
    "q9": {d: "q10" for d in DIGITS},
    "q10": {d: "q11" for d in DIGITS},
    "q11": {d: "q12" for d in DIGITS},
    "q12": {d: "q13" for d in DIGITS},
    "q13": {},  # Any trailing character traps to q_trap
    "q_trap": {},
}

START_STATE = "q0"
ACCEPTING_STATES = {"q13"}
TRAP_STATE = "q_trap"
ALPHABET = {"E", "M", "P", "-", *DIGITS}
```
