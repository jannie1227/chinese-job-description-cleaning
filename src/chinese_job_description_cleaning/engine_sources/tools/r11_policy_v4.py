"""Remaining literal layout, nominal-office tasks, and benefit-caption fixes."""
import re
from tools import r11_policy_v3 as v3
from tools.r11_io import *
rules=v3.rules;engine=v3.engine
BASE_NORMALIZE=rules.normalize;BASE_OLD_SPANS=engine.source_old_spans;BASE_HEADINGS=rules.headings;BASE_DECIDE=rules.decide;BASE_QUAL=rules.qualification;BASE_TASK=rules.is_task
BR=re.compile(r'(?<!<)(?:br)+(?=\s|[1-9]\d{0,2}[.、)]|[\u3400-\u9fff]|Responsibilities|Requirements|Qualifications|Key Skills|[;；。\]}]|$)')
BR_HEAD=re.compile(r'(?:Responsibilities|Requirements|Qualifications?|岗位职责|任职要求|任职资格|工作职责|工作内容|职责描述)\s*[:：]?\s*br',re.I)
_br_active=False

def br_layout(raw):return bool(len(list(BR.finditer(raw)))>=3 and (BR_HEAD.search(raw) or len(re.findall(r'br[1-9]\d?[.、)]',raw))>=3))
def br_edits(s):
 out=[]
 for m in BR.finditer(s):
  if re.match('标签|元素|节点|指令',s[m.end():]):continue
  out.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='COHERENT_BARE_BR_WITH_ALPHABETIC_NEIGHBOUR_OR_FREE_TEXT'))
 return out

def normalize(raw):
 global _br_active
 _br_active=br_layout(raw);s=raw;st=[]
 if _br_active:
  s,es=rules.apply(s,br_edits(s))
  if es:st.append(dict(name='complete_bare_br_boundaries_v4',edits=es))
 s,rest=BASE_NORMALIZE(s);st.extend(rest)
 if any(stage['name']=='nested_ordinals' for stage in st):v3._nested_context=True
 if _br_active:v3._source_has_br=True
 return s,st
rules.normalize=normalize

def source_old_spans(before,s):
 prefix=[];clean=before
 if _br_active:
  clean,es=rules.apply(clean,br_edits(clean))
  if es:prefix.append(dict(name='source_proven_legacy_br_alignment_v4',edits=es))
 spans,miss=BASE_OLD_SPANS(clean,s);v3._parent_events=prefix+v3._parent_events;return spans,miss
engine.source_old_spans=source_old_spans

rules.HROLE['员工待遇']='B'
rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)
def headings(s):
 hs=[]
 for h in BASE_HEADINGS(s):
  if h['name']=='员工待遇' and re.search(r'(?:负责|协助|办理|管理|核算|处理|落实|完善|制定|统筹)$',s[max(0,h['a']-12):h['a']]):continue
  hs.append(h)
 return hs
rules.headings=headings
KNOW=re.compile(r'^(?:深入|全面|充分|熟练)?(?:通晓|熟谙|谙熟|熟识)')
AUX=re.compile(r'^当好.{0,30}(?:参谋|助手|把关人|工作窗口|业务窗口)[。;；]?$')
OBJ=re.compile('办公室|办公设施|办公位|厂商|用车|车辆|通讯补贴|行政公告|前台|物资|库存|订单|合同|票据|仓库|设备|客户|供应商|工程|生产|现场|材料|产品|图纸|档案|会议|员工|薪酬|餐饮|经费|资产|报销|考勤|文印')
SOFT_END=re.compile(r'(?:管理|事务|安排|发布|采购|收发|对接|接待|保养|巡查|盘点|调度|核算|制作发布|报销|维护)[。;；:：]*$')
FIELD_ONLY=re.compile(r'^(?:行政管理|人力资源管理|财务管理|公共管理|工商管理|企业管理|旅游管理|酒店管理|工程管理|信息管理|经济管理|管理科学)$')

def qualification(t):return bool(KNOW.match(rules.cleantext(t))) or BASE_QUAL(t)
rules.qualification=qualification

def is_task(t):return bool(AUX.match(rules.cleantext(t))) or BASE_TASK(t)
rules.is_task=is_task

def office_nominal(t):
 return bool(OBJ.search(t) and SOFT_END.search(t.rstrip(')）')) and not FIELD_ONLY.fullmatch(t) and not rules.DAMAGE.search(t) and not qualification(t) and not re.search('经验|能力|知识|熟悉|熟练|掌握|精通|优先|学历|学位|相关专业|公司提供|我们提供|享受',t))
def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if t in {'其他','其它'}:return 'S','BARE_OTHER_SECTION_TOKEN'
 if KNOW.match(t):return 'N','EXPLICIT_KNOWLEDGE_PROFICIENCY'
 if role=='Q' and office_nominal(t):return 'R','CONCRETE_WORK_OBJECT_AND_ADMINISTRATIVE_FUNCTION'
 if AUX.match(t) and not rules.DAMAGE.search(t) and role in {None,'R','Q'}:return 'R','EXPLICIT_ASSIGNED_ADVISORY_AUXILIARY_TASK'
 return BASE_DECIDE(text,role,previous)
rules.decide=decide

def applicable_row(raw,row):
 if not row['responsibility_text'].strip() or row['r11_group']=='PRIOR_ALIGNMENT_PRESERVED' or re.search(r'(?m)^\s*(?:其他|其它)\s*$',row['responsibility_text']):return True
 if br_layout(raw) or re.search(r'员工待遇|通晓|熟谙|谙熟|熟识|当好.{0,30}(?:参谋|助手|把关人|工作窗口|业务窗口)',raw):return True
 if v3.QCAP.search(raw) and OBJ.search(raw):
  for m in v3.QCAP.finditer(raw):
   nxt=v3.RCAP.search(raw,m.end());block=raw[m.end():nxt.start() if nxt else len(raw)]
   if re.search('管理|事务|安排|发布|采购|收发|对接|接待|保养|巡查|盘点|调度|核算|报销|维护',block):return True
 return False

def process(raw,row):
 p=v3.process(raw,row);p['policy_version']='R11_V4_LITERAL_LAYOUT_NOMINAL_WORK_AND_CAPTIONS';return p

# Protect literal quantities and referenced document identifiers. A decimal is
# a task-list marker only when a list boundary or matching parent proves it.
_NESTED_BASE=v3.nested_markers
v3.NESTED=re.compile(r'(?<![A-Za-z0-9.])([1-9]\d?)\.([1-9]\d?)[ \t]*(?=[\u3400-\u9fff])(?!(?:万|千|百|十|亿|年|月|天|岁|米|吨|元|寸|英寸|秒|小时|分钟|毫|伏|瓦|安培|赫兹|度|升|克|公斤|倍|条|章|节|款|号|版))')
REF_CUE=re.compile(r'(?:依据|根据|参照|按照|遵循|符合|满足|阅读|查阅|学习|执行|标准|版本|编号)\s*$')
def nested_markers(s):
 ms=_NESTED_BASE(s);allowed=[]
 for m in ms:
  if REF_CUE.search(s[max(0,m.start()-15):m.start()]):continue
  major=m[1];chinese='一二三四五六七八九'[int(major)-1] if 1<=int(major)<=9 else None
  parent=bool(re.search(r'(?<![A-Za-z0-9.])'+re.escape(major)+r'[、.)](?!\d)',s)) or bool(chinese and re.search(re.escape(chinese)+r'[、.)]',s))
  group_anchor=any(x[1]==major and (not s[:x.start()].strip() or re.search(r'[\n;；。:：]\s*$',s[:x.start()])) for x in ms)
  if parent or group_anchor:allowed.append(m)
 return allowed
v3.nested_markers=nested_markers
_norm4=rules.normalize

def normalize(raw):
 s,st=_norm4(raw)
 if any(stage['name']=='nested_ordinals' for stage in st):
  es=[]
  for m in v3.NESTED.finditer(s):
   if not s[:m.start()].strip() or re.search(r'\n\s*$',s[:m.start()]):es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='SINGLE_CHILD_WITHIN_PROVEN_NESTED_LIST'))
  s,es=rules.apply(s,es)
  if es:st.append(dict(name='singleton_child_list_marker',edits=es))
 return s,st
rules.normalize=normalize

rules.HROLE['工作内容与要求']='R';rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)
INTEREST=re.compile(r'^(?:对|对于)[^,，;；。]{1,80}(?:热爱|热情|兴趣)(?:浓厚|极大|很高|十足)?(?=[,，;；。]|$)')
MODAL_CORRECT=re.compile(r'^(?:能(?:够)?|可)(?:正确|准确|安全|规范|独立|熟练)(?:地|的)?(?:操作|使用|处理|维修|检修|执行|完成|判断).{2,}')
_qu4=rules.qualification;_ta4=rules.is_task;_de4=rules.decide;_sp4=rules.split_mixed

def qualification(t):return bool(INTEREST.match(rules.cleantext(t))) or _qu4(t)
rules.qualification=qualification

def is_task(t):
 t=rules.cleantext(t)
 if re.match(r'^(?:准确|正确|及时)?判断(?:各种|设备|系统|产品|异常|故障|运行|生产|客户|业务|问题)',t):return True
 return _ta4(t)
rules.is_task=is_task

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if INTEREST.match(t):return 'N','EXPLICIT_PERSONAL_INTEREST_OR_ENTHUSIASM'
 question=re.search(r'是否(?:做|参与|负责|开发|完成)过',t)
 if question and re.match(r'^(?:在|对|是否|你|您)',t) and not re.search(r'检查|审核|核查|核对|评估|调查|确认|统计|记录|询问',t[:question.start()]):return 'N','APPLICANT_PAST_EXPERIENCE_QUESTION'
 if re.search('从基层做起|从基层岗位做起|方可成为管理干部',t) and not re.match(r'^(?:负责|协助|制定|组织|实施|开展|建立|安排)',t):return 'N','APPLICANT_DEVELOPMENT_PATH'
 if role=='R' and MODAL_CORRECT.match(t) and not rules.HARDQUAL.search(t) and not rules.DAMAGE.search(t):return 'R','EXPLICIT_CORRECT_OPERATION_IN_DUTY_SECTION'
 return _de4(text,role,previous)
rules.decide=decide
CAUSE=re.compile(r'确保|保证|使其|让|使|帮助|促使|培训|指导|推动|促进|培养|提升|提高|协助|支持|组织')

def split_mixed(s,a,b,role):
 intervals=_sp4(s,a,b,role);points={a,b}
 for lo,hi in intervals:points.update((lo,hi))
 for point in list(points-{a,b}):
  if s[point-1] in ',，;；。\n':continue
  right=rules.cleantext(s[point:b]);last_clause=re.split('[,，;；。\n]',s[a:point])[-1]
  if re.match('对|具备|具有|拥有',right) and CAUSE.search(last_clause) and not re.search('者优先|最好|为佳|学历|学位|本科|大专',right):points.discard(point)
 if role=='R':
  cs=rules._clauses(s,a,b)
  for i in range(1,len(cs)):
   lo,hi=cs[i];left=rules.cleantext(s[cs[i-1][0]:cs[i-1][1]]);right=rules.cleantext(s[lo:hi])
   if (MODAL_CORRECT.match(left) or rules.is_task(left)) and qualification(right):points.add(lo)
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed
_app4=applicable_row

def applicable_row(raw,row):
 return _app4(raw,row) or bool(re.search(r'工作内容与要求|是否(?:做|参与|负责|开发|完成)过|对[^。;；\n]{1,80}(?:热爱|热情|兴趣)|从基层做起|从基层岗位做起|方可成为管理干部|(?:能(?:够)?|可)(?:正确|准确|安全|规范)(?:操作|使用|处理|维修|检修|执行|完成|判断)',raw)) or bool(re.search(r'(?:确保|保证|使其|让|帮助|促使|培训|指导|推动|促进|培养|提升|提高|协助|支持|组织)[^。;；\n]{0,80}(?:对[^,，;；]{1,35}有|具备|具有|拥有)',raw)) or bool(re.search(r'\d+[.．]\d+\s*[\u3400-\u9fff]',raw))

_wrapper_base=v3._wrapper
CAPTION_EVIDENCE=re.compile(r'(?:岗位职责|工作职责|职责描述|工作内容|岗位要求|任职要求|任职资格|技能要求)\s*[:：]')
def wrapper(s):
 a=len(s)-len(s.lstrip());b=s.rfind(']')
 if a<len(s) and s[a]=='[' and b>a and b-a>40 and len(list(CAPTION_EVIDENCE.finditer(s[a:b])))>=2:return (a,b)
 return _wrapper_base(s)
v3._wrapper=wrapper
_de5=rules.decide

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if re.match(r'^(?:详见官网|详情见官网|更多职位上|更多职位请|更多招聘信息)',t):return 'N','SOURCE_OR_JOB_BOARD_FOOTER'
 return _de5(text,role,previous)
rules.decide=decide
_app5=applicable_row

def applicable_row(raw,row):return _app5(raw,row) or (raw.lstrip().startswith(('[','［')) and len(list(CAPTION_EVIDENCE.finditer(raw)))>=2)

# Past-tense suffixes must not match the first character of 过程 or related
# work objects (负责过程管理 / 负责过账 / 管理过期物料).
COMPOUND_AFTER_GUO='程|账|户|磅|站|检|期|渡|氧'
rules.HARDQUAL=re.compile(rules.HARDQUAL.pattern.replace('从事过','从事过(?!'+COMPOUND_AFTER_GUO+')').replace('负责过','负责过(?!'+COMPOUND_AFTER_GUO+')').replace('参与过','参与过(?!'+COMPOUND_AFTER_GUO+')').replace('做过','做过(?!'+COMPOUND_AFTER_GUO+')'))
rules.PAST=re.compile(rules.PAST.pattern.replace(')过',')过(?!'+COMPOUND_AFTER_GUO+')'))
rules.ACTION=re.compile(rules.ACTION.pattern.replace('(?!过|','(?!过(?!'+COMPOUND_AFTER_GUO+')|'))
_task5=rules.is_task;_qual5=rules.qualification;_decide7=rules.decide;_operational=rules.operational_knowledge
PROCESS_WORK=re.compile(r'^(?:负责|参与|主导|从事|设计|开发|操作|完成|组织|使用|处理|管理|做好)(?:过程|过账|过户|过磅|过站|过检|过期|过渡|过氧)')
HAVE_ATTRIBUTE=re.compile(r'^(?:在|于)[^,，;；。]{0,45}(?:有|具有|具备|拥有)[^,，;；。]{0,35}(?:人脉|关系|资源|经验|经历|能力)')
DEGREE_FIELD=re.compile(r'^[^。;；:：]{1,90}(?:相关)?专业[。;；]*$')

OBJ=re.compile(OBJ.pattern+'|厂区|绿化|卫生|环境|运输|油卡|厂务')
SOFT_END=re.compile(r'(?:管理|事务|安排|发布|采购|收发|对接|接待|保养|巡查|盘点|调度|核算|制作发布|报销|维护|监督|改善|跟进|充值|提交)(?:等|工作|等工作)?[。;；:：]*$')

def is_task(t):
 t=rules.cleantext(t);core=rules.ADVERB.sub('',t)
 if PROCESS_WORK.match(core):return True
 if re.match(r'^交流(?:工作|项目|管理|先进|实践|技术|相关)?经验',core):return True
 if re.match(r'^(?:严格)?(?:按照|根据|按)',core) and re.search(r'摆放|放置|挂在|挂放|归位|理货|查找',core) and not re.search('能力|经验|知识|技能|者优先',core):return True
 if re.match(r'^保持',core) and re.search('设备|工具|机器|机台|场地|厂区|现场|车内|车外|卫生|清洁|库房|货架',core):return True
 return _task5(t)
rules.is_task=is_task

def qualification(t):
 t=rules.cleantext(t)
 if HAVE_ATTRIBUTE.match(t):return True
 if DEGREE_FIELD.match(t) and not re.match(r'^(?:负责|协助|培养|培训|讲授|教学|授课|招聘|指导|学习|教授|从事|开展)',t):return True
 if PROCESS_WORK.match(rules.ADVERB.sub('',t)) and not re.search('学历|学位|能力|经验|经历|技能|知识|优先',t):return False
 return _qual5(t)
rules.qualification=qualification

def operational_knowledge(t):
 return _operational(t) or bool(re.match(r'^(?:及时|深入|充分|全面)?(?:了解|掌握|熟悉|理解)',t) and re.search('运行状况|设备状况|生产状况|工况',t) and not re.search('学历|学位|经验|能力|者优先|精通|熟练|软件|工具|编程',t))
rules.operational_knowledge=operational_knowledge

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if HAVE_ATTRIBUTE.match(t):return 'N','EXPLICIT_PERSONAL_RELATIONSHIP_RESOURCE_OR_CAPABILITY'
 if DEGREE_FIELD.match(t) and not re.match(r'^(?:负责|协助|培养|培训|讲授|教学|授课|招聘|指导|学习|教授|从事|开展)',t):return 'N','EXPLICIT_APPLICANT_DISCIPLINE_LIST'
 if re.match(r'^(?:以上|上述|所有|本次)(?:招聘)?(?:岗位|职位).{0,70}(?:签订|签署).{0,30}(?:劳动合同|劳务合同)',t):return 'N','RECRUITMENT_EMPLOYMENT_CONTRACT_NOTICE'
 if role in {None,'R','Q'} and office_nominal(t):return 'R','LITERAL_WORK_OBJECT_AND_NOMINAL_OPERATION'
 if role=='R' and re.match(r'^(?:了解|熟悉|掌握)(?:并|和|及)(?:发掘|挖掘|开拓|开发|维护|操作|处理|解决)',t) and not rules.DAMAGE.search(t):return 'R','KNOWLEDGE_JOINED_TO_CURRENT_OPERATION'
 if role=='R' and re.match(r'^(?:学习|练习)(?!能力|意愿|成绩|兴趣|效率|素质).{2,}',t) and not rules.HARDQUAL.search(t) and not rules.DAMAGE.search(t):return 'R','EXPLICIT_ASSIGNED_LEARNING_OR_PRACTICE'
 return _decide7(text,role,previous)
rules.decide=decide

# Explicit field captions. Working objects preceded by an assignment verb are
# not interpreted as a new metadata section.
NEW_HEADS={'角色和责任':'R','角色和职责':'R','职位概要':'R','Post summary':'R','Work contents':'R','Work content':'R','Work experience':'Q_FIELD','语言要求':'Q_FIELD','Language requirement':'Q_FIELD','职业生涯规划':'B','Career planning':'B','培训需求':'Q_FIELD','Training requirements':'Q_FIELD','工作条件':'A','Work conditions':'A'}
for name,role in NEW_HEADS.items():rules.HROLE[name.lower()]=role
rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)
_heads4=rules.headings

def headings(s):
 result=[]
 for h in _heads4(s):
  if h['name'].lower() in {x.lower() for x in NEW_HEADS} and re.search(r'(?:负责|协助|办理|管理|核算|处理|落实|完善|制定|统筹|改善|优化|编制)$',s[max(0,h['a']-12):h['a']]):continue
  result.append(h)
 return result
rules.headings=headings

# A trailing dot is a conventional list-marker delimiter, not a third level.
v3.NESTED=re.compile(v3.NESTED.pattern.replace(r'\.([1-9]\d?)[ \t]*',r'\.([1-9]\d?)\.?[ \t]*'))
_removed_markers=set();_normal5=rules.normalize;_oldspans4=engine.source_old_spans

def normalize(raw):
 global _removed_markers
 s,st=_normal5(raw);_removed_markers=set()
 for stage in st:
  if stage['name'] in {'nested_ordinals','singleton_child_list_marker'}:
   for e in stage['edits']:
    m=re.match(r'\s*(\d+(?:\.\d+)+)',e['old'])
    if m:_removed_markers.add(m[1])
 return s,st
rules.normalize=normalize

def source_old_spans(before,s):
 es=[];offset=0;hay=engine.flat(s)
 if _removed_markers:
  for line in before.splitlines(keepends=True):
   content=line.rstrip('\r\n');m=re.search(r'(?<![\d.])(\d+(?:\.\d+)+)\.?\s*$',content)
   if m and m[1] in _removed_markers and engine.flat(content) not in hay:es.append(dict(a=offset+m.start(),b=offset+m.end(),old=m[0],new='',rule='SOURCE_PROVEN_PRIOR_TRAILING_LIST_NUMBER_FOR_ALIGNMENT_ONLY'))
   offset+=len(line)
 clean,es=rules.apply(before,es);prefix=[dict(name='prior_trailing_list_number_alignment',edits=es)] if es else []
 spans,miss=_oldspans4(clean,s);v3._parent_events=prefix+v3._parent_events;return spans,miss
engine.source_old_spans=source_old_spans
_app6=applicable_row

def applicable_row(raw,row):
 return _app6(raw,row) or bool(re.search(r'(?:负责|参与|主导|从事|设计|开发|操作|完成|组织|使用|做|处理|管理)(?:过程|过账|过户|过磅|过站|过检|过期|过渡|过氧)|交流.{0,6}经验|人脉|角色和责任|角色和职责|职位概要|Work experience|Work contents|培训需求|工作条件|职业生涯规划|(?:保持).{0,35}(?:机台|设备|现场|卫生|清洁)|(?:按照|按|根据).{0,55}(?:摆放|放置|挂在|查找)|油卡|厂区卫生|绿化|工作环境.{0,15}改善|运行状况|(?:以上|上述)招聘岗位|了解和发掘|学习幻灯片|练习幻灯片|类专业',raw,re.I))

# A caption may introduce a numbered duty without a colon or dot.
_normal6=rules.normalize
BARE_CAPTION=re.compile(r'(职位描述|岗位职责|职责描述|工作职责|工作内容|任职要求|任职资格)\s*(?=[1-9]\d?(?:能|可|需|负责|协助|在|按|完成))')
MODAL_ENUM=re.compile(r'(?<![A-Za-z0-9.])([1-9]\d?)\s*(?=(?:能够|能|可|需)(?:保持|协助|完成|正确|准确|独立|熟练|操作|使用))')

def normalize(raw):
 s,st=_normal6(raw);es=[]
 for m in BARE_CAPTION.finditer(s):
  if re.search('编写|制定|编制|撰写|根据|修改|界定|定义',s[max(0,m.start()-12):m.start()]):continue
  es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n'+m[1]+':\n',rule='CAPTION_BEFORE_BARE_TASK_ORDINAL'))
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='bare_caption_boundary',edits=es))
 ms=list(MODAL_ENUM.finditer(s))
 if len(ms)>=2 and any(int(y[1])==int(x[1])+1 for x,y in zip(ms,ms[1:])):
  es=[dict(a=m.start(),b=m.end(),old=m[0],new='\n'+m[1]+'、',rule='COHERENT_MODAL_TASK_ORDINAL') for m in ms];s,es=rules.apply(s,es)
  if es:st.append(dict(name='modal_task_ordinals',edits=es))
 return s,st
rules.normalize=normalize
_decide8=rules.decide

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if role=='R' and re.match(r'^(?:能(?:够)?|可)(?:独立|高效|及时|正确|准确|有效|熟练)*(?:协助|保持|完成)',t) and re.search('工作|任务|客户|沟通|对接|设备|设计|勘察|操作',t) and not rules.HARDQUAL.search(t) and not rules.DAMAGE.search(t):return 'R','EXPLICIT_MODAL_COLLABORATION_OR_OPERATION'
 return _decide8(text,role,previous)
rules.decide=decide
_app7=applicable_row

def applicable_row(raw,row):
 return _app7(raw,row) or bool(BARE_CAPTION.search(raw) or re.search(r'学习(?!能力|意愿|成绩|兴趣|效率|素质)|练习|(?:能(?:够)?|可)(?:独立|高效|及时|正确|准确|有效|熟练)*(?:协助|保持|完成)',raw))

# Attribute adjectives are not assignments; explicit modal work under a duty
# caption is retained, but a degree/tenure/preference clause remains excluded.
rules.POSITIVE_ASSIGN=re.compile(rules.POSITIVE_ASSIGN.pattern.replace('(?!过|人|心)',r'(?!过|人|心|的(?:职业态度|工作态度|态度|精神)|态度|精神)'))
DEGREE_CONDITION=re.compile(r'^[^。;；:：]{1,100}(?:相关|类)?专业(?:者|人员|毕业)?(?:优先考虑|优先录用|优先)?[。;；!！]*$')
MODAL_JOB=re.compile(r'^(?:能(?:够)?|可)(?:(?:正确|准确|安全|规范|独立|熟练|高效|及时|快速|有效)(?:地|的)?)*(?:协调|响应|支撑|应对|组织|维护|执行|操作|使用|协助|完成|提供|处理|开发|设计|分析|判断).{2,}')
_task6=rules.is_task;_qual6=rules.qualification;_decide9=rules.decide;_split6=rules.split_mixed

OBJ=re.compile(OBJ.pattern+'|工作时间|工时|数据库|系统')
SOFT_END=re.compile(SOFT_END.pattern.replace('|提交)', '|提交|录入|运维|支撑)'))

def is_task(t):
 core=rules.ADVERB.sub('',rules.cleantext(t))
 if re.match(r'^(?:配置|调配|部署|分发)(?!过|能力|经验|要求|参数).{2,}',core):return True
 return _task6(t)
rules.is_task=is_task

def qualification(t):
 t=rules.cleantext(t)
 if re.match(r'^负责(?:的)?(?:职业态度|工作态度|态度|精神|意识|心)',t):return True
 if DEGREE_CONDITION.match(t) and not re.match(r'^(?:负责|协助|培养|培训|讲授|教学|授课|招聘|指导|学习|教授|从事|开展)',t):return True
 return _qual6(t)
rules.qualification=qualification

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if re.match(r'^负责(?:的)?(?:职业态度|工作态度|态度|精神|意识|心)',t):return 'N','RESPONSIBLE_AS_PERSONAL_ATTITUDE_ADJECTIVE'
 if DEGREE_CONDITION.match(t) and not re.match(r'^(?:负责|协助|培养|培训|讲授|教学|授课|招聘|指导|学习|教授|从事|开展)',t):return 'N','EXPLICIT_APPLICANT_DISCIPLINE_OR_PREFERENCE'
 if re.match(r'^(?:有想学|想学.{1,30}(?:人员|人才)|有意学习)',t):return 'N','APPLICANT_LEARNING_INTEREST'
 if role=='R' and MODAL_JOB.match(t) and not rules.HARDQUAL.search(t) and not rules.DAMAGE.search(t):return 'R','EXPLICIT_ASSIGNED_MODAL_WORK'
 if role=='Q' and not qualification(t) and not re.search('经验|经历|能力|知识|熟悉|熟练|精通|掌握|优先|学历|学位',t):
  cs=[rules.cleantext(x) for x in re.split('[,，]',t)]
  if len(cs)>1 and OBJ.search(cs[0]) and re.search('工作|运维|维护|支撑|开发|设计|管理|服务',cs[0]) and any(rules.is_task(x) for x in cs[1:]):return 'R','CONCRETE_NOMINAL_WORK_WITH_ASSIGNED_CONTINUATION'
 return _decide9(text,role,previous)
rules.decide=decide

def split_mixed(s,a,b,role):
 intervals=_split6(s,a,b,role);points={a,b}
 for lo,hi in intervals:points.update((lo,hi))
 if role=='R':
  cs=rules._clauses(s,a,b)
  for i in range(1,len(cs)):
   lo,hi=cs[i];left=rules.cleantext(s[cs[i-1][0]:cs[i-1][1]]);right=rules.cleantext(s[lo:hi])
   if MODAL_JOB.match(left) and qualification(right):points.add(lo)
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed
rules.HROLE['全方位保障']='B';rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)

# Final policy is evaluated on all 4,073,781 rows. No lexical applicability
# screen can omit a case affected by any of the accumulated corrections.
def applicable_row(raw,row):return True

# Personal opportunities/advantages are not a source of additional assigned
# work. The next actual duty caption resets this role in the usual way.
for h in ['你将获得','您将获得','职位优势','培训成长']:
 rules.HROLE[h.lower()]='OFFER'
for h in ['销售指标达成','数据报表管理','主要职责Essential responsibilities and duties','Essential responsibilities and duties','主要任务The main missions of the role are','The main missions of the role are','通用职责General responsibilities','通用职责','General responsibilities']:
 rules.HROLE[h.lower()]='R'
for h in ['技术和能力/ Skills and competencies','Skills and competencies','领导力模型LCM','领导力模型','公司期望的行为 Company’s Expected Behaviors','Company’s Expected Behaviors','公司期望的行为','资格要求Qualifications']:
 rules.HROLE[h.lower()]='Q_FIELD'
rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)
_head7=rules.headings

GENERIC_JD={'职位描述','岗位描述','职位说明','岗位说明','job description'}

def headings(s):
 hs=_head7(s);out=[]
 for h in hs:
  before=s[:h['a']];pre=before.rstrip()
  if h['name']=='工作经验':
   boundary=not pre or bool(re.search(r'\n\s*$',before)) or pre[-1:] in '。;；:：[(【' or bool(re.search(r'(?:\d+[、.)]|[一二三四五六七八九十][、.)])\s*$',before))
   explicit_colon=bool(re.search('[:：]',s[h['a']:h['b']]))
   if not boundary and not explicit_colon:continue
  if h['name'].lower() in GENERIC_JD:
   lead=s[h['b']:].lstrip();lead=re.sub(r'^\d+[.、)]\s*','',lead);first=re.split('[,，。;；\n]',lead,1)[0].strip()
   academic=bool(DEGREE_FIELD.fullmatch(first) or re.fullmatch(r'(?:全日制|统招)?(?:本科|大专|专科|硕士|博士)(?:及以上|以上)?(?:学历|毕业)?',first))
   if academic and not re.match(r'^(?:负责|协助|培养|培训|讲授|教学|授课|招聘|指导|学习|教授|从事|开展)',first):h=dict(h,role=None,neutral_container=True)
  out.append(h)
 return out
rules.headings=headings
_task7=rules.is_task;_decide10=rules.decide;_split7=rules.split_mixed;_operational2=rules.operational_knowledge
ANIMAL_OPERATION=re.compile(r'^.{1,45}(?:隔离驯化|饲养管理|饲喂|育种|驯化)(?:\([^)]{0,45}\))?[。;；]?$')

def is_task(t):
 t=rules.cleantext(t)
 if re.match(r'^(?:专业)?(?:处理|接待|解答|维护|分析)(?!能力|经验|知识|技能).{0,}',t) and t.startswith('专业') and not re.search('能力|经验|知识|技能|优先',t):return True
 if re.match(r'^(?:了解收集|了解并收集|了解并发掘|熟悉并操作).{2,}',t):return True
 if re.fullmatch(r'[^,，;；。]{1,65}跑市场[。;；]?',t) and not re.search('经验|能力|能适应|可接受|愿意|喜欢|希望|热爱|兴趣|具备|具有',t):return True
 if ANIMAL_OPERATION.match(t) and not re.search('熟悉|掌握|了解|经验|能力|学历|专业',t):return True
 return _task7(t)
rules.is_task=is_task

def operational_knowledge(t):
 return _operational2(t) or bool(re.match(r'^(?:及时|充分)?(?:了解|掌握|熟悉)',t) and re.search('售点|市场动态|市场变化',t) and not re.search('经验|能力|知识|技巧|课程|软件|工具|规则|流程|学历|学位',t))
rules.operational_knowledge=operational_knowledge

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if role=='OFFER':return 'N','EXPLICIT_PERSONAL_BENEFIT_OR_CAREER_OPPORTUNITY_SECTION'
 if re.fullmatch(r'本岗位为.{1,45}(?:岗|职位|岗位)[。;；]?',t):return 'N','EXPLICIT_POSITION_IDENTITY_ONLY'
 if role=='R' and re.match(r'^(?:能(?:够)?|可)(?:高效|有效|正确|准确|及时|快速|独立|熟练)*(?:制定|识别|遵守).{2,}',t) and not rules.HARDQUAL.search(t) and not rules.DAMAGE.search(t):return 'R','EXPLICIT_ASSIGNED_PROCEDURE_OR_COMPLIANCE'
 if role in {None,'R'} and ANIMAL_OPERATION.match(t) and not qualification(t):return 'R','LITERAL_ANIMAL_OPERATION_WITH_OBJECT_AGE_ANNOTATION'
 return _decide10(text,role,previous)
rules.decide=decide

def split_mixed(s,a,b,role):
 ints=_split7(s,a,b,role);points={a,b}
 for lo,hi in ints:points.update((lo,hi))
 if role is None:
  first=rules.cleantext(s[a:b]);cs=rules._clauses(s,a,b)
  if re.match(r'^(?:熟悉|精通|掌握|了解)',first):
   for lo,hi in cs[1:]:
    prefix=s[a:lo];right=rules.cleantext(s[lo:hi])
    if not re.search('经验|能力|学历|学位|具备|具有|拥有',prefix) and rules.is_task(right) and not qualification(right):points.add(lo)
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

# The original bilingual matcher treated Chinese characters as adjacent
# English letters. Correct its word boundary without altering any source text.
from tools.r11_headings_v4 import headings as ascii_word_headings
v3.base_headings=ascii_word_headings
_qual7=rules.qualification;_decide11=rules.decide;_split8=rules.split_mixed
LOCATION_CONDITION=re.compile(r'^服从.{0,35}(?:工作地|工作地点|驻地|就近工作地)安排[。;；]?$')
def _without_connector(t):return re.sub(r'^(?:另|另外|此外)\s*[,，:：]\s*','',rules.cleantext(t))
def qualification(t):return bool(LOCATION_CONDITION.match(_without_connector(t))) or _qual7(t)
rules.qualification=qualification

def decide(text,role,previous=None):
 if LOCATION_CONDITION.match(_without_connector(text)):return 'N','APPLICANT_WORK_LOCATION_ALLOCATION_CONDITION'
 return _decide11(text,role,previous)
rules.decide=decide

def split_mixed(s,a,b,role):
 ints=_split8(s,a,b,role);points={a,b}
 for lo,hi in ints:points.update((lo,hi))
 cs=rules._clauses(s,a,b)
 for i in range(1,len(cs)):
  lo,hi=cs[i];left=rules.cleantext(s[cs[i-1][0]:cs[i-1][1]]);right=_without_connector(s[lo:b])
  if rules.is_task(left) and LOCATION_CONDITION.match(right):points.add(lo)
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

_finish5=rules.finish_body

def finish_body(body):
 s,st=_finish5(body);majors={x.split('.')[0] for x in _removed_markers};es=[]
 for m in re.finditer(r'(?m)^([1-9]\d?)[ \t]*(?=[\u3400-\u9fff])(?![万千百十亿元年月日周时分秒天岁米吨寸型号级类代维相核轴系国家个件次批种套台人位户条头只辆间层期段项所座份张株升毫克斤页])',s):
  if m[1] in majors:es.append(dict(a=m.start(),b=m.end(),old=m[0],new='',rule='MAJOR_ORDINAL_WITH_PROVEN_CHILD_LIST'))
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='proven_parent_list_marker',edits=es))
 return s,st
rules.finish_body=finish_body

# Recover a last single-child 'other' section only inside an already proven
# hierarchy. Do not change an unproven decimal or a referenced document ID.
_norm7=rules.normalize

def normalize(raw):
 s,st=_norm7(raw)
 if len({x.split('.')[0] for x in _removed_markers})>=2:
  es=[]
  for m in re.finditer(r'(?<![\d.])([1-9]\d?)(?:其他|其它)\s*\1\.1\s*(?=完成|负责|协助|承担)',s):
   if REF_CUE.search(s[max(0,m.start()-20):m.start()]):continue
   es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='PROVEN_LAST_OTHER_SECTION_WITH_SINGLE_CHILD'))
  s,es=rules.apply(s,es)
  if es:st.append(dict(name='last_other_child_structure',edits=es))
 return s,st
rules.normalize=normalize
_decide12=rules.decide

def decide(text,role,previous=None):
 t=rules.cleantext(text)
 if t=='执行机构':return 'N','BARE_TECHNICAL_COMPONENT_IS_NOT_A_TASK'
 if t=='自我管理':return 'N','GENERIC_SELF_MANAGEMENT_ATTRIBUTE'
 return _decide12(text,role,previous)
rules.decide=decide
_finish6=rules.finish_body

def finish_body(body):
 s=body;st=[];majors={x.split('.')[0] for x in _removed_markers};es=[]
 for m in re.finditer(r'(?m)^([1-9]\d?)\s*(?:管理|其他|其它)\s*(?=\n|$)',s):
  if m[1] in majors:es.append(dict(a=m.start(),b=m.end(),old=m[0],new='',rule='BARE_PARENT_CATEGORY_WITH_PROVEN_CHILD_TASKS'))
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='bare_parent_category_syntax',edits=es))
 s,rest=_finish6(s);st.extend(rest);return s,st
rules.finish_body=finish_body
