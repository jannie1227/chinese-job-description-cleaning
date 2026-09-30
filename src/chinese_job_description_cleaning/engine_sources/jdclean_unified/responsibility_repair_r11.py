"""Terminal operational cleaning decisions over complete supplied descriptions.

R=literal task, N=non-task, S=syntax, X=unusable literal fragment. No U label.
Decisions express a documented extraction convention, not human gold labels.
Every output word is retained from the normalized supplied source; only recorded
format transformations and separators are permitted. No predicted missing text.
"""
import re,html,hashlib

HEADS={
 'R':('岗位职责 工作职责 职责描述 主要职责 工作内容 职位描述 职位职责 岗位描述 岗位工作内容 岗位主要工作内容 主要工作内容 主要工作任务 工作任务 工作概要 工作概述 岗位定位 工作责任 负责内容 职责说明 核心职责 你的工作 你需要做 需要你做 你将负责 你将会做 岗位职责描述 核心岗位职责描述 岗位职责与要求 工作职责及任职要求 岗位职责及任职要求 工作职责及内容 工作内容及要求').split()+['Job Responsibilities','Key Responsibilities','Main Responsibilities','Responsibilities','Job Duties','Job Description','Position Summary','The Role','Your Responsibilities'],
 'Q':('任职要求 任职资格 任职条件 职位要求 岗位要求 岗位需求 职责要求 职责资格 任职需求 资格条件 基本要求 岗位基本要求 招聘基本要求 加分要求 必备技能 专业知识及技能要求 相关经验和资质要求 应聘条件 招聘条件 招聘要求 学历要求 技能要求 工作经验 专业要求 教育背景 经验要求 能力要求 素质要求 其他要求 岗位人员要求 人员要求 用人要求').split()+['Position Qualifications','Qualifications','Requirements','Job Requirements','Qualification Criteria','Required Skills','Skills and Experience','Education and Experience','Your Profile','About You'],
 'B':('福利待遇 薪资待遇 薪资福利待遇 薪酬福利待遇 薪酬福利 工资待遇 工资福利待遇 岗位待遇 福利保障 员工福利待遇 员工福利 薪资构成 培训晋升 发展通道 职业发展规划 晋升空间 晋升方向 发展空间 福利 薪酬待遇 薪资 工作福利').split()+['Benefits','We Offer','What We Offer','Compensation and Benefits'],
 'A':('工作地点 工作地址 上班地点 面试地点 面试地址 面试时间 工作时间 上班时间 联系方式 联系电话 联系人 联系邮箱 简历请投递 简历投递 报名时间 投递方式 招聘程序 招聘需求 岗位名称 培养岗位 从事岗位 职能类别 关键字 关键词 温馨提示 乘车路线 招聘人数 招聘岗位 面试方式 备注 应聘方式').split()+['Location','How to Apply'],
 'C':('公司简介 企业简介 公司介绍 企业介绍 公司概况 部门介绍 职位介绍 项目背景介绍 项目介绍 团队背景 招聘面向人群 培训目标 关于我们').split()+['About Us','About the Company','Company Profile','Company Overview']}
HEADS['R']+=['主要工作职责','岗位工作职责','学习内容','实习内容','定岗职责','职责内容','工作内容/职位描述']
HEADS['A']+=['培养方向','发展方向','未来培养','招聘负责人','招聘联系方式','实习部门','实习岗位','实习地点','公司网址','官网']
HEADS['B']+=['公司亮点','公司优势','工作氛围','员工保障','员工培训','奖励机制','福利假期']
HEADS['R']+=['内容']
HEADS['Q']+=['技能','加分项','要求']
HEADS['B']+=['待遇']
HEADS['R']+=['关于该岗位','主要工作内容及职责','Responsibilities description','Responsibilities Description','Main Responsibilies']
HEADS['Q']+=['工作要求','具体要求','我们希望您','我们希望你','我们对您的期望','任职资格条件及技能要求','Position Requirements','Responsibility requirements','岗位任职要求','开发经验要求']
HEADS['B']+=['我们为您提供','我们为你提供','您对我们的期望','岗位培养及发展通道','明确职业发展通道','全面的发展路线','专业的培训','就职待遇']
HEADS['A']+=['培养城市','应聘邮箱']
HEADS['R']+=['职责表述','主要工作内容及时间','工作内容及时间','主要工作职责及要求','工作职责及要求','岗位职责及要求']
HEADS['Q']+=['面试条件','面试要求','岗位基本条件','技术要求']
HEADS['Q']+=['相关要求','实习要求','应聘要求','任职基本条件']
HEADS['B']+=['我们提供','我们可以提供','加入我们,您将获得','加入我们你将获得']
HEADS['R']+=['岗位说明','岗位工作说明','职位说明']
HEADS['R']+=['职责']
HEADS['Q']+=['其它要求','其他条件','优先经验和技能','优先条件','性别要求','年龄要求','英语能力','经历要求','经验要求']
HEADS['B']+=['公司福利关怀','公司福利','待遇福利','薪资待遇概述','薪资保障','工资福利','工作时间及薪资待遇']
HEADS['A']+=['Base地','BASE地','工 作 地点','数量']
HEADS['C']+=['公司业绩','企业业绩','寄语','企业荣誉','品牌介绍']
HEADS['Q']+=['业绩要求','我们的要求']
HEADS['B']+=['你能获得','实习生&管培生培养计划']
HEADS['R']+=['而你所需要做的事情是','你所需要做的事情是','你需要做的事情','工作主要内容','你的职责','您的职责','工作任务描述','Contractor的工作内容','主要任务和职责','岗位和职责','团队发展']
HEADS['Q']+=['任职学历、经历要求','任职资格要求','个人要求','专业技能','个人素质','岗位资格','技能与经验','Qualification','Competency','Basic Skills','Educational Background','Relevant Working Experience','任职要求与核心条件']
HEADS['Q']+=['我们需要怎样的人','我们希望怎样的你']
HEADS['C']+=['公司业务','我们是谁','我们的愿景和优势','公司背景','企业背景','公司情况','企业发展']
HEADS['A']+=['Network 主要工作联系','主要工作联系','原标题','职位关键词','职务名称','投递要求','工作制度']
HEADS['B']+=['我们能带给你','我们所提供的','其他你可能想知道的事情','工作时间与薪资福利','公司可提供以下待遇','公司提供以下待遇','上班地点与薪资待遇','薪资方面','福利方面','食宿情况']
HROLE={h.lower():r for r,hs in HEADS.items() for h in hs}
HEAD=re.compile('|'.join(sorted(map(re.escape,HROLE),key=len,reverse=True)),re.I)
SPACED_HEAD=re.compile('(?:'+'|'.join(r'\s*'.join(map(re.escape,h)) for h in sorted(HROLE,key=len,reverse=True) if re.fullmatch(r'[\u3400-\u9fff]{2,15}',h))+r')(?=\s*[:：])')
HTML=re.compile(r'</?(?:p|br|div|span|b|strong|i|em|u|font|ul|ol|li|table|tbody|tr|td|a|h[1-6])(?:\s+[^<>]*?)?\s*/?>',re.I)
ENTITY=re.compile(r'&(?:nbsp|amp|lt|gt|quot|apos|#\d{1,7}|#x[0-9a-fA-F]{1,6});',re.I)
CODE=re.compile(r'换行符|文件路径|转义|字面|字符串|字符集|正则|代码示例|源代码|HTML代码|HTML标记|代码片段|ASCII|Unicode',re.I)
MAC=r'(?:马[\s\-]*克[\s\-]*(?:数[\s\-]*据(?:[\s\-]*网)?|团[\s\-]*队)|(?:www\.)?macrodatas\.cn)'
SOURCE=re.compile(r'(?:\(\s*(?:来源|来自)?\s*'+MAC+r'\s*\)|(?:来源|来自|关注微信公众号|微信公众号|关注公众号|搜索|百度搜索|数据由|该数据由)\s*[:：]?\s*<?\s*'+MAC+r'\s*>?(?:整理|[-—]官网)?)',re.I)
ACTION_WORDS='负责 协助 参与 完成 编制 制定 制订 执行 处理 办理 回复 核算 审核 归档 登记 整理 寄送 报送 统计 巡查 检查 监控 跟踪 跟进 维护 开发 设计 指导 开展 承担 收集 搜集 接待 录入 监督 协调 核对 制作 组织 安排 检修 维修 清洁 配送 研究 策划 落实 建立 更新 对接 撰写 编写 测试 评估 操作 分析 优化 保管 安装 销售 开拓 拓展 推动 推进 搭建 完善 塑造 宣传 主持 配合 主导 履行 培养 提高 提升 培训 沟通 拟订 识别 改进 降低 增加 签订 签发 发放 发货 接听 收发 联系 带领 接收 发送 进行 督促 开具 调试 引导 统筹 生产 组装 打包 检验 转接 翻译 提供 增强 加强 训练 反馈 引入 填写 支持 使用 采购 协作 辅助 管理 总结 汇总 帮助 协同 传达 讲解 出具 报销 解释 验收 签署 保证 确保 关注 授课 教授 教学 装卸 分拣 编辑 确认 申请 整合 解决 优选 营销 推广 探索 优化 评审 评价 保障 掌控 把控 指挥 核查 调查 审计 发起 实施 遵守 服从'.split()
ACTION_WORDS+=['学习','从事','担任','争取','解答','寻找','保守','接洽','检索','审查','设定','打造','挖掘','做好','安抚','回访','招聘培训','招聘员工','招聘人员','回收','审批','巡检','防护','制止','领取','退还','维系','传递','预防','纠正','清理','转化','转换','挑货','下单','开具','报告','确定','收派','记录','建设','攻克','互动','实现','组建','孵化','布道','经营','接驳','宣传','促成','订货','备货','结算','梳理','检测','拍摄','剪辑','配送','搬运','核查','诊断','培养','保洁','送达','收取','查验','巡逻','保养','输出','报备','催收','汇报','修订','修理','执教','授课','回收','分配']
AW='(?:'+'|'.join(ACTION_WORDS)+')'
ACTION=re.compile(r'^(?:(?:主要|具体|日常|全面|独立|及时|定期|每日|每天|每周|每月|按时|认真|严格|积极|主动|共同|并且|并|同时|协同|持续|不断|深度|有效|耐心|热情|准确|熟练地|须|需|需要|应当|必须|将)\s*)*'+AW+r'(?!过|能力|经验|精神|人员必须|人职位|生毕业)(?=.{2,})')
ACT_ANY=re.compile(AW)
NOMINAL=re.compile(r'(?:工作|任务|管理|运营|维护|核对|报送|审核|统计|分析|研究|设计|开发|试验|检测|评估|规划|培训|接待|收集|整理|归档|考核|建设|检查|制作|编制|签发|盘点|处理|推进|执行|保障|沟通|洽谈|投标|实施|服务|支持|存档|报表|接收|申报|缴费|缴纳|发放|汇总|报账|密封|盘活|协调|跟进|保养|安装|调试|改善|填写|装订|解释|管控|交付|追踪|解决|编辑|寻源|比价|复核|风控|授课|生产|装卸|分拣|拍摄|剪辑|运营|上架|下架|排版|绘图|制图|控制|保密义务)(?:等|等工作|相关工作|工作事项|及完善)?[。;；]*$')
QUAL=re.compile(r'^(?:(?:要求|至少|必须|须|需|应|需要|基本|比较|较为)\s*)?(?:具有|具备|拥有|有着|有过|有(?:良好|较强|很强|丰富|一定|相关|\d|[一二两三四五六七八九十])|熟悉|熟练|精通|掌握|了解|懂|理解|能够|能独立|能熟练|能看懂|能承受|能接受|能适应|能完成|能处理|会用|会使用|会操作|会开车|善于|擅长|喜欢|热爱|愿意|乐于|认同|认可|良好|优秀|较强|扎实|丰富|性格|身体|为人|做事|工作态度|工作经验|学历|学位|教育|专业|年龄|性别|身高|体重|英语|英文|普通话|口语|证书|资格证|户口|居住在|家住|男女不限|不限|无刑事)')
HARDQUAL=re.compile(r'学历|学位|相关专业|专业毕业|专业优先|者优先|优先考虑|优先录用|优先录取|工作经验|行业经验|从业经验|相关经验|工作经历|从事过|负责过|参与过|做过|\d+年(?:以上|及以上)|[一二两三四五六七八九十]+年(?:以上|及以上)|(?:本科|大专|硕士|博士|高中|中专|专科)(?:及以上|以上)?|毕业生|\d+\s*[-~至到]\s*\d+\s*(?:周岁|岁)')
TRAIT=re.compile(r'^(?:工作|做事|为人|态度)?(?:认真负责|认真细致|细心|细致|耐心|勤奋|敬业|诚实|正直|踏实|严谨|积极|热情|开朗|责任心|执行力|沟通能力|表达能力|学习能力|形象|声音|思路|思维|逻辑|口齿|身体|五官|人品|品行|抗压能力|吃苦耐劳|遵纪守法)')
BENEFIT=re.compile(r'底薪|工资|薪资|薪酬|奖金|提成|五险|六险|社保|公积金|年假|年终奖|月薪|年薪|补助|补贴|津贴|包吃|包住|食宿|免费|双休|调薪|晋升|提拔|优惠|油卡|法定假期|法定节假日|团建|聚餐|年度旅游|节日|员工关怀|工作环境|商业保险|绩效奖金|带薪|两班倒|月休|加班费')
BENEFIT_START=re.compile(r'^(?:享受|入职|我们提供|公司提供|本公司提供|公司为|公司承担|可享|缴纳(?:社保|社会保险|五险|公积金)|按照国家及地方规定缴纳|购买(?:五险|社保)|提供(?:食宿|住宿|三餐|免费)|免费提供|免费|包吃|包住|五险|六险|社保|公积金|底薪|工资|薪资|月薪|年薪|综合工资|基本工资|年终奖|周末双休|双休|月休|带薪|法定节假日|节日福利|生日福利|晋升|完善的晋升)')
HR=re.compile(r'负责|协助|核算|审核|计算|办理员工|办理职工|办理.{0,15}(?:社保|公积金)|薪酬管理|缴费申报|制定|统计|编制|报表|申报|代缴|管理员工')
META=re.compile(r'^(?:联系电话|联系人|联系地址|手机|电话|传真|邮箱|邮件|网址|地址|地点|工作地|工作地址|上班地点|面试|应聘|简历|投递|报名|乘车|公交|地铁|招聘|诚聘|招收|招募|招聘岗位|职位名称|岗位名称|职能类别|关键字|关键词|详情请|请联系|有意者|欢迎|温馨提示|温馨提醒|友情提示|特别提醒|备注|备注说明)')
EMPLOYER=re.compile(r'^(?:公司|本公司|企业|集团|我们|本集团|本企业|本部门|该平台|本平台|目前公司|近年来公司)(?:目前|现|自|始终|长期|一直|主要|已经|已|于|均)?(?:成立|成立于|致力于|位于|坐落|专注|主要从事|是一家|是|拥有|总部|主营|提供|秉承|经营|占地|注册|发展|承担福利|执行[“"简单])')
ENQ=re.compile(r'^(?:at least|minimum|bachelor|master|ph\.?d|degree|diploma|education|experience|knowledge|proficien|familiar|fluent|fluency|excellent|strong|good|ability|able to|must have|should have|required|requirements|qualifications|you have|you are|we are looking|we seek|\d+\+?\s*(?:years|year))\b',re.I)
ENA=re.compile(r'^(?:(?:you|the candidate|the employee|he/she)\s+(?:will|shall|must|is to)\s+|(?:to|and|also|proactively|independently|effectively|regularly|timely)\s+)*(?:responsible for|assist|support|manage|develop|design|perform|conduct|execute|implement|deliver|provide|ensure|maintain|monitor|prepare|review|coordinate|lead|drive|analy[sz]e|create|build|plan|organize|organise|work|collaborate|communicate|collect|report|resolve|handle|identify|participate|establish|improve|process|track|test|evaluate|write|translate|train|operate|validate|check|control|supervise|follow|achieve|optimi[sz]e|take|be responsible|seek|promote|understand)\b',re.I)
TAIL=re.compile(r'^(?:负责|协助|包括|主要负责|负责相关|完成相关|负责公司|负责产品|协助完成|根据|按照|以及|并且|主要|工作|岗位|职位|任职|要求|职责|来源|关注)[:：。;；\s]*$')
PUNCT=' \t\n\r\xa0,，;；。!！:：[]【】"“”•·◆★●§'

def cleantext(t):return t.strip(PUNCT).lstrip('‐—·').strip()
def apply(s,events):
 events=sorted(events,key=lambda e:(e['a'],-e['b']));chosen=[]
 for e in events:
  if chosen and e['a']<chosen[-1]['b']:continue
  if e['old']!=e['new']:chosen.append(e)
 out=[];last=0
 for e in chosen:
  assert last<=e['a']<e['b']<=len(s) and s[e['a']:e['b']]==e['old'];out.extend([s[last:e['a']],e['new']]);last=e['b']
 out.append(s[last:]);return ''.join(out),chosen

def normalize(raw):
 s=raw;stages=[]
 def stage(es,name):
  nonlocal s
  s,es=apply(s,es)
  if es:stages.append(dict(name=name,edits=es))
 def events(rx,fn,why):return [dict(a=m.start(),b=m.end(),old=m[0],new=fn(m),rule=why) for m in rx.finditer(s)]
 stage(events(re.compile('[\uff01-\uff5e\u3000]'),lambda m:chr(ord(m[0])-65248) if m[0]!='\u3000' else ' ','WIDTH_NORMALIZATION'),'width')
 for _ in range(3):
  es=events(ENTITY,lambda m:html.unescape(m[0]),'COMPLETE_HTML_ENTITY')
  if not es:break
  stage(es,'entity')
 es=[]
 for m in HTML.finditer(s):
  if CODE.search(s[max(0,m.start()-25):m.end()+25]):continue
  es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n' if re.match(r'</?(?:p|br|div|li|ul|ol|tr|h[1-6])\b',m[0],re.I) else '',rule='HTML_LAYOUT'))
 stage(es,'html')
 if len(re.findall(r'br(?=\s*\d+[.、)]|岗位职责|任职要求|工作地点|入职)',s,re.I))>=3 and not CODE.search(s):
  stage(events(re.compile(r'br(?=\s*\d+[.、)]|岗位职责|任职要求|工作地点|入职)',re.I),lambda m:'\n','REPEATED_BARE_BR_LAYOUT'),'bare_br')
 stage(events(re.compile('[\u200b\ufeff\x00-\x08\x0b\x0c\x0e-\x1f\x7f]'),lambda m:'','FORMAT_CONTROL'),'control')
 stage(events(re.compile('[\uf0d8\uf0b7\uf0fc\uf06c\uf06e]'),lambda m:'\n','FONT_LIST_BULLET'),'font')
 es=[]
 for m in re.finditer(r'(?:\\+r\\+n|\\+[rn](?=[\s\d\u3400-\u9fff]|\\+[rn])|\\+t(?=[\u3400-\u9fff]))',s):
  ctx=s[max(0,m.start()-30):m.end()+30]
  if CODE.search(ctx) or re.search(r'802\.11[a-z\\/]+',ctx,re.I):continue
  es.append(dict(a=m.start(),b=m.end(),old=m[0],new='\n' if m[0][-1] in 'rn' else ' ',rule='ESCAPED_LAYOUT'))
 stage(es,'escaped_layout')
 stage(events(re.compile(r'[\u200c\u200d\u2060]'),lambda m:'' if (m.start()>0 and re.match(r'[A-Za-z0-9\u3400-\u9fff]',s[m.start()-1]) or m.end()<len(s) and re.match(r'[A-Za-z0-9\u3400-\u9fff]',s[m.end()])) else m[0],'CJK_LATIN_JOINER'),'joiner')
 stage(events(re.compile('\xa0'),lambda m:' ','NONBREAKING_SPACE'),'space')
 # Only heading letters separated by whitespace are joined, followed by a
 # caption colon. No task words are rewritten or joined across free prose.
 es=[]
 for m in SPACED_HEAD.finditer(s):
  if any(c.isspace() for c in m[0]):es.append(dict(a=m.start(),b=m.end(),old=m[0],new=re.sub(r'\s+','',m[0]),rule='SPACED_LITERAL_SECTION_CAPTION'))
 stage(es,'spaced_captions')
 return s,stages

def headings(s):
 hs=[];stack=[];enclosures=[]
 for i,c in enumerate(s):
  if c in '([【':stack.append((i,c))
  elif c in ')]】' and stack and {'(':')','[':']','【':'】'}[stack[-1][1]]==c:
   lo,op=stack.pop();enclosures.append((lo,i+1,op))
 for m in HEAD.finditer(s):
  a,b=m.span();pre=s[max(0,a-22):a];post=s[b:b+60]
  # Examples and task objects inside parentheses are not section transitions.
  if any(lo<a and b<hi and not (op=='[' and not s[:lo].strip() and not s[hi:].strip()) and s[lo+1:hi-1].strip(' :：')!=m[0] for lo,hi,op in enclosures):continue
  if m[0] in {'内容','技能','要求','待遇','职责'} and a and not (pre[-1:].isspace() or pre[-1:] in '[【。;；:：' or re.search(r'[一二三四五六七八九十][、.)]$',pre)):continue
  if re.search(r'(?:制定|编写|编制|发布|界定|定义|修订|完善|履行|根据|明确|熟悉|了解|执行|满足|符合|确认|梳理|优化|做好|开展|相关)(?:相关|各岗位|公司|员工|的)?$',pre) and not re.match(r'\s*[:：]\s*\(?[1-9][.、)]',post):continue
  if re.search('[A-Za-z]',m[0]) and ((a and s[a-1].isalpha()) or b<len(s) and s[b].isalpha()):continue
  anno=re.match(r'\s*\((?:详细说明|Job Responsibilities|Responsibilities|Requirements|教育|经验|技能)[^()]{0,80}\)\s*',s[b:],re.I)
  if anno:b+=anno.end();post=s[b:b+60]
  narrative=m[0] in {'我们需要怎样的人','我们希望怎样的你'} and re.match(r'\s*[?？]',post) or m[0]=='我们所提供的' and (a==0 or pre[-1:] in '-—\n。;；')
  if not (narrative or re.match(r'\s*(?:[:：;；]|[】\]【])',post) or re.match(r'\s*[1-9][.、)]',post) or m[0] in {'福利待遇','任职资格条件及技能要求','主要工作内容及职责'} or (a==0 or pre[-1:] in '\n\r\t。;；[【、)]') and (not post or post[:1].isspace()) or re.match(r'\s*'+HEAD.pattern,post,re.I)):continue
  if a and s[a-1] in '[【':a-=1
  close=re.match(r'\s*(?:[:：]\s*)?[】\]]?\s*(?:[:：])?',s[b:])
  if close:b+=close.end()
  if narrative and b<len(s) and s[b] in '?？':b+=1
  if narrative and a and s[a-1] in '-—':a-=1
  prefix=re.search(r'[一二三四五六七八九十]+[、.)]\s*$',s[:a])
  if prefix:a=prefix.start()
  if m[0] in {'公司业绩','企业业绩'}:
   prefix=re.search(r'[一二三四五六七八九十]+[、.)][^;；。\n]{0,45}$',s[:a])
   if prefix:a=prefix.start()
  if hs and a<hs[-1]['b']:continue
  hs.append(dict(a=a,b=b,role=HROLE[m[0].lower()],name=m[0]))
 return hs

def partitions(s):
 hs=headings(s);structures=[dict(a=h['a'],b=h['b'],label='S',reason='EXPLICIT_SECTION_HEADING',section=h['role'],heading=h['name']) for h in hs]
 for h in hs:
  m=re.match(r'[-•·●◆■▪▶►][ \t]+(?=[\u3400-\u9fffA-Za-z])',s[h['b']:])
  if m:structures.append(dict(a=h['b'],b=h['b']+m.end(),label='S',reason='EXPLICIT_FIRST_BULLET_AFTER_HEADING'))
 for m in SOURCE.finditer(s):structures.append(dict(a=m.start(),b=m.end(),label='S',reason='LITERAL_SOURCE_ATTRIBUTION'))
 # Known provider's bare domain at document edges is an attribution too.
 for m in re.finditer(MAC,s,re.I):
  if not s[:m.start()].strip(' \t\n\r([【。') or not s[m.end():].strip(' \t\n\r)]】。;；'):structures.append(dict(a=m.start(),b=m.end(),label='S',reason='EDGE_PROVIDER_ATTRIBUTION'))
 markers=[]
 rx=re.compile(r'(?<![A-Za-z0-9])(?:\(?([1-9]\d?)\s*([.,)、])|([一二三四五六七八九十]+)[、.)]|([a-zA-Z])[.)])\s*(?=\S)')
 for m in rx.finditer(s):
  a,b=m.span();pre=s[:a];rest=s[b:];value=int(m[1]) if m[1] else None
  if m[1] and rest[:1].isdigit() and not re.match(r'\d+(?:年以上|年及以上|年|[-~至到]\d+岁)',rest):continue
  boundary=not pre.strip() or pre[-1:] in '\n\r\t;；。:：[【' or pre[-1:].isspace() or any(h['b']==a for h in hs)
  if m[3] and not boundary:continue
  if m[4] and not boundary:continue
  if m[2]=='.' and not boundary and a>0 and s[a-1] in './\\':continue
  markers.append(dict(a=a,b=b,value=value,boundary=boundary,text=m[0]))
 for i,m in enumerate(markers):
  sibling=any(markers[j]['value'] is not None and m['value'] is not None and abs(markers[j]['value']-m['value'])<=2 for j in [i-1,i+1] if 0<=j<len(markers))
  if m['boundary'] or sibling:structures.append(dict(a=m['a'],b=m['b'],label='S',reason='EXPLICIT_LIST_MARKER'))
 cms=list(re.finditer(r'([一二三四五六七八九十])[、.)]\s*(?=[\u3400-\u9fffA-Za-z])',s))
 if len(cms)>=2:
  for i,m in enumerate(cms):
   value='一二三四五六七八九十'.index(m[1])
   if any('一二三四五六七八九十'.index(cms[j][1])-value==j-i for j in [i-1,i+1] if 0<=j<len(cms)):structures.append(dict(a=m.start(),b=m.end(),label='S',reason='COHERENT_INLINE_CHINESE_ORDINAL'))
 bare=list(re.finditer(r'(?:^|(?<=[;；。\n:]))\s*([1-9]\d?)(?=(?:配合|跟踪|根据|服从|负责|协助|完成|进行|操作|整理|维护|开发|设计|编制))',s))
 if len(bare)>=2 and any(int(y[1])==int(x[1])+1 for x,y in zip(bare,bare[1:])):
  for m in bare:structures.append(dict(a=m.start(1),b=m.end(1),label='S',reason='COHERENT_BARE_ORDINAL'))
 spaced=list(re.finditer(r'(?<!\d)([1-9]\d?)[ \t]+(?=(?:负责|协助|参与|要求|加分项|根据|完成|操作|设计|开发|维护|整理))',s))
 if len(spaced)>=2 and any(int(y[1])==int(x[1])+1 for x,y in zip(spaced,spaced[1:])):
  for m in spaced:structures.append(dict(a=m.start(),b=m.end(),label='S',reason='COHERENT_SPACED_ORDINAL'))
 for m in re.finditer(r'(?:^|(?<=[\n\r:：;；。]))[ \t]*[-•·●◆■▪▶►★☆█]+\s*|[•●◆■▪▶►█]',s):structures.append(dict(a=m.start(),b=m.end(),label='S',reason='DECORATIVE_LIST_MARKER'))
 # Delimiters inside brackets stay attached to the task's examples/objects.
 cut={0,len(s)};depth=0
 for i,c in enumerate(s):
  if c in '([【《':depth+=1
  elif c in ')]】》':depth=max(0,depth-1)
  if c in '\n\r;；。' and (depth==0 or c in '\n\r'):cut.add(i+1)
 for d in structures:cut.update((d['a'],d['b']))
 # Recover an explicit assignment following a qualification/skill tag without a
 # sentence separator; the former text is still independently excluded.
 for m in re.finditer(r'(?:负责(?!过|人|心)|协助)(?=.{3,})',s):
  a=m.start();line=max(s.rfind(';',0,a),s.rfind('。',0,a),s.rfind('\n',0,a))+1;pre=s[line:a]
  if (re.search(r'经验者$',pre) or re.search(r'技能要求.{0,65}销售$',pre)) and not re.search(r'能(?:够|独立)|参与过|曾|有过',pre):cut.add(a)
 for m in re.finditer(r'\s{2,}',s):cut.update(m.span())
 # Fixed headed records with a single outer wrapper must not suppress splits.
 if s.strip().startswith('[') and s.strip().endswith(']'):
  for m in re.finditer('[;；。]',s):cut.add(m.end())
 points=sorted(cut);out=[];hidx=-1
 for a,b in zip(points,points[1:]):
  while hidx+1<len(hs) and hs[hidx+1]['a']<=a:hidx+=1
  h=hs[hidx] if hidx>=0 else {'role':None,'name':None}
  st=next((d for d in structures if d['a']<=a and b<=d['b']),None)
  if st:out.append(dict(a=a,b=b,label='S',reason=st['reason'],section=h['role'],heading=h['name']));continue
  t=s[a:b]
  if not cleantext(t) or re.fullmatch(r'[\W\d_]+',t):out.append(dict(a=a,b=b,label='S',reason='SEPARATOR_OR_ISOLATED_NUMBER',section=h['role'],heading=h['name']));continue
  out.append(dict(a=a,b=b,section=h['role'],heading=h['name']))
 return out

def is_task(t):
 t=cleantext(t)
 if not t:return False
 if re.search(r'^(?:研究生|审核人员必须|设计思路|开拓精神|分析性思维|执行力|培养方向|发展方向)',t):return False
 if re.match(r'^(?:专业销售|销售|管理|多元化发展|职业发展)(?:路线|通道|方向)',t):return False
 if re.fullmatch(r'.{1,35}(?:工程师|经理|总监|主管|专员|技术员|顾问|助理|优化师|医师|岗位|职位)(?:\([^)]{0,20}\))?',t):return False
 if re.match(r'^(?:沟通|表达|协调|管理|组织|逻辑|思维|领导|执行|抗压|学习|创新)[^,，;；]{0,12}(?:能力|素质|意识|技巧|精神)',t):return False
 if re.search(r'(?:负责|参与|主导|从事|设计|开发|操作|完成|组织|使用|做)过(?!程)',t[:30]):return False
 if ACTION.match(t) or ENA.match(t):return True
 if re.match(r'^(?:不定期|定时|每季度|每年|每周|每月|提前|及时准确地)',t) and ACTION.match(re.sub(r'^(?:不定期|定时|每季度|每年|每周|每月|提前|及时准确地)','',t)):return True
 if caption_assignment(t):return True
 if re.match(r'^(?:主要|具体)?做(?!事|人|过|为).{2,}',t):return True
 if re.match(r'^(?:本岗位|本职位|你将|您将|你需要|您需要|我们需要你)',t) and ACT_ANY.search(t):return True
 if re.match(r'^(?:根据|按照|依据|在|对|为|与|向|通过|利用|借助|结合|基于|作为|就|将|围绕|按|针对|归属|所负责)',t) and ACT_ANY.search(t) and not QUAL.match(t) and not re.search(r'(?:有|具备|具有).{0,25}(?:经验|能力)|经验优先|者优先',t):return True
 return False

def qualification(t):
 if ENQ.match(t):return True
 if t.startswith('要求') and re.search(r'经验|熟悉|掌握|能力|学历|背景',t):return True
 if re.match(r'^(?:熟知|基本了解|善于|擅长)',t):return True
 if re.match(r'^有(?!权).{0,55}(?:能力|意识|精神|资格证|证者|证书|经验|经历)',t):return True
 if re.match(r'^(?:受过|接受过|参加过|经历过|曾经).{0,100}(?:培训|课程|工作|项目|学习)',t):return True
 if re.match(r'^(?:需|须|必须|请)?(?:持有|持本人|携带|持|提供本人).{0,20}(?:身份证|证件|资格证|健康证)|^(?:喜爱|对.{0,25}有.{0,20}(?:兴趣|热情))',t):return True
 if QUAL.match(t):return True
 if HARDQUAL.search(t) and not is_task(t):return True
 if re.search(r'(?:有|具有|具备).{0,60}(?:经验|能力|知识)|(?:相关|设计|工程|技术|学)专业[。;；]?$|(?:知识|理论)(?:扎实|丰富|良好)|经验(?:丰富|优先|为佳|尤佳)?[。;；]?$',t) and not is_task(t):return True
 if TRAIT.match(t) and not is_task(t):return True
 if re.fullmatch(r'.{0,30}(?:能力|精神|意识|素质|素养|责任心|执行力|亲和力)(?:强|佳|好|良好|较强)?',t) and not is_task(t):return True
 return False

def decide(t,role,previous=None):
 t=cleantext(t)
 if not t:return 'S','SEPARATOR'
 if role!='R' and re.fullmatch(r'(?:服从|听从).{0,18}(?:安排|管理|指挥|调配)(?:等)?',t):return 'N','GENERIC_APPLICANT_COMPLIANCE'
 if t.lower() in HROLE or t in {'微信分享','分享微信','分享到微信'}:return 'S','BARE_HEADING_OR_SHARE_UI'
 if role!='R' and re.fullmatch(r'(?:服从|听从)(?:公司|领导|上级)?(?:安排|指挥|管理)',t):return 'N','GENERIC_APPLICANT_COMPLIANCE'
 if len(t)<=2 and t in ACTION_WORDS:return 'X','INCOMPLETE_LITERAL_PREDICATE'
 if TAIL.fullmatch(t):return 'X' if re.search('负责|协助|完成|根据|按照',t) else 'S','INCOMPLETE_LITERAL_PREDICATE' if re.search('负责|协助|完成|根据|按照',t) else 'BARE_HEADING_TOKEN'
 # Literal encoding loss/masking stays in excluded-fragment ledger, never guessed.
 if re.search(r'\ufffd|锟斤拷|烫烫烫|屯屯屯',t):return 'X','LITERAL_ENCODING_LOSS'
 if re.search(r'(?<=[\u3400-\u9fff])\*+(?=[\u3400-\u9fff])|(?<=[\u3400-\u9fff])\?{2,}(?=[\u3400-\u9fff])',t) and not CODE.search(t):return 'X','SOURCE_MASK_WITHIN_WORD'
 if re.search(r'&(?:nbs?p?|quo?t?|am?p?|#\d*)$',t):return 'X','INCOMPLETE_LITERAL_ENTITY'
 if re.search(r'(?:\.{3,}|…+)',t) and not re.search(r'[,，、/].*(?:\.{3,}|…+)\s*(?:等)?[)）]',t) and not CODE.search(t):return 'X','SOURCE_ELLIPSIS_FRAGMENT_EXCLUDED'
 if re.search(r'[\ue000-\uf8ff]',t):return 'X','UNDECODABLE_PRIVATE_FONT_CHARACTER'
 if re.match(r'^(?:公司|我们|本公司).{0,12}(?:诚聘|招聘|直招)',t):return 'N','RECRUITMENT_ADVERTISEMENT'
 if re.match(r'^.{2,70}(?:有限公司|有限责任公司|股份公司|集团|设计院|研究院)(?:是|已|下设|成立|目前|主要|拥有|位于|创建|创立|以)',t):return 'N','NAMED_EMPLOYER_DESCRIPTION'
 if EMPLOYER.match(t) and not re.search(r'你将|您将|你负责|您负责|你的职责|您的职责',t):return 'N','EMPLOYER_SUBJECT_DESCRIPTION'
 if re.match(r'^(?:电话|网络|微信)(?:推广|销售|邀约|拜访|沟通|回访)',t) and role not in {'B','A','C'}:return 'R','EXPLICIT_COMMUNICATION_TASK'
 if re.match(r'^(?:邮件回复|邮件接收|邮件处理|招聘手续|招聘流程|招聘管理|招聘渠道|面试安排|面试接待|简历筛选|电话接听)',t) and (role=='R' or NOMINAL.search(t)):return 'R','ADMINISTRATIVE_AUXILIARY_TASK'
 if META.match(t) and not is_task(t):return 'N','RECRUITMENT_CONTACT_OR_METADATA'
 if re.search(r'^(?:可接受|接受|欢迎|面向).{0,10}(?:实习生|应届|毕业生)|https?://|www\.',t) and not is_task(t):return 'N','RECRUITMENT_OR_WEB_ADDRESS'
 if BENEFIT_START.match(t) and not HR.search(t):return 'N','EMPLOYEE_COMPENSATION_OR_BENEFIT'
 if re.match(r'^(?:高薪入职|开启财富|稳定的收入|快速积累财富|广阔的职业发展|实习期\d|实习期[一二三四五六七八九十])',t):return 'N','EMPLOYMENT_PROMOTION_OR_DURATION'
 if re.match(r'^(?:全天班|早班|晚班|夜班|白班|中班|长白班|班次|工时)\s*[:：]?\s*[0-9一二三四五六七八九十]',t):return 'N','EXPLICIT_SHIFT_TIME_OR_PAY'
 if role in {'B','C','A'} and BENEFIT.search(t) and not caption_assignment(t) and not re.match(r'^(?:负责|协助|核算|办理|审核|编制|制定|统计|申报)',t):return 'N','BENEFIT_IN_EMPLOYER_SECTION'
 if re.match(r'^(?:工作简单|生熟手均可|靠岸安排休息|休息期间|一个航期|出差一次|工作轻松|无规则休息|闲时多休|最多不超过\d+公斤|大件有叉车|无重大体力活)',t):return 'N','EMPLOYMENT_SCHEDULE_OR_EASE_CLAIM'
 if role in {'B','C','A'} and re.match(r'^(?:办理离职手续|每日办理入职|只需|即可|欢迎|参加招聘|应聘)',t):return 'N','APPLICANT_ENTRY_EXIT_PROCEDURE'
 if BENEFIT.search(t) and not is_task(t) and not HR.search(t):return 'N','EMPLOYEE_BENEFIT_OR_SCHEDULE'
 if re.match(r'^(?:全部)?新(?:厂区|宿舍)|^(?:机器化程度|两班倒工作|全程智能化生产车间)',t):return 'N','WORKPLACE_DESCRIPTION'
 # Modal operation is a task inside a duties section; elsewhere it is a stated skill.
 if role=='R' and modal_task(t):return 'R','OPERATION_PRESCRIBED_IN_DUTY_SECTION'
 if role=='R' and operational_knowledge(t):return 'R','CURRENT_OPERATIONAL_KNOWLEDGE'
 if qualification(t):return 'N','APPLICANT_CAPABILITY_OR_CONDITION'
 if re.search(r'对.{0,40}(?:较为|有一定|有所)?(?:了解|熟悉)|^(?:高度的工作热情|精力充沛|语言表达|有上进心)',t) and not is_task(t):return 'N','APPLICANT_KNOWLEDGE_OR_TRAIT'
 if role=='Q' and not is_task(t) and not re.match(r'^(?:负责(?!过)|协助|每天|每日|定期|按时|根据|按照|你将|您将)',t) and not (NOMINAL.search(t) and not re.search(r'优先|经验|经历|能力|熟练|熟悉|能够|掌握|精通|知识|要求',t)):return 'N','APPLICANT_SECTION_CONTINUATION'
 if role in {'B','C','A'} and not (caption_assignment(t) or re.match(r'^(?:负责(?!过)|协助|核算|审核|编制|制定|办理员工|办理职工|你将|您将)',t)):return 'N','NON_DUTY_SECTION_CONTENT'
 if is_task(t):return 'R','EXPLICIT_CURRENT_TASK'
 if re.fullmatch(r'.{0,25}(?:上级|领导|经理|店长|主管|管理者).{0,12}(?:交办|安排|交代|交待|布置).{0,18}(?:工作|任务|事项)[。;；]*',t):return 'R','ASSIGNED_AUXILIARY_TASK'
 if role in {'B','A','C'}:return 'N','NON_DUTY_SECTION_CONTENT'
 if re.fullmatch(r'.{1,35}(?:工程师|经理|总监|主管|专员|技术员|顾问|助理|优化师|医师|岗位|职位)(?:\([^)]{0,20}\))?',t):return 'N','POSITION_TITLE_ONLY'
 if NOMINAL.search(t) and len(t)>3:return 'R','NOMINAL_WORK_OR_DELIVERABLE'
 cs=[cleantext(c) for c in re.split('[,，]',t) if cleantext(c)]
 if cs and (NOMINAL.search(cs[0]) or len(cs)>1 and any(is_task(c) for c in cs[1:])) and not any(qualification(c) for c in cs):return 'R','NOMINAL_TASK_WITH_ACTION_CONTINUATION'
 if role is None and re.search(r'客户|项目|产品|设备|图纸|资料|合同|报告|报表|数据|业务|财务|生产|订单|文件|交货|采购|研发|材料|技术|工艺|员工|团队|计划|流程|成本|品牌|教学|课程|指标|资产|库存|税务|账务|编制|盘点',t) and ACT_ANY.search(t) and not re.search(r'招聘|应聘|优先|经验|经历|能力|学历|熟练|熟悉|具备|具有|希望|发展空间|晋升',t):return 'R','LITERAL_WORK_OBJECT_AND_FUNCTION'
 if role=='R':return 'R','LITERAL_CONTENT_OF_EXPLICIT_DUTY_SECTION'
 if previous=='R' and re.match(r'^(?:并|以及|同时|包括|包含|如|例如|其中|以便|从而|保证|确保|以|使|达到)',t):return 'R','DEPENDENT_TASK_CONTINUATION'
 return 'N','NO_EXPLICIT_TASK_STATEMENT'

def operational_knowledge(t):
 return bool(re.match(r'^(?:及时|深入|充分)?(?:了解|掌握|熟悉|理解)',t) and re.search(r'情况|进展|进度|行情|需求|状态|库存|动态|诉求|特点',t) and not re.search(r'学历|学位|经验|能力|者优先|精通|熟练|软件|工具|编程|规则|流程',t))

def modal_task(t):
 if re.match(r'^熟练(?:操作|使用|运用|掌握)',t) and re.search(r'Python|Java|C\+\+|Office|CAD|软件|工具|Word|Excel',t,re.I) and not re.search(r'(?:完成|编写|编制|设计|开发|解决|维修|生产|处理|作业).{2,}',t[4:]):return False
 return bool(re.match(r'^(?:能(?:够|独立|快速|及时|熟练)?|会|熟练)(?:(?:地|的|准确|快速|高效|独立|及时|熟练|全面))*?(?:完成|处理|进行|操作|使用|编写|编制|设计|开发|解决|维修|保养|维护)',t) and not HARDQUAL.search(t))

def caption_assignment(t):
 if ':' in t:
  head,tail=t.split(':',1)
  if len(head)<=32 and not re.search(r'条件|要求|经验|能力|学历|薪酬|薪资|工资|福利|联系方式|地址|招聘|面试',head) and (ACTION.match(tail.lstrip()) or re.match(r'^(?:定期|每日|每天).{0,10}',tail) and ACT_ANY.search(tail)):return True
 return bool(re.match(r'^.{1,20}(?:工|厨师|员|经理|岗位)(?:主要工作是|主要负责|负责|工作是)',t) or re.match(r'^(?:随船|普通|大锅饭|仓库|搬运|叉车|电焊|普工|跟单).{0,30}(?:主要负责|负责日常|主要工作是)',t))

def split_mixed(s,a,b,role):
 # Split only commas that introduce an independent requirement/benefit or a new
 # task after a requirement. Preserve task objects, quantities and outcome tails.
 t=s[a:b];points=[a];depth=0;start=a
 for i,c in enumerate(t):
  if c in '(【《[':depth+=1
  elif c in ')】》]':depth=max(0,depth-1)
  if c not in ',，、' or depth:continue
  pos=a+i+1;left=cleantext(s[start:pos]);right=cleantext(re.split('[,，;；。\n]',s[pos:b],maxsplit=1)[0])
  if not right:continue
  lq=qualification(left);rq=qualification(right)
  if role=='R' and (operational_knowledge(right) or modal_task(right)):rq=False
  rb=(BENEFIT_START.match(right) and not HR.search(right)) or (META.match(right) and not is_task(right) and (':' in right or re.match(r'^(?:请投递|有意者|面试时间|面试地点)',right))) or bool(re.match(r'^(?:每月平均|平均每月|以上岗位|岗位|第一个月|月平均).{0,15}(?:工资|月薪)|^(?:工作简单|生熟手均可|最多不超过|大件有叉车|无重大体力活)',right))
  if c=='、' and not re.match(r'^(?:每月平均|平均每月|以上岗位|第一个月|月平均).{0,15}(?:工资|月薪)|^(?:工作简单|生熟手均可|无重大体力活)',right):continue
  independent=bool(re.match(r'^(?:负责(?!过)|协助|每天|每日|定期|按时|根据|按照|你将|您将)',right)) or bool(role=='R' and is_task(right) and not re.match(r'^(?:完成|操作|使用|开发|设计)',right))
  left_task=is_task(left) or bool((NOMINAL.search(left) or re.search(r'.{2,}(?:操作|作业|销售)$',left)) and not qualification(left))
  switch=((left_task or role=='R') and (rq or rb)) or (lq and independent and not rq) or (is_task(right) and BENEFIT_START.match(left)) or (role in {'A','B','C'} and independent and not rq)
  if switch:points.append(pos);start=pos
 points.append(b)
 return list(zip(points,points[1:]))

def finish_body(body):
 # Cosmetic operations only. Unpaired brackets do not prove absent words.
 stages=[];s=body
 def stage(es,name):
  nonlocal s
  s,es=apply(s,es)
  if es:stages.append(dict(name=name,edits=es))
 pairs={'(':')','[':']','【':'】','《':'》'};stack=[];bad=[]
 for i,c in enumerate(s):
  if c in pairs:stack.append((i,c))
  elif c in pairs.values():
   if stack and pairs[stack[-1][1]]==c:stack.pop()
   else:bad.append(i)
 bad.extend(i for i,c in stack)
 stage([dict(a=i,b=i+1,old=s[i],new='',rule='UNPAIRED_BRACKET_SYNTAX_ONLY') for i in bad],'bracket_syntax')
 es=[]
 for m in re.finditer(r'(?m)^[ \t.,，、;；。:："“”\[\]【】]+|[ \t,，、;；。:："“”\[\]【】]+$|[ \t]{2,}',s):es.append(dict(a=m.start(),b=m.end(),old=m[0],new=' ' if not (m.start()==0 or s[m.start()-1:m.start()]=='\n' or m.end()==len(s) or s[m.end():m.end()+1]=='\n') else '',rule='BOUNDARY_PUNCTUATION_AND_SPACE'))
 stage(es,'edges')
 return s,stages

def process(raw):
 s,norm=normalize(raw);units=[];prev=None;previous_heading=None
 for base in partitions(s):
  if base.get('label')=='S':units.append(base);continue
  for a,b in split_mixed(s,base['a'],base['b'],base['section']):
   role=base['section'];t=cleantext(s[a:b]);effective=role
   if role in {'Q','B','C','A'} and prev=='R' and previous_heading==base['heading'] and is_task(t) and not qualification(t) and not BENEFIT.search(t):effective='R'
   lab,why=decide(s[a:b],effective,prev);units.append(dict(base,a=a,b=b,label=lab,reason=why,effective_section=effective));prev=lab;previous_heading=base['heading']
 assert units and units[0]['a']==0 and units[-1]['b']==len(s) and all(x['b']==y['a'] for x,y in zip(units,units[1:])) if s else not units
 spans=[]
 for u in units:
  if u['label']!='R':continue
  a,b=u['a'],u['b']
  while a<b and s[a].isspace():a+=1
  while a<b and s[b-1].isspace():b-=1
  if a<b:spans.append(dict(a=a,b=b,text=s[a:b]))
 before='\n'.join(x['text'] for x in spans);body,fmt=finish_body(before)
 defects=[u for u in units if u['label']=='X'];r=[u for u in units if u['label']=='R']
 status=('PARTIAL_DUTIES_SOURCE_FRAGMENT_EXCLUDED' if defects else 'DUTIES_RETAINED') if body.strip() else ('NO_USABLE_DUTIES_SOURCE_FRAGMENT' if defects else 'NO_EXPLICIT_DUTIES')
 return dict(normalized_sha256=hashlib.sha256(s.encode()).hexdigest(),normalization=norm,partition=units,render_spans=spans,body_before_format=before,format=fmt,after=body,status=status,excluded_fragment_count=len(defects),retained_unit_count=len(r),undecided_units=0)

# R11: source structure precedes damage classification; qualifications and
# employer offers require positive evidence. Prior R text is protected when no
# positive removal evidence exists. Nothing below consults company/SOC/year.
_normalize10=normalize
_partitions10=partitions
_task10=is_task
_qual10=qualification
_decide10=decide
_finish10=finish_body
ADVERB=re.compile(r'^(?:(?:正确|合理|高效|有效|切实|积极|及时|准确|严格|认真|充分|主动|耐心|妥善|科学|定期|每天|每日|每月|每周|及时准确|认真细致|深入|独立)(?:地)?)+')
PAST=re.compile(r'^(?:在校|曾经|曾|以前|过去|以往|原先)|^(?:有|具备|具有|拥有).{0,70}(?:经验|经历|能力|知识|意识|精神|证书)|^(?:接触|参与|负责|从事|开发|设计|使用|操作|管理|承担|完成|带领|主导|组织|安装|做|带)过')
ATTRIBUTE=re.compile(r'^(?:(?:学习|执行|判断|沟通|抗压|表达|观察|协调|统筹|领导|洞察)(?:力|能力)(?:较强|强|良好|优秀|出色)|积极向上|乐观开朗)(?=[,，;；。]|$)')
KNOWLEDGE_STATE=re.compile(r'^对[^,，;；。]{1,90}(?:有|具有|拥有).{0,12}(?:认知|认识|了解|理解|掌握|兴趣|热情|经验|知识|敏感度)(?=[,，;；。]|$)')
TRAIT_ONLY=re.compile(r'^(?:洞察力|结果导向|分析和目标导向|学习成绩|成绩优秀|职业素养|人际交往能力|沟通表达能力|团队精神|团队协作能力|有机化学基础|专业基础|基础知识|身体健康|诚实正直|敬业精神|逻辑思维|热情自信|耐心细致|品行|服从组织统一安排|服从公司统一调配|服从领导安排|服从管理)')
PAY=re.compile(r'非计件工资|计件工资|(?:底薪|月薪|年薪|综合工资|到手工资)\s*[:：]?\s*[\d一二三四五六七八九十]|\d+\s*(?:元[/／](?:月|天|小时)|[kKwW][/／]月)|年终奖金|每月\d+号发工资')
TASK_EN_NOUN=re.compile(r'^(?:product|project|data|system|customer|service|quality|risk|software|technical|business|team|supply chain|account|sales|marketing)\b.{0,80}(?:management|development|design|analysis|support|maintenance|testing|operations|delivery)(?:\s*[+.&/]\s*.{1,90})?[.。;；]?$',re.I)
DAMAGE=re.compile(r'\ufffd|锟斤拷|烫烫烫|屯屯屯|(?<=[\u3400-\u9fff])\*+(?=[\u3400-\u9fff])|\*{2,}|(?<=[\u3400-\u9fff])\?{2,}(?=[\u3400-\u9fff])|[\ue000-\uf8ff]|\.{3,}|…+')
POSITIVE_ASSIGN=re.compile(r'^(?:(?:主要|具体|日常|全面|独立|及时|积极|主动|并|同时)\s*)*(?:负责(?!过|人|心)|协助|承担|主导|组建|带领|你将|您将)')
LOW_EVIDENCE_N={'NO_EXPLICIT_TASK_STATEMENT','APPLICANT_SECTION_CONTINUATION','SOURCE_DEPENDENT_CONTEXT_NOT_STANDALONE'}
NOMINAL=re.compile(NOMINAL.pattern+r'|.{2,}(?:编程|标注|巡检|稽核|调研|仿真|配送|加工|值守|报关|编码|实验|领用|回收|研发|经营|接收)(?:等|等工作)?[。;；]*$')

def normalize(raw):
 s,stages=_normalize10(raw)
 def stage(es,name):
  nonlocal s
  s,chosen=apply(s,es)
  if chosen:stages.append(dict(name=name,edits=chosen))
 # Repeated same private-font characters at entry beginnings are layout. A
 # private glyph within a word is never decoded into a guessed character.
 es=[]
 for glyph in set(re.findall('[\ue000-\uf8ff]',s)):
  positions=[m.start() for m in re.finditer(re.escape(glyph),s)]
  layout=[i for i in positions if (i==0 or s[i-1].isspace() or s[i-1] in ':：;；。[]【】') and re.match(r'\s*[\u3400-\u9fffA-Za-z0-9]',s[i+1:])]
  if len(layout)>=2 and len(layout)==len(positions):
   es.extend(dict(a=i,b=i+1,old=glyph,new='\n',rule='REPEATED_ENTRY_INITIAL_FONT_MARKER') for i in layout)
 stage(es,'proven_font_layout')
 # A complete explicit heading followed by a star establishes the start of a
 # star list. Require multiple substantial entries; double stars are not bullets.
 es=[];hs=headings(s)
 for j,h in enumerate(hs):
  a=h['b'];b=hs[j+1]['a'] if j+1<len(hs) else len(s);chunk=s[a:b];marks=list(re.finditer(r'(?<!\*)\*(?!\*)',chunk))
  if len(marks)<2 or chunk[:marks[0].start()].strip():continue
  texts=[chunk[m.end():marks[k+1].start() if k+1<len(marks) else len(chunk)].strip() for k,m in enumerate(marks)]
  if not all(len(t)>=6 for t in texts):continue
  for m in marks:es.append(dict(a=a+m.start(),b=a+m.end(),old='*',new='\n',rule='EXPLICIT_HEADING_STAR_LIST'))
 stage(es,'proven_star_layout')
 # Word-internal spaces in qualification terms are formatting, not new words.
 es=[]
 for m in re.finditer(r'经[ \t]+验|学[ \t]+历|能[ \t]+力|任[ \t]+职',s):
  es.append(dict(a=m.start(),b=m.end(),old=m[0],new=re.sub(r'\s+','',m[0]),rule='BROKEN_COMMON_FIELD_WORD_SPACE'))
 stage(es,'split_field_word')
 # Only a literal line-wrapped continuation is joined. Independent next tasks,
 # requirements, headings and numbered entries keep their boundary.
 es=[]
 for m in re.finditer(r'(?<=[\u3400-\u9fffA-Za-z])\r?\n[ \t]*(?=[\u3400-\u9fffA-Za-z])',s):
  left=s[s.rfind('\n',0,m.start())+1:m.start()];right=s[m.end():s.find('\n',m.end()) if '\n' in s[m.end():] else len(s)]
  if left.strip(' :：') in HEADS.get('R',[]) or left.strip(' :：').lower() in HROLE or right.strip(' :：').lower() in HROLE:continue
  if POSITIVE_ASSIGN.match(right) or QUAL.match(right) or re.match(r'^[1-9][.、)]',right):continue
  if re.search(r'各项|质量标准|维护保养|中间|产品检|验证工|工作的|相关的|公司的|其它单位的|其他单位的$',left) and not right.startswith(('职责','要求','任职')):
   es.append(dict(a=m.start(),b=m.end(),old=m[0],new='',rule='LITERAL_SOFT_LINE_WRAP'))
 stage(es,'soft_line_wrap')
 return s,stages

def is_task(t):
 t=cleantext(t);core=ADVERB.sub('',t)
 core=re.sub(r'^(?:并且|并|同时|仅|只)(?=负责|协助|处理|总结|归纳|分享|收集|记录|积累|负责|使用)','',core)
 if PAST.search(t) or TRAIT_ONLY.match(t) or ATTRIBUTE.match(t):return False
 if KNOWLEDGE_STATE.match(t) and not re.search(r'使其|促使|从而|确保|帮助.*形成',t):return False
 if re.match(r'^(?:总结|归纳|分享|传授|积累|沉淀|收集|记录|报告|提炼)(?:工作|实践|相关)?经验',core):return True
 if _task10(t) or core!=t and _task10(core):return True
 if re.match(r'^(?:报告|确定|收派|记录|实现|组建|建设|攻克|孵化|布道|经营|输出|采集|保洁|送达|结算|修订|修理|加工)(?!过|能力|经验|人员)(?=.{2,})',core):return True
 if re.match(r'^(?:与|对|向|通过|根据|按照|依据|利用|结合|在|为)',core) and re.search(r'进行|沟通|互动|解答|报告|完成|处理|管理|设计|开发|使用|提供|制定|执行|安装|维护|经营',core) and not re.search(r'有.{0,20}(?:经验|能力|理解|了解)|者优先',core):return True
 return False

def qualification(t):
 t=cleantext(t)
 if PAST.search(t) or TRAIT_ONLY.match(t) or ATTRIBUTE.match(t):return True
 if KNOWLEDGE_STATE.match(t) and not re.search(r'使其|促使|从而|确保|帮助.*形成',t):return True
 if re.fullmatch(r'.{0,30}(?:基础|理论|知识)(?:扎实|丰富|良好)',t):return True
 if re.search(r'经验者(?:优先|$)|经验(?:丰富|优先|者优先)|曾担任|在校曾|接触过',t) and not re.match(r'^(?:总结|归纳|汇总|分享|传授|积累|沉淀|收集|记录|报告|提炼)',ADVERB.sub('',t)) and not POSITIVE_ASSIGN.match(t):return True
 # A work action ending in “总结经验” is not an experience qualification.
 if is_task(t) and not re.search(r'者优先|学历|学位|从事过|参与过|工作经验|任职条件',t):return False
 return _qual10(t)

def decide(t,role,previous=None):
 t=cleantext(t)
 if not t:return 'S','SEPARATOR'
 if re.match(r'^(?:重点提示|请看清|请看清楚|特别提醒|请注意|请仔细阅读)',t):return 'N','EXPLICIT_RECRUITMENT_NOTICE'
 if re.search(r'均有岗位|不卡地域|面试成绩通用|多个岗位可选',t) and not POSITIVE_ASSIGN.match(t):return 'N','RECRUITMENT_POSITION_CATALOG'
 if re.match(r'^(?:确定后|面试通过后|通过后|录用后).{0,20}(?:入职|报到|录用)',t):return 'N','APPLICANT_ENTRY_PROCEDURE'
 if re.match(r'^(?:描述为完成该岗位|请描述|请填写|请在此填写|此处填写)',t):return 'N','UNFILLED_TEMPLATE_INSTRUCTION'
 if PAST.search(t) or TRAIT_ONLY.match(t):return 'N','EXPLICIT_PERSONAL_HISTORY_OR_ATTRIBUTE'
 if ATTRIBUTE.match(t) or KNOWLEDGE_STATE.match(t) and not re.search(r'使其|促使|从而|确保|帮助.*形成',t):return 'N','EXPLICIT_PERSONAL_KNOWLEDGE_OR_TRAIT'
 if role=='Q' and re.search(r'(?:设计|编程|开发|沟通|分析|理解|判断|学习|管理|阅读|写作|协调|组织)能力(?:强|好|较强)?[。;；]?$|(?:知识|技能|素质|意识|精神)(?:强|好|较强)?[。;；]?$',t) and not POSITIVE_ASSIGN.match(t) and not re.search(r'培养|提高|提升|考核|评价|评估',t):return 'N','EXPLICIT_CAPABILITY_IN_QUALIFICATION_SECTION'
 if re.fullmatch(r'.{0,35}(?:基础|理论|知识)(?:扎实|丰富|良好)',t):return 'N','EXPLICIT_PERSONAL_KNOWLEDGE_ATTRIBUTE'
 if PAY.search(t) and not re.match(r'^(?:负责|协助|核算|计算|统计|制定|审核|编制|发放员工|办理员工)',ADVERB.sub('',t)):return 'N','EXPLICIT_PAY_INFORMATION'
 if role in {'B','A','C','Q'} and re.match(r'^(?:签订|签署)(?:正式)?(?:劳动合同|劳务合同)',t) and re.search(r'五险|保险|社保|待遇',t):return 'N','EMPLOYER_EMPLOYMENT_OFFER'
 if re.search(r'不用担心客户资源|您不用担心|无需大海捞针|公司每天会给您分发|我们所提供的客户案例',t):return 'N','EMPLOYER_RESOURCES_OR_RECRUITMENT_PITCH'
 if re.search(r'(?:累积|累计)?注册用户.{0,12}(?:亿|万)',t) and not POSITIVE_ASSIGN.match(t):return 'N','COMPANY_SCALE_DESCRIPTION'
 if role in {'B','C','A'} and not POSITIVE_ASSIGN.match(t):return 'N','EXPLICIT_NON_DUTY_SECTION'
 if role=='Q' and not is_task(t):return 'N','APPLICANT_SECTION_CONTINUATION'
 if DAMAGE.search(t) and not CODE.search(t):
  # The source has already been separated into layout entries and local
  # clauses. Never let a positive action verb bypass a real local defect.
  dl,dw=_decide10(t,role,previous)
  if dl=='X':return dl,dw
 if TASK_EN_NOUN.match(t) and role in {'R',None}:return 'R','EXPLICIT_ENGLISH_NOMINAL_WORK'
 if is_task(t) and not qualification(t):return 'R','COMPLETE_CURRENT_TASK_STATEMENT'
 if role=='R' and re.match(r'^(?:能(?:够)?|可)(?:独立|及时|准确|快速|有效|熟练)*(?:解答|接待|回复|沟通|处理|销售|安装|收派)',t) and not HARDQUAL.search(t):return 'R','OPERATIONAL_ACTION_IN_DUTY_SECTION'
 return _decide10(t,role,previous)

def _clauses(s,a,b):
 # Enumerated noun objects separated by 、 remain one clause. Full source
 # punctuation and byte-for-byte intervals stay in the audit.
 out=[];last=a
 for m in re.finditer('[,，;；。]',s[a:b]):out.append((last,a+m.end()));last=a+m.end()
 if last<b:out.append((last,b))
 return out

def split_mixed(s,a,b,role):
 t=s[a:b];points={a,b};cs=_clauses(s,a,b)
 # A mask or truncation affects only its local clause, not every work statement
 # before or after it. Classification decides whether intact clauses stand alone.
 if DAMAGE.search(t) and not CODE.search(t):
  for lo,hi in cs:points.update((lo,hi))
  for m in re.finditer(r'并且|并|以及|同时|然后',t):
   pos=a+m.start()
   if _standalone(s[a:pos]) and DAMAGE.search(s[pos:b]):points.add(pos)
 for i in range(1,len(cs)):
  lo,hi=cs[i];left=cleantext(s[cs[i-1][0]:cs[i-1][1]]);right=cleantext(s[lo:hi])
  ql=qualification(left);qr=qualification(right);workl=is_task(left) or bool(NOMINAL.search(left) and not ql)
  if role=='R' and (modal_task(right) or operational_knowledge(right)):qr=False
  benefit=bool(BENEFIT_START.match(right) and not HR.search(right) or PAY.search(right))
  meta=bool(META.match(right) and (':' in right or re.match(r'^(?:请|有意者|面试)',right)))
  if workl and (qr or benefit or meta):points.add(lo)
  if ql and POSITIVE_ASSIGN.match(right):points.add(lo)
  if role in {'A','B','C'} and POSITIVE_ASSIGN.match(right):points.add(lo)
 # Strong assignments embedded in parentheses after a list separator are
 # independent literal clauses; never strip an employer/candidate subject.
 for m in re.finditer(r'(?<=[,，、;；。(])\s*(?=(?:主要|具体)?(?:负责(?!过|人|心)|协助|组建|带领))',t):
  pos=a+m.end();prefix=cleantext(s[a:pos])
  if role in {'B','C','A'} or qualification(prefix):
   points.add(pos)
   close=s.find(')',pos,b)
   if close>=0:points.add(close)
 # Unpunctuated work+requirement joins, e.g. 收派快递对快递有了解的最好.
 for m in re.finditer(r'(?=对[^,，;；。]{1,35}有[^,，;；。]{0,10}(?:了解|理解)|(?:具备|具有|拥有).{0,30}(?:学历|经验|能力)|(?:本科|大专|硕士)以上|原标题\s*[:：])',t):
  pos=a+m.start();prefix=cleantext(s[a:pos])
  if prefix and is_task(prefix):points.add(pos)
 return list(zip(sorted(points),sorted(points)[1:]))

def _standalone(t):
 t=cleantext(t).strip('()')
 if not t or re.search(r'(?:从|到|至|与|和|的|及|其|所|向|对|为|并|中|通过|根据|按照)$',t):return False
 if re.fullmatch(r'(?:主要|具体)?(?:负责|协助|参与)(?:'+AW+r')?',t):return False
 if re.match(r'^(?:结合|按照|根据|依据|通过|在).{0,70}(?:情况|方式|要求|规定|基础上|过程中)$',t) and not re.search(r'负责|完成|开展|进行|实施|提供|管理|处理|执行|制定|确定',t):return False
 return is_task(t) or bool(NOMINAL.search(t)) or bool(TASK_EN_NOUN.match(t))

def _complete_before_ellipsis(t):
 t=cleantext(t)
 if not _standalone(t):return False
 return bool(re.search(r'(?:工作|任务|事项|报告|服务|管理|系统|平台|数据|资料|文件|客户|问题|方案|目标|维护|检查|质量|进度|需求|流程|光纤|设计|开发|编制|编程|安装|施工|保养|操作|经营|推广|销售|采购|分析|等)$',t) or re.fullmatch(r'[A-Za-z].{8,}[.!?]',t))

def finish_body(body):
 # Preserve punctuation inside technical names. Remove only complete source
 # title wrappers and boundary delimiters; then balance residual wrappers.
 s=body;stages=[]
 es=[]
 for m in re.finditer(r'(?m)^\s*【[^】\n]{1,35}】(?=[\u3400-\u9fffA-Za-z])',s):
  es.append(dict(a=m.start(),b=m.end(),old=m[0],new='',rule='COMPLETE_SHORT_TITLE_WRAPPER'))
 s,es=apply(s,es)
 if es:stages.append(dict(name='complete_title_wrappers',edits=es))
 s,old=_finish10(s);stages.extend(old)
 # A boundary strip may expose a closing wrapper; remove that same unmatched
 # syntax in a second pass, never words around it.
 pairs={'(':')','[':']','【':'】','《':'》'};stack=[];bad=[]
 for i,c in enumerate(s):
  if c in pairs:stack.append((i,c))
  elif c in pairs.values():
   if stack and pairs[stack[-1][1]]==c:stack.pop()
   else:bad.append(i)
 bad.extend(i for i,c in stack);es=[dict(a=i,b=i+1,old=s[i],new='',rule='BOUNDARY_EXPOSED_UNPAIRED_WRAPPER') for i in bad];s,es=apply(s,es)
 if es:stages.append(dict(name='final_wrapper_syntax',edits=es))
 es=[dict(a=m.start(),b=m.end(),old=m[0],new='\n',rule='EMPTY_LINE_COLLAPSE') for m in re.finditer('\n{2,}',s)];s,es=apply(s,es)
 if es:stages.append(dict(name='empty_lines',edits=es))
 return s,stages

def process(raw):
 s,norm=normalize(raw);units=[];prev=None
 for base in _partitions10(s):
  if base.get('label')=='S':units.append(base);continue
  group_damaged=bool(DAMAGE.search(s[base['a']:base['b']]) and not CODE.search(s[base['a']:base['b']]))
  for a,b in split_mixed(s,base['a'],base['b'],base['section']):
   text=s[a:b];t=cleantext(text);role=base['section'];lab,why=decide(text,role,prev)
   # Known benign “带*星*” notation is not a missing word in job content.
   if lab=='X' and '*星*' in t and not DAMAGE.search(t.replace('*星*','星')):lab,why=decide(t.replace('*星*','星'),role,prev)
   # Keep a complete enumerated task list before an ellipsis. No continuation
   # after the ellipsis is reconstructed, and truncated predicates stay excluded.
   ell=re.search(r'(?:\.{3,}|…+)\s*[。;；)]*\s*$',text)
   if lab=='X' and ell and not DAMAGE.search(text[:ell.start()]) and _complete_before_ellipsis(text[:ell.start()]):
    cut=a+ell.start();prefix=text[:ell.start()];pl,pw=decide(prefix,role,prev)
    if pl=='R':
     units.append(dict(base,a=a,b=cut,label='R',reason='COMPLETE_LITERAL_WORK_BEFORE_SOURCE_ELLIPSIS',source_tail_not_reconstructed=True));units.append(dict(base,a=cut,b=b,label='S',reason='SOURCE_ELLIPSIS_NOT_EXPANDED'));prev='R';continue
   if lab=='R' and group_damaged and not _standalone(t) and why=='LITERAL_CONTENT_OF_EXPLICIT_DUTY_SECTION':lab,why='N','SOURCE_DEPENDENT_CONTEXT_NOT_STANDALONE'
   units.append(dict(base,a=a,b=b,label=lab,reason=why));prev=lab
 assert (not s and not units) or units[0]['a']==0 and units[-1]['b']==len(s) and all(x['b']==y['a'] for x,y in zip(units,units[1:]))
 spans=[]
 for u in units:
  if u['label']!='R':continue
  a,b=u['a'],u['b']
  while a<b and s[a].isspace():a+=1
  while a<b and s[b-1].isspace():b-=1
  if a<b:spans.append(dict(a=a,b=b,text=s[a:b]))
 before='\n'.join(x['text'] for x in spans);after,fmt=finish_body(before);nx=sum(u['label']=='X' for u in units)
 status=('DUTIES_WITH_SOURCE_LIMIT' if nx else 'DUTIES_RETAINED') if after.strip() else ('NO_USABLE_DUTIES_SOURCE_LIMIT' if nx else 'NO_EXPLICIT_DUTIES')
 return dict(normalized_sha256=hashlib.sha256(s.encode()).hexdigest(),normalization=norm,partition=units,render_spans=spans,body_before_format=before,format=fmt,after=after,status=status,excluded_fragment_count=nx,retained_unit_count=sum(u['label']=='R' for u in units),undecided_units=0,_normalized_text=s)
