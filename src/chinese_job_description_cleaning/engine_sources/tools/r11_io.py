"""Isolated full-corpus correction; published R10 and original files stay frozen."""
import sys,json,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R10=ROOT.parent/'05_后续任务输出/剩余正文终结清洗_R10_20260927'
QA=ROOT.parent/'05_后续任务输出/R10_独立质量抽查_20260927'
OUT=ROOT.parent/'05_后续任务输出/全库职责纠错_R11_20260927'
RAW=ROOT/'3.指标构建/0.招聘数据清洗原始文件/原始数据2.0版本.csv'
LOCK=Path(__file__).resolve().parent/'runtime.lock'
def digest(b):return hashlib.sha256(b).hexdigest()
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,p)
