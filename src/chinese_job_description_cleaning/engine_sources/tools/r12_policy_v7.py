"""Two fully reviewed original templates: deterministic literal-span cleanup."""
import copy,hashlib,json,re
from pathlib import Path
from tools import r12_policy_v6 as v6
from tools.r11_verify_release import replay
OUT=Path(__file__).resolve().parents[2]/'05_后续任务输出/三类共性问题修正_R12_20260928'
REVIEWS={x['raw_sha256']:x for x in BUNDLED_RESOURCES['v7_reviews']}
def process(raw,row):
 review=REVIEWS[hashlib.sha256(raw.encode()).hexdigest()];assert review['raw']==raw
 p=copy.deepcopy(v6.process(raw,row));s,_=replay(raw,p['normalization']);changes=[]
 for d in review['decisions']:
  matches=list(re.finditer(re.escape(d['text']),s));assert len(matches)==1,d['text'];m=matches[0]
  changes.append(dict(a=m.start(),b=m.end(),label=d['label'],reason=d['reason']))
 v6.v5._overlay(p,s,changes);v6.engine.rebuild(p,s)
 p.update(proposed_after=p['after'],adopted=True,text_changed=p['after']!=p['before'],preserve_parent_reason=None,policy_version='R12_V7_REVIEWED_COMPLETE_ORIGINAL_MIXED_TEXT',complete_source_review_sha256=hashlib.sha256(raw.encode()).hexdigest())
 return p
