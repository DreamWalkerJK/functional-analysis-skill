# Writing guide / 写作规范

Write in the user's language. Chinese examples below illustrate the requested technical but readable style; the principles apply to any language.

## Explain behavior rather than source layout

Lead with business purpose, then explain conditions, actions, and effects. Keep each paragraph about one idea. Use class names to locate implementation; avoid making class inventories the main narrative.

- Weak: “The service uses a repository and calls Update.”
- Better: “After validating the selected records, the handler updates their processing status and saves the changes. Records rejected by validation remain outside this batch.” Only include the latter sentence if the branch is supported.
- 中文示例：“处理器先校验所选记录是否允许重新处理，再写入新的处理状态并提交。后续任务如何感知该变化，在当前分析范围内尚未确认。”

## Keep technical precision and readable language together

- State who performs an operation, under which condition, and what observable result follows.
- Define business terms once. Preserve code identifiers, field names, enum values and protocol literals. Do not translate an identifier into a different contract.
- Use ordered lists for meaningful processing order. Avoid converting every assignment into a separate step.
- Use tables for capability maps, field meanings, decision rules and state transitions. Specify units, time zones, null handling and boundary inclusivity when they affect behavior and are known.
- Use direct, neutral sentences. Remove unsupported adjectives such as “complete,” “robust,” “strict,” “seamless,” “完整,” “稳定,” and “天然.”
- Distinguish “configured,” “registered,” “reachable,” and “observed in a running environment.”
- Prefer a short explanation plus a precise example over a long list of implementation details.

## Separate evidence levels without making prose mechanical

Group related established facts under one source citation. Label inferences or unknowns where they arise; there is no need to prefix every sentence with “observed.”

| Situation | Precise wording |
| --- | --- |
| A handler assigns a status but its lifecycle is unclear | “该操作将 `status` 写为 `Pending`；后续消费条件尚未确认。” |
| Documentation differs from code | “注释描述为删除关联项；当前可达路径只显式更新主记录。关联删除是否由框架钩子执行，尚缺少证据。” |
| A helper exists without a found caller | “代码保留了该方法，但在所检索入口及其直接调用链中未发现调用。” |
| A test was read | “现有测试包含这一预期；本次未执行该测试。” |
| A rule looks intentional but no requirement supports it | Describe the condition and consequence; label the proposed rationale as inference or omit it |

## Scale the document

For a small module, combine object/state and collaboration sections. For a service, group related CRUD operations but expand domain rules and complex flows. For a system, map capabilities to owners and explain selected end-to-end scenarios before service internals. A fixed number of headings or pages is not a quality target.

Keep implementation discrepancies that change functional understanding. Offer improvement suggestions only when requested, and distinguish them from the current behavior. End with unresolved boundaries or validation notes when useful; a generic conclusion repeating the whole document adds little.
