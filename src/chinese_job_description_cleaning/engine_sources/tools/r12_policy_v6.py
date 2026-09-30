"""Narrow final protection against Chinese substring ambiguities.

过程 is a current-work object, not the experiential aspect marker 过.
实现招聘目标 is assigned work, not the notice 现招聘. No past-experience
or advertisement statement is rescued merely by containing these characters.
"""
import copy,re
from tools import r12_policy_v5 as v5
from tools.r11_verify_release import replay
rules=v5.rules;engine=v5.engine
PROCESS_OBJECT=r'过程(?:质量|控制|管理|检验|检测|审核|监控|优化|改进|改善|策划|验证|分析|文件|文档|风险|异常|能力|中|的|设计|确认|审查)'
RAW=re.compile(r'(?:负责|参与|承担|从事)'+PROCESS_OBJECT+r'|实现招聘(?:目标|计划|指标|任务)')
START=re.compile(r'^(?:(?:负责|参与|承担|从事)'+PROCESS_OBJECT+r'|实现招聘(?:目标|计划|指标|任务))')
CONDITION=re.compile(r'经验|经历|者优先|优先考虑|优先录用|学历|学位|相关专业|(?:能力|条件|资格)[。;；,，]*$')
def applicable(raw):return bool(RAW.search(raw))
def process(raw,row):
 p=copy.deepcopy(v5.process(raw,row));s,_=replay(raw,p['normalization'])
 for u in p['partition']:
  if u['label'] in {'S','X'} or u.get('section') in {'A','B','C','OFFER','NOTICE','COMPETENCY','Q_FIELD'}:continue
  t=v5.v1.strip_clause(s[u['a']:u['b']])
  if START.match(t) and not CONDITION.search(t) and not rules.DAMAGE.search(t):
   u.update(label='R',reason='R12V6_CURRENT_PROCESS_OR_RECRUITMENT_GOAL_NOT_PAST_OR_ADVERTISEMENT')
 engine.rebuild(p,s);p.update(proposed_after=p['after'],adopted=True,text_changed=p['after']!=p['before'],preserve_parent_reason=None,policy_version='R12_V6_NARROW_CHINESE_SUBSTRING_DUTY_GUARD')
 return p
