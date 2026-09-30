"""Source-based corrections with protection for previously retained tasks."""
import sys,re,html,copy,json,functools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from tools.r11_io import *
from jdclean_unified import responsibility_repair_r11 as rules

def folded(s):
 for _ in range(3):
  q=html.unescape(s)
  if q==s:break
  s=q
 return ''.join(chr(ord(c)-65248) if '\uff01'<=c<='\uff5e' else ' ' if c=='\u3000' else c for c in s)
def flat(s):return ''.join(c for c in folded(s) if c.isalnum() or c in '+#')
def fingerprint(s):return re.sub(r'[\s,，;；。:："“”\[\]【】]+','',folded(s))
def source_old_spans(before,s):
 chars=[];positions=[]
 for i,c in enumerate(s):
  if c.isalnum() or c in '+#':chars.append(c);positions.append(i)
 hay=''.join(chars);cursor=0;spans=[];miss=[]
 for line in before.splitlines():
  needle=flat(line)
  if not needle:continue
  a=hay.find(needle,cursor)
  if a<0:a=hay.find(needle)
  if a<0:miss.append(line);continue
  b=a+len(needle);spans.append(dict(a=positions[a],b=positions[b-1]+1,prior_text=line));cursor=b
 return spans,miss

@functools.lru_cache(None)
def prior_reviews():
 return {x['raw_sha256']:x for x in BUNDLED_RESOURCES['r10_reviews']}

def rebuild(p,s):
 spans=[]
 for u in p['partition']:
  if u['label']!='R':continue
  a,b=u['a'],u['b']
  while a<b and s[a].isspace():a+=1
  while a<b and s[b-1].isspace():b-=1
  if a<b:spans.append(dict(a=a,b=b,text=s[a:b]))
 p['render_spans']=spans;p['body_before_format']='\n'.join(x['text'] for x in spans);p['after'],p['format']=rules.finish_body(p['body_before_format']);nx=sum(x['label']=='X' for x in p['partition']);p['excluded_fragment_count']=nx;p['retained_unit_count']=sum(x['label']=='R' for x in p['partition']);p['status']=('DUTIES_WITH_SOURCE_LIMIT' if nx else 'DUTIES_RETAINED') if p['after'].strip() else ('NO_USABLE_DUTIES_SOURCE_LIMIT' if nx else 'NO_EXPLICIT_DUTIES');return p

def process(raw,row):
 before=row['responsibility_text'];p=rules.process(raw);s=p.pop('_normalized_text');assert digest(s.encode())==p['normalized_sha256'];oldspans,miss=source_old_spans(before,s);protected=[]
 # Only weak absence-of-evidence decisions can inherit a previously retained
 # span. Explicit conditions/benefits/company statements are never rescued.
 for u in p['partition']:
  if u['label']!='N' or u['reason'] not in rules.LOW_EVIDENCE_N or u.get('section') not in {None,'R'}:continue
  for old in oldspans:
   a=max(u['a'],old['a']);b=min(u['b'],old['b'])
   if a<b and s[a:b].strip(rules.PUNCT) and not rules.qualification(rules.cleantext(s[a:b])):
    protected.append(dict(a=a,b=b,label='R',reason='PRIOR_LITERAL_DUTY_PRESERVED_WITHOUT_POSITIVE_REMOVAL_EVIDENCE'))
 corrections=list(protected);exact=prior_reviews().get(digest(raw.encode()));prior_review_applied=False
 if exact:
  assert exact['raw']==raw
  for e in exact['decisions']:
   text=e['text'];locations=[m.start() for m in re.finditer(re.escape(text),s)]
   if len(locations)==1:corrections.append(dict(a=locations[0],b=locations[0]+len(text),label=e['label'],reason=e['reason'],exact_source_review=True))
   elif s[e['a']:e['b']]==text:corrections.append(dict(a=e['a'],b=e['b'],label=e['label'],reason=e['reason'],exact_source_review=True))
   else:raise AssertionError(('old reviewed interval requires explicit remapping',exact['review_id'],text))
  prior_review_applied=True
 if corrections:
  points={0,len(s)}
  for u in p['partition']:points.update((u['a'],u['b']))
  for e in corrections:points.update((e['a'],e['b']))
  us=[];j=0
  for a,b in zip(sorted(points),sorted(points)[1:]):
   while p['partition'][j]['b']<=a:j+=1
   u=dict(p['partition'][j],a=a,b=b);matches=[e for e in corrections if e['a']<=a and b<=e['b']]
   if matches:
    exactmatches=[e for e in matches if e.get('exact_source_review')];e=exactmatches[0] if exactmatches else matches[0];u.update(label=e['label'],reason=e['reason'],prior_preservation=not bool(exactmatches),exact_source_review=bool(exactmatches))
   if u['label']=='R' and not s[a:b].strip(rules.PUNCT):u.update(label='S',reason='FORMAT_BOUNDARY_ONLY')
   us.append(u)
  p['partition']=us;rebuild(p,s)
 # Never discard a previous task merely because a newer mapper cannot locate
 # it. Cases requiring this branch are separately sampled before publication.
 uncovered=[t for t in miss if flat(t) not in flat(p['after'])]
 syntax_bad=bool(re.search(r'<[/]?(?:p|br|div|span)\b|&(?:amp|nbsp|quot);|[\u200b\ufeff\ue000-\uf8ff]',before,re.I) or before.count('【')!=before.count('】') or before.count('[')!=before.count(']'))
 unchanged=fingerprint(before)==fingerprint(p['after']) and not syntax_bad
 adopt=not uncovered and not unchanged
 p.update(record_id=row['record_id'],raw_sha256=digest(raw.encode()),before_sha256=digest(before.encode()),before=before,proposed_after=p['after'],source_alignment_missing=miss,source_alignment_uncovered=uncovered,prior_literal_spans=oldspans,prior_preserved_intervals=protected,exact_prior_review_applied=prior_review_applied,adopted=adopt,text_changed=adopt and p['after']!=before,preserve_parent_reason='UNMAPPED_PRIOR_TEXT_RETAINED' if uncovered else 'SAME_CONTENT_KEEP_PRIOR_PRESENTATION' if unchanged else None,human_gold_standard=False,undecided_units=0)
 if not adopt:p['after']=before;p['status']='PRIOR_DUTIES_RETAINED' if before.strip() else 'NO_EXPLICIT_DUTIES'
 return p
