"""R12: complete qualification scope, assigned work, and nominal work lists.

Additive policy in a new module. All retained text remains a source interval.
Frozen R11 modules and data are never edited. No record-ID-specific decisions.
"""
import re
from tools import r11_policy_v5 as parent
from tools.r11_verify_release import replay

rules=parent.rules
engine=parent.engine
BASE_DECIDE=rules.decide
BASE_QUAL=rules.qualification
BASE_TASK=rules.is_task
BASE_SPLIT=rules.split_mixed
BASE_HEADINGS=rules.headings
BASE_FINISH=rules.finish_body

ADV=r'(?:(?:并且|并|同时|主要|具体|日常|及时|准确|充分|深入|全面|有效|独立|快速|严格|认真|积极|持续|不断|进一步)(?:地)?)*'
DYNAMIC=re.compile(r'^'+ADV+r'(?:了解|掌握|理解|熟悉)(?:客户.{0,8}(?:需求|诉求|动态|状况|状态|进展|业务)|市场.{0,8}(?:动态|行情|变化|信息|需求)|行业.{0,8}(?:动态|态势|趋势)|(?:业务|项目|生产|设备|库存|销售).{0,8}(?:进展|进度|状态|状况|动态|情况))')
MODAL=re.compile(r'^(?:能(?:够)?|可|会)(?:(?:独立|高效|准确|及时|有效|熟练|完全|快速|安全|规范)(?:地|的|、|,)?)*(?:开展|进行|完成|处理|解决|控制|分析|判断|识别|制定|编制|编写|开发|设计|维护|安装|检修|沟通|协调|提供|支持|出具|承担|带领|组织|实施|操作|使用|维修|接待|回复|销售|举办).{2,}')
EXPERIENCE=re.compile(r'(?:经验|经历|年限|履历)(?:丰富|扎实|优先|者优先|为佳|尤佳)?[。;；,，\s]*$|(?:\d+|[一二两三四五六七八九十]+)\s*年(?:以上|及以上|左右)?(?:的)?(?:相关)?(?:经验|工作|经历)?[。;；,，\s]*$')
KNOW=re.compile(r'^(?:一定程度上|一定程度|基本|比较|较为|全面|深入|充分|并|同时)*(?:熟悉|熟知|通晓|精通|了解|掌握|理解|善于|擅长)')
PERSONAL=re.compile(r'^(?:对[^,，;；。]{1,45}(?:敏感|领悟深|有[^,，;；。]{0,25}(?:认识|认知|见解|想法|理解|意识))|逻辑性强|思维敏捷|学习(?:力|成绩|能力|和适应能力)|执行力|开发基础(?:良好|扎实)|负责的职业态度|(?:优秀|良好|较强)的.{0,40}(?:能力|精神|意识)|对[^,，;；。]{1,35}有(?:强烈|较强|良好)的意识)')
CREDENTIAL=re.compile(r'^(?:需|须|必须|要求)?(?:持有|持|具备|取得).{1,35}(?:资格证(?:书)?|操作证|上岗证|电工证|会计师证|驾驶证|消防操作证|职称)[。;；,，\s]*$')
OBJECT=re.compile(r'订单|工单|料单|排期|齐套|备损|试产|物料|存货|呆料|库存|交货|备料|供应商|客户|品质|质量|产品|项目|设备|模型|数据|系统|档案|文件|资料|合同|报表|报告|票据|费用|成本|风险|生产|技术|工艺|异常|需求|OB|OTD|效率|流程|人员|员工|车辆|仓库',re.I)
NOM_END=re.compile(r'(?:搭建|建设|建立|结清|清理|清点|上报|填报|预测|评审|改善|改进|推动|跟进|减少|降低|提升|提高|准确性|准确率|齐套率|及时性|模型|维护|保养|盘点|检查|管理|核算|分析|检测|调研|汇总|整理|审核|收集|记录|处理|跟踪|培训|编制|编写|规划|排程|安排|优化|支持|开发|设计|制作|交付|落实)(?:等|工作|等工作)?[。;；,，\s]*$')
HARD_PERSON=re.compile(r'学历|学位|者优先|优先考虑|优先录用|毕业|本科|硕士|研究生|大专|高中|中专|从业经验|工作经验|工作履历|相关经验|(?:具备|具有|拥有).{0,30}(?:经验|能力|知识)|有.{0,10}(?:年|经验)|适应.{0,8}(?:出差|倒班|加班)')
CURRENT=re.compile(r'^'+ADV+r'(?:负责(?!过)|协助|承担|主导|推动|推进|跟进|形成|建立|搭建|培养|提高|提升|增强|整合|识别|监控|监测|执行|开展|进行|制定|编制|编写|组织|指导|协调|处理|解决|维护|开发|设计|管理|支持|提供|实施|总结|学习|阅读|研究|关注)(?=.{2,})')
BENEFIT_ROLES={'B','OFFER','C','A'}

def strip_clause(t):
    t=rules.cleantext(t)
    return t[1:-1].strip() if t.startswith('(') and t.endswith(')') else t

def operational(t):
    if DYNAMIC.match(t) or parent.BUSINESS_INFO.match(t) or re.match(r'^'+ADV+r'(?:了解(?:和|并|及)?(?:发掘|收集)|掌握售点|(?:善于)?(?:捕捉|把握)(?:客户需求|市场.{0,10}(?:动态|信息)|行业.{0,12}趋势))',t):return True
    first=re.split('[,，;；。]',t,1)[0]
    if re.search('法规|法律|政策|标准|规范|原则|原理|规律|编程|软件|工具|流程|技巧|技术|专业知识',first):return False
    return bool(rules.operational_knowledge(t))

def nominal(t):
    t=strip_clause(t)
    t=re.sub(r'\([^()]*\)\s*$', '',t).rstrip()
    return bool(len(t)>3 and OBJECT.search(t) and NOM_END.search(t)
        and not re.search('学历|学位|经验|经历|能力|知识|熟悉|熟练|精通|掌握|优先|要求|职业发展|培养方向|公司提供|招聘|应聘|福利|补贴|奖金',t)
        and not re.match(r'^(?:能|可|会|至少|如|例如|研究生|本科|硕士|博士|\d+年)',t)
        and not rules.DAMAGE.search(t))

def current(t):
    t=strip_clause(t)
    if HARD_PERSON.search(t) or PERSONAL.match(t) or re.search('从基层做起|职业态度|培养方向|培养计划',t):return False
    if EXPERIENCE.search(t) and not (CURRENT.match(t) or re.match(r'^对现有',t)):return False
    return bool(CURRENT.match(t) or operational(t) or nominal(t))

def personal(t):
    t=strip_clause(t)
    if CREDENTIAL.match(t) or PERSONAL.match(t):return True
    if KNOW.match(t) and not operational(t):return True
    if re.match(r'^(?:对于|对|在).{0,160}(?:需要|要求)(?:有|具备|具有).{0,65}(?:知识|经验|能力)',t):return True
    if (t.startswith(('有','具备','具有','拥有','对','在','对于')) or re.search('岗位工作|职位工作',t)) and EXPERIENCE.search(t):
        if not re.match(ADV+r'(?:总结|归纳|分享|积累|沉淀|交流|传授|收集|记录|提炼|整合|组织)|^对现有',t):return True
    return False

def is_task(t):
    t=strip_clause(t)
    if personal(t):return False
    if operational(t):return True
    core=rules.ADVERB.sub('',t)
    if core!=t and BASE_TASK(core) and not HARD_PERSON.search(t):return True
    return BASE_TASK(t)
rules.is_task=is_task

def qualification(t):
    t=strip_clause(t)
    if personal(t):return True
    # Do not read 有效整合...能力 as 有...能力 (possession).
    core=rules.ADVERB.sub('',t)
    if operational(t) or core!=t and BASE_TASK(core) and not HARD_PERSON.search(t):return False
    return BASE_QUAL(t)
rules.qualification=qualification

def decide(text,role,previous=None):
    t=strip_clause(text)
    if not t:return 'S','R12_EMPTY_SEPARATOR'
    if role in {'NOTICE','COMPETENCY'}:return 'N','R12_EXPLICIT_NON_TASK_NOTICE_OR_COMPETENCY_BLOCK'
    if re.fullmatch(r'\*{2,}(?:大|高|低)?(?:限度|程度)地?',t):return 'X','R12_UNRECOVERABLE_MASKED_DEGREE_MODIFIER'
    if t in {'权责范围','权利','责任','一','二','三','四','五','全面负责','机修机电'}:return 'S','R12_ORPHAN_STRUCTURE_OR_RESPONSIBILITY_LEVEL'
    if re.match(r'^(?:我司|本司|本公司|公司|本企业|企业|集团)(?:目前|现|主要|长期|一直)?(?:为|是一家|从事|经营|主营|的.{0,18}(?:规模|业务|产品)(?:主要)?(?:有|为|是))',t):return 'N','R12_EMPLOYER_SUBJECT_PROFILE'
    if re.match(r'^(?:储备干部|管理培训生|管培生)?.{0,12}培养方向(?:为|是|:)',t):return 'N','R12_TRAINING_DIRECTION_NOT_ASSIGNED_TASK'
    if re.search(r'诚聘|工厂直聘|不收取任何介绍费',t[:60]) and not re.match(ADV+r'(?:负责|协助|组织|开展|管理)',t):return 'N','R12_RECRUITMENT_ADVERTISEMENT'
    if re.match(r'^岗位\*?【[^】]+】.{0,40}详情',t):return 'N','R12_RECRUITMENT_TITLE'
    if re.match(r'^(?:不穿无尘服|不看显微镜|中央空调车间|空调车间)',t):return 'N','R12_WORKPLACE_ENVIRONMENT'
    if re.match(r'^.{0,65}派遣制员工',t) or re.match(r'^(?:需|须|需要)与.{0,50}(?:签字|签订|签署)劳动合同',t):return 'N','R12_EMPLOYMENT_RELATIONSHIP'
    if role in BENEFIT_ROLES and not rules.POSITIVE_ASSIGN.match(t) and not parent.ASSIGN_SUBJECT.match(t) and not re.match(r'^'+ADV+r'(?:核算|审核|统计|编制|办理员工|办理职工|申报员工)',t):return 'N','R12_NON_DUTY_SECTION_SCOPE'
    if re.match(r'^(?:新员工|员工|职工).{0,25}(?:费用|补贴|补助).{0,12}(?:公司报销|公司承担|企业承担)',t):return 'N','R12_EMPLOYEE_BENEFIT'
    if re.match(r'^.{1,12}奖\s*[:：(].{0,30}(?:元|\d)',t) and not re.match(r'负责|制定|核算|审核|统计',t):return 'N','R12_BENEFIT_AWARD_AMOUNT'
    if personal(t):return 'N','R12_COMPLETE_PERSONAL_CONDITION'
    if role in {'Q','Q_FIELD'} and KNOW.match(t):return 'N','R12_KNOWLEDGE_IN_APPLICANT_SECTION'
    if role in {None,'Q','Q_FIELD'} and re.match(r'^至少.{0,100}全程参与.{0,30}完整.{0,15}项目',t):return 'N','R12_MINIMUM_COMPLETE_PROJECT_EXPERIENCE'
    if role in {'Q','Q_FIELD'} and HARD_PERSON.search(t) and not rules.POSITIVE_ASSIGN.match(t) and not parent.ASSIGN_SUBJECT.match(t):return 'N','R12_EXPLICIT_APPLICANT_ELIGIBILITY_SCOPE'
    if role in {'Q','Q_FIELD'} and (MODAL.match(t) or re.match(r'^(?:对|针对|根据|按照|在).{0,70}[,，].{0,5}(?:能|可)',t)):
        return 'N','R12_MODAL_APPLICANT_CAPABILITY'
    if role in {None,'R'} and operational(t) and not HARD_PERSON.search(t):return 'R','R12_CURRENT_INFORMATION_ACQUISITION'
    if role=='R' and MODAL.match(t) and not HARD_PERSON.search(t) and not rules.DAMAGE.search(t):return 'R','R12_ASSIGNED_MODAL_WORK'
    if current(t) and not rules.DAMAGE.search(t) and role in {None,'R'}:
        return 'R','R12_LITERAL_ACTION_OR_NOMINAL_DELIVERABLE'
    return BASE_DECIDE(text,role,previous)
rules.decide=decide

def clauses(s,a,b):
    out=[];start=a;depth=0
    for i in range(a,b):
        c=s[i]
        if c in '([【《':depth+=1
        elif c in ')]】》':depth=max(0,depth-1)
        if depth==0 and c in ',，':out.append((start,i+1));start=i+1
    if start<b:out.append((start,b))
    return out

def split_mixed(s,a,b,role):
    t=s[a:b];cs=clauses(s,a,b);points={a,b}
    for lo,hi in BASE_SPLIT(s,a,b,role):points.update((lo,hi))
    if role=='R' and cs and rules.HARDQUAL.search(s[cs[0][0]:cs[0][1]]) and qualification(s[cs[0][0]:cs[0][1]]) and not CURRENT.match(strip_clause(t)) and not rules.DAMAGE.search(t):
        # A mislabeled degree/tenure item still governs following skill clauses;
        # only explicit responsible-for assignments can escape that scope.
        safe=[lo for lo,hi in cs[1:] if re.match(ADV+r'(?:负责|协助|关注|处理|识别出|严格按照)',strip_clause(s[lo:hi])) and not qualification(s[lo:hi])]
        ps=sorted({a,b,*safe,*[x for x in points if safe and x>=min(safe)]});return list(zip(ps,ps[1:]))
    if cs and role in {'Q','Q_FIELD',None} and qualification(s[cs[0][0]:cs[0][1]]) and not rules.DAMAGE.search(t):
        verbs=r'(?:负责|协助|主导|承担)' if MODAL.match(strip_clause(s[cs[0][0]:cs[0][1]])) else r'(?:负责|协助|主导|承担|关注|识别出|严格按照|处理)'
        safe=[lo for lo,hi in cs[1:] if re.match(ADV+verbs,strip_clause(s[lo:hi])) and not qualification(s[lo:hi])]
        safe.extend(lo for lo in points-{a,b} if rules.POSITIVE_ASSIGN.match(strip_clause(s[lo:b])) and not qualification(s[lo:b]))
        ps=sorted({a,b,*safe,*[x for x in points if safe and x>=min(safe)]});return list(zip(ps,ps[1:]))
    # A complete reversed experience predicate governs the entire leading
    # object list. Explicit subsequent work clauses may still start a new item.
    if role in {None,'Q','Q_FIELD'} and EXPERIENCE.search(strip_clause(t)) and not CURRENT.match(strip_clause(t)) and not re.match(r'^对现有',strip_clause(t)):
        return [(a,b)]
    if role in {'Q','Q_FIELD'} and (PERSONAL.match(strip_clause(t)) or re.match(r'^(?:对|针对).{0,70}[,，]\s*(?:能|可)',strip_clause(t)) or re.match(r'^(?:对于|对|在).{0,160}(?:需要|要求)(?:有|具备|具有).{0,65}(?:知识|经验|能力)',strip_clause(t))):return [(a,b)]
    for i,(lo,hi) in enumerate(cs):
        c=strip_clause(s[lo:hi]);left=strip_clause(s[cs[i-1][0]:cs[i-1][1]]) if i else ''
        # Split genuine skills/environment fragments from neighboring tasks.
        if personal(c) or re.match(r'^(?:不穿无尘服|不看显微镜|中央空调车间|空调车间)',c):
            points.update((lo,hi))
        if i and personal(left) and (current(c) or role=='R' and MODAL.match(c)):
            points.add(lo)
        if role in {'Q','Q_FIELD'} and i and (qualification(left) or HARD_PERSON.search(s[a:lo])):
            if re.match(ADV+r'(?:负责|协助|主导|承担|识别出|严格按照|按照|组织|编制|审核|开展|进行)',c) and current(c):points.add(lo)
        # A work result and a prescribed learning goal belong to the action.
        if i and re.match(r'^(?:形成|提升|提高|增强).{1,65}能力',c) and current(left):points.discard(lo)
        if i and re.search(r'学习|阅读|培训|研习',left) and KNOW.match(c) and not HARD_PERSON.search(c):points.discard(lo)
        if i and role in {None,'R'} and operational(left) and re.match(r'^掌握(?:行业|业务|项目|客户).{0,15}案例',c):points.discard(lo)
        # A named task topic can precede a personal condition on the same line.
        inner=re.match(r'^.{1,22}:\s*',s[lo:hi])
        if inner:
            at=lo+inner.end()
            if personal(s[at:hi]):points.update((at,hi))
    # Parenthetical applicant credentials are local conditions, not task text.
    for m in re.finditer(r'\([^()]{1,55}\)',t):
        if CREDENTIAL.match(strip_clause(m[0])):points.update((a+m.start(),a+m.end()))
    mask=re.match(r'\s*\*{2,}(?:大|高|低)?(?:限度|程度)地?',t)
    if mask:points.add(a+mask.end())
    for m in re.finditer(r'(?<=[)）])\s+(?=(?:总经理|上级|领导|经理|主管).{0,8}(?:交待|交办|交代|安排))',t):points.add(a+m.end())
    # Do not preserve prefix fragments such as 在...至少 after splitting 具备.
    for lo in list(points-{a,b}):
        prefix=strip_clause(s[a:lo]);suffix=strip_clause(s[lo:b])
        if role in {None,'Q','Q_FIELD'} and prefix.startswith(('对','对于','在','针对')) and re.match(r'^(?:有|具有|具备|拥有)',suffix) and re.search('经验|经历|知识|能力',suffix):points.discard(lo)
        if rules.HARDQUAL.search(prefix) and qualification(prefix) and MODAL.match(suffix):points.discard(lo)
    return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

for name,role in {'岗位概述':'R','权责范围':'R','权利':'B','责任':'R','相关福利':'B','招聘要求描述':'Q','任职能力要求':'Q_FIELD','求职者隐私声明':'NOTICE','求职者隐私申明':'NOTICE','申请人隐私声明':'NOTICE','Job Applicant Privacy Policy':'NOTICE','全球胜任力':'COMPETENCY','Global Competencies':'COMPETENCY','技能这些必须有':'Q','这些可以有':'Q'}.items():rules.HROLE[name.lower()]=role
rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)

def headings(s):
    out=[h for h in BASE_HEADINGS(s) if h['name'] not in {'责任','权利'} or ':' in s[h['a']:h['b']]]
    for m in rules.HEAD.finditer(s):
        name=m[0].lower();role=rules.HROLE[name]
        if any(h['a']<=m.start()<h['b'] for h in out):continue
        pre=s[max(0,m.start()-35):m.start()];post=s[m.end():]
        boundary=not s[:m.start()].strip() or bool(re.search(r'[\n,，;；。:]\s*$',pre))
        is_caption=(name in {'员工福利待遇','员工福利','福利待遇','薪资福利','薪资待遇'} and boundary and re.match(r'\s*[,，:：\n]',post))
        is_block=name in {'全球胜任力','global competencies'} and re.match(r'\s+',post) and not re.search(r'负责|制定|建立|设计|开发|评估|编制',pre)
        if is_caption or is_block:
            out.append(dict(a=m.start(),b=m.end(),role=role,name=m[0]))
    # Preserve ordinal scope but suppress isolated Chinese chapter numbers.
    for h in out:
        m=re.search(r'[一二三四五六七八九十]+:\s*$',s[:h['a']])
        if m:h['a']=m.start()
    return sorted(out,key=lambda x:(x['a'],x['b']))
rules.headings=headings

def finish_body(body):
    s,st=BASE_FINISH(body)
    # Balance only orphan quote syntax; no task words or technical numbers.
    es=[]
    for op,cl in [('“','”'),('‘','’')]:
        stack=[]
        for i,c in enumerate(s):
            if c==op:stack.append(i)
            elif c==cl:
                if stack:stack.pop()
                else:es.append(dict(a=i,b=i+1,old=c,new='',rule='R12_ORPHAN_QUOTE'))
        es.extend(dict(a=i,b=i+1,old=s[i],new='',rule='R12_ORPHAN_QUOTE') for i in stack)
    s,es=rules.apply(s,es)
    if es:st.append(dict(name='r12_orphan_quotes',edits=es))
    return s,st
rules.finish_body=finish_body

def process(raw,row):
    p=parent.process(raw,row);s,_=replay(raw,p['normalization'])
    # Inheritance may protect only weak evidence. Explicit new exclusions
    # override old literal retention, including old exact development cases.
    changed=False
    for u in p['partition']:
        if u['label']=='S':continue
        lab,why=decide(s[u['a']:u['b']],u.get('section'))
        if why.startswith('R12_') and (lab in {'N','S','X'} or lab=='R' and u['label']!='X'):
            if u['label']!=lab:changed=True
            u.update(label=lab,reason=why)
    if changed:
        engine.rebuild(p,s)
        p['proposed_after']=p['after'];p['adopted']=True;p['text_changed']=p['after']!=p['before'];p['preserve_parent_reason']=None
    elif any(p['before'].count(op)!=p['before'].count(cl) for op,cl in [('“','”'),('‘','’')]) and p['proposed_after']!=p['after']:
        p['after']=p['proposed_after'];p['adopted']=True;p['text_changed']=p['after']!=p['before'];p['preserve_parent_reason']=None
    p['policy_version']='R12_COMPLETE_CLAUSE_TASK_AND_NOMINAL_REPAIR'
    return p
