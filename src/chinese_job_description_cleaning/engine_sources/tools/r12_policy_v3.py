"""Unified full-corpus policy: no keyword eligibility gate, literal-source only."""
import re,functools
from tools import r12_policy_v2 as v2
from tools.r11_verify_release import replay
v1=v2.v1;rules=v2.rules;engine=v2.engine
BASE_HEADS=rules.headings;RAW_PARTS=v2.BASE_PARTS
BASE_DECIDE=rules.decide;BASE_TASK=rules.is_task;BASE_SPLIT=rules.split_mixed
OLD_OPERATIONAL=v1.operational;BASE_NORMAL=rules.normalize
NON_DUTY={'A','B','C','OFFER','NOTICE','COMPETENCY'}
DEGREE_START=re.compile(r'^(?:全日制|统招|大学)?(?:本科|专科|大专|中专|硕士|博士|研究生|高中)|^(?:年龄|学历|学位|性别|身高|工作年限)')
TRAIT=re.compile(r'^(?:对)?(?:工作|本职工作|做事|为人|工作态度)?(?:负责认真|认真负责|认真|细致负责|细致|细心|严谨|踏实|诚实|正直|勤奋|阳光|乐观|开朗|有责任心|责任心|有上进心|积极主动|主动积极|热爱|热衷|认同|认可|敢想敢干)(?=[、,，;；。]|负责|细心|踏实|严谨|吃苦|工作|公司|企业|销售|本职|游戏|$)')
REVERSED_STATE=re.compile(r'^(?:对|对于)[^。;；]{1,90}(?:熟悉|精通|娴熟|了解深入|认识深刻|理解深入|高度认同|非常认同|有[^,，;；]{0,15}(?:兴趣|逻辑概念|表现力))(?=[、,，;；。]|者|优先|$)')
STATE_LEAD=re.compile(r'^(?:具备|具有|拥有|有着|有良好|有较强|有丰富)')
GENERIC_REQUIREMENT=re.compile(r'^(?:服从|听从|遵守|遵循)(?:公司|部门|工作|国家|法律|法令|各项|相关|上级|领导|的|和|与|及|安排|管理|指挥|制度|规定|规章|法规|要求|纪律|劳动|生产|安全|职业|道德|[、,，]){1,45}[。;；]*$')
EMPLOYER=re.compile(r'^(?!负责|协助|参与|审核|管理|维护|联系|对接|代表|帮助|支持|为|与|向|对|根据|按照)(?:[^。;；:]{1,85}(?:有限责任公司|股份有限公司|有限公司|集团|公司)(?:\([^)]{0,60}\))?\s*[,，]?\s*(?:成立|是|主要从事|主营|位于|专注|致力|总部|拥有)|(?:我司|本司|本公司)(?:为|是|主要)|[^。;；]{1,50}(?:工厂|新厂|公司|企业|中心)[,，]?\s*(?:大量招聘|诚聘|招聘普工))')
RECRUIT_NOTICE=re.compile(r'^(?!负责|协助|组织|策划|实施|开展|安排|发布|编写|制作|管理|参与).{0,50}(?:欢迎(?:您|你|大家|各位)(?:的)?加入|期待(?:您|你)(?:的)?加入|简历的小伙伴.{0,18}面试机会|投递简历|求职者请|报名咨询)')
ENVIRONMENT=re.compile(r'^(?:简单易懂|无需任何技术|无需技术|无需学历|工作简单|生熟手均可|不重|有活就干|没活休息|中途休息|休息时间长|车间内设|舒适优越工作环境|有人带教|可培训)[。;；!！,，]*')
LOCATION=re.compile(r'^(?:长期驻场|驻场地点|办公地址|办公地点|工作地点|上班地点|工作地址|负责区域|工作区域|服务区域|驻点地点)\s*[:：]?\s*[^。;；]*$')
PAYROLL_OP=re.compile(r'^(?:员工|职工|公司员工|公司|企业|人事)?(?:的)?(?:社保|社会保险|公积金|薪资|薪酬|工资|奖金|津贴|补贴|费用|报销)[^。;；]{0,55}(?:核算|计算|审核|登记|申报|办理|审批|增减员|停缴|续缴|补缴|转移|对账)')
MACHINE=re.compile(r'^(?:开|开启|操作|操纵|启动|运行|驾驶|驾驭)(?:CNC|数控|冲压|冲床|机床|车床|磨床|铣床|设备|机器|叉车|行车|吊车|货车|挖掘机|压铸|注塑|缝纫|自动机)',re.I)
BUSINESS_OBJECT=re.compile(r'客户|顾客|用户|市场|行业|项目|产品|商品|收费|校区|设备|设施|生产|工艺|订单|业务|运行|政策|技术|专业沟通|机床|车辆|材料|数据|需求|投诉|反馈|信息')
STATIC_KNOWLEDGE=re.compile(r'规则|规律|法规|法律|政策|原理|理论|软件|工具|协议|编程|语言|基础知识|技术知识|规范|标准|方法')
SOFTWARE_KNOWLEDGE=re.compile(r'数据库|框架|组件|类库|开发环境|软件|工具|脚本|语言|springcloud|mysql|oracle|springboot',re.I)
DYNAMIC_CONTEXT=re.compile(r'变化|变动|动态|进展|进度|状况|现状|现有|目前|及时|实时|随时|最新|痛点|诉求|配置|重点部位|隐蔽工程|发展要求|收费项目')
MODAL_PREFIX=re.compile(r'^(?:能(?:够)?|可以?|会)(?:独立|自主|高效|准确|及时|有效|熟练|完全|快速|安全|规范|主动|较好|很好的|很好|高质量|地|的|、|,)*')
MODAL_ACTION=re.compile(r'^(?:负责|协助|开展|进行|完成|处理|解决|控制|分析|判断|识别|制定|编制|编写|开发|设计|维护|安装|检修|沟通|协调|提供|支持|出具|承担|带领|组织|实施|操作|使用|维修|接待|回复|销售|举办|挖掘|抓住|运用|为.{1,45}(?:提供|解决)|(?:对|与|和|结合|根据|按照|通过|针对).{1,65}(?:负责|协助|完成|分析|解决|沟通|协调|提供|开发|设计|处理|制作|吸引))')
MODAL_ACTION=re.compile(MODAL_ACTION.pattern.replace('|运用|','|运用|还原|').replace('|制作|吸引','|制作|还原|吸引'))
OFFER_CLAUSE=re.compile(r'^(?!负责|协助|制定|规划|拓展|培养|促进|推动|管理)(?:公司|企业|工厂|新厂|本厂|平台|岗位)?.{0,8}(?:晋升空间|发展空间|晋升机会|发展机会).{0,15}$')
PLAIN_JOB_TITLE=re.compile(r'^(?:(?:电子|手工)?装配工|普工|操作员|物料员|质检员|检验员|测试员|搬运工|焊工|铆工|叉车工|保洁员)[。;；]*$')
WEAK_DUTY_HEADINGS={'职位描述','岗位描述','职位说明','岗位详情','职位详情'}
PURE_BENEFIT=re.compile(r'^(?:享有|享受|提供(?:住宿|食宿|工作餐|餐补|午餐|免费)|员工旅游|生日礼物|节日物资|到公司面试者报销|(?:[一二三四五六七八九十]+[:：])?完善的福利保障)')
BENEFIT_ADMIN=re.compile(r'负责|协助|核算|审核|审批|采购|策划|组织|制定|统计|登记|办理|管理')
COMMON_FIELD_WORDS={'学历','专业','经验','要求','技能','职责','内容','待遇','福利','岗位','职位'}
v2.QUANTITY=re.compile(v2.QUANTITY.pattern.replace('年|月|','款|项|台|套|份|门|张|批|辆|组|类|年|月|'))

for name,role in {
 '工作目标':'R','岗位目标':'R','主要工作目标':'R','职位详情':'R','岗位详情':'R',
 '岗位内容':'R','职责范围':'R','工作范围':'R','岗位基本需求':'Q',
 '基本技能和素质':'Q_FIELD','RequiredSkills&Knowledge':'Q_FIELD',
 '核心能力':'COMPETENCY','完善的福利保障':'B','相关待遇':'B',
 '学历背景及工作经验':'Q_FIELD','Education&Experience':'Q_FIELD',
 '办公地址':'A','办公地点':'A','驻场地点':'A','负责区域':'A','工作区域':'A'
}.items():rules.HROLE[name.lower()]=role
rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)
GENERIC_FIELDS=re.compile(r'(?P<q>(?:岗位|职位|任职|招聘|应聘|录用|招募)(?:基本|任职|资格|专业|技能|人员|素质)?(?:需求|要求|条件|资格))|(?P<r>(?:主要|核心|日常)?(?:工作|岗位|职位)(?:主要|基本|核心)?(?:目标|内容|任务|职责|范围|详情))|(?P<a>(?:办公|工作|上班|联系|驻场|驻点|面试)(?:地址|地点|区域))')

def headings(s):
 out=[]
 for h in BASE_HEADS(s):
  a,b=h['a'],h['b'];pre=s[:a];post=s[b:]
  inside=bool(a and re.search(r'[\u3400-\u9fffA-Za-z]$',pre))
  caption=(h['role'] in {'COMPETENCY','NOTICE'} or ':' in s[a:b] or s[a:a+1] in '-—[【(' or re.match(r'\s*[1-9]\d?[.、)]',post) or re.match(r'[ \t]*\n',post))
  if h['name'] in {'福利待遇','薪酬福利','薪资福利','员工福利'} and re.match(r'[ \t]*(?:技能培训|五险|六险|年底|年终|带薪|双休|绩效|岗位晋升|免费|节日)',post):caption=True
  if inside and h['name'] in COMMON_FIELD_WORDS and ':' not in s[a:b]:continue
  if inside and not caption:continue
  out.append(h)
 for m in GENERIC_FIELDS.finditer(s):
  a,b=m.span()
  if any(h['a']<=a<h['b'] for h in out):continue
  if a and not (s[a-1].isspace() or s[a-1] in '[【:：;；。,，)'):continue
  tail=re.match(r'[ \t]*(?:[:：][ \t]*|\r?\n)',s[b:])
  if not tail:continue
  role='Q' if m['q'] else 'R' if m['r'] else 'A'
  out.append(dict(a=a,b=b+tail.end(),role=role,name=m[0]))
 for m in re.finditer(r'(?m)^[ \t]*(核心能力)[ \t]*(?:\r?\n|[:：])',s):
  if not any(h['a']<=m.start(1)<h['b'] for h in out):out.append(dict(a=m.start(1),b=m.end(),role='COMPETENCY',name='核心能力'))
 return sorted(out,key=lambda h:(h['a'],h['b']))
rules.headings=headings

def normalize(raw):
 s,st=BASE_NORMAL(raw);es=[]
 # Exclamation marks delimit advertising sentences, except in programming code.
 if not rules.CODE.search(s):
  for m in re.finditer(r'[!！]+(?=\s*[\u3400-\u9fff(])',s):
   es.append(dict(a=m.start(),b=m.end(),old=m[0],new='。\n',rule='R12V3_AD_SENTENCE_BOUNDARY'))
 s,es=rules.apply(s,es)
 if es:st.append(dict(name='r12v3_sentence_layout',edits=es))
 return s,st
rules.normalize=normalize

def personal(t):
 t=v1.strip_clause(t)
 if TRAIT.match(t) or REVERSED_STATE.match(t):return True
 if STATE_LEAD.match(t) and not re.search(r'(?:系统|平台|产品|设备).{0,15}(?:开发|设计|建设|测试|改进)$',t):return True
 return False

def operational(t):
 t=v1.strip_clause(t)
 if re.search(r'(?:经验|经历|能力|者优先)[。;；,，]*$',t):return False
 if re.match(r'^(?:及时|定期|持续|深入|全面|充分|实时|随时)?(?:获悉|获知)',t) and BUSINESS_OBJECT.search(t):return True
 if re.match(r'^(?:及时|定期|持续|深入|全面|充分|实时|随时)?(?:了解|掌握|熟悉|理解)',t):
  first=re.split('[,，;；。]',t,1)[0]
  if BUSINESS_OBJECT.search(first) and (DYNAMIC_CONTEXT.search(first) or not (STATIC_KNOWLEDGE.search(first) or SOFTWARE_KNOWLEDGE.search(first))):
   return True
 return OLD_OPERATIONAL(t)
v1.operational=operational

def modal(t):
 t=re.sub(r'^(?:并且|并|同时)\s*','',v1.strip_clause(t));m=MODAL_PREFIX.match(t)
 return bool(m and MODAL_ACTION.match(t[m.end():]) and not v1.HARD_PERSON.search(t))

def is_task(t):
 t=v1.strip_clause(t)
 if personal(t):return False
 if MACHINE.match(t) or operational(t) or PAYROLL_OP.match(t):return True
 core=v2.CURRENT_ADV.sub('',t)
 if core!=t and BUSINESS_OBJECT.search(core) and not re.match(r'^(?:认可|认同|喜欢|热爱|向上|有责任|具备|具有|拥有|承担压力|吃苦)',core):return True
 return BASE_TASK(t)
rules.is_task=is_task

def decide(text,role,previous=None):
 t=v1.strip_clause(text)
 if not t:return 'S','R12V3_EMPTY'
 if EMPLOYER.match(t):return 'N','R12V3_NAMED_EMPLOYER_DESCRIPTION'
 if RECRUIT_NOTICE.match(t):return 'N','R12V3_RECRUITMENT_INVITATION_OR_APPLICATION_NOTICE'
 if re.match(r'^(?:接受|接收|可接受)(?:学徒工|学徒|应届生|应届毕业生)',t):return 'N','R12V3_APPLICANT_CATEGORY'
 if PURE_BENEFIT.match(t) and not BENEFIT_ADMIN.search(t):return 'N','R12V3_EXPLICIT_BENEFIT_OR_RECRUITMENT_PAYMENT'
 if OFFER_CLAUSE.match(t):return 'N','R12V3_EMPLOYER_DEVELOPMENT_OFFER'
 if PLAIN_JOB_TITLE.fullmatch(t):return 'N','R12V3_STANDALONE_WORKER_TITLE'
 if ENVIRONMENT.match(t) and not re.search(r'负责|核算|审核|办理|制定|安排',t[:12]):return 'N','R12V3_EMPLOYMENT_EASE_OR_ENVIRONMENT'
 if LOCATION.fullmatch(t) and not re.search(r'区域内|市场|客户|开拓|开发|销售|维护|管理|巡查|安装|检查|测试|实施|支持',t):return 'N','R12V3_STANDALONE_LOCATION_OR_DEPLOYMENT'
 if personal(t):return 'N','R12V3_EXPLICIT_PERSONAL_STATE_OR_TRAIT'
 if re.fullmatch(r'.{1,35}(?:业务岗|业务岗位|技术岗|技术岗位)[。;；]*',t) and not v2.ASSIGN.match(t):return 'N','R12V3_POSITION_TITLE'
 if re.match(r'^(?:需|需要)(?:在|到)?客户现场.{0,20}(?:共同)?(?:开发|调试|安装|实施)',t):return 'R','R12V3_EXPLICIT_CUSTOMER_SITE_ASSIGNMENT'
 if role is None and v1.KNOW.match(t) and not DYNAMIC_CONTEXT.search(t):return 'N','R12V3_UNHEADED_STATIC_KNOWLEDGE_CONDITION'
 if role in {'Q','Q_FIELD'}:
  if re.match(r'^(?:或|或者|且|以及|并|同时)\s*(?:从事过|参与过|负责过(?!程|账|户|期)|曾经|有过)',t):return 'N','R12V3_COORDINATED_PAST_EXPERIENCE'
  if MODAL_PREFIX.match(t) or GENERIC_REQUIREMENT.fullmatch(t) or v1.KNOW.match(t):return 'N','R12V3_APPLICANT_MODAL_KNOWLEDGE_OR_COMPLIANCE'
  if re.match(r'^(?:员工全国跟随项目出差|员工入职后|培训完成后|对于交通不便者)',t) or re.search(r'(?:周|入职|园区).{0,30}(?:培训|住宿)',t):return 'N','R12V3_ENTRY_TRAINING_OR_DEPLOYMENT_CONDITION'
 if role=='Q' and v1.nominal(t) and not v1.parent.v4.FIELD_ONLY.fullmatch(t):return 'R','R12V3_CONCRETE_NOMINAL_WORK_IN_MIXED_LIST'
 if re.match(r'^熟练(?:使用|运用|掌握)',t) and SOFTWARE_KNOWLEDGE.search(t) and not re.search(r'(?:完成|编写|编制|开发|设计|制作|处理).{2,}',t[4:]):return 'N','R12V3_SOFTWARE_PROFICIENCY_WITHOUT_TASK'
 if role in {'R',None}:
  if MACHINE.match(t) and not v1.HARD_PERSON.search(t):return 'R','R12V3_EXPLICIT_MACHINE_OPERATION'
  if operational(t) and not v1.HARD_PERSON.search(t):return 'R','R12V3_CURRENT_BUSINESS_INFORMATION_ACQUISITION'
  if PAYROLL_OP.match(t) and not re.search(r'\d+\s*(?:元|号|月)|公司为|我们为',t):return 'R','R12V3_EXPLICIT_HR_PAYROLL_ADMINISTRATION'
  if role=='R' and (modal(t) or re.match(r'^能(?:够)?保持良好沟通',t)) and not rules.DAMAGE.search(t):return 'R','R12V3_CURRENT_MODAL_ACTION'
  core=v2.CURRENT_ADV.sub('',t)
  if core!=t and BUSINESS_OBJECT.search(core) and is_task(t) and not rules.DAMAGE.search(t) and not v1.HARD_PERSON.search(t):return 'R','R12V3_BUSINESS_ACTION_WITH_MANNER_ADVERB'
 return BASE_DECIDE(text,role,previous)
rules.decide=decide

def partitions(s):
 out=[];key=None;inferred=None;company=False;tasks=benefits=0;had_work=False;qcontinuation=False
 for base in RAW_PARTS(s):
  u=dict(base);original=u.get('section');newkey=(original,u.get('heading'))
  if newkey!=key:
   key=newkey;inferred=None;tasks=benefits=0;had_work=False;qcontinuation=False;company=original=='C'
  if u.get('label')=='S':
   if u['reason']=='EXPLICIT_SECTION_HEADING':company=original=='C'
   if 'LIST_MARKER' in u['reason'] or 'ORDINAL' in u['reason']:qcontinuation=False
   out.append(u);continue
  t=v1.strip_clause(s[u['a']:u['b']])
  if EMPLOYER.match(t):company=True
  if company and not v1.parent.ASSIGN_SUBJECT.match(t):
   u.update(original_section=original,section='C',context_basis='COMPLETE_EMPLOYER_PREFACE_UNTIL_NEW_SECTION');out.append(u);continue
  weak=original=='R' and u.get('heading') in WEAK_DUTY_HEADINGS
  first=v1.strip_clause(re.split('[,，;；。]',t,1)[0])
  if weak and not had_work and (v1.KNOW.match(first) or DEGREE_START.match(first) or personal(first)):inferred='Q'
  effective=inferred if (original in {None,'A'} or weak) and inferred else original
  lab,why=decide(t,effective)
  firstlab,firstwhy=decide(first,effective)
  weak_reasons={'LITERAL_CONTENT_OF_EXPLICIT_DUTY_SECTION','DEPENDENT_TASK_CONTINUATION','PRIOR_LITERAL_DUTY_PRESERVED_WITHOUT_POSITIVE_REMOVAL_EVIDENCE'}
  clear=lab=='R' and why not in weak_reasons and not personal(t)
  firstclear=firstlab=='R' and firstwhy not in weak_reasons and not personal(first)
  if firstclear:clear=True
  if effective=='R' and modal(first):clear=True
  q=(DEGREE_START.match(first) or personal(first) or v1.qualification(first)) and not clear
  offer=lab=='N' and any(w in why for w in ['BENEFIT','PAY_INFORMATION','EMPLOYMENT_OFFER','COMPENSATION','EMPLOYEE_BENEFIT']) and not v2.ASSIGN.match(t)
  if original=='R' and not had_work and offer:
   benefits+=1
   if benefits>=2:inferred='B'
  if original in {None,'A'} or weak:
   if clear:inferred='R';had_work=True;tasks+=1
   elif q and not (weak and (had_work or MODAL_PREFIX.match(first) and inferred is None)):inferred='Q'
   if inferred:u.update(original_section=original,section=inferred,context_basis='FULL_SOURCE_TASK_AND_QUALIFICATION_SEQUENCE')
  elif original=='Q' and u.get('heading') in {'岗位要求','岗位需求'}:
   if clear:tasks+=1
   elif q:tasks=0;inferred='Q'
   if tasks>=2:inferred='R'
   if inferred=='R':u.update(original_section=original,section='R',context_basis='CONSECUTIVE_EXPLICIT_ASSIGNMENTS')
  elif original=='R' and inferred=='B' and not v2.ASSIGN.match(t):
   u.update(original_section=original,section='B',context_basis='EXPLICIT_BENEFIT_SEQUENCE_WITHOUT_ASSIGNED_WORK')
  if original=='R' and clear:had_work=True
  if qcontinuation and not clear and not MODAL_PREFIX.match(t) and u['section'] not in NON_DUTY:
   u.update(original_section=original,section='Q_FIELD',context_basis='KNOWLEDGE_ITEM_CONTINUATION')
  if q and (v1.KNOW.match(t) or v2.KNOWLEDGE_TOPIC.match(t)):qcontinuation=True
  elif clear:qcontinuation=False
  out.append(u)
 return out
rules._partitions10=partitions

def split_mixed(s,a,b,role):
 points={a,b}
 for lo,hi in BASE_SPLIT(s,a,b,role):points.update((lo,hi))
 cs=v1.clauses(s,a,b)
 for i,(lo,hi) in enumerate(cs):
  t=v1.strip_clause(s[lo:hi]);left=v1.strip_clause(s[a:lo])
  if ENVIRONMENT.match(t) or LOCATION.fullmatch(t) or RECRUIT_NOTICE.match(t) or OFFER_CLAUSE.match(t) or PLAIN_JOB_TITLE.fullmatch(t):points.update((lo,hi))
  if role=='R' and i:
   if personal(t) or DEGREE_START.match(t):points.add(lo)
   if modal(left) and (personal(t) or v1.HARD_PERSON.search(t)):points.add(lo)
   if v1.qualification(left) and (modal(t) or operational(t)):points.add(lo)
   if PAYROLL_OP.match(t) and re.search('员工|人事|入职|离职|劳动合同|考勤',left):points.add(lo)
  if role in {'Q','Q_FIELD'} and MODAL_PREFIX.match(v1.strip_clause(s[a:b])):
   # The ability modal governs coordinated predicates throughout this item.
   return [(a,b)]
 first=v1.strip_clause(s[cs[0][0]:cs[0][1]]) if cs else ''
 hard_governor=bool(rules.HARDQUAL.search(first) and v1.qualification(first) and not v2.ASSIGN.match(first))
 if role=='R' and not hard_governor:
  for m in re.finditer(r'并(?:且)?能(?:够)?',s[a:b]):
   pos=a+m.start()
   if modal(s[pos:b]) and v1.qualification(s[a:pos]):points.add(pos)
 if hard_governor and not (role=='R' and modal(first)):
  for pos in list(points-{a,b}):
   if modal(s[pos:b]):points.discard(pos)
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

def _process(raw,row):
 p=v2.process(raw,row);s,_=replay(raw,p['normalization']);changed=False
 for u in p['partition']:
  if u['label']=='S':continue
  lab,why=decide(s[u['a']:u['b']],u.get('section'))
  if why.startswith('R12V3_') and (lab in {'N','S','X'} or lab=='R' and u['label']!='X'):
   if u['label']!=lab:changed=True
   u.update(label=lab,reason=why)
 if changed:
  engine.rebuild(p,s);p['proposed_after']=p['after'];p['adopted']=True;p['text_changed']=p['after']!=p['before'];p['preserve_parent_reason']=None
 p['policy_version']='R12_V3_UNIFIED_FULL_SOURCE_RULES'
 return p

@functools.lru_cache(maxsize=4096)
def _cached(raw,before):
 return _process(raw,dict(record_id='LITERAL_SOURCE_CACHE',responsibility_text=before))

def process(raw,row):
 # No metadata, record identity, employer or year enters the classification.
 p=dict(_cached(raw,row['responsibility_text']));p['record_id']=row['record_id'];return p
