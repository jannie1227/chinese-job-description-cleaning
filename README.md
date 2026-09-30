# 中文岗位描述职责清洗

独立、可安装的 Python 工具，从普通职位描述中提取实际职责正文，按规则隔离应聘要求、福利宣传、结构标记及来源损伤。默认只需要使用者自己的文本，不需要本研究原始数据、私有复核表或 API 密钥。

本仓库只处理岗位描述。职位名称及分类预处理见 [chinese-job-title-cleaning](https://github.com/jannie1227/chinese-job-title-cleaning)。

## 安装与直接调用

使用 Python **3.12.x**，运行时只依赖标准库。

```sh
python -m pip install "git+https://github.com/jannie1227/chinese-job-description-cleaning.git@v0.1.0"
```

也可从 [Releases](https://github.com/jannie1227/chinese-job-description-cleaning/releases) 下载 wheel，使用 `python -m pip install 下载的.whl` 安装。

```python
from chinese_job_description_cleaning import clean_description, clean_record, clean_records

text = "岗位职责：负责设备安装与维护。\n任职要求：大专以上学历。"
clean_description(text)
# '负责设备安装与维护'

clean_record(text, record_id="SYNTH_001")
# 返回原文、职责、原文哈希、生效阶段和规则状态

clean_records([{"description": text}, {"description": "任职要求：本科以上学历。"}])
# 两条都保留；第二条没有可提取职责时正文为空
```

展示文字全部为人工构造。Python 接口直接接收字符串，不要求复制原研究四列 CSV、不校验使用者输入必须与本研究语料相同。

## 普通 CSV

人工 CSV 位于本仓库 `examples/`，下载示例或使用自己的文件路径即可。最少只需一列 `description`，可选唯一字符串 ID：

```sh
job-description-clean --input examples/input_synthetic.csv --output cleaned.csv --id-column example_id
job-description-clean --input my_jobs.csv --output my_jobs_cleaned.csv --text-column 职位描述 --id-column record_id
```

也可用 `python -m chinese_job_description_cleaning ...`。输入支持 UTF-8 CSV / CSV.gz，输出为新 CSV 文件。保留 ID、原文和空正文记录，不按相同描述删除行；不自动透传输入的其他列。已存在输出文件不会覆盖。

## 公开规则与研究复现

默认接口执行 **R12 V7 公开规则**，返回 `rule_scope=R12_V7_PUBLIC_RULES`。一般使用不需要任何私有配置。

原研究另有十九项逐原文定案（R10 十三项、V5 四项、V7 两项），含真实招聘文本，已从公开代码中移除。数据持有者可以通过 `DescriptionCleaner(review_resources=本地文件)` 或命令行 `--review-resources` 加载自己的配置。私有数据不会因接口存在而上传或在仓库中分发。

普通调用与原研究全库复现分别提供入口：后者使用 `job-description-reproduce`，需要原始研究 CSV 与匹配的本地定案配置，并保留原输入和整库校验契约。默认通用接口不把其他语料标记为原研究复现通过。

原研究于 2026-09-29 采用 R12 V7 并停止清洗。本次拆分提供调用接口与安装封装，保留规则，不重新改变研究正文。历史质量限制和复现条件见 [研究说明](docs/RESEARCH.md)，字段及线程调用契约见 [API 文档](docs/API.md)。

## 可读的规则源码与注释

```text
src/chinese_job_description_cleaning/
  api.py                     # 普通字符串/记录调用、实例隔离与中文契约注释
  cli.py                     # 普通 CSV 映射、逐条处理和安全写出
  _frozen.py                 # 研究引擎及高级全库复现入口
  engine_sources/
    jdclean_unified/          # 原职责修复函数
    tools/r11_*.py            # 原文结构、栏目及任务规则
    tools/r12_*.py            # 后续语义边界与定案机制
```

十六个原内嵌模块已拆成可阅读的 `.py` 文件，规则正文与上一公开版逐字相同。运行时仍使用隔离的版本命名空间，避免不同阶段的可变函数状态混用。续跑指纹包含运行文件和全部规则模块，规则变化后不能继续使用旧缓存。

## 验证、数据与许可

```sh
python -m pip install .
python -m unittest discover -s tests -v
python scripts/check_public_files.py
python examples/demo.py
```

测试调用安装后的包、从临时目录处理普通 CSV，并检查线程共享实例、重复记录、空正文、ID、原文保留和输出不覆盖。GitHub Actions 在 Linux、Windows、macOS 上运行这些人工输入。

源码和示例不分发真实招聘数据、完整研究正文或十九项私有定案。输入仅在调用者本地处理。代码为 [MIT](LICENSE)，人工示例为 [CC BY 4.0](LICENSE-DATA)。规则候选不是人工金标准，也不代表内容完全正确。源码哈希见 [source_manifest.json](docs/source_manifest.json)；引用见 [CITATION.cff](CITATION.cff)。
