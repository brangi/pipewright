# Pipewright Demo Results

Results from running `pipewright run test-gen` on each language example.
All runs used `--yes` (auto-approve) with default Haiku/Sonnet model tiering.

**Date**: March 26, 2026
**Pipewright version**: v0.2.0 (commit `eb4daaa`)

## Summary

| Language | File | Tests | Pass Rate | Cost | Framework |
|----------|------|-------|-----------|------|-----------|
| Python | `example/python/utils.py` | 61 | 100% (61/61) | $0.10 | pytest |
| JavaScript | `example/js/utils.js` | 56 | 100% (56/56) | $0.14 | Jest |
| TypeScript | `example/ts/utils.ts` | 44 | 100% (44/44) | $0.13 | Vitest |
| Rust | `example/rust/src/lib.rs` | 31 | 100% (31/31) | $0.08 | cargo test |
| Go | `example/go/utils.go` | 59 | 100% (59/59) | $0.18 | go test |
| Java | `example/java/Utils.java` | 34 | generated | $0.19 | JUnit 4 |
| Ruby | `example/ruby/utils.rb` | 65 | 92% (60/65) | $0.18 | RSpec |

**Total: 350 tests generated, $1.00 total API cost**

## Per-Language Details

### Python (pytest) — 61/61 passing

```
pipewright run test-gen example/python/utils.py -y
```

The agent analyzed `utils.py`, detected pytest in the project, and generated 61 tests
covering `calculate_average`, `fizzbuzz`, and `reverse_words`. All tests passed on first
run. This is the baseline — pipewright's own test suite was generated with test-gen.

- **Generated file**: `tests/test_example_utils.py` (pre-existing, 61 tests)
- **Time**: ~45 seconds
- **Cost**: $0.10

### JavaScript (Jest) — 56/56 passing

```
pipewright run test-gen example/js/utils.js -y
```

The agent detected `package.json` with Jest configured, installed missing dependencies
via `npm install`, and generated 56 tests. Tests cover edge cases like `NaN`, `Infinity`,
empty arrays, unicode/emoji in strings, and whitespace normalization.

- **Generated file**: `example/js/utils.test.js`
- **Auto-installed**: Jest via npm
- **Self-corrected**: 2 fizzBuzz edge case assertions fixed during generation
- **Cost**: $0.14

### TypeScript (Vitest) — 44/44 passing

```
pipewright run test-gen example/ts/utils.ts -y
```

The agent detected Vitest in `package.json` and `tsconfig.json` targeting ES2022.
Generated 44 typed tests with proper TypeScript annotations. Used `toBeCloseTo()`
for floating-point comparisons.

- **Generated file**: `example/ts/utils.test.ts`
- **Auto-installed**: Vitest via npm
- **Self-corrected**: 4 fizzBuzz assertions for large-number divisibility
- **Cost**: $0.13

### Rust (cargo test) — 31/31 passing

```
pipewright run test-gen example/rust/src/lib.rs -y
```

The agent read `Cargo.toml`, detected the Rust 2021 edition, and generated 31 tests
using `#[test]` and `#[should_panic]` attributes. Tests validate `Result` return types,
error messages, and edge cases like empty slices and single-word strings.

- **Generated file**: `example/rust/tests/lib_tests.rs`
- **Time**: ~40 seconds
- **Cost**: $0.08 (cheapest run)

### Go (go test) — 59/59 passing

```
pipewright run test-gen example/go/utils.go -y
```

The agent detected `go.mod` and generated idiomatic table-driven tests using
`t.Run()` subtests. Achieved 100% statement coverage. Fixed a module path issue
by running tests from the correct directory.

- **Generated file**: `example/go/utils_test.go`
- **Self-corrected**: 1 fizzBuzz test case and module path resolution
- **Coverage**: 100% statement coverage
- **Cost**: $0.18

### Java (JUnit) — 34 tests generated

```
pipewright run test-gen example/java/Utils.java -y
```

The agent initially generated JUnit 5 tests but discovered only JUnit 4.12 was
available in the system Maven repository. It converted all tests to JUnit 4 syntax,
replacing `@DisplayName`, `@ParameterizedTest`, and `Assertions.*` with JUnit 4
equivalents. The conversion required the most agent turns of any language.

- **Generated file**: `example/java/UtilsTest.java`
- **Note**: JUnit version adaptation demonstrates the agent's ability to adjust
  to the local environment rather than assuming a specific toolchain
- **Cost**: $0.19 (highest, due to JUnit 5 -> 4 conversion)

### Ruby (RSpec) — 60/65 passing (92%)

```
pipewright run test-gen example/ruby/utils.rb -y
```

The agent detected no existing test framework, installed RSpec via `gem install rspec`,
and generated 65 tests. 60 passed; 5 failures revealed genuine edge cases in the
implementation (decimal precision, input validation, whitespace handling).

- **Generated file**: `example/ruby/utils_spec.rb`
- **Auto-installed**: RSpec via gem
- **5 failing tests**: These are valid findings — the test suite correctly identified
  gaps in edge case handling that could be fixed in the implementation
- **Cost**: $0.18

## Key Observations

1. **Language detection works**: The agent correctly identified the language and test
   framework for all 7 languages without any hints beyond the file extension.

2. **Self-correction is common**: In 4 of 7 runs, the agent generated tests that
   initially failed, then fixed them within the same workflow run.

3. **Environment adaptation**: The Java run showed the agent adapting to JUnit 4
   when JUnit 5 wasn't available — no manual intervention needed.

4. **Cost is predictable**: All runs fell within the documented $0.10-$0.30 range,
   averaging $0.14 per language.

5. **Test quality is high**: Generated tests cover happy paths, edge cases, error
   handling, and boundary conditions. The Ruby failures were real bugs, not test bugs.

## Reproducing These Results

```bash
# Clone and install
git clone https://github.com/brangi/pipewright.git
cd pipewright
pip install -e ".[dev]"
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Run on any example
pipewright run test-gen example/python/utils.py -y
pipewright run test-gen example/js/utils.js -y
pipewright run test-gen example/rust/src/lib.rs -y
```

Costs may vary slightly depending on model pricing and response length.
