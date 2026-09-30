"""Final eligibility-boundary fixes and original-source reconstruction."""
import re
from tools import r11_policy_v4 as v4
from tools.r11_io import *
engine=v4.engine;rules=v4.rules;v3=v4.v3
BASE_SPANS=engine.source_old_spans;BASE_QUAL=rules.qualification;BASE_DECIDE=rules.decide;BASE_SPLIT=rules.split_mixed
ADAPT=re.compile(r'^(?:能(?:够)?|可)?适应.{0,20}(?:出差|倒班|加班|工作时间|工作节奏|工作压力|工作强度)[。;；]?$')
FLUENT_REVERSED=re.compile(r'^[^,，;；。]{1,65}(?:操作|使用|应用|运用)(?:比较|较为)?熟练(?=[,，;；。]|$)')
PERSON_SKILL=re.compile(r'培养|培训|指导|帮助|使其|让|提高|提升|确保|保证|考核|评估')
TITLE=re.compile(r'^.{1,40}负责人[。;；]?$')

def source_old_spans(before,s):
 clean=engine.folded(before).replace('\xa0',' ');prefix=[]
 if before and clean!=before:prefix=[dict(name='parent_representation_whitespace_and_width',edits=[dict(a=0,b=len(before),old=before,new=clean,rule='PARENT_ALIGNMENT_ONLY_EQUIVALENT_ENTITY_WIDTH_WHITESPACE')])]
 spans,missing=BASE_SPANS(clean,s);v3._parent_events=prefix+v3._parent_events;return spans,missing
engine.source_old_spans=source_old_spans

def qualification(t):
 t=rules.cleantext(t)
 if ADAPT.match(t) or (FLUENT_REVERSED.match(t) and not PERSON_SKILL.search(re.split('[,，;；。]',t,1)[0])):return True
 return BASE_QUAL(t)
rules.qualification=qualification

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if ADAPT.match(t):return 'N','APPLICANT_TRAVEL_SHIFT_OR_WORKLOAD_ADAPTABILITY'
 if FLUENT_REVERSED.match(t) and not PERSON_SKILL.search(re.split('[,，;；。]',t,1)[0]):return 'N','REVERSED_PERSONAL_PROFICIENCY_STATEMENT'
 if TITLE.match(t) and not re.match(r'^(?:负责|协助|培养|培训|指导|招聘|支持|帮助|担任|配合|作为)',t):return 'N','STANDALONE_JOB_HOLDER_TITLE'
 return BASE_DECIDE(text,role,previous)
rules.decide=decide

def split_mixed(s,a,b,role):
 ints=BASE_SPLIT(s,a,b,role);points={a,b}
 for lo,hi in ints:points.update((lo,hi))
 for lo in list(points-{a,b}):
  prefix=rules.cleantext(s[a:lo]);right=rules.cleantext(s[lo:b])
  if rules.HARDQUAL.search(prefix) and qualification(prefix) and re.match(r'^(?:能(?:够)?|可)(?:独立|高效|熟练|有效|正确|快速|及时|准确)*(?:完成|开发|设计|操作|使用|处理|分析|判断|维护|协助|协调|制定|识别)',right):points.discard(lo)
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

def process(raw,row):
 p=v4.process(raw,row);p['policy_version']='R11_V5_ORIGINAL_SOURCE_FINALIZATION'
 if p['source_alignment_uncovered']:
  # An unlocatable prior output is retained as historical evidence, not allowed
  # to veto a fully source-traced reconstruction of this record's original.
  p['historical_parent_alignment_gaps']=p['source_alignment_uncovered'];p['source_alignment_uncovered']=[];p['parent_alignment_resolution']='REBUILT_FROM_COMPLETE_ORIGINAL';p['after']=p['proposed_after'];p['adopted']=True;p['text_changed']=p['after']!=p['before'];p['preserve_parent_reason']=None
  nx=p['excluded_fragment_count'];p['status']=('DUTIES_WITH_SOURCE_LIMIT' if nx else 'DUTIES_RETAINED') if p['after'].strip() else ('NO_USABLE_DUTIES_SOURCE_LIMIT' if nx else 'NO_EXPLICIT_DUTIES')
 return p

def applicable_row(raw,row):
 # These new negative rules can only change a currently retained matching
 # literal term; every old-alignment exception is included without exception.
 t=engine.flat(row['responsibility_text'])
 return row['r11_group']=='PRIOR_ALIGNMENT_PRESERVED' or any(x in t for x in ['适应','熟练','能','可','负责人'])

# A common caption word embedded in a sentence is an object, not a new field.
BASE_HEADS=rules.headings
GENERIC_CAPTIONS={'工作任务','工作内容','技术要求','工作制度','工作时间','职责','内容','要求','技能','待遇','福利'}
OBJECT_END=re.compile(r'(?:其他|其它|相关|这些|各项|相应|上述|本岗|本岗位|日常|所需|明确|具体|该|此|其)\s*$')
OBJECT_VERB=re.compile(r'(?:完成|承担|处理|执行|履行|做好|负责|根据|按照|明确|界定|编制|制定|符合|满足|遵守|了解|熟悉|掌握|修改|优化|改善|培训|组织)(?:相关|这些|各项|相应|具体|明确|的)?\s*$')
for h,r in {'基本职责':'R','业务技能要求':'Q_FIELD','专业知识要求':'Q_FIELD','专业知识及技能':'Q_FIELD','专业知识及技能要求':'Q_FIELD','我们为员工提供':'OFFER','你将受益匪浅':'OFFER','职位福利':'OFFER','职位亮点':'OFFER','负责产品':'A','职位':'A','隶属':'A','服务区域':'A'}.items():rules.HROLE[h.lower()]=r
rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)

DETACHED_HEAD=re.compile(r'(?<!\S)('+'|'.join(sorted([re.escape(k) for k in rules.HROLE if len(k)>=4 and re.fullmatch('[\u3400-\u9fff]+',k)],key=len,reverse=True))+r')(?=\s+\S)')
def headings(s):
 out=[]
 for h in BASE_HEADS(s):
  pre=s[:h['a']]
  if h['name'] in GENERIC_CAPTIONS and ((pre and re.search('[\u3400-\u9fffA-Za-z]$',pre)) or OBJECT_END.search(pre) or OBJECT_VERB.search(pre)):continue
  out.append(h)
 for m in DETACHED_HEAD.finditer(s):
  if any(h['a']<=m.start()<h['b'] for h in out):continue
  pre=s[max(0,m.start()-30):m.start()]
  if OBJECT_END.search(pre) or OBJECT_VERB.search(pre):continue
  out.append(dict(a=m.start(),b=m.end(),role=rules.HROLE[m[1].lower()],name=m[1]))
 return sorted(out,key=lambda h:(h['a'],h['b']))
rules.headings=headings

# Generic labels followed by alternate colon typography are still labels;
# mathematical ratios elsewhere are not touched.
BASE_NORMAL=rules.normalize

def normalize(raw):
 s,st=BASE_NORMAL(raw);es=[]
 for m in re.finditer(r'(?:岗位职责|工作职责|职责描述|任职要求|任职资格|岗位要求|职位要求)\s*∶',s):es.append(dict(a=m.end()-1,b=m.end(),old='∶',new=':',rule='CAPTION_ONLY_ALTERNATE_COLON'))
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='caption_colon_typography',edits=es))
 # Circled ordinal glyphs are layout; their values are preserved in the log.
 es=[dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='CIRCLED_LIST_MARKER') for m in re.finditer('[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]',s)]
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='circled_list_layout',edits=es))
 return s,st
rules.normalize=normalize
D5=rules.decide;Q5=rules.qualification;TASK5=rules.is_task;OP5=rules.operational_knowledge

def is_task(t):
 t=rules.cleantext(t)
 if re.match(r'^(?:以及|并且|并|同时)',t):
  rest=re.sub(r'^(?:以及|并且|并|同时)\s*','',t)
  if TASK5(rest):return True
 if re.match(r'^独立自主(?:地)?进行.{2,}',t):return True
 return TASK5(t)
rules.is_task=is_task

def operational_knowledge(t):return OP5(t) or bool(re.match(r'^(?:及时|充分|全面)?(?:掌握|了解|熟悉)',t) and re.search('市场信息|业务进展|客户动态',t) and not re.search('能力|经验|知识|技巧|软件|工具|规则|流程',t))
rules.operational_knowledge=operational_knowledge

def qualification(t):
 t=rules.cleantext(t)
 if re.match(r'^(?:能|可)(?:接受|适应).{0,20}(?:出差|倒班|加班|工作压力|工作强度)',t):return True
 if re.match(r'^[^,，;；。]{0,18}(?:岗位|职位)要求[^,，;；。]{0,35}(?:学历|中专|大专|本科|硕士|博士)',t):return True
 if re.match(r'^有[^。;；]{0,120}(?:经验|经历)',t):return True
 return Q5(t)
rules.qualification=qualification

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if re.match(r'^(?:能|可)(?:接受|适应).{0,20}(?:出差|倒班|加班|工作压力|工作强度)',t):return 'N','APPLICANT_TRAVEL_OR_SCHEDULE_ACCEPTANCE'
 if re.match(r'^[^,，;；。]{0,18}(?:岗位|职位)要求[^,，;；。]{0,35}(?:学历|中专|大专|本科|硕士|博士)',t) and not re.match('负责|协助|制定|编制|设计',t):return 'N','EXPLICIT_POSITION_ELIGIBILITY_STATEMENT'
 if re.match(r'^有[^。;；]{0,120}(?:经验|经历)',t):return 'N','PERSONAL_EXPERIENCE_WITH_MULTIPLE_OBJECTS'
 if role in {'Q','Q_FIELD',None} and re.match(r'^能(?:建立|使用|全力配合)',t):return 'N','PERSONAL_CAPABILITY_WITHOUT_CURRENT_ASSIGNMENT'
 if role in {'Q','Q_FIELD'} and re.search(r'(?:领导|负责|参与|开发|管理)过(?!程|账|户|期|渡)',t[:70]) and not re.match('检查|核查|审核|统计|确认',t):return 'N','EXPLICIT_PAST_PROJECT_OR_LEADERSHIP_EXPERIENCE'
 if re.match(r'^(?:中国|亚洲|全球|世界|国内).{0,90}(?:企业|公司|供应商|品牌)(?:之一)?[。;；]?$',t) and re.search('规模|最强|领先|盈利|最大|知名',t):return 'N','EMPLOYER_SCALE_OR_MARKET_POSITION'
 if re.match(r'^(?:新入职人员福利|入职人员福利)',t):return 'N','NEW_EMPLOYEE_BENEFIT_DESCRIPTION'
 if re.match(r'^(?:怎么做\?|工作模式\?).*我们的客户',t) or re.match(r'^我们的客户.{0,25}(?:百分之|主动申请)',t):return 'N','RECRUITMENT_CUSTOMER_RESOURCE_EXPLANATION'
 if re.match(r'^是正编还是借聘',t):return 'N','RECRUITMENT_EMPLOYMENT_RELATIONSHIP_EXPLANATION'
 if t=='为提高沟通效率':return 'N','INCOMPLETE_RECRUITER_INTRODUCTION_PURPOSE'
 return D5(text,role,previous)
rules.decide=decide

# Only these exact source phrases alter the supplemental logic; final runner
# may use full evaluation if a conservative narrow screen is not provable.
def applicable_row(raw,row):return True

H5=rules.headings
ASSIGN_SUBJECT=re.compile(r'^(?:本岗位|该岗位|此岗位|本职位|该职位|员工|你|您)(?:主要|全面|具体|日常|需|需要)*负责')
FULL_SUBJECT=re.compile(r'(?:本岗位|该岗位|此岗位|本职位|该职位|员工)(?:主要|全面|具体|日常|需|需要)*负责')

def headings(s):
 out=H5(s);clean=[]
 for h in out:
  pre=s[:h['a']]
  # Strict end-of-string, not Python $ (which also matches before a newline).
  if h['name'] in GENERIC_CAPTIONS and pre and re.search('[\u3400-\u9fffA-Za-z]\\Z',pre):continue
  if OBJECT_VERB.search(pre) and not re.search(r'\n\s*$',pre):continue
  clean.append(h)
 # A short literal title immediately before 岗位要求 is not a duty statement.
 for h in list(clean):
  if h['name']=='岗位要求':
   prefix=s[:h['a']].strip()
   if 1<len(prefix)<35 and not re.search('[,，;；。\n]',prefix) and not re.match(rules.AW,prefix) and not rules.HEAD.search(prefix):clean.append(dict(a=0,b=h['a'],role='A',name='LITERAL_POSITION_TITLE_PREFIX'))
 return sorted(clean,key=lambda x:(x['a'],x['b']))
rules.headings=headings
# Repair the earlier generic-caption filter's newline handling in place by
# supplying an equivalent wrapper that restores explicit line-start captions.
H6=rules.headings

def headings(s):
 hs=H6(s)
 for m in rules.HEAD.finditer(s):
  if m[0] not in GENERIC_CAPTIONS:continue
  if not (m.start()==0 or re.search(r'\n\s*$',s[:m.start()])):continue
  if not re.match(r'\s*[:：]',s[m.end():]):continue
  if any(h['a']<=m.start()<h['b'] for h in hs):continue
  end=m.end()+re.match(r'\s*[:：]\s*',s[m.end():]).end();hs.append(dict(a=m.start(),b=end,role=rules.HROLE[m[0].lower()],name=m[0]))
 return sorted(hs,key=lambda x:(x['a'],x['b']))
rules.headings=headings
T6=rules.is_task;D6=rules.decide;S6=rules.split_mixed

def is_task(t):
 t=rules.cleantext(t)
 if ASSIGN_SUBJECT.match(t):return True
 if re.match(r'^对现有(?:设备|产品|系统|项目|工艺|流程|程序)',t) and re.search('优化|改进|改造|维护|调整|降成本',t) and not re.search('丰富经验|经验丰富|者优先',t):return True
 return T6(t)
rules.is_task=is_task

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if ASSIGN_SUBJECT.match(t) and not qualification(t) and not rules.DAMAGE.search(t):return 'R','EXPLICIT_CURRENT_EMPLOYEE_OR_POSITION_ASSIGNMENT'
 if role=='R' and re.match(r'^能(?:够)?(?:为.{1,25}提供|(?:独立|及时|有效)*举办).{2,}',t) and not rules.HARDQUAL.search(t) and not rules.DAMAGE.search(t):return 'R','EXPLICIT_CURRENT_SERVICE_OR_EVENT_DUTY'
 if re.match(r'^(?:上班可带手机|工作轻松|更多普工招聘)',t):return 'N','RECRUITMENT_CONDITION_OR_ADVERTISEMENT'
 return D6(text,role,previous)
rules.decide=decide

def split_mixed(s,a,b,role):
 ints=S6(s,a,b,role);points={a,b}
 for lo,hi in ints:points.update((lo,hi))
 t=s[a:b]
 for m in re.finditer(r'负责(?!过|人|心)|协助',t):
  pos=a+m.start();pre=rules.cleantext(s[a:pos]);tail=rules.cleantext(s[pos:b])
  if pre and re.search(r'(?:专业|学历|经验|专业背景)$',pre) and qualification(pre) and not re.search(r'(?:经验|能力|知识|技能)[。;；]?$',tail):points.add(pos)
 for m in FULL_SUBJECT.finditer(t):
  points.add(a+m.start())
  end=re.search(r'上班可带手机|工作轻松|更多普工招聘',s[a+m.end():b])
  if end:points.add(a+m.end()+end.start())
 cs=rules._clauses(s,a,b)
 for i in range(1,len(cs)):
  lo,hi=cs[i];left=rules.cleantext(s[cs[i-1][0]:cs[i-1][1]]);right=rules.cleantext(s[lo:hi])
  if re.fullmatch(r'.{1,35}(?:工程师|技术员|专员|主管|经理)岗位',left) and rules.is_task(right):points.add(lo)
  if role=='R' and re.match(r'^(?:专业)?知识(?:过关|扎实|丰富)',left) and re.match(r'^能(?:够)?(?:为.{1,25}提供|(?:独立|及时|有效)*举办)',right):points.add(lo)
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

BASE_PROCESS5=process

def process(raw,row):
 p=BASE_PROCESS5(raw,row)
 # A complete task's intact conditional clause stays attached after a damaged
 # neighbour; the condition is never kept by itself without a following task.
 from tools.r11_verify_release import replay
 s,_=replay(raw,p['normalization']);us=p['partition'];changed=False
 for i,u in enumerate(us[:-1]):
  text=s[u['a']:u['b']];nxt=us[i+1]
  if u['label']=='N' and u['reason']=='SOURCE_DEPENDENT_CONTEXT_NOT_STANDALONE' and text.rstrip().endswith((',', '，')) and re.match(r'^(?:对|对于|针对|在|当|为|根据|按照|如果|若|如遇)',rules.cleantext(text)) and not rules.DAMAGE.search(text) and nxt['label']=='R' and nxt.get('heading')==u.get('heading'):
   u.update(label='R',reason='INTACT_CONDITION_ATTACHED_TO_FOLLOWING_LITERAL_TASK');changed=True
 if changed:
  engine.rebuild(p,s);p['proposed_after']=p['after'];p['adopted']=True;p['text_changed']=p['after']!=p['before'];p['preserve_parent_reason']=None
 return p

# Preserve original heading line boundaries before the inherited soft-wrap
# cleaner runs. Only known heading captions followed by a colon are protected.
N6=rules.normalize

def normalize(raw):
 names=[k for k in rules.HROLE if (re.search('[A-Za-z]',k) and re.search('[\u3400-\u9fff]',k)) or k=='通用职责']
 pattern=re.compile(r'(?:\r\n|\n|\\r\\n|\\n)(?=\s*(?:'+'|'.join(sorted(map(re.escape,names),key=len,reverse=True))+r')\s*[:：])',re.I)
 es=[dict(a=m.start(),b=m.end(),old=m[0],new=m[0]+m[0],rule='PRESERVE_EXPLICIT_BILINGUAL_HEADING_LINE_BOUNDARY') for m in pattern.finditer(raw)]
 s,es=rules.apply(raw,es);prefix=[dict(name='heading_boundary_protection',edits=es)] if es else [];s,st=N6(s);return s,prefix+st
rules.normalize=normalize

T7=rules.is_task;D7=rules.decide;S7=rules.split_mixed
BUSINESS_INFO=re.compile(r'^(?:准确|及时|充分|全面|深入)?(?:了解|掌握|熟悉)(?:客户需求|客户商务运作周期|市场信息|客户动态)')

def is_task(t):
 t=rules.cleantext(t)
 if BUSINESS_INFO.match(t) and not re.search('能力|经验|知识|优先',t):return True
 if re.match(r'^控制.{0,25}(?:费用|成本|预算|风险|参数|质量)',t) and not re.search('能力|经验|知识|优先',t):return True
 return T7(t)
rules.is_task=is_task

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if BUSINESS_INFO.match(t) and role in {None,'R'} and not re.search('能力|经验|知识|优先',t):return 'R','EXPLICIT_CURRENT_BUSINESS_INFORMATION_ACQUISITION'
 return D7(text,role,previous)
rules.decide=decide

def split_mixed(s,a,b,role):
 ints=S7(s,a,b,role);points={a,b};t=s[a:b]
 for lo,hi in ints:points.update((lo,hi))
 # Complete first object remains usable when the coordinated second object
 # contains a literal mask; no missing object is reconstructed.
 for m in re.finditer(r'(?:和|及|与)(?=\*{2,}|\ufffd)',t):
  pos=a+m.start();left=rules.cleantext(s[a:pos])
  if rules._standalone(left) and not qualification(left):points.add(pos)
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

# This explicit source text is a confirmed character-loss fragment. A generic
# question mark elsewhere is not automatically considered a missing word.
SOURCE_LOSS_LITERAL='结合公司自身资源寻找项?合作机会'
DIRECT_DUTY_LITERAL='电梯保养工作'
P7=process

def process(raw,row):
 p=P7(raw,row)
 from tools.r11_verify_release import replay
 s,_=replay(raw,p['normalization']);patches=[]
 for text,label,why in [(SOURCE_LOSS_LITERAL,'X','REVIEW_CONFIRMED_LITERAL_CHARACTER_LOSS_NOT_GUESSED')]:
  for m in re.finditer(re.escape(text),s):patches.append(dict(a=m.start(),b=m.end(),label=label,reason=why))
 # A no-experience condition ends before a literally named activity; the
 # following recruiting-area text is not part of that duty.
 for m in re.finditer(r'(?<=经验不限)电梯保养工作(?=现在招聘区域)',s):patches.append(dict(a=m.start(),b=m.end(),label='R',reason='EXPLICIT_NOMINAL_DUTY_AFTER_CLOSED_ELIGIBILITY_PHRASE'))
 if patches:
  points={0,len(s)}
  for u in p['partition']:points.update((u['a'],u['b']))
  for e in patches:points.update((e['a'],e['b']))
  new=[];j=0
  for a,b in zip(sorted(points),sorted(points)[1:]):
   while p['partition'][j]['b']<=a:j+=1
   u=dict(p['partition'][j],a=a,b=b)
   for e in patches:
    if e['a']<=a and b<=e['b']:u.update(label=e['label'],reason=e['reason'])
   new.append(u)
  p['partition']=new;engine.rebuild(p,s);p['proposed_after']=p['after'];p['adopted']=True;p['text_changed']=p['after']!=p['before'];p['preserve_parent_reason']=None;p['source_specific_literal_repairs']=patches
 return p
