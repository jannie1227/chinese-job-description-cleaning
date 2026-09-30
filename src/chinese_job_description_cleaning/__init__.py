"""从普通职位描述提取职责正文；默认不需要原研究数据或私有配置。"""
from .api import DescriptionCleaner, clean_description, clean_record, clean_records

__version__ = '0.1.0'
__all__ = ['DescriptionCleaner','clean_description','clean_record','clean_records']
