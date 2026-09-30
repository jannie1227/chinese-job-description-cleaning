"""Second R12 policy: source-list context and predicate scope, frozen V1 intact."""
import re
from tools import r12_policy as v1
from tools.r11_verify_release import replay
rules=v1.rules;engine=v1.engine
BASE_NORMAL=rules.normalize;BASE_HEADS=rules.headings;BASE_PARTS=rules._partitions10
BASE_DECIDE=rules.decide;BASE_SPLIT=rules.split_mixed;BASE_TASK=rules.is_task
BASE_OP=v1.operational
COMPOUND=re.compile(r'^(?:及时|深入|全面|充分|快速|准确)*(?:熟悉|了解|掌握|理解)(?:并且|并|及|和|、)(?:严格|及时|深入|全面|认真)*(?:执行|梳理|分析|收集|反馈|挖掘|发掘|跟踪|研究|判断|制定|优化|实施)')
CURRENT_ADV=re.compile(r'^(?:(?:积极|主动|认真|努力|持续|不断|定期|及时|准确|快速|高效|独立|全面|充分|深入|严格|合理|有效)(?:地)?)+')
WORK_START=re.compile(r'^(?:负责(?!的?职业态度|心|人|[、,，])|协助|承担|主导|推动|推进|跟进|形成|建立|搭建|培养|提高|提升|增强|整合|识别|监控|监测|执行|开展|进行|制定|编制|编写|组织|指导|协调|处理|解决|维护|开发|设计|管理|支持|提供|实施|总结|学习|阅读|研究|关注|参加|参与|完成|丰富产品线|据.{0,40}进行)(?=.{2,})')
CAPABILITY_NOUN=re.compile(r'^(?:开发|运维|设计|编程|沟通|组织|协调|学习|分析|执行|逻辑|亲和|抗压|适应|创新|判断|写作|专业|业务)(?:能力|力)(?:[、,，。;；]|方面|良好|强|优秀|$)')
GENERIC_COMPLIANCE=re.compile(r'^(?:服从|听从).{0,25}(?:管理|指挥|安排|调配)[。;；,，]*$')
KNOWLEDGE_TOPIC=re.compile(r'^(?:常见|相关|基本|基础|各种|各类|主要|专业).{0,35}(?:原理|基础概念|技术知识|理论知识)(?:和|及|、|[,，]|$)')
MODAL_CONDITION=re.compile(r'^(?:能(?:够)?|可以?|会)(?:结合|根据|通过|围绕|按照|依据|针对|对).{2,}')
LEARNING_ACT=re.compile(r'(?:努力|积极|不断|持续)?学习(?!能力|成绩|意识|意愿|力)|(?:参加|参与|开展|进行).{0,25}(?:培训|学习)|提高自身业务水平|进行.{0,5}(?:了解|研究|调查|调研|学习|分析)|直播前')
NOMINAL_EVENT=re.compile(r'^(?:公司|部门|项目|团队)(?:的)?(?:团建|培训|会议|活动).{0,25}(?:策划|组织|执行|安排|管理|协调|落实|开展)')
ASSIGN=re.compile(r'^(?:(?:主要|具体|全面|日常|及时|独立|严格)\s*)*(?:负责(?!的?职业态度|心|人|[、,，])|协助|承担|主导)')
BARE=re.compile(r'(?<![A-Za-z0-9.])([1-9]\d?)(?=[\u3400-\u9fff])')
QUANTITY=re.compile(r'^(?:年|月|天|时|分钟|岁|个|人|名|位|届|元|万|千|百|亿|米|吨|兆|号|级|倍|层|种|次|条|家|日|以内|以上|以下|及以上|年限)')
BLOCK_ROLES={'A','B','C','OFFER','NOTICE','COMPETENCY','Q_FIELD'}

def txt(s):return v1.strip_clause(s)
def actual(t):
    t=txt(t)
    if CAPABILITY_NOUN.match(t) or v1.PERSONAL.match(t) or re.match(r'^研究生|^认真负责[、,，]',t):return False
    core=CURRENT_ADV.sub('',t)
    return bool(COMPOUND.match(t) or NOMINAL_EVENT.match(t) or WORK_START.match(core) or ASSIGN.match(t) or BASE_TASK(t))

def coherent_bare(s):
    ms=[m for m in BARE.finditer(s) if not QUANTITY.match(s[m.end():])]
    if not ms:return []
    anchors=list(re.finditer(r'(?<![A-Za-z0-9.])([1-9]\d?)[.、)]\s*(?=[^\d\s])',s))
    seq=sorted(ms+anchors,key=lambda m:m.start())
    if len(seq)<3:return []
    supported=set()
    for i,m in enumerate(seq):
        near=[j for j in range(max(0,i-2),min(len(seq),i+3)) if j!=i and int(seq[j][1])-int(m[1])==j-i]
        if near:supported.add(m.start())
    return [m for m in ms if m.start() in supported] if len(supported)>=3 else []

def normalize(raw):
    s,st=BASE_NORMAL(raw);es=[]
    for m in coherent_bare(s):es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='R12V2_COHERENT_BARE_ORDINAL'))
    marks=list(re.finditer(r'\d{1,2}[.、)]\s*(\?)(?=[\u3400-\u9fff])',s))
    if len(marks)>=2:
        for m in marks:es.append(dict(a=m.start(1),b=m.end(1),old='?',new='',rule='R12V2_REPEATED_ENTRY_INITIAL_QUESTION_LAYOUT'))
    for m in re.finditer(r'(?<=[\u3400-\u9fff])\.(?=\d{1,2}\.)',s):es.append(dict(a=m.start(),b=m.end(),old='.',new='.\n',rule='R12V2_SENTENCE_BEFORE_LIST_NUMBER'))
    for m in re.finditer(r'(?<=[A-Za-z])Responsibilities\s*:',s):
        es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n'+m[0],rule='R12V2_CONCATENATED_EXPLICIT_ENGLISH_CAPTION'))
    s,es=rules.apply(s,es)
    if es:st.append(dict(name='r12v2_proven_list_and_caption_boundaries',edits=es))
    return s,st
rules.normalize=normalize

for name,role in {
    '工作情况':'R','录用条件':'Q','招募要求':'Q','岗位福利':'B','品牌优势':'B',
    '硬福利':'B','软福利':'B','培训福利':'B','岗位':'A','Objectives of the Position':'R',
    'Technical Professional Knowledge':'Q_FIELD'
}.items():rules.HROLE[name.lower()]=role
rules.HEAD=re.compile('|'.join(sorted(map(re.escape,rules.HROLE),key=len,reverse=True)),re.I)

def headings(s):
    hs=[]
    for h in BASE_HEADS(s):
        a,b=h['a'],h['b'];name=h['name'];post=s[b:b+30]
        # Benefit/qualification labels inside an assigned work object are not
        # section boundaries. An actual caption colon/list still establishes one.
        line=max(s.rfind('\n',0,a),s.rfind(';',0,a),s.rfind('。',0,a),s.rfind(',',0,a))+1
        pre=s[line:a]
        if h['role'] in {'A','B','C','OFFER','Q','Q_FIELD'} and re.search(r'负责|核算|审核|编制|制定|统计|办理|管理|统筹|完善|计算|跟进',pre) and not ':' in s[a:b]:
            if pre and re.search(r'[\u3400-\u9fffA-Za-z]$',pre) and not re.match(r'\s*[1-9][.、)]',post):continue
        if name=='岗位' and (':' not in s[a:b] or a and re.search(r'[\u3400-\u9fffA-Za-z]',s[a-1])):continue
        hs.append(h)
    for m in re.finditer(r'加入[^。;；\n:]{1,30}(?:您|你)?将享有(?:以下)?福利\s*:',s):
        hs=[h for h in hs if not (m.start()<=h['a']<m.end())]
        hs.append(dict(a=m.start(),b=m.end(),role='B',name='EXPLICIT_EMPLOYMENT_BENEFIT_INTRODUCTION'))
    return sorted(hs,key=lambda h:(h['a'],h['b']))
rules.headings=headings

def operational(t):
    return bool(COMPOUND.match(txt(t)) or BASE_OP(t))
v1.operational=operational

def is_task(t):
    t=txt(t)
    if CAPABILITY_NOUN.match(t) or re.match(r'^热衷|^研究生|^认真负责[、,，]',t):return False
    if COMPOUND.match(t) or NOMINAL_EVENT.match(t):return True
    core=CURRENT_ADV.sub('',t)
    if core!=t and WORK_START.match(core) and not re.match(r'^负责[、,，]|^负责的?职业态度',core):return True
    if re.match(r'^据.{0,65}(?:进行|开展|制定|执行)',t):return True
    return BASE_TASK(t)
rules.is_task=is_task

def contextual_partitions(s):
    parts=BASE_PARTS(s);out=[];heading_key=None;inferred=None;clear_count=0;benefit_count=0;had_work=False;qual_cont=False
    for base in parts:
        u=dict(base);role=u.get('section');key=(role,u.get('heading'))
        if key!=heading_key:
            heading_key=key;inferred=None;clear_count=benefit_count=0;had_work=False;qual_cont=False
        if u.get('label')=='S':
            if u.get('reason') in {'EXPLICIT_LIST_MARKER','COHERENT_INLINE_CHINESE_ORDINAL','COHERENT_BARE_ORDINAL','COHERENT_SPACED_ORDINAL','DECORATIVE_LIST_MARKER'}:qual_cont=False
            out.append(u);continue
        t=txt(s[u['a']:u['b']]);lab,why=BASE_DECIDE(t,role)
        clear=lab=='R' and actual(t) and not v1.personal(t) and not CAPABILITY_NOUN.match(t)
        if role in {None,'A'} and inferred=='R' and v1.MODAL.match(t) and not v1.HARD_PERSON.search(t):clear=True
        condition=(v1.qualification(t) or CAPABILITY_NOUN.match(t) or KNOWLEDGE_TOPIC.match(t)) and not clear
        benefit=lab=='N' and any(k in why for k in ['BENEFIT','PAY_INFORMATION','EMPLOYMENT_OFFER','COMPENSATION']) and not ASSIGN.match(t)
        if role=='R' and not had_work and benefit:
            benefit_count+=1
            if benefit_count>=2:inferred='B'
        if role in {None,'A'}:
            if clear:
                inferred='R';had_work=True;clear_count+=1
            elif condition:inferred='Q'
            if inferred:
                u['original_section']=role;u['section']=inferred;u['context_basis']='LITERAL_ASSIGNMENTS_AND_QUALIFICATIONS_IN_SAME_SOURCE_BLOCK'
        elif role=='Q' and u.get('heading')=='岗位要求':
            if clear:
                clear_count+=1
                if clear_count>=2:inferred='R'
            elif condition:inferred='Q';clear_count=0
            if inferred=='R':u['original_section']=role;u['section']='R';u['context_basis']='CONSECUTIVE_EXPLICIT_TASKS_UNDER_WEAK_REQUIREMENTS_CAPTION'
        elif role=='R' and inferred=='B' and not ASSIGN.match(t):
            u['original_section']=role;u['section']='B';u['context_basis']='CONSECUTIVE_EMPLOYER_BENEFITS_BEFORE_ANY_ASSIGNED_WORK'
        if role=='R' and clear:had_work=True
        # Semicolon-separated knowledge examples stay attached to the original
        # skill item; a new numbered item or actual action resets this scope.
        if qual_cont and not clear and u['section'] not in {'B','C','A','OFFER','NOTICE','COMPETENCY'}:
            u['original_section']=role;u['section']='Q_FIELD';u['context_basis']='CONTINUATION_OF_EXPLICIT_KNOWLEDGE_ITEM'
        if condition and (v1.KNOW.match(t) or KNOWLEDGE_TOPIC.match(t)):qual_cont=True
        elif clear:qual_cont=False
        out.append(u)
    return out
rules._partitions10=contextual_partitions

def decide(text,role,previous=None):
    t=txt(text)
    if not t:return 'S','R12V2_EMPTY'
    if re.fullmatch(r'(?:各|不同|多个|相关)(?:学科|专业|岗位|职位)(?:分别|均|单独)?招聘[。;；]*',t):return 'N','R12V2_RECRUITMENT_DISTRIBUTION_NOTICE'
    if re.match(r'^上市公司直聘|^.{1,30}公司直聘[!！。;；]*$',t):return 'N','R12V2_EMPLOYER_DIRECT_RECRUITMENT'
    if re.match(r'^这里有一份.{0,35}(?:工作|职位)',t):return 'N','R12V2_EMPLOYER_RECRUITMENT_PITCH'
    if CAPABILITY_NOUN.match(t) or KNOWLEDGE_TOPIC.match(t) or re.match(r'^热衷',t):return 'N','R12V2_PERSONAL_CAPABILITY_KNOWLEDGE_OR_INTEREST'
    if re.match(r'^[^,，;；。]{1,25}(?:技巧|能力|技能)(?:娴熟|熟练|扎实|优秀|较强|强)[。;；,，]*$',t) and not re.match(r'^(?:提高|提升|增强|训练|培训|培养|指导|考核|评估)',t):return 'N','R12V2_REVERSED_PERSONAL_PROFICIENCY'
    if re.match(r'^(?:担任|从事|任职).{1,60}(?:岗位|工作|职位)\s*\d+(?:\.\d+)?年(?:以上|及以上)',t):return 'N','R12V2_PRIOR_EMPLOYMENT_DURATION'
    if role in {'Q','Q_FIELD',None} and GENERIC_COMPLIANCE.fullmatch(t):return 'N','R12V2_APPLICANT_COMPLIANCE_CONDITION'
    if re.match(r'^实现个人.{0,70}职业(?:转型|发展)',t):return 'N','R12V2_PERSONAL_CAREER_PROMOTION'
    if re.search(r'\bexperience\b.*\bis a plus\b',t,re.I):return 'N','R12V2_ENGLISH_EXPERIENCE_PREFERENCE'
    if re.search(r'(?:工作的|文件的|报告的)编[。;；]*$',t):return 'X','R12V2_TRUNCATED_DOCUMENT_PREDICATE'
    if re.fullmatch(r'\*{2,}(?:大|高|低)?(?:限度|程度)地?',t):return 'X','R12V2_UNRECOVERABLE_DEGREE_MODIFIER'
    if role in {'R',None} and not v1.HARD_PERSON.search(t) and not rules.DAMAGE.search(t):
        if COMPOUND.match(t) or NOMINAL_EVENT.match(t):return 'R','R12V2_COMPOUND_ACTION_OR_ADMINISTRATIVE_WORK'
        core=CURRENT_ADV.sub('',t)
        if core!=t and WORK_START.match(core) and not v1.personal(t) and not re.match(r'^负责[、,，]|^负责的?职业态度',core):return 'R','R12V2_ACTION_AFTER_MANNER_ADVERBS'
        if re.match(r'^丰富(?:公司|业务)?(?:产品线|产品矩阵|产品类型|产品种类|品类|内容)',t):return 'R','R12V2_TRANSITIVE_PRODUCT_OR_CONTENT_EXPANSION'
        if re.match(r'^据.{0,65}(?:进行|开展|制定|执行)',t):return 'R','R12V2_LITERAL_TASK_BASIS_AND_ACTION'
        if MODAL_CONDITION.match(t) and re.search(r'完成|分析|处理|提供|解决|制定|设计|开发|编制|开展',t):return 'R','R12V2_ASSIGNED_ACTION_WITH_ITS_BASIS'
        if re.match(r'^(?:直播|工作|作业|销售)前对.{0,90}进行.{0,5}了解',t):return 'R','R12V2_EXPLICIT_WORK_PREPARATION_AND_INFORMATION_ACQUISITION'
    return BASE_DECIDE(text,role,previous)
rules.decide=decide

def split_mixed(s,a,b,role):
    t=s[a:b];points={a,b}
    for lo,hi in BASE_SPLIT(s,a,b,role):points.update((lo,hi))
    cs=v1.clauses(s,a,b)
    if role in {'R',None}:
        for i,(lo,hi) in enumerate(cs):
            c=txt(s[lo:hi])
            if i and role=='R' and MODAL_CONDITION.match(c) and re.search(r'完成|分析|处理|提供|解决|制定|设计|开发|编制|开展',c):points.add(lo)
            if i and role=='R' and (GENERIC_COMPLIANCE.fullmatch(txt(s[cs[i-1][0]:cs[i-1][1]])) or v1.qualification(s[cs[i-1][0]:cs[i-1][1]])) and re.match(r'^(?:按照|根据).{0,50}(?:完成|执行|开展|进行)',c):points.add(lo)
        for lo in list(points-{a,b}):
            prefix=txt(s[a:lo]);tail=txt(s[lo:b])
            if LEARNING_ACT.search(prefix) and v1.KNOW.match(tail) and not v1.HARD_PERSON.search(prefix+tail):points.discard(lo)
            if re.search('系统|平台|设备|产品',prefix) and re.match(r'^(?:设计|开发|建立|搭建|负责.{0,15}(?:设计|开发))',prefix) and re.match(r'^能(?:够)?(?:支持|满足|实现|处理|承载)',tail):points.discard(lo)
            if MODAL_CONDITION.match(prefix) and actual(tail) and not v1.HARD_PERSON.search(prefix):points.discard(lo)
        for i,(lo,hi) in enumerate(cs):
            if i and txt(s[lo:hi]).startswith('实现个人') and '职业' in s[lo:hi]:points.add(lo)
        # Preserve explicit post-production work examples after a proficiency
        # modifier in a current task; these are operations, not tool names.
        if re.match(r'^(?:负责|参与|完成).{0,35}(?:拍摄|制作|剪辑)',txt(t)) and re.search(r'包括.{0,80}(?:剪辑|调色|字幕|特效)',t):
            for lo in list(points-{a,b}):
                if re.match(r'^(?:熟练运用镜头语言|包括剪辑|字幕处理|特效合成)',txt(s[lo:b])):points.discard(lo)
    if role=='Q':
        for i,(lo,hi) in enumerate(cs):
            if i and re.match(r'^(?:按照要求完成.{0,20}(?:交办|安排)|进行风险识别|独立完成)',txt(s[lo:hi])):points.add(lo)
    for m in re.finditer(r'\*{2,}(?:大|高|低)?(?:限度|程度)地?',t):points.update((a+m.start(),a+m.end()))
    return list(zip(sorted(points),sorted(points)[1:]))
rules.split_mixed=split_mixed

TRIGGER=re.compile(r'工作情况|录用条件|招募要求|岗位福利|品牌优势|Objectives of the Position|[A-Za-z]Responsibilities\s*:|分别招聘|加入[^。;；\n]{0,30}将享有|熟悉[、和并及]|了解[、和并及]|掌握[、和并及]|能够结合|能对.{0,45}(?:分析|提供|解决)|能够支持|能(?:够)?独立完成(?:公司|部门|日常)|(?:学习|培训|提高自身业务水平)[^。;；]{0,90}掌握|(?:积极|主动|认真|努力)+地?(?:完成|参加)|丰富(?:公司|业务)?产品|公司团建活动|据市场信息|岗位\s*[:：]|实现个人.{0,70}职业|(?:负责|核算|审核|编制|制定|统计|办理|管理|统筹)[^。;；\n]{0,70}(?:薪资福利|薪酬福利|工资|薪资|福利待遇)|按照要求完成.{0,20}(?:交办|安排)|进行风险识别|(?:^|[。;；\n])工作地点|(?:服从|听从)[^。;；]{0,50}(?:按照|根据|完成)|熟练运用镜头语言',re.I)
BODY_TRIGGER=re.compile(r'原理和主要应用|开发能力|运维方面|热衷|无不良从业|连续任职满|工作的编|\*{2,}限度地|experience.{0,80}is a plus|服从公司和部门管理|担任.{0,50}岗位\d+年',re.I)
def applicable(raw,body):
    return bool(TRIGGER.search(raw) or '培训福利' in raw or BODY_TRIGGER.search(body) or coherent_bare(raw)
        or re.search(r'(?<=[\u3400-\u9fff])\.\d{1,2}\.',raw)
        or len(re.findall(r'\d{1,2}[.、)]\s*\?(?=[\u3400-\u9fff])',raw))>=2
        or ('工作地点' in raw[:180] and re.search(r'维护.{0,40}财务',raw))
        or (re.search(r'针对优秀员工.{0,25}培训',body) and re.search('底薪|工资|薪资|待遇',raw)))

def process(raw,row):
    p=v1.process(raw,row);s,_=replay(raw,p['normalization']);changed=False
    previous_work=None
    for u in p['partition']:
        if u['label']=='S':
            if u['reason']=='EXPLICIT_SECTION_HEADING':previous_work=None
            continue
        lab,why=decide(s[u['a']:u['b']],u.get('section'))
        if why.startswith('R12V2_') and (lab in {'N','S','X'} or lab=='R' and u['label']!='X'):
            if u['label']!=lab:changed=True
            u.update(label=lab,reason=why)
        t=rules.cleantext(s[u['a']:u['b']])
        if u['label']=='N' and t.startswith('(') and t.rstrip('。;；').endswith(')') and previous_work and previous_work.get('heading')==u.get('heading') and not v1.qualification(t) and not rules.DAMAGE.search(t):
            u.update(label='R',reason='R12V2_PARENTHESES_DETAIL_OF_PRECEDING_TASK');changed=True
        previous_work=u if u['label']=='R' else None
    if changed:
        engine.rebuild(p,s);p['proposed_after']=p['after'];p['adopted']=True;p['text_changed']=p['after']!=p['before'];p['preserve_parent_reason']=None
    p['policy_version']='R12_V2_SOURCE_ITEM_CONTEXT_AND_COMPOUND_PREDICATES'
    return p
