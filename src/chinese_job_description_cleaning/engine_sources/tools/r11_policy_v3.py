"""Nested-list, caption-object, and legacy-alignment corrections over frozen V2."""
import re,html
from collections import defaultdict
from tools import r11_policy_v2 as v2
from tools.r11_io import *
engine=v2.engine;rules=v2.rules
base_normalize=rules.normalize;base_headings=rules.headings;base_decide=rules.decide
NESTED=re.compile(r'(?<![A-Za-z0-9.])([1-9]\d?)\.([1-9]\d?)[ \t]*(?=[\u3400-\u9fff])(?![万千百十亿年月天岁米吨元])')
_nested_context=False
_source_entity_names={}
_parent_events=[]

def nested_markers(s):
 ms=list(NESTED.finditer(s));groups=defaultdict(list)
 for m in ms:groups[int(m[1])].append(m)
 valid={k for k,v in groups.items() if len({int(m[2]) for m in v})>=2 and any(0<int(b[2])-int(a[2])<=3 for a,b in zip(v,v[1:]))}
 selected=[m for m in ms if int(m[1]) in valid]
 return selected if len(selected)>=3 else []

def normalize(raw):
 s,st=base_normalize(raw);ms=nested_markers(s)
 if ms:
  es=[dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='COHERENT_MULTI_LEVEL_LIST_MARKER') for m in ms];s,es=rules.apply(s,es);st.append(dict(name='nested_ordinals',edits=es))
 return s,st
rules.normalize=normalize

def headings(s):
 out=[]
 for h in base_headings(s):
  a,b=h['a'],h['b'];name=h['name'];pre=s[:a];post=s[b:]
  if name in {'工作制度','工作时间','团队发展','内容','技能','要求','待遇','职责'} and pre and re.search(r'[\u3400-\u9fffA-Za-z]$',pre) and not re.search(r'[:：]',s[a:b]):continue
  out.append(h)
 return out
rules.headings=headings

# Normalize each prior line separately. Cleaning a whole previous body can join
# adjacent list entries whose intervening source ordinals were already removed.
def source_old_spans(before,s):
 global _parent_events
 es=[];offset=0
 for line in before.splitlines(keepends=True):
  content=line.rstrip('\r\n');transformed=content
  for name,value in _source_entity_names.items():
   transformed=re.sub(re.escape('&'+name)+r'(?:;|(?=$|[,，]))',lambda m:value,transformed)
  transformed,_=base_normalize(transformed)
  if _nested_context:
   transformed=NESTED.sub('\n',transformed)
   transformed=re.sub(r'\d{1,2}\.\s*$','',transformed)
  if content and transformed!=content:es.append(dict(a=offset,b=offset+len(content),old=content,new=transformed,rule='SOURCE_PROVEN_LEGACY_LAYOUT_FOR_ALIGNMENT_ONLY'))
  offset+=len(line)
 clean,events=rules.apply(before,es);_parent_events=[dict(name='prior_line_layout_only',edits=events)] if events else []
 return v2.base_old_spans(clean,s)
engine.source_old_spans=source_old_spans
EMPLOYER_HISTORY=re.compile(r'^(?:自(?:公司)?成立以来|自成立至今|经过.{0,12}发展|经相关监管部门批准|截至\d{4}年|为实现对优秀人才的系统培养)')
EMPLOYER_SENTENCE=re.compile(r'(?:公司|企业|集团|证券|银行).{0,22}(?:建立了良好的声誉|连续.{0,8}被|评为|主要业务范围|各项业务快速发展|核心业务优势|推出.{0,12}培养)')

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if role in {None,'C','B','A'} and (EMPLOYER_HISTORY.match(t) or EMPLOYER_SENTENCE.search(t)) and not re.match(r'^(?:负责|协助|你将|您将)',t):return 'N','EXPLICIT_EMPLOYER_HISTORY_SCALE_OR_TRAINING_PROMOTION'
 if re.match(r'^通过.{0,35}(?:从业资格|执业资格|职业资格).{0,10}考试',t):return 'N','APPLICANT_CERTIFICATION_EXAM'
 if role=='Q' and re.match(r'^(?:从事|担任|任职|工作).{0,70}(?:\d+|[一二三四五六七八九十两]+)年(?:以上|及以上|$|[,，;；。])',t):return 'N','EXPLICIT_PAST_EMPLOYMENT_DURATION'
 if re.fullmatch(r'在提升自我专业能力的同时',t):return 'N','DEPENDENT_EMPLOYER_PROMOTION_PREFIX'
 return base_decide(text,role,previous)
rules.decide=decide

def applicable(raw):
 return v2.applicable(raw) or bool(nested_markers(raw)) or bool(re.search('工作制度|工作时间|自成立以来|主要业务范围|从业资格.{0,10}考试|为实现对优秀人才的系统培养',raw))

def process(raw,row):
 global _nested_context,_source_entity_names,_parent_events
 _nested_context=bool(nested_markers(raw));_source_entity_names={m[0][1:-1]:html.unescape(m[0]) for m in v2.ENTITY_ALL.finditer(raw) if html.unescape(m[0])!=m[0]};_parent_events=[]
 v2._context_br=len(list(v2.BR_ANCHOR.finditer(raw)))>=3
 p=engine.process(raw,row);p['policy_version']='R11_V3_NESTED_LIST_AND_LEGACY_ALIGNMENT';p['parent_alignment_normalization']=_parent_events
 v2._context_br=False;_nested_context=False;return p

# Additional mechanisms exposed by the frozen first fresh risk sample.
_base_norm3=rules.normalize
LETTER_LIST=re.compile(r'(?<![A-Za-z0-9])l(?=[\u3400-\u9fff0-9])')
LETTER_HEADING=re.compile(r'(岗位职责|职责描述|工作职责|任职要求|任职资格)l')
EN_BR=re.compile(r'(?:br)+(?=\s|Responsibilities|Qualifications|Requirements|Key Skills|[;；。\]}]|$)')
BARE_NUMBER=re.compile(r'(?<![A-Za-z0-9.])([1-9]\d?)(?=严格|对疑难|对客户|按照|负责|做好|定期|主动|其他与|组织|协助|完成|参与|指导|检查|维护|开发|设计|编制)')

def _wrapper(s):
 a=len(s)-len(s.lstrip());b=s.rfind(']')
 if a<len(s) and s[a]=='[' and b>a:
  tail=s[b+1:].strip();tail=rules.SOURCE.sub('',tail).strip(rules.PUNCT+'()')
  return (a,b) if not tail and re.search('岗位职责|职责描述|任职要求|任职资格',s[a:b]) else None
 return None

def normalize(raw):
 s=raw;st=[]
 def stage(es,name):
  nonlocal s
  s,es=rules.apply(s,es)
  if es:st.append(dict(name=name,edits=es))
 if LETTER_HEADING.search(s) and len(list(LETTER_LIST.finditer(s)))>=3:
  es=[dict(a=m.start(),b=m.end(),old=m[0],new='\n'+m[1]+':\n',rule='HEADING_WITH_REPEATED_LETTER_LIST_MARKER') for m in LETTER_HEADING.finditer(s)]
  es += [dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='COHERENT_LETTER_LIST_MARKER') for m in LETTER_LIST.finditer(s)];stage(es,'letter_list')
 if len(list(EN_BR.finditer(s)))>=3 and re.search(r'Responsibilities|Qualifications?|Key Skills',s,re.I) and not rules.CODE.search(s):
  stage([dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='REPEATED_ENGLISH_BARE_BR_LAYOUT') for m in EN_BR.finditer(s)],'english_br')
 s,rest=_base_norm3(s);st.extend(rest)
 # A single source wrapper around the entire job ad is layout, not an example.
 wrap=_wrapper(s)
 if wrap:
  stage([dict(a=i,b=i+1,old=s[i],new='',rule='WHOLE_DESCRIPTION_WRAPPER') for i in wrap],'source_outer_wrapper')
 ms=list(BARE_NUMBER.finditer(s))
 if len(ms)>=3 and sum(int(y[1])==int(x[1])+1 for x,y in zip(ms,ms[1:]))>=2:
  stage([dict(a=m.start(),b=m.end(),old=m[0],new='\n'+m[0]+'、',rule='COHERENT_BARE_NUMBER_LIST_DELIMITER') for m in ms],'bare_number_list')
 es=[]
 for m in re.finditer(r'(?<=[A-Za-z])\.(?=\s*(?:[A-Z][a-z]|I\s))',s):
  if re.search(r'(?:\be\.g|\bi\.e|\bMr|\bMrs|\bDr|\bProf|\bvs|\bU\.S)$',s[max(0,m.start()-10):m.start()],re.I):continue
  if not rules.CODE.search(s[max(0,m.start()-35):m.end()+35]):es.append(dict(a=m.start(),b=m.end(),old=m[0],new='.\n',rule='COMPLETE_ENGLISH_SENTENCE_BOUNDARY'))
 stage(es,'english_sentences')
 stage([dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='LITERAL_CONCATENATED_ENGLISH_ROLE_CAPTION') for m in re.finditer(r'Your\s+Role(?=You\s+will)',s)],'english_role_caption')
 return s,st
rules.normalize=normalize

_heading3=rules.headings
HARD_FIELDS={'专业要求','学历要求','教育背景','年龄要求','性别要求','英语能力','经历要求','经验要求','工作经验'}
def headings(s):
 out=_heading3(s)
 for h in out:
  if h['name'] in HARD_FIELDS:h['role']='Q_FIELD'
 return out
rules.headings=headings

ATTR=re.compile(r'^(?:工作主动|积极主动|纪律性强|责任心强|适应能力强)(?=[、,，;；。]|$)|^[^,，;；。]{1,45}(?:能力|动手能力)(?:较强|很强|强|良好|优秀)(?=[,，;；。]|$)')
PAST_Q=re.compile(r'^(?:在|于|曾|此前).{0,80}(?:提交|参与|完成|开发|设计|主导|负责|任职|从事|工作)过')
CREDENTIAL=re.compile(r'^(?:主治|副主任|主任|执业)(?:医师|医生)?(?:及)?以上职称')
CAPABILITY_ACTION=re.compile(r'^(?:负责|协助|通过.{0,30})?.{0,12}(?:提升|提高|培养|培训|考核|评价|评估|增强|开发)')
_qualification3=rules.qualification

def qualification(t):
 t=rules.cleantext(t)
 if (ATTR.search(t) and not CAPABILITY_ACTION.search(t)) or CREDENTIAL.match(t):return True
 return _qualification3(t)
rules.qualification=qualification

MODAL_WORK=re.compile(r'^(?:能(?:够)?|可)(?:独立|高效|准确|及时|有效|熟练|完全)*(?:地|的)?(?:对.{1,25}(?:提出|提供)|编制|编写|拓展|优化|支持|指导|完成|处理|解答|制作|设计|开发|维护).{3,}')
DELIVERABLE=re.compile(r'(?:制作|评审|验证|检讨改善|推进实施|试模|交付|验收|核对|审核|检查|编制|编写|归档|维护|开发|设计|定义改善)[。;；:：]*$')
_decide3=rules.decide

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if role=='Q_FIELD' and not rules.POSITIVE_ASSIGN.match(t):return 'N','EXPLICIT_APPLICANT_EDUCATION_OR_FIELD'
 if qualification(t) and (ATTR.search(t) and not CAPABILITY_ACTION.search(t) or CREDENTIAL.match(t)):return 'N','EXPLICIT_PERSONAL_CAPABILITY_OR_CREDENTIAL'
 if role=='Q' and PAST_Q.match(t):return 'N','EXPLICIT_PAST_SUBMISSION_OR_PROJECT_EXPERIENCE'
 if re.match(r'^(?:Clear mind|Good understanding|hands on experience)\b',t,re.I):return 'N','EXPLICIT_ENGLISH_CAPABILITY_OR_EXPERIENCE'
 if role in {None,'B','C','A'} and re.match(r'^(?:培养期结束后|并将培养期间考核|经校园招聘录用的|将由各单位负责培养)',t):return 'N','APPLICANT_TRAINING_PLAN_OR_PROMOTION'
 if role=='Q' and DELIVERABLE.search(t) and not qualification(t) and not re.search('能力|经验|熟悉|熟练|掌握|精通|知识|优先|能够|会使用|能独立',t):return 'R','CONCRETE_NOMINAL_DELIVERABLE_DESPITE_QUALIFICATION_CAPTION'
 if role=='R' and MODAL_WORK.match(t) and not rules.HARDQUAL.search(t):return 'R','CURRENT_MODAL_OPERATION_IN_DUTY_SECTION'
 if role in {None,'R'} and re.match(r'^(?:You|The employee|The candidate)\s+(?:will|shall)\s+be\s+(?:working|responsible|managing|providing|performing)\b',t,re.I) and not rules.DAMAGE.search(t):return 'R','EXPLICIT_ENGLISH_ASSIGNED_OPERATION'
 return _decide3(text,role,previous)
rules.decide=decide

_split3=rules.split_mixed
def split_mixed(s,a,b,role):
 intervals=_split3(s,a,b,role);points={a,b}
 for x,y in intervals:points.update((x,y))
 cs=rules._clauses(s,a,b)
 if role=='R':
  for i in range(1,len(cs)):
   lo,hi=cs[i];left=rules.cleantext(s[cs[i-1][0]:cs[i-1][1]]);right=rules.cleantext(s[lo:hi])
   if qualification(left) and (rules.is_task(right) and not qualification(right) or MODAL_WORK.match(right)):points.add(lo)
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

# A deliberately broad lexical screen is evaluated on every raw record.
# Every record with a possible new mechanism is recomputed from R10 + source.
def applicable(raw):
 return bool(nested_markers(raw) or LETTER_HEADING.search(raw) or re.search(r'Responsibilities|Your(?:\s|&nbsp;)+Role|工作制度|工作时间|自成立以来|主要业务范围|从业资格.{0,10}考试|为实现对优秀人才的系统培养|培养期结束后|校园招聘录用|工作主动|动手能力|纪律性强|主治.*职称|提交过|\bClear mind\b',raw,re.I) or (re.search('任职要求|任职资格',raw) and DELIVERABLE.search(raw)) or re.search(r'任职(?:要求|资格)[\s\S]*(?:制作|评审|验证|检讨改善|推进实施|试模|交付|验收|核对|审核|检查|编制|编写|归档|维护|开发|设计|定义改善)',raw) or (raw.lstrip().startswith('[') and ('职责' in raw or '任职' in raw)) or len(list(BARE_NUMBER.finditer(raw)))>=3 or re.search(r'熟悉|精通|掌握|能力(?:较强|很强|强|良好|优秀)',raw))

# Parent alignment needs only source-proven layout changes, not the full source
# normalizer (which could join separate already-cleaned lines).
_source_has_br=False
_source_has_letter=False

def source_old_spans(before,s):
 global _parent_events
 clean=before;st=[]
 def stage(es,name):
  nonlocal clean
  clean,es=rules.apply(clean,es)
  if es:st.append(dict(name=name,edits=es))
 es=[]
 for name,value in _source_entity_names.items():
  for m in re.finditer(re.escape('&'+name)+r'(?:;|(?=$|[,，\n]))',clean):es.append(dict(a=m.start(),b=m.end(),old=m[0],new=value,rule='SOURCE_PROVEN_LEGACY_ENTITY_FOR_ALIGNMENT_ONLY'))
 stage(es,'legacy_entities_for_alignment')
 if _source_has_br:
  rx=re.compile(v2.BR_ALL.pattern+'|'+EN_BR.pattern)
  stage([dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='SOURCE_PROVEN_LEGACY_BR_FOR_ALIGNMENT_ONLY') for m in rx.finditer(clean)],'legacy_br_for_alignment')
 if _source_has_letter:
  stage([dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='SOURCE_PROVEN_LEGACY_LETTER_FOR_ALIGNMENT_ONLY') for m in LETTER_LIST.finditer(clean)],'legacy_letter_for_alignment')
 if _nested_context:
  stage([dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='SOURCE_PROVEN_NESTED_ORDINAL_FOR_ALIGNMENT_ONLY') for m in NESTED.finditer(clean)],'legacy_nested_ordinals')
  stage([dict(a=m.start(),b=m.end(),old=m[0],new='',rule='SOURCE_PROVEN_DANGLING_ORDINAL_FOR_ALIGNMENT_ONLY') for m in re.finditer(r'(?m)\d{1,2}\.\s*$',clean)],'legacy_ordinal_remnants')
 _parent_events=st;return v2.base_old_spans(clean,s)
engine.source_old_spans=source_old_spans

def process(raw,row):
 global _nested_context,_source_entity_names,_parent_events,_source_has_br,_source_has_letter
 _nested_context=bool(nested_markers(raw));_source_entity_names={m[0][1:-1]:html.unescape(m[0]) for m in v2.ENTITY_ALL.finditer(raw) if html.unescape(m[0])!=m[0]};_parent_events=[]
 v2._context_br=len(list(v2.BR_ANCHOR.finditer(raw)))>=3
 _source_has_br=v2._context_br or (len(list(EN_BR.finditer(raw)))>=3 and bool(re.search(r'Responsibilities|Qualifications?|Key Skills',raw,re.I)))
 _source_has_letter=bool(LETTER_HEADING.search(raw) and len(list(LETTER_LIST.finditer(raw)))>=3)
 p=engine.process(raw,row);p['policy_version']='R11_V3_SOURCE_STRUCTURES_AND_EXPLICIT_TASKS';p['parent_alignment_normalization']=_parent_events
 v2._context_br=False;_nested_context=False;_source_has_br=False;_source_has_letter=False;return p

# Prevent a qualification's leading object from becoming a new task merely
# because a following comma carries the experience predicate.
OBJECT_EXPERIENCE=re.compile(r'^对[^。;；]{1,150}[,，]\s*(?:有|具有|具备).{0,40}(?:经验|经历|能力)')
BELIEF=re.compile(r'^对[^,，;；。]{1,80}(?:有|具有).{0,10}(?:信念|热诚|热情|兴趣)')
_decide4=rules.decide

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if role in {None,'Q','Q_FIELD'} and (OBJECT_EXPERIENCE.search(t) or BELIEF.search(t)):return 'N','EXPLICIT_KNOWLEDGE_EXPERIENCE_OR_INTEREST_PREDICATE'
 if role is None and re.fullmatch(r'(?:院长|病理医生|口腔医生|医生|护士|诊所主任)(?:职位描述[:：]?)?',t):return 'N','EXPLICIT_STANDALONE_POSITION_TITLE'
 return _decide4(text,role,previous)
rules.decide=decide

_split4=rules.split_mixed

def split_mixed(s,a,b,role):
 text=s[a:b];t=rules.cleantext(text)
 if role in {None,'Q','Q_FIELD'} and OBJECT_EXPERIENCE.search(t) and not rules.POSITIVE_ASSIGN.match(t):return [(a,b)]
 # A degree/tenure requirement in the same item makes weak "can do" phrases
 # part of that requirement; explicit independent assignments still split.
 if role=='R' and rules.HARDQUAL.search(t):return _split3(s,a,b,role)
 return _split4(s,a,b,role)
rules.split_mixed=split_mixed
BARE_NUMBER=re.compile(r'(?<![A-Za-z0-9.])([1-9]\d{0,2})(?=严格|对疑难|对客户|按照|负责|做好|定期|主动|其他与|组织|协助|完成|参与|指导|检查|维护|开发|设计|编制|制定|依照|统筹|完善|领导|参加|审查|监督|授权|控制|推动|支持|督导|辅导|建立|配合|离开|适时|教导|规划|制订|在上级)')
_prev_applicable=applicable

def applicable(raw):return _prev_applicable(raw) or bool(OBJECT_EXPERIENCE.search(raw) or BELIEF.search(raw) or re.search(r'(?:院长|医生|护士)职位描述',raw))

_norm4=rules.normalize
SPACED_NUMBER=re.compile(r'(?<![A-Za-z0-9.])([1-9]\d?)[ \t]+(?=[\u3400-\u9fffA-Za-z])(?![年月天岁米吨元万千百亿])')
def normalize(raw):
 s,st=_norm4(raw);es=[]
 for m in re.finditer(r'(?:工作内容|岗位职责|工作职责|职责描述|任职要求|任职资格)(?=\s{2,})',s):
  if re.search(r'(?:根据|按照|制定|编制|编写|明确|相关|履行|的)$',s[max(0,m.start()-12):m.start()]):continue
  es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n'+m[0]+':\n',rule='MULTISPACE_SECTION_CAPTION'))
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='caption_whitespace_boundaries',edits=es))
 ms=list(SPACED_NUMBER.finditer(s))
 if len(ms)>=3 and sum(int(y[1])==int(x[1])+1 for x,y in zip(ms,ms[1:]))>=2:
  es=[dict(a=m.start(),b=m.end(),old=m[0],new='\n'+m[1]+'、',rule='COHERENT_SPACED_LIST_ORDINAL') for m in ms];s,es=rules.apply(s,es)
  if es:st.append(dict(name='spaced_list_ordinals',edits=es))
 return s,st
rules.normalize=normalize
_task3=rules.is_task

def is_task(t):
 t=rules.cleantext(t)
 if re.match(r'^(?:承接|支撑|主攻|解读|抓好|预估)(?!过|能力|经验).{2,}',t):return True
 return _task3(t)
rules.is_task=is_task
_decide5=rules.decide

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if re.fullmatch(r'.{1,25}管理员(?:\([^)]{1,25}\))?',t) and not re.match(r'^(?:负责|协助|指导|培养|培训|担任|配合|招聘|管理)',t):return 'N','EXPLICIT_STANDALONE_POSITION_TITLE'
 return _decide5(text,role,previous)
rules.decide=decide

def split_mixed(s,a,b,role):
 text=s[a:b];t=rules.cleantext(text)
 if role in {None,'Q','Q_FIELD'} and OBJECT_EXPERIENCE.search(t) and not rules.POSITIVE_ASSIGN.match(t):return [(a,b)]
 intervals=_split3(s,a,b,role);points={a,b}
 for x,y in intervals:points.update((x,y))
 cs=rules._clauses(s,a,b)
 if role=='R':
  hard=bool(rules.HARDQUAL.search(t))
  for i in range(1,len(cs)):
   lo,hi=cs[i];left=rules.cleantext(s[cs[i-1][0]:cs[i-1][1]]);right=rules.cleantext(s[lo:hi]);prefix=rules.cleantext(s[a:lo])
   if qualification(left) or qualification(prefix):
    if rules.is_task(right) and not qualification(right) or (not hard and MODAL_WORK.match(right)):points.add(lo)
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed
_applicable4=applicable

def applicable(raw):return _applicable4(raw) or len(list(SPACED_NUMBER.finditer(raw)))>=3 or bool(re.search('工作内容|管理员|承接|支撑|主攻|解读|预估',raw))
_finish3=rules.finish_body

def finish_body(body):
 s,st=_finish3(body);es=[dict(a=m.start(),b=m.end(),old=m[0],new='',rule='EXPLICIT_THREE_DIGIT_LIST_MARKER') for m in re.finditer(r'(?m)^\s*\d{3}、\s*',s)];s,es=rules.apply(s,es)
 if es:st.append(dict(name='three_digit_list_syntax',edits=es))
 return s,st
rules.finish_body=finish_body
_headings4=rules.headings

def headings(s):
 out=[]
 for h in _headings4(s):
  if h['name']=='工作经验' and re.search(r'(?:总结|积累|分享|提炼|收集|报告|交流)(?:相关|已有)?$',s[max(0,h['a']-12):h['a']]):continue
  out.append(h)
 return out
rules.headings=headings

# The completed V2 scan already evaluates all source records. This final pass
# re-evaluates every potentially affected record, including empty and inherited
# results, and leaves verified unaffected bodies byte-identical.
QCAP=re.compile(r'任职要求|任职资格|岗位要求|职位要求|资格条件|招聘要求|应聘要求')
RCAP=re.compile(r'岗位职责|工作职责|职责描述|工作内容|主要职责')
PAIR_QUAL_TASK=re.compile(r'(?:熟悉|精通|掌握|具备|具有|经验|学历)[^。;；\n]{0,140}[,，]\s*(?:能|可|根据|通过|对|为|按照|提供|处理|维护|开展|负责|协助|关注)')
BODY_RISK=re.compile(r'能力(?:较强|很强|强|良好|优秀)|工作主动|纪律性强|信念|热诚|提交过|主治.*职称|培养期结束后|培养期间考核|校园招聘录用|管理类|经济类|思想政治|从事.{0,60}年|担任.{0,60}年|自成立以来|主要业务范围|建立了良好的声誉|公司.*(?:重视|关爱)|(?:院长|管理员)(?:\(|$)|任职要求|(?:^|\n)(?:br)+|&[A-Za-z]+',re.M)
OBJECT_EXPERIENCE_ANY=re.compile(OBJECT_EXPERIENCE.pattern[1:])

def applicable_row(raw,row):
 body=row['responsibility_text']
 if not body.strip() or row['r11_group']=='PRIOR_ALIGNMENT_PRESERVED':return True
 if BODY_RISK.search(body):return True
 if LETTER_HEADING.search(raw) or re.search(r'Responsibilities|Your(?:\s|&nbsp;)+Role|\bClear mind\b',raw,re.I):return True
 if raw.lstrip().startswith('[') and re.search('职责|任职',raw):return True
 if nested_markers(raw) or len(list(BARE_NUMBER.finditer(raw)))>=3 or len(list(SPACED_NUMBER.finditer(raw)))>=3:return True
 if re.search(r'(?:工作内容|岗位职责|工作职责|职责描述|任职要求|任职资格)\s{2,}',raw):return True
 if re.search(r'(?:编制|制定|修订|更改|安排|调整|优化|控制|减少)[^。;；\n]{0,35}(?:工作制度|工作时间)',raw):return True
 if re.search(r'从业资格.{0,10}考试|为实现对优秀人才的系统培养|培养期结束后|校园招聘录用|承接|主攻|解读|预估|信念|热诚|提交过|主治.*职称',raw):return True
 if OBJECT_EXPERIENCE_ANY.search(raw) or PAIR_QUAL_TASK.search(raw):return True
 # Nominal concrete outputs can appear under a mistakenly named Q caption.
 # This cheap structural screen deliberately over-selects; the full policy
 # still excludes knowledge, experience, and ability statements.
 if QCAP.search(raw):
  t=html.unescape(raw) if '&' in raw else raw
  if '<' in t:t=re.sub(r'<[^<>]{0,300}>','\n',t)
  t=t.replace('\\n','\n').replace('\\r','\n')
  for m in QCAP.finditer(t):
   nxt=RCAP.search(t,m.end());block=t[m.end():nxt.start() if nxt else len(t)]
   for line in re.split(r'[。;；\n]|\d+[.、)]',block):
    line=line.strip()
    if DELIVERABLE.search(line) and not re.search('能力|经验|熟悉|熟练|掌握|精通|知识|优先|能够|会使用|能独立',line):return True
 return False
_decide6=rules.decide

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if role=='Q' and previous=='R' and re.match(r'^(?:包括|包含|涵盖|例如|其中|以及)',t) and not qualification(t):return 'R','LITERAL_OBJECT_CONTINUATION_OF_EXPLICIT_TASK'
 return _decide6(text,role,previous)
rules.decide=decide
_finish4=rules.finish_body

def finish_body(body):
 s,st=_finish4(body);es=[]
 for m in re.finditer(r'\s+微信分享\s*$',s):
  if re.search(r'(?:工作|任务|架构|系统|资料|文档|计划|方案|流程|业务|服务|能力|经验)$',s[:m.start()]):es.append(dict(a=m.start(),b=m.end(),old=m[0],new='',rule='TRAILING_SHARE_WIDGET_AFTER_COMPLETE_STATEMENT'))
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='trailing_share_widget',edits=es))
 return s,st
rules.finish_body=finish_body
_applicable_row4=applicable_row

def applicable_row(raw,row):return _applicable_row4(raw,row) or '微信分享' in row['responsibility_text'] or bool(re.search(r'任职(?:要求|资格)[\s\S]*[;；]\s*(?:包括|包含|涵盖|例如|其中|以及)',raw))
