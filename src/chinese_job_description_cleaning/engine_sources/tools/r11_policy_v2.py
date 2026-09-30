"""Explicit actor guard for HR duties and employer promotion; frozen V1 preserved."""
import re
from tools import r11_engine as engine
from tools.r11_io import *
rules=engine.rules
original_decide=rules.decide
HR_OPERATION=re.compile(r'^(?:(?:及时|定期|每月|按时|按规定|按要求|依法|代为|代办)地?)*(?:缴纳|交纳|缴交|申报|代缴|核缴|补缴)(?:公司|企业|本公司|全体|在职)?(?:员工|职工|雇员|人员|同事)(?:的)?(?:社保|社会保险|五险|住房公积金|公积金|保险费)')
EMPLOYER_PROMO=re.compile(r'^(?:我们|公司|本公司|本企业|企业|本集团|集团)(?:一直|始终|非常|十分|高度|格外|更加|都|也)?(?:重视|关注|关心|关爱|尊重|珍惜|鼓励|倡导|崇尚|坚持|坚信)(?!客户投诉处理)')
TRIGGER=re.compile(r'(?:缴纳|交纳|缴交|申报|代缴|核缴|补缴)[^。;；\n]{0,15}(?:员工|职工|雇员|人员|同事)|(?:我们|公司|企业|集团)(?:一直|始终|非常|十分|高度|格外|更加|都|也)?(?:重视|关注|关心|关爱|尊重|珍惜|鼓励|倡导|崇尚|坚持|坚信)')
def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if EMPLOYER_PROMO.match(t):return 'N','EMPLOYER_SUBJECT_VALUES_OR_CARE_STATEMENT'
 if HR_OPERATION.match(t) and role in {None,'R'} and not rules.DAMAGE.search(t) and not rules.qualification(t):return 'R','EXPLICIT_EMPLOYEE_INSURANCE_ADMINISTRATION'
 return original_decide(text,role,previous)
rules.decide=decide
def applicable(raw):return bool(TRIGGER.search(raw))
def process(raw,row):
 p=engine.process(raw,row);p['policy_version']='R11_V2_EXPLICIT_HR_ACTOR';return p

# Decode complete standard entities before sentence partitioning; entity
# semicolons must never become sentence cuts. Unknown names remain untouched.
import html,html.entities
base_normalize=rules.normalize
ENTITY_ALL=re.compile(r'&(?:[A-Za-z][A-Za-z0-9]{1,31}|#\d{1,7}|#x[0-9a-fA-F]{1,6});')
BR_ANCHOR=re.compile(r'(?<![A-Za-z])(?:br)+(?=\s*(?:\d{1,2}(?:[.、)]|(?=[\u3400-\u9fff]))|岗位|职责|工作职责|工作内容|任职|福利|微信|分享|公司提供|家住|[\]}】]|$))')
BR_ALL=re.compile(r'(?<![A-Za-z])(?:br)+(?=\s*(?:\d{1,2}(?:[.、)]|(?=[\u3400-\u9fff]))|岗位|职责|工作职责|工作内容|任职|福利|微信|分享|公司提供|家住|[\]}】]|$|br))')
_context_br=False

def normalize(raw):
 s=raw;stages=[]
 for _ in range(3):
  es=[]
  for m in ENTITY_ALL.finditer(s):
   name=m[0][1:]
   if name.startswith('#') or name in html.entities.html5:
    if not rules.CODE.search(s[max(0,m.start()-25):m.end()+25]):es.append(dict(a=m.start(),b=m.end(),old=m[0],new=html.unescape(m[0]),rule='STANDARD_COMPLETE_HTML_ENTITY'))
  s,es=rules.apply(s,es)
  if es:stages.append(dict(name='all_complete_html_entities',edits=es))
  else:break
 if (_context_br or len(list(BR_ANCHOR.finditer(s)))>=3) and not rules.CODE.search(s):
  es=[dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='COHERENT_REPEATED_BARE_BR_LAYOUT') for m in BR_ALL.finditer(s)];s,es=rules.apply(s,es)
  if es:stages.append(dict(name='complete_bare_br_layout',edits=es))
 s,rest=base_normalize(s);return s,stages+rest
rules.normalize=normalize
base_old_spans=engine.source_old_spans
_parent_norm=[]
def source_old_spans(before,s):
 global _parent_norm
 clean,_parent_norm=normalize(before)
 return base_old_spans(clean,s)
engine.source_old_spans=source_old_spans
base_task=rules.is_task
def is_task(t):
 core=rules.ADVERB.sub('',rules.cleantext(t))
 if re.match(r'^参加(?!过)(?:班组|安全|业务|工作|生产|班前|项目|会议|培训|学习|验收|评审|招聘|定期)',core) and not rules.HARDQUAL.search(t):return True
 return base_task(t)
rules.is_task=is_task
base_decide=rules.decide
def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if re.fullmatch(r'(?:br)+',t):return 'S','ISOLATED_LAYOUT_TOKEN'
 return base_decide(text,role,previous)
rules.decide=decide
original_applicable=applicable
def applicable(raw):
 return original_applicable(raw) or bool(ENTITY_ALL.search(raw) and re.search('&(?!nbsp;|amp;|lt;|gt;|quot;|apos;|#)',raw)) or len(list(BR_ANCHOR.finditer(raw)))>=3 or bool(re.search(r'(?:积极|主动|定期|按时)?参加(?:班组|安全|业务|工作|生产|班前|项目|会议|培训|学习|验收|评审|招聘|定期)',raw))
def process(raw,row):
 global _context_br,_parent_norm
 _context_br=len(list(BR_ANCHOR.finditer(raw)))>=3;_parent_norm=[]
 p=engine.process(raw,row);p['policy_version']='R11_V2_SOURCE_LAYOUT_AND_EXPLICIT_ACTOR';p['parent_alignment_normalization']=_parent_norm
 _context_br=False;return p
# Legacy saved bodies sometimes contain standalone br lines or trailing br.
# The source must already establish a repeated layout convention.
BR_ALL=re.compile(BR_ALL.pattern+r'|(?<![A-Za-z])(?:br)+(?=\s*(?:\n|$))')
BR_ALL=re.compile(BR_ALL.pattern.replace('(?:br)+','(?:br)+(?![A-Za-z])'))
# Add a delimiter only to already proven bare list ordinals, never quantities.
base_normalize_v2=rules.normalize
def normalize(raw):
 s,stages=base_normalize_v2(raw)
 ms=list(re.finditer(r'(?m)^(\d{1,2})(?=组织|生产车间|协调|负责|协助|完成|进行|操作|整理|维护|开发|设计|编制)',s))
 if _context_br and len(ms)>=2 and any(int(b[1])==int(a[1])+1 for a,b in zip(ms,ms[1:])):
  es=[dict(a=m.start(),b=m.end(),old=m[0],new=m[0]+'、',rule='COHERENT_BARE_ORDINAL_DELIMITER') for m in ms];s,es=rules.apply(s,es)
  if es:stages.append(dict(name='bare_ordinal_delimiter',edits=es))
 return s,stages
rules.normalize=normalize
