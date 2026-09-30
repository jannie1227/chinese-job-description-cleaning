def replay(s,stages):
 count=0
 for stage in stages:
  out=[];last=0
  for e in stage['edits']:
   a,b=e['a'],e['b'];assert 0<=last<=a<b<=len(s) and s[a:b]==e['old'];out.extend([s[last:a],e['new']]);last=b;count+=1
  out.append(s[last:]);s=''.join(out)
 return s,count
