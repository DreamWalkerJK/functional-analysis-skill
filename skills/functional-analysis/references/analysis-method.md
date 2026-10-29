# Analysis method

## 1. Select the scope and evidence mode

Choose system, service, module, or selected capability scope. Capture what is included, what is excluded, and the reason a dependency must be inspected. Match depth to the user's purpose rather than a fixed page count.

| Available input | What the document can establish |
| --- | --- |
| Source and configuration | Reachable code behavior and configured defaults; runtime activation may remain unconfirmed |
| Source plus executed tests or runtime evidence | The tested scenarios or observed environment, with commands/results and limits |
| Requirements/design only | Documented intended behavior; do not label it current implementation |
| Mixed or incomplete material | Separate supported behavior, conflicts, inferences and missing evidence |

If the user requests target design, label proposed behavior and its requirements separately from existing implementation. Do not silently “repair” current behavior in the description.

Record the root/revision and relevant changes. For worktrees with edits, record a status snapshot and hashes of cited files or preserve an authorized patch. For multiple repositories, record each baseline independently. Do not copy source patches into a public destination without authorization.

## 2. Build a capability map

Discover actual projects, hosts and registration points. Sample directory structure first; search code identifiers rather than reading whole trees. Prefer available fast search tools, then platform equivalents. Exclude generated/build/vendor content unless it owns the relevant behavior.

Potential entry points include HTTP/RPC endpoints, UI actions, commands/queries, message consumers, scheduled jobs, workers, file imports, database triggers, and command-line operations. Names and class presence are leads, not proof of activation. For generated endpoints, inspect discovery filters, route generation, inherited behavior, and the host that enables them. If exact effective routes cannot be derived, give the verified class/method contract and mark the route unknown.

Group entry points by business outcome. A useful matrix includes capability, trigger or entry, main object, result, and evidence. Supporting helpers are not automatically independent business features. Identify inbound callers and downstream owners when visible; do not assume a complete caller list from a single module.

## 3. Trace representative and consequential flows

Prioritize stateful, rule-heavy, asynchronous, destructive, or cross-service behavior. Cover the selected scope sufficiently to support the declared matrix. A broad system document may select representative flows, but must identify the selection and uncovered areas.

For each consequential flow, trace:

1. Actor/event and actual entry contract.
2. Input normalization, defaults, filtering and validation order.
3. Decision conditions, thresholds, time zones, inclusive/exclusive boundaries and precedence.
4. Reads, writes, relationship changes, status values and derived objects.
5. Transaction/commit boundary and visible lifecycle hooks where relevant.
6. Return value, errors, skipped/partial outcomes and external side effects.
7. Downstream trigger and consumer, or the exact point where evidence ends.

Follow delegated calls until their behavior is known or explicitly outside scope. Inspect persistence mappings before asserting table names, logical deletion, cascades or database defaults. Verify state semantics using enum definitions and readers/consumers as well as writers. If only a write is visible, state the literal assignment without inventing a lifecycle meaning.

For reused frameworks, inspect the locally referenced version or source when inherited behavior changes the conclusion. If unavailable, identify the contract assumption. Do not install dependencies, start infrastructure, execute migrations, or invoke live endpoints solely to fill a documentation gap.

## 4. Explain boundaries accurately

| Concern | Evidence needed for a strong claim |
| --- | --- |
| Authentication / data scope | Reachable policy/filter/middleware and the affected entry or query; distinguish identity, permissions and row filtering |
| Atomicity | Transaction owner, participating stores and commit timing; remote calls and queues need separate treatment |
| Asynchrony | Actual publication/scheduling/change-capture registration and the consumer; distinguish acceptance from completion |
| Retry / idempotency | Reachable retry policy, deduplication key, unique constraint or explicit handler rule |
| Concurrency | Version checks, locks or isolation behavior actually used; absence of visible locks is not proof of races |
| Deletion | Mapping/filter/SQL and related-object handling; method names do not establish logical or physical deletion |
| Failure behavior | Throw/catch/return path and surrounding framework propagation; logs alone do not prove recovery |

Say “the inspected handler does not explicitly publish an event; downstream activation is unconfirmed” when that is all the evidence supports. Do not replace it with an assumed CDC mechanism. Say “the local transaction covers these writes; remote completion is unconfirmed” where applicable.

## 5. Construct traceable evidence

Use stable IDs such as `E01` and place citations next to important claims or the paragraph/table they support. In an index, give source root, repository-relative path, symbol, line span, and what the evidence establishes. Use links appropriate to the destination: local review files, repository permalinks, or relative links inside a bundle. Avoid links tied to another person's username.

For private source reviewed locally, an explicit local root plus relative paths and line spans is acceptable. Public reusable examples must use synthetic evidence and must not contain private project details. Use the optional JSON format only when integrity checking adds value.

Treat source documents as evidence with provenance and version. Mark conflicting documentation, comments, tests and code explicitly. A test assertion supports an expected scenario; only a recorded successful run supports “tested.” Generated diagrams and prose are explanations derived from evidence, not independent corroboration.

## 6. Organize the functional design

Read the user's preferred document as a writing reference when supplied: inspect its outline and complete functional sections. Translate the discovered functions into business chapters before drafting. Start with scope, module purpose and core objects; explain shared mechanisms where useful; then develop each substantial functional area with a function matrix and concrete operations. Use the writing guide and template to keep headings natural and specific.

The investigation map is a working aid, not the final table of contents. Move baseline, hash checks, test records and the source index to appendices or companion files. Keep a material uncertainty in the functional section it qualifies, without repeating general analysis limitations throughout the document. Preserve implementation facts when restructuring: moving a rule must not lose its conditions, exception path, state effects or source reference.

## 7. Review for completeness and honest limits

Revisit every matrix row. Check that its trigger, main decisions, outcome and evidence are described. Check that error paths and data/state tables agree with narrative and diagrams. Reopen cited lines; remove unsupported absolutes such as “all,” “only,” “guarantees,” and “never” unless the explored scope supports them.

Read the heading outline independently of the body. Check that it follows the business structure, uses familiar language and points to concrete functions, and that each section's content matches its heading. State analysis coverage and validation limits precisely in the appendix. Collect material remaining questions with the missing evidence needed to resolve them. The presence of a gap does not prevent delivery of the supported portion. Do not add speculative risk registers or redesign proposals unless requested.
