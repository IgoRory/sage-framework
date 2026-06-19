# TDD Test Quality Bar

Use this rubric for product-level SAGE TDD work. A test passes the quality bar when it proves behavior that would fail for a realistic defect, not merely when it matches the current fixture.

## Required quality checks

- **Behavior proof:** Exercise the lowest meaningful public or observable interface for the requirement. Static/source-shape checks are secondary tripwires unless behavior is impractical to execute.
- **Fault model:** State the bug the test is meant to catch. The test must fail if that bug exists.
- **Independent oracle:** Derive expected results from a rule, invariant, relationship, or independently verified source. Do not co-author expected output from the same fixture rows that drive the implementation.
- **Fixture-overfit risk:** Mark each scenario low, medium, or high risk. High risk includes customer-specific SQL, seeded IDs, literal row snapshots, profitability measures, pointer relationships, and copied production examples.
- **Anti-overfit mechanism:** For medium/high fixture-overfit risk, include at least one mechanism that prevents a false green: alternate IDs, second-customer data, disjoint data, parameterized variants, omitted-coincidence fixtures, invariant assertions, relationship assertions, set comparisons, or negative/failure paths.
- **Meaningful RED:** `STATUS: RED CONFIRMED` is valid only when failure is caused by missing behavior. Compile, import, auth, fixture setup, Docker, or unrelated infrastructure failures do not prove RED.

## Common fail patterns

- **False-green test:** The implementation can pass while failing real customer data.
- **Fixture-coupled test:** Assertions depend on hardcoded examples such as fixed customer IDs, process IDs, measure IDs, or known names like `RTL 46`.
- **Implementation-mirroring test:** The test reimplements the production mechanism instead of checking observable behavior with an independent oracle.
- **Vacuous assertion:** The assertion only checks row count, file existence, non-null output, `0 == 0`, or a literal snapshot where correctness matters.
- **Mechanism-reimplemented test:** The test duplicates the SQL/procedure/algorithm and compares the implementation to itself.

## Strong assertion examples

- Relationship assertion: every child row points to a parent row created in the same run and customer scope.
- Invariant assertion: totals, uniqueness, status transitions, or set membership hold across disjoint inputs.
- Omitted-coincidence fixture: remove or omit a row that previously made a hardcoded path appear correct.
- Second-customer data: prove the behavior works for a customer or process with different IDs and values.
