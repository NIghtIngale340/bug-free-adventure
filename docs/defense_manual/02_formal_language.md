# 02 — The Formal Language

[← 01 Project Context](01_project_context.md) · [Index](README.md) · Next: [03 Automata Theory →](03_automata_theory.md)

Slide: **2 — The Employee ID Language** (presenter: Mark Anub)

---

## 1. Beginner explanation

Forget computers for a second. A **language** in this course is just **a set of strings**.

- English is a (huge, messy) language.
- "All valid employee IDs" is a (small, precise) language.

To define a language you need two things:

1. **The alphabet (Σ, "sigma"):** which characters you're allowed to use at all.
2. **The rule:** which strings made from those characters are "in" the language.

For us:

- **Alphabet:** the letters `E`, `M`, `P`, the hyphen `-`, and the digits `0`–`9`. That's it. 14 characters.
- **Rule:** `EMP`, then `-`, then 4 digits, then `-`, then 4 digits.

So:

| String | In the language? | Why |
|---|---|---|
| `EMP-2026-0042` | Yes | Follows the rule exactly |
| `EMP-0000-0000` | Yes | The year is *any* four digits; we check format, not whether the year makes sense |
| `EMP2026-0042` | No | Every character is allowed, but the first hyphen is missing |
| `emp-2026-0042` | No | Lowercase `e`, `m`, `p` aren't in the alphabet at all |
| `EMP-2026-0042 ` | No | A space isn't in the alphabet |
| (empty string) | No | Too short; the rule needs 13 characters |

---

## 2. Technical explanation

### Alphabet Σ

```text
Σ = { E, M, P, -, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 }        |Σ| = 14
```

- 3 letters + 1 hyphen + 10 digits = **14 symbols**.
- Σ is **ASCII-only**. Outside Σ: lowercase letters, spaces, tabs, `_`, full-width digits (`０`), Arabic-Indic digits
  (`٣`), look-alike hyphens (`‐` U+2010, `–` en dash), Cyrillic `Е` that looks like Latin `E`.
- In code, Σ is **not typed by hand**. It is computed from the regex: `ALPHABET = frozenset(alphabet_of(ID_REGEX))`
  in `app/data/id_rules.py`.

### Strings and Σ*

- A **string** (or word) over Σ is a finite sequence of symbols from Σ. Example: `EMP-2026-0042`.
- **Σ\*** is the set of *all* strings over Σ, of any length, including the empty string ε.
- A **language over Σ** is any subset of Σ\*.

### Language L

```text
L = { w ∈ Σ* | w = E M P - d₁d₂d₃d₄ - d₅d₆d₇d₈,  dᵢ ∈ {0,…,9} }
```

Read it as: "L is the set of strings w over Σ such that w is `EMP-`, four digits, `-`, four digits."

- **Valid strings** = members of L.
- **Invalid strings** = everything else, including strings that aren't even over Σ (they contain a symbol
  outside Σ).

### Exact string length

Every string in L has length **13**:

```text
E M P - d d d d - d d d d
1 2 3 4 5 6 7 8 9 10 11 12 13
```

3 (prefix) + 1 (hyphen) + 4 (year) + 1 (hyphen) + 4 (number) = 13. In code: `TOTAL_LENGTH = length_of(ID_REGEX)`.

This is why the DFA has states `q0` through `q13`: one state for "I've read *i* symbols correctly so far", for
*i* = 0…13.

### Cardinality: |L| = 10⁸

**Beginner version:** how many different valid IDs are there? The `EMP-`, `-` parts never change. Only the 8
digit positions vary, and each one has 10 choices.

```text
10 × 10 × 10 × 10 × 10 × 10 × 10 × 10 = 10⁸ = 100,000,000
```

Like a combination lock with 8 dials of 10 digits each: 100 million combinations.

**Technical version:** |L| = |{0,…,9}|⁸ = 10⁸, because the fixed symbols contribute one choice each and the
eight digit positions are independent.

### Why |Σ| = 14 matters

**Beginner:** it's the number of different keys on our "keyboard". Every DFA state must say what to do for each
of the 14 keys.

**Technical:** a complete DFA has |Q| × |Σ| transitions = 15 × 14 = **210** entries in its transition table. The
docs compress digits into one "0–9" column, but there are really 14 columns.

### Why the language is finite

L contains exactly 10⁸ strings, a finite number. Every string has the same fixed length 13. There is no
"repeat as many times as you like" (no Kleene star `*`) anywhere in the definition.

### Why a finite language is regular

**Beginner:** if a language has finitely many strings, you could in principle list them all and write a regex
`string1 ∪ string2 ∪ … ∪ string100000000`. Any language you can write as a regex is regular. So every
finite language is regular.

**Technical (the theorem):** every finite language is regular. Proof sketch: each single string `w = a₁a₂…aₙ` is
regular (the concatenation `a₁·a₂·…·aₙ`), and regular languages are **closed under finite union**, so a finite
union of them is regular.

**Practical consequence:** a DFA for L is *guaranteed* to exist. We don't need a stack (pushdown automaton) or
unbounded memory. The DFA only needs to "count" how far along it is, 0…13, plus a dead state.

> Careful: the converse is **false**. Regular languages can be infinite (e.g. `a*`). "Finite ⇒ regular", not
> "regular ⇒ finite".

### Closure properties (in case the panel asks)

Regular languages are closed under union, concatenation, Kleene star, complement and intersection. Relevant
examples:

- **Concatenation:** our regex *is* a concatenation of smaller regular pieces (`EMP`, `-`, `D⁴`, `-`, `D⁴`).
- **Union:** `D = (0 ∪ 1 ∪ … ∪ 9)`. Allowing a second prefix would be a union too.
- **Complement:** the set of *invalid* strings over Σ, Σ\* ∖ L, is also regular: same DFA with the
  accepting/non-accepting states swapped (this only works because our DFA is complete; see the trap state in
  [03](03_automata_theory.md)).

The project doesn't implement complement or intersection operations. This is theory you should know, not a
feature.

---

## 3. Why `EMP-YYYY-NNNN` is a formal language, not "just a string format"

A "string format" is an informal description that people interpret. A **formal language** is a precisely
defined set with:

1. a fixed **alphabet** (so "is `е` allowed?" has one answer: no, it's Cyrillic, not in Σ),
2. a precise **membership rule** (so every string is either in L or not, no ambiguity),
3. **mathematical properties** you can prove (finite, |L| = 10⁸, regular, minimal DFA has 15 states).

Because L is formal, we can **derive** a machine from it with algorithms and **prove** facts about that machine.
That's impossible with an informal "format".

Example of the difference: is `EMP-2026-0042\n` (with a trailing newline) valid? An informal format might
shrug. In our formal language it's clearly **not**, because `\n ∉ Σ`. (This is also why the tests use
`re.fullmatch` and not `^…$`: Python's `$` matches before a trailing newline and would wrongly accept it.)

---

## 4. Where this lives in code

| What | Where |
|---|---|
| The regex (single source of truth) | `app/data/id_rules.py::ID_REGEX` |
| Σ (derived) | `app/data/id_rules.py::ALPHABET` |
| Length 13 (derived) | `app/data/id_rules.py::TOTAL_LENGTH` |
| Alphabet check (Layer 1) | `app/core/language.py::validate_symbols` |
| Full write-up | `docs/formal_language.md` |
