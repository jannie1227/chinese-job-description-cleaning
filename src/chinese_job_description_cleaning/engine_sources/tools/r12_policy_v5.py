"""Final scoped repairs after the V4 full-source baseline.

Every record is screened. A selected original is fully re-extracted; the
selection reasons and unchanged baseline are retained in the final receipt.
"""
import re,html,functools,json,hashlib
from pathlib import Path
from tools import r12_policy_v4 as v4
from tools.r11_verify_release import replay
v3=v4.v3;v2=v4.v2;v1=v4.v1;rules=v4.rules;engine=v4.engine
BASE_HEAD=rules.headings;BASE_NORM=rules.normalize;BASE_DECIDE=rules.decide;BASE_SPLIT=rules.split_mixed;BASE_TASK=rules.is_task
REVIEW_PATH=Path(__file__).resolve().parents[2]/'05_后续任务输出/三类共性问题修正_R12_20260928/V5完整原文定案补丁.json'
REVIEWS={x['raw_sha256']:x for x in BUNDLED_RESOURCES['v5_reviews']}
RAW_SIGNAL=re.compile(r'资格要求|上岗要求|职们要求|培养方向|培养期|厂购会|按时.{0,18}公司总部|主要在.{0,25}从事|熟练(?:进行|应用)|能(?:够)?(?:独立或|独立完|发现问题)|我们的优势|生活环境|(?:创立|成立)于\d{4}|(?<=[\u3400-\u9fff])[?？](?=[\u3400-\u9fff])|制作.{0,15}节日|培训期|具备.{0,35}能力[,，].{0,5}开展|(?:熟悉|熟知).{0,30}(?:付款方式|帐务|账务|加盟政策|企业文化|紧急事件)',re.I)
BODY_SIGNAL=re.compile(r'工作时间|资格要求|上岗要求|职们要求|薪资|福利|吃苦耐劳|坐姿为主|重体力|老员工带|家乡城市|调剂|(?:接受|适应).{0,20}出差|投简历|欢迎|创立于|作业员|装配工|储备干部|有一定的.{0,20}基础|结果导向|组建团推|来\s*自|更多数据|职能类|主要职责包括|(?m:^\s*(?:次要|导购|0[、.]|\d+:|\d+[、,]\d+[、,]|职责[一二三四五六七八九十]+|\*\s))|熟(?:悉|知|练)|精通|掌握',re.I)
QHEAD=re.compile(r'任职要求|任职资格|岗位要求|职位要求|资格要求|上岗要求|工作要求|应聘要求')
RHEAD=re.compile(r'岗位职责|工作职责|职责描述|工作内容|岗位内容')
def applicability(raw,body):
 reasons=[]
 if hashlib.sha256(raw.encode()).hexdigest() in REVIEWS:reasons.append('EXACT_COMPLETE_SOURCE_ADJUDICATION')
 if RAW_SIGNAL.search(raw):reasons.append('RAW_STRUCTURAL_OR_TASK_PATTERN')
 if BODY_SIGNAL.search(body) or '地点不限' in body:reasons.append('RETAINED_NON_DUTY_OR_SCOPE_PATTERN')
 # A whole saved line also in the trailing applicant block warrants inspection.
 # This is a trigger, never an instruction to drop that line.
 s=v4.engine.folded(raw);qs=list(QHEAD.finditer(s))
 if qs:
  q=s[qs[-1].end():];r=RHEAD.search(q)
  if r:q=q[:r.start()]
  compact=lambda t:re.sub(r'[\W_]+','',t)
  q=compact(q)
  if any(5<=len(z:=compact(line))<=100 and z in q for line in body.splitlines()):reasons.append('RETAINED_LINE_IN_APPLICANT_BLOCK')
 return reasons

for name,role in {'资格要求':'Q','上岗要求':'Q','职们要求':'Q','生活环境':'B','我们的优势':'B','我们向你提供':'B','基层培养期':'R','主管锻炼期':'R','经理提升期':'R','总经理的高端晋升期':'R'}.items():rules.HROLE[name.lower()]=role
rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)
EXTRA_HEAD=re.compile(r'(资格要求|上岗要求|职们要求|生活环境|我们的优势|我们向你提供|工作时间)\s*[】\]]?\s*[:：]?')
def headings(s):
 hs=BASE_HEAD(s)
 for m in EXTRA_HEAD.finditer(s):
  a,b=m.span()
  if m[1]=='工作时间' and ':' not in m[0]:continue
  if a and s[a-1] in '[【':a-=1
  if any(h['a']<=a and b<=h['b'] for h in hs):continue
  hs=[h for h in hs if not(h['a']<b and a<h['b'])];hs.append(dict(a=a,b=b,role='A' if m[1]=='工作时间' else rules.HROLE[m[1]],name=m[1]))
 return sorted(hs,key=lambda h:(h['a'],h['b']))
rules.headings=headings

def normalize(raw):
 s,st=BASE_NORM(raw);es=[]
 review=REVIEWS.get(hashlib.sha256(raw.encode()).hexdigest())
 if review:
  assert review['raw']==raw
  for r in review['normalization']:
   for m in re.finditer(re.escape(r['old']),s):es.append(dict(a=m.start(),b=m.end(),old=m[0],new=r['new'],rule='R12V5_REVIEWED_TECHNICAL_TOKEN_SEPARATOR'))
  s,es=rules.apply(s,es)
  if es:st.append(dict(name='reviewed_literal_token_spacing',edits=es))
  es=[]
 # These are explicit repeated list/section markers, not numerical quantities.
 for m in re.finditer(r'(?m)(?:(?<=^)|(?<=[。;；\n:]))\s*(?:职责[一二三四五六七八九十]+[:：]+|0[、.]\s*|[1-9]\d?[:：](?=[\u3400-\u9fff]))',s):
  es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='R12V5_EXPLICIT_ORDINAL_LAYOUT'))
 for m in re.finditer(r'(?m)^\s*\*\s+(?=[\u3400-\u9fff])',s):es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='R12V5_ASTERISK_BULLET'))
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='r12v5_list_layout',edits=es))
 return s,st
rules.normalize=normalize

EXPLICIT_TASK=re.compile(r'^(?:(?:按时|按质|按量)[、,，]?)+(?:完成|提交|编写)|^(?:主要|日常)?在.{1,30}从事.{2,}|^熟练(?:进行.{2,}|应用.{1,35}(?:进行|编制|绘制|完成).{2,})|^能(?:够)?(?:独立或带领团队完成|独立完(?=现场)|发现问题并).{2,}|^.{0,45}制作宣传(?:节日|节气|新闻).{1,}')
NEGATIVE=re.compile(r'^(?:能(?:够)?吃苦耐劳|遇事懂得思考|有(?:一定|较强|良好)的.{0,30}基础|执行结果导向|目标导向及结果导向思维|服从公司调剂|急需储备干部|作业员[。;；]*$|产品装配工[。;；]*$|坐姿为主|无重体力劳动|没经验前期有老员工带|可根据员工家乡城市|同样享受国家|我们欢迎.{0,40}回家|本职位需要.{0,40}培训|注[:：]负责.{1,15}区域|地点不限|组建团推[。;；]*$)')
TRAVEL=re.compile(r'^(?:能(?:够)?|可以?|愿意)?接受(?:经常|长期|短期|频繁)?出差[。;；,，]*$')
PROFILE=re.compile(r'^(?!负责|协助|参与|管理|监督|制定|跟进|推动|组织).{1,40}(?:创立|成立|诞生)于\d{4}年')
EMPTY_META=re.compile(r'^(?:来\s*自|更多数据\s*[,，]?\s*详见|职能类|(?:该职位的)?主要职责包括|次要|导购)[。;；,，:：]*$')
SOFT_KNOWLEDGE=re.compile(r'^熟练(?:使用|掌握|应用).{1,80}(?:SQL语句|Linux基本命令|编程语言|软件工具)(?:[、,，].*)?$',re.I)
INFO=re.compile(r'^(?:熟悉|熟知)(?:所有付款方式|帐务的处理|账务的处理|公司全品牌加盟政策|司企业文化)|^熟知所有关于紧急事件的处理计划')
def is_task(t):return bool(EXPLICIT_TASK.match(v1.strip_clause(t))) or BASE_TASK(t)
rules.is_task=is_task

def decide(text,role,previous=None):
 t=v1.strip_clause(text)
 if EMPTY_META.fullmatch(t.strip('()[] ')):return 'S','R12V5_ORPHAN_METADATA_OR_HEADING'
 if t.strip('()[] 。;；')=='项目地' or re.match(r'^\d*:?一个月出差\d+天',t):return 'N','R12V5_LOCATION_AND_SHIFT_SCHEDULE'
 if NEGATIVE.match(t) or TRAVEL.fullmatch(t):return 'N','R12V5_EXPLICIT_APPLICANT_ENVIRONMENT_OR_RECRUITMENT'
 if PROFILE.match(t):return 'N','R12V5_BRAND_HISTORY_PREFACE'
 if len(re.findall(r'(?<=[\u3400-\u9fff])\?(?=[\u3400-\u9fff])',t))>=2:return 'X','R12V5_MULTIPLE_UNRECOVERABLE_WORD_GAPS'
 if SOFT_KNOWLEDGE.match(t) and not re.search(r'(?:进行|完成|编写|制作|生成|开发|设计).{2,}',t):return 'N','R12V5_SOFTWARE_PROFICIENCY_WITHOUT_ASSIGNED_ACTION'
 if EXPLICIT_TASK.match(t) and role not in {'Q','Q_FIELD','B','OFFER','NOTICE','COMPETENCY'} and not rules.DAMAGE.search(t):return 'R','R12V5_COMPLETE_MODAL_OR_NOMINAL_ASSIGNED_WORK'
 if role=='R' and INFO.match(t):return 'R','R12V5_IN_ROLE_BUSINESS_PREPARATION'
 return BASE_DECIDE(text,role,previous)
rules.decide=decide

def split_mixed(s,a,b,role):
 cs=v1.clauses(s,a,b);points={a,b};full=v1.strip_clause(s[a:b]);first=v1.strip_clause(s[cs[0][0]:cs[0][1]]) if cs else ''
 for lo,hi in BASE_SPLIT(s,a,b,role):points.update((lo,hi))
 if role in {'Q','Q_FIELD'} and (v1.KNOW.match(first) or re.search(r'(?:等)?相关专业[。;；,，]*$',full)):
  safe=[lo for lo,hi in cs[1:] if re.match(r'^(?:负责(?!过|人)|协助|开展|主导|承担(?!过)|严格按照|处理|实现)',v1.strip_clause(s[lo:hi])) and not re.search(r'能力|经验|经历',s[lo:hi])]
  return list(zip(sorted({a,b,*safe}),sorted({a,b,*safe})[1:]))
 for i,(lo,hi) in enumerate(cs):
  t=v1.strip_clause(s[lo:hi])
  if NEGATIVE.match(t) or TRAVEL.fullmatch(t) or role=='R' and EXPLICIT_TASK.match(t):points.add(lo)
  if t.strip(' ,，。;；')=='地点不限':points.add(hi)
  if role=='R' and i and NEGATIVE.match(v1.strip_clause(s[a:lo])) and re.match(r'^(?:对.{1,30}进行|负责|协助|完成|开展)',t):points.add(lo)
  if role in {'Q','Q_FIELD'} and i and re.match(r'^开展.{2,30}工作',t):points.add(lo)
 if role=='R' and re.match(r'^熟悉8D[,，]',full):return [(a,b)]
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

BASE_FINISH=rules.finish_body
def finish_body(body):
 s,st=BASE_FINISH(body);es=[]
 for m in re.finditer(r'(?m)^\s*(?:0[、.]\s*|([1-9]\d?)[、,]\1[、,]\s*|\*\s+)',s):es.append(dict(a=m.start(),b=m.end(),old=m[0],new='',rule='R12V5_RESIDUAL_PROVEN_LIST_MARKER'))
 cols=list(re.finditer(r'(?m)^\s*\d{1,2}:(?=[\u3400-\u9fff])',s))
 if len(cols)>=2:
  for m in cols:es.append(dict(a=m.start(),b=m.end(),old=m[0],new='',rule='R12V5_REPEATED_COLON_ORDINAL'))
 captions=list(re.finditer(r'(?:^|(?<=\s))职责[一二三四五六七八九十]+(?::+|(?=\n|$))',s))
 if len(captions)>=2:
  for m in captions:es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='R12V5_NUMBERED_DUTY_CAPTION'))
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='r12v5_residual_layout',edits=es))
 es=[dict(a=m.start(),b=m.end(),old=m[0],new='',rule='R12V5_EMPTY_OR_DUPLICATED_LEADING_CAPTION') for m in re.finditer(r'(?m)^主要负责:(?=负责)|[ \t]+(?=\n|$)',s)]
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='r12v5_line_edge_cleanup',edits=es))
 return s,st
rules.finish_body=finish_body

def _overlay(p,s,changes):
 points={0,len(s)}
 for u in p['partition']:points.update((u['a'],u['b']))
 for c in changes:points.update((c['a'],c['b']))
 result=[];j=0
 for a,b in zip(sorted(points),sorted(points)[1:]):
  while p['partition'][j]['b']<=a:j+=1
  u=dict(p['partition'][j],a=a,b=b)
  for c in changes:
   if c['a']<=a<b<=c['b']:u.update(label=c['label'],reason=c['reason'])
  result.append(u)
 p['partition']=result

@functools.lru_cache(maxsize=8192)
def _cached(raw):
 # Clear the baseline cache between policies by using its private uncached body.
 p=v4._cached.__wrapped__(raw);s,_=replay(raw,p['normalization']);changes=[]
 duty_heads=[h for h in headings(s) if h['role']=='R'];first_duty=duty_heads[0]['a'] if duty_heads else None
 if first_duty and PROFILE.match(v1.strip_clause(s[:first_duty])):changes.append(dict(a=0,b=first_duty,label='N',reason='R12V5_COMPLETE_BRAND_HISTORY_BEFORE_EXPLICIT_DUTIES'))
 for u in p['partition']:
  if u['label']=='S':continue
  t=s[u['a']:u['b']];lab,why=decide(t,u.get('section'))
  if why.startswith('R12V5_'):u.update(label=lab,reason=why)
  if u.get('section')=='R' and re.match(r'^熟悉8D[,，]',v1.strip_clause(t)):u.update(label='N',reason='R12V5_SKILL_LIST_WITH_SHARED_KNOWLEDGE_PREDICATE')
 # A knowledge-led item with explicit experience/ability remains an eligibility
 # item, even when its source section is mislabeled as responsibilities.
 groups=[];group=[]
 for u in p['partition']:
  if u['label']=='S' and ('MARKER' in u['reason'] or 'ORDINAL' in u['reason'] or u['reason']=='EXPLICIT_SECTION_HEADING'):
   if group:groups.append(group);group=[]
  elif u['label']!='S':group.append(u)
 if group:groups.append(group)
 for group in groups:
  whole=''.join(s[u['a']:u['b']] for u in group);first=v1.strip_clause(whole)
  if v1.KNOW.match(first) and re.search(r'经验|经历|能力',whole):
   for u in group:
    if u['label']=='R' and v1.KNOW.match(v1.strip_clause(s[u['a']:u['b']])):u.update(label='N',reason='R12V5_KNOWLEDGE_GOVERNED_BY_EXPLICIT_EXPERIENCE_ITEM')
 # Explicit duties after a career-direction title are work, not the title.
 for m in re.finditer(r'培养方向\s*[:：]\s*[^。;；\n]{1,28}?工程师\s+(?P<t>[^。\n]+[。]?)',s):
  t=m['t']
  if re.search(r'推广|技术支持|收集|翻译|编制|客户|负责',t):changes.append(dict(a=m.start('t'),b=m.end('t'),label='R',reason='R12V5_ACTUAL_WORK_AFTER_CAREER_DIRECTION_TITLE'))
 review=REVIEWS.get(hashlib.sha256(raw.encode()).hexdigest())
 if review:
  assert review['raw']==raw
  for d in review['decisions']:
   matches=list(re.finditer(re.escape(d['text']),s));assert len(matches)==1,(review['draw_index'],d['text'],s)
   m=matches[0];changes.append(dict(a=m.start(),b=m.end(),label=d['label'],reason=d['reason']))
 if changes:_overlay(p,s,changes)
 engine.rebuild(p,s);p.update(proposed_after=p['after'],adopted=True,preserve_parent_reason=None,policy_version='R12_V5_FINAL_SCOPED_SOURCE_REPAIRS')
 return p
def process(raw,row):
 p=dict(_cached(raw));before=row['responsibility_text'];p.update(record_id=row['record_id'],before=before,before_sha256=engine.digest(before.encode()),text_changed=p['after']!=before,parent_role='COMPARISON_ONLY_NOT_CLASSIFICATION');return p
