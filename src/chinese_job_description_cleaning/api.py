"""R12 V7 通用调用接口，封装原规则并隔离每个清洗实例的状态。"""
from functools import lru_cache
import hashlib
from pathlib import Path
from threading import RLock
from typing import Iterable, Mapping

from . import _frozen

_CONSTRUCTION_LOCK = RLock()


class DescriptionCleaner:
    """可复用的职责清洗器，默认使用公开规则，不联网、不加载私有原文。

    可选 review_resources 为调用者自己持有的本地定案 JSON。初始化时
    将资源绑定到独立引擎；单实例调用加锁，避免规则的可变状态交叉。
    """
    def __init__(self, review_resources=None):
        self.review_resources = Path(review_resources).resolve() if review_resources else None
        with _CONSTRUCTION_LOCK:
            _frozen.load_review_resources(self.review_resources)
            self.engine = _frozen.Cleaner()
        self.lock = RLock()

    def clean_description(self, text: str) -> str:
        """只返回职责正文；要求、福利等按原规则隔离，空正文仍返回空串。"""
        return self.clean_record(text)['responsibility_text']

    def clean_record(self, text: str, *, record_id='') -> dict:
        """返回原文、职责正文、原文哈希、生效阶段及公开规则状态。

        原文保留在调用者内存或其本地输出中，不发送外部服务。
        rule_candidate 表示规则生成结果，不表示人工金标准或内容无误。
        """
        if not isinstance(text, str) or not isinstance(record_id, str):
            raise TypeError('text and record_id must be strings.')
        with self.lock:
            try:
                body, stage = self.engine.clean(text)
            except Exception:
                # 避免底层断言把调用者的完整原文拼接到日志或异常消息中。
                raise RuntimeError('Description cleaning failed; input text was not logged.') from None
        return {'record_id':record_id,'description_raw':text,'responsibility_text':body,'raw_text_sha256':hashlib.sha256(text.encode('utf-8')).hexdigest(),'applied_stage':stage,'rule_scope':'R12_V7_WITH_LOCAL_REVIEWS' if self.review_resources else 'R12_V7_PUBLIC_RULES','quality_status':'rule_candidate','human_gold_standard':False}

    def iter_clean_records(self, records: Iterable[Mapping]) -> Iterable[dict]:
        """逐条输出并保留空正文、重复描述和调用者 ID。"""
        seen = set()
        for number, row in enumerate(records, 1):
            if not isinstance(row, Mapping) or 'description' not in row:
                raise ValueError('Each record must contain a description field.')
            record_id = row.get('record_id', f'PUBLIC_{number:010d}')
            if not isinstance(record_id,str) or not record_id or record_id in seen:
                raise ValueError('record_id must be a unique nonempty string.')
            seen.add(record_id)
            yield self.clean_record(row['description'],record_id=record_id)

    def clean_records(self, records: Iterable[Mapping]) -> list[dict]:
        """小批量便利接口；大文件用 iter_clean_records 或命令行入口。"""
        return list(self.iter_clean_records(records))


@lru_cache(maxsize=1)
def _default():
    return DescriptionCleaner()


def clean_description(text: str) -> str:
    """清洗一个普通职位描述字符串，无需私有原文配置。"""
    return _default().clean_description(text)


def clean_record(text: str, **metadata) -> dict:
    """清洗一条普通描述并返回审计字段。"""
    return _default().clean_record(text, **metadata)


def clean_records(records: Iterable[Mapping]) -> list[dict]:
    """批量清洗，保留输入行和记录身份。"""
    return _default().clean_records(records)
