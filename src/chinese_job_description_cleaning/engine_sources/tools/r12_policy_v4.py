"""Fourth candidate: explicit section boundaries and clause-level duty scope.

Source-only decisions; historical body is comparison evidence, never a label.
No identifier, company, occupation or year is used for classification.
"""
import re, functools
from tools import r12_policy_v3 as v3
from tools.r11_verify_release import replay
v2=v3.v2;v1=v3.v1;rules=v3.rules;engine=v3.engine
BASE_HEAD=rules.headings;BASE_NORMAL=rules.normalize;BASE_DECIDE=rules.decide
BASE_SPLIT=rules.split_mixed;BASE_TASK=rules.is_task;BASE_OP=v1.operational
for name,role in {'理想中的你':'Q','我们期待的你':'Q','我们希望你':'Q','你需要具备':'Q','应具备条件':'Q','企业福利':'B','报酬福利':'B','其他福利':'B','培训体系':'B','平台优势':'B','位职责':'R'}.items():rules.HROLE[name.lower()]=role
rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)
STRONG_CAPTIONS=re.compile(r'(?P<bracket>[【\[](?P<name>[^】\]\n]{2,25})[】\]])|(?P<plain>岗位职责|岗位要求|工作内容|任职要求|任职资格|职位要求|职责描述|福利待遇|薪资福利|薪酬福利|员工福利)(?P<end>\s*[:：]|(?=[1-9][.、)]))')
BENEFIT_HEAD=re.compile(r'(?:福利待遇|员工福利|薪酬福利)(?=\s*(?:技能培训|五险|六险|带薪|年终|年底|绩效|免费|节日|双休))')

def headings(s):
 hs=BASE_HEAD(s);extra=[]
 for m in STRONG_CAPTIONS.finditer(s):
  name=m['name'] or m['plain'];role=rules.HROLE.get(name.lower())
  if not role:continue
  # Brackets/colon are explicit field syntax, even after a task predicate.
  a,b=m.span();tail=re.match(r'\s*[:：]?\s*',s[b:]);b+=tail.end()
  extra.append(dict(a=a,b=b,role=role,name=name))
 for m in BENEFIT_HEAD.finditer(s):extra.append(dict(a=m.start(),b=m.end(),role='B',name=m[0]))
 for e in extra:
  covering=[h for h in hs if h['role']==e['role'] and h['a']<=e['a'] and e['a']<h['b']<=e['b']]
  if covering:e['a']=min(e['a'],*(h['a'] for h in covering))
  hs=[h for h in hs if not (h['a']<e['b'] and e['a']<h['b'])];hs.append(e)
 return sorted(hs,key=lambda h:(h['a'],h['b']))
rules.headings=headings

def normalize(raw):
 s,st=BASE_NORMAL(raw);ms=list(re.finditer(r'(?<![\d.])([1-9]\d?)\.02(?=[\u3400-\u9fff])',s))
 # Repeated ordinal+02 artifacts only; decimals and single occurrences stay.
 if len(ms)>=3 and any(int(y[1])==int(x[1])+1 for x,y in zip(ms,ms[1:])):
  es=[dict(a=m.start(),b=m.end(),old=m[0],new=m[1]+'、',rule='R12V4_REPEATED_ORDINAL_ENCODING_ARTIFACT') for m in ms]
  s,es=rules.apply(s,es);st.append(dict(name='r12v4_proven_ordinal_layout',edits=es))
 return s,st
rules.normalize=normalize

TRAIT=re.compile(r'^(?:(?:沟通|表达|沟通表达|沟通协调|语言表达|逻辑思维|学习|执行|抗压)(?:能力)?(?:良好|优秀|较好|出色|强)|关注细节(?=[。;；,，]|$))')
Q_RESEARCH=re.compile(r'^(?:对|对于).{1,55}有(?:一定|较深|深入|较多|深刻)?(?:的)?(?:研究|认识|理解|了解|认知)(?=[,，;；。]|$)')
CREDENTIAL=re.compile(r'^(?:通过|取得|持有|具备|具有|拥有).{0,45}(?:从业考试|从业资格|执业资格|资格考试|资格证书)(?=[,，;；。]|$)')
APPLICATION=re.compile(r'^(?:需|须|需要|要求|请|必须)(?:提供|提交|携带|附上)(?:个人|本人|相关|设计|原创|代表)?(?:作品|简历|证件|证书|照片|材料)(?=[,，;；。]|集|$)')
RECRUIT=re.compile(r'^(?!负责|协助|管理|组织|制定|实施|开展|发布|编写|维护|更新|优化|统筹).{0,65}(?:欢迎投递|同步招聘|现正招聘|现招聘|现招|诚招|诚聘|针对.{0,15}招聘.{0,25}\d+名)')
EMPLOYMENT=re.compile(r'^(?:可以?|能(?:够)?|愿意)?(?:接受|适应|服从)(?:公司|集团|单位|部门|上级|领导|的|安排|调配|管理|短期|长期|异地|全国|外派|出差|倒班|加班|[()、,，\u3400-\u9fff]){0,60}$')
HR_WORK=re.compile(r'^(?:(?:应聘|求职|候选)(?:人员|者|人)(?:的)?(?:预约|接待|初面|面试|筛选)|招聘[、,，].{0,35}(?:培训|管理|考核)|(?:每周|每月|每日|定期|月度|周度).{0,45}(?:核对考勤|处理考勤|考勤异常|工资异常)|(?:对|根据|依据).{0,45}(?:员工|人员|人才).{0,15}招聘.{0,40}(?:协调|共享|计划|管理))')
NOMINAL_INFO=re.compile(r'^.{2,85}(?:信息|通知|文件|决议|政策)(?:的)?(?:上传下达|传达|传递)[。;；,，]*$')
DRAWING=re.compile(r'^(?:绘制.{2,90}(?:图|图纸)|.{2,40}图纸绘制)[。;；,，]*$')
MANAGEMENT=re.compile(r'^(?:领导|带领|组织|指导)(?:下属|团队|员工|人员).{1,80}(?:建设|提升|提高|培养|完成|执行|落实|做好)')
ADDITIONAL_WORK=re.compile(r'^(?:(?:依据|根据).{0,30}招聘计划.{0,55}发布.{0,15}招聘信息|(?:人员|人才|员工)招聘[,，].{0,40}招聘人才|.{2,40}(?:辅材|物料|材料|设备)验收[。;；,，]*$|.{2,70}(?:车辆|运力|车队).{0,50}(?:询价|询价工作)[。;；,，]*$|(?:及时|定期)?补足.{1,25}库存|满足.{1,25}(?:客户|销售|市场|业务)需求|服务好客户|介绍[、,，]销售.{2,}|(?:通过|使用).{0,25}电话\d+\*{1,6}系统呼出|供应商考评[:：].{1,140}对供应商进行考评)')
v3.MODAL_ACTION=re.compile(v3.MODAL_ACTION.pattern.replace('|开展|','|部署|驱动|改善|提升|开展|').replace('|制作|还原|吸引','|制作|还原|驱动|改善|提升|进行|吸引'))

def operational(t):
 t=v1.strip_clause(t)
 if re.match(r'^(?:及时|定期|深入|全面|充分)?(?:掌握|了解|熟悉|理解)',t) and re.search(r'竞争对手|竞品|供应商|经销商|价格策略|经营策略|经销手段',t) and not re.search('经验|能力|者优先|方法|知识',t):return True
 if re.match(r'^(?:及时|深入|全面|充分)?(?:了解|掌握|理解)',t) and re.search(r'(?:行业|市场|业务).{0,10}(?:现状|动态|变化|行情)',t) and not re.search('能力|经验|优先',t):return True
 return BASE_OP(t)
v1.operational=operational;v3.operational=operational

def is_task(t):
 t=v1.strip_clause(t)
 if TRAIT.match(t) or CREDENTIAL.match(t) or APPLICATION.match(t):return False
 if HR_WORK.match(t) or NOMINAL_INFO.match(t) or DRAWING.match(t) or MANAGEMENT.match(t) or ADDITIONAL_WORK.match(t):return True
 return BASE_TASK(t)
rules.is_task=is_task

def decide(text,role,previous=None):
 t=v1.strip_clause(text).lstrip('、').strip()
 if TRAIT.match(t):return 'N','R12V4_PERSONAL_COMMUNICATION_OR_ATTITUDE'
 if re.match(r'^(?:曾经|曾|过去)?(?:负责过|承担过|担任过|参与过|从事过)',t):return 'N','R12V4_PAST_WORK_EXPERIENCE'
 if role is None and v1.KNOW.match(t) and not v3.DYNAMIC_CONTEXT.search(t):return 'N','R12V4_UNHEADED_STATIC_KNOWLEDGE'
 if re.fullmatch(r'(?:承担|承受|接受)(?:工作|一定|较大|各种)?压力[。;；,，]*',t):return 'N','R12V4_PERSONAL_PRESSURE_TOLERANCE'
 if v1.KNOW.match(t) and re.search(r'经验[^。;；]{0,12}优先[。;；,，]*$',t):return 'N','R12V4_KNOWLEDGE_WITH_EXPERIENCE_GOVERNOR'
 if CREDENTIAL.match(t):return 'N','R12V4_APPLICANT_CREDENTIAL'
 if APPLICATION.match(t):return 'N','R12V4_APPLICATION_SUBMISSION'
 if RECRUIT.match(t) and not HR_WORK.match(t):return 'N','R12V4_RECRUITMENT_NOTICE'
 if re.match(r'^岗前(?:有|提供|带薪|免费)',t):return 'N','R12V4_PRE_EMPLOYMENT_TRAINING'
 if role in {None,'R'} and ADDITIONAL_WORK.match(t) and not re.search(r'经验|能力|优先|具备|熟悉|要求',t):return 'R','R12V4_COMPLETE_ADMINISTRATIVE_COMMERCIAL_OR_NOMINAL_WORK'
 if role in {'Q','Q_FIELD'}:
  if re.match(r'^(?:提供|提交|携带)(?:个人|本人|相关)?(?:简历|证件|照片|作品)(?=[,，;；。]|集|$)',t):return 'N','R12V4_APPLICANT_SUBMISSION_LIST'
  if re.match(r'^(?:遵守|服从|听从).{0,45}(?:制度|安排|纪律|管理|规定|文化)[。;；,，]*$',t):return 'N','R12V4_GENERIC_APPLICANT_COMPLIANCE'
  if Q_RESEARCH.match(t) or re.search(r'专业(?:者)?优先|专业不限|不受专业限制',t) and not v2.ASSIGN.match(t):return 'N','R12V4_EDUCATION_OR_KNOWLEDGE_BACKGROUND'
  if re.match(r'^(?:可以?|能(?:够)?|愿意)?(?:接受|适应|服从|听从)',t) and re.search(r'出差|外派|调配|安排|倒班|加班|企业文化',t):return 'N','R12V4_EMPLOYMENT_ACCEPTANCE'
 if role in {None,'R'} and not rules.DAMAGE.search(t):
  if HR_WORK.match(t):return 'R','R12V4_RECRUITMENT_AND_PAYROLL_ADMINISTRATION'
  if NOMINAL_INFO.match(t):return 'R','R12V4_NOMINAL_INFORMATION_DISTRIBUTION'
  if DRAWING.match(t):return 'R','R12V4_COMPLETE_DRAWING_TASK'
  if MANAGEMENT.match(t):return 'R','R12V4_MANAGING_OTHERS_AND_IMPROVING_CAPACITY'
  if re.match(r'^(?:固定|指定|负责)?区域.{0,15}(?:收派件|收件|派件|揽件|配送)',t):return 'R','R12V4_NOMINAL_DELIVERY_WORK'
  if operational(t) and not v1.HARD_PERSON.search(t):return 'R','R12V4_OPERATIONAL_INFORMATION'
 if re.match(r'^(?:\d+[、.])?\d*\s*(?:Six\s*Sigma|Sigma|6\s*Sigma|六西格玛).{0,30}(?:知识|能力|优先)',t,re.I):return 'N','R12V4_EXPLICIT_SKILL_CREDENTIAL'
 return BASE_DECIDE(text,role,previous)
rules.decide=decide

def split_mixed(s,a,b,role):
 cs=v1.clauses(s,a,b);points={a,b}
 for lo,hi in BASE_SPLIT(s,a,b,role):points.update((lo,hi))
 full=v1.strip_clause(s[a:b]);first=v1.strip_clause(s[cs[0][0]:cs[0][1]]) if cs else ''
 # Experience/ability governs its skill object list; actual assignments escape.
 if v1.KNOW.match(first) and (v1.EXPERIENCE.search(full) or re.search(r'经验[^。;；]{0,12}优先[。;；,，]*$',full)):
  return [(a,b)]
 if re.match(r'^(?:良好|优秀|较强|流利).{0,25}(?:英语|英文|外语|语言).{0,15}能力',first):return [(a,b)]
 if role in {'Q','Q_FIELD'}:
  for i,(lo,hi) in enumerate(cs):
   t=v1.strip_clause(s[lo:hi]).lstrip('、')
   if i and re.match(r'^(?:负责(?!人|过)|协助|主导|承担(?!过)|实现)',t) and not re.search(r'能力|经验|经历|者优先',t) and not (t.startswith('实现') and (v3.MODAL_PREFIX.match(first) or not v1.KNOW.match(first.lstrip('、')))):points.add(lo)
  if re.match(r'^(?:可以?|能(?:够)?|愿意)?(?:接受|适应)',first):
   for lo,hi in cs:points.update((lo,hi))
 # Current information may have a comma-separated object list before 现状.
 if role=='R' and v1.KNOW.match(first) and operational(full):
  for lo in list(points-{a,b}):
   suffix=v1.strip_clause(s[lo:b])
   if not re.match(r'^(?:并|同时|负责|协助|对|根据|针对|完成|制定|编写|确保|能|可|有|具备|具有|拥有)',suffix) and not v1.qualification(suffix):points.discard(lo)
 for m in re.finditer(r'岗前(?:有|提供)?(?:带薪|免费)?培训',s[a:b]):points.add(a+m.start())
 return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

@functools.lru_cache(maxsize=8192)
def _cached(raw):
 # The empty comparison prevents historical output from acting as evidence.
 # Historical exact-source reviews remain source-keyed, not record-keyed.
 p=v3._process(raw,dict(record_id='CACHE',responsibility_text=''));s,_=replay(raw,p['normalization'])
 changed=False
 for u in p['partition']:
  if u['label']=='S':continue
  lab,why=decide(s[u['a']:u['b']],u.get('section'))
  if why.startswith('R12V4_') and (lab in {'N','S','X'} or lab=='R' and u['label']!='X'):
   changed |= lab!=u['label'];u.update(label=lab,reason=why)
 # Preserve a complete work target attached to the following retained action.
 us=p['partition']
 for i,u in enumerate(us):
  t=v1.strip_clause(s[u['a']:u['b']])
  if u['label']=='N' and u['reason']=='SOURCE_DEPENDENT_CONTEXT_NOT_STANDALONE' and u.get('section')=='R' and re.match(r'^针对.{2,55}(?:客户|产品|项目|设备|系统)[,，;；。]*$',t):
   nxt=next((v for v in us[i+1:] if v['label']!='S'),None)
   if nxt and nxt['label']=='R' and nxt.get('heading')==u.get('heading') and not rules.DAMAGE.search(t):u.update(label='R',reason='R12V4_WORK_TARGET_OF_ADJACENT_ACTION');changed=True
 engine.rebuild(p,s);p['proposed_after']=p['after'];p['adopted']=True;p['preserve_parent_reason']=None
 p['policy_version']='R12_V4_SOURCE_ONLY_COMPLETE_CLAUSE'
 return p

def process(raw,row):
 p=dict(_cached(raw));before=row['responsibility_text']
 p.update(record_id=row['record_id'],before=before,before_sha256=engine.digest(before.encode()),text_changed=p['after']!=before,parent_role='COMPARISON_ONLY_NOT_CLASSIFICATION')
 return p
