"""所有文字均为人工构造；不需要研究者的原始数据或定案表。"""
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from chinese_job_description_cleaning import clean_description, clean_record

text = '岗位职责：负责设备安装与维护。\n任职要求：大专以上学历。'
print(clean_description(text))
print(clean_record(text, record_id='SYNTH_DEMO'))
