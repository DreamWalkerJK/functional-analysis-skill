# Writing functional design documents / 功能设计文档写作规范

Write in the user's language. The Chinese examples illustrate natural technical writing; preserve the same principles in other languages.

## Follow the business structure

When a user supplies a preferred document, inspect both its heading outline and several complete functional sections. Follow its useful organization and explanation style, adapting them to the new subject. Do not import its business facts, unsupported claims or irrelevant chapters.

A useful service/module document starts with “文档范围” and “模块定位”, explains “总体设计”, and then develops concrete functional areas. Close with “状态与字段约束”, “外部依赖与协作关系” and material “当前实现差异”. Keep revision information, validation records and source locations in appendices. A system document may instead organize functional chapters by subsystem or end-to-end scenario. These are compositional choices, not a fixed form to fill.

“总体设计” explains mechanisms shared across the selected functions, such as the separation of records and binary content or the relationship between current and historical records. Describe what the code does and what that means for the module. A source-code design description does not establish formal approval. Omit this chapter for a small module where it would merely repeat later sections.

## Write headings people can recognize

Use the actual business object, operation or rule. Familiar headings such as “服务定位”, “核心数据对象”, “功能矩阵”, “分页查询”, “新增与编辑设计” and “状态与字段约束” are appropriate. Under a business chapter, “批量处理” is clear; repeating the service name or adding “设计” at every level is unnecessary.

| Avoid abstract or overloaded headings | Prefer a heading that identifies the subject |
| --- | --- |
| 服务职责与能力图谱 | 模块定位 |
| 分析基线与覆盖边界 | 文档范围; move revision details to “附录：分析记录” |
| 协作与一致性边界 | 外部依赖与协作关系; describe transaction behavior beside the affected function |
| 航季导入：业务保存、原件归档与恢复 | 航季文件导入设计 → 保存导入结果 / 原文件归档 / 保存失败后的恢复处理 |
| 实现差异、待确认事项与验证说明 | 当前实现差异; move analysis records to an appendix |

Avoid invented metaphors such as “能力图谱”, slash-separated labels, and headings that bundle unrelated topics with “与/及/和”. “新增与编辑设计” is natural when both operations share a coherent section; do not ban conjunctions mechanically. Use code identifiers in headings only when they are the clearest subject name.

Read the outline alone before drafting. It should help a maintainer locate a function and understand chapter relationships. Before delivery, check that each section delivers what its heading promises. Changing headings without reorganizing mismatched paragraphs is insufficient.

## Explain each function as a design

For a substantial functional area, present a compact matrix mapping functions to interfaces or triggers, core implementation and purpose. Then explain important operations in a natural sequence:

1. Introduce the purpose or use case in a short paragraph.
2. State meaningful inputs, prerequisites and validation in their actual order.
3. Describe processing steps and the decisions that change the outcome.
4. Identify records, fields, relationships, states and events that change.
5. Explain the result, subsequent processing and relevant failure behavior.

Use ordered lists when sequence matters. Do not create a subheading for every item or turn every assignment into a separate step. Use tables for field inventories, state values and rule comparisons. Group simple CRUD operations; expand complex import, split/merge, batch and asynchronous operations.

For example, “修改待办设计” should explain which record is found, which conditions reject the operation, what fields or next occurrence change, and what the caller receives. “It uses a repository and calls Update” does not describe a function. “人工处理重复待办后，系统保留该事项，并按重复设置顺延下一次截止时间” explains a design consequence; use it only when supported by code.

## Keep technical precision and readable language together

- Explain purpose before implementation detail. Use classes and methods to locate logic while keeping the business operation as the section's subject.
- State who acts, under which condition, and what follows. Prefer direct prose to repeated “本次已确认”“当前可见路径”“解释限制” formulations.
- Preserve identifiers, protocol literals and state values. Explain units, time zones, null handling and comparison boundaries where they affect results.
- Place material caveats beside the behavior they qualify. Consolidate repeated framework or runtime limitations in the appendix.
- Distinguish configured, registered, reachable and observed runtime behavior. Avoid unsupported words such as “guarantees”, “all”, “完整”, “稳定” and “天然”.
- Put short source references after related paragraphs or matrix rows. Keep hashes and lengthy paths in the source index or companion JSON.

| Situation | Precise wording |
| --- | --- |
| A handler assigns a state but later processing is unknown | “该操作将 `status` 写为 `Pending`；后续由哪个任务消费，尚未确认。” |
| Comment and implementation differ | “接口注释描述为同时新增主记录和明细；当前方法只写入主记录，因此应按人工补录主记录理解这一操作。” |
| A helper has no found caller | “该方法保留在代码中，但在所检查的入口及调用链中未发现调用。” |
| A test was read but not run | Record “现有测试包含这一预期；本次未执行” in the analysis appendix; cite near the claim if needed |
| Apparent intent has no requirement evidence | Describe the condition and result. Omit assumed rationale or label it as inference |

## Keep the document proportional

Combine chapters for small modules, add separate business chapters for large services, and retain only sections with useful content. Do not copy a fixed heading count, force a repetitive “结论”, or expand functional description into an unsolicited audit.

Retain differences affecting functional understanding. Give each a concrete heading, such as “文件名预检查未由唯一索引保证”, explain the implementation and consequence, then state what remains unknown. Recommendations, if requested, must be separate from current behavior.
