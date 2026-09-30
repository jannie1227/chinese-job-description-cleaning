# Python 调用契约

`clean_description(text: str) -> str`：只返回职责正文，默认加载随包提供的公开规则。不需要研究原始数据，不联网；空输入或仅有应聘要求时允许返回空正文。

`clean_record(text, *, record_id='') -> dict`：返回单条审计字典。

`clean_records(records) -> list[dict]`：每条为包含 `description` 的字典；可选 `record_id`。按输入顺序保留重复原文和空正文，未提供 ID 时生成按序 ID。显式 ID 必须非空且唯一。

大批量可复用 `DescriptionCleaner()`，用 `iter_clean_records` 逐条处理。单实例内部加锁，允许多线程调用；不同实例的规则状态隔离。可选 `review_resources` 指向调用者自己的本地定案资源，默认无需提供。

| 返回字段 | 意义 |
| --- | --- |
| `record_id` | 调用者的字符串身份键 |
| `description_raw` | 原文原样保留，供调用者本地追溯 |
| `responsibility_text` | 规则提取的职责正文 |
| `raw_text_sha256` | 原文 UTF-8 字节的 SHA-256 |
| `applied_stage` | 原研究引擎最后生效阶段；V4/V5/V6/V7 是内部阶段名 |
| `rule_scope` | 默认 R12_V7_PUBLIC_RULES；加载本地资源时为 R12_V7_WITH_LOCAL_REVIEWS |
| `quality_status` | rule_candidate，表示规则输出 |
| `human_gold_standard` | false，不冒称人工标签 |

返回原文不表示向第三方发送数据：它只存在于调用者的内存和其选择的本地文件。接口不采集日志或上传文本，运行错误也不打印完整原文。

默认示例展示通用调用，不宣称原研究全库复现通过。原语料的高级 CSV 复现入口为 `job-description-reproduce`；资源配置身份和规则指纹参与续跑核对，条件见研究说明。
