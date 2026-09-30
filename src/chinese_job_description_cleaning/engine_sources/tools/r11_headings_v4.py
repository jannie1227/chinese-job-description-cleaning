"""ASCII word boundaries permit directly adjacent Chinese-English captions."""
import re
from jdclean_unified import responsibility_repair_r11 as rules

def headings(s):
 hs=[];stack=[];enclosures=[]
 for i,c in enumerate(s):
  if c in '([【':stack.append((i,c))
  elif c in ')]】' and stack and {'(':')','[':']','【':'】'}[stack[-1][1]]==c:
   lo,op=stack.pop();enclosures.append((lo,i+1,op))
 for m in rules.HEAD.finditer(s):
  a,b=m.span();pre=s[max(0,a-22):a];post=s[b:b+60]
  # Examples and task objects inside parentheses are not section transitions.
  if any(lo<a and b<hi and not (op=='[' and not s[:lo].strip() and not s[hi:].strip()) and s[lo+1:hi-1].strip(' :：')!=m[0] for lo,hi,op in enclosures):continue
  if m[0] in {'内容','技能','要求','待遇','职责'} and a and not (pre[-1:].isspace() or pre[-1:] in '[【。;；:：' or re.search(r'[一二三四五六七八九十][、.)]$',pre)):continue
  if re.search(r'(?:制定|编写|编制|发布|界定|定义|修订|完善|履行|根据|明确|熟悉|了解|执行|满足|符合|确认|梳理|优化|做好|开展|相关)(?:相关|各岗位|公司|员工|的)?$',pre) and not re.match(r'\s*[:：]\s*\(?[1-9][.、)]',post):continue
  if re.search('[A-Za-z]',m[0]) and ((a and bool(re.match('[A-Za-z]',s[a-1]))) or b<len(s) and bool(re.match('[A-Za-z]',s[b]))):continue
  anno=re.match(r'\s*\((?:详细说明|Job Responsibilities|Responsibilities|Requirements|教育|经验|技能)[^()]{0,80}\)\s*',s[b:],re.I)
  if anno:b+=anno.end();post=s[b:b+60]
  narrative=m[0] in {'我们需要怎样的人','我们希望怎样的你'} and re.match(r'\s*[?？]',post) or m[0]=='我们所提供的' and (a==0 or pre[-1:] in '-—\n。;；')
  if not (narrative or re.match(r'\s*(?:[:：;；]|[】\]【])',post) or re.match(r'\s*[1-9][.、)]',post) or m[0] in {'福利待遇','任职资格条件及技能要求','主要工作内容及职责'} or (a==0 or pre[-1:] in '\n\r\t。;；[【、)]') and (not post or post[:1].isspace()) or re.match(r'\s*'+rules.HEAD.pattern,post,re.I)):continue
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
  hs.append(dict(a=a,b=b,role=rules.HROLE[m[0].lower()],name=m[0]))
 return hs
