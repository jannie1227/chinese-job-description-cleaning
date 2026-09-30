#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Frozen R12 V7 runtime with packaged engine_sources semantic modules.

Advanced CSV reproduction: job-description-reproduce --input YOUR_LOCAL_CSV --output-dir NEW_DIRECTORY
Public rules contain no private reviews. Exact corpus reproduction additionally
requires the separately held local review-resources JSON. No network or pip packages.
This reproduces cleaning, not embeddings or semantic-drift indicators.
"""
BUNDLED_RESOURCES = {'r10_reviews': [], 'v5_reviews': [], 'v7_reviews': []}
BUNDLED_PROVENANCE = [{'module': 'jdclean_unified.responsibility_repair_r11', 'original_file': '工作区/jdclean_unified/responsibility_repair_r11.py', 'original_sha256': '7933d94f0c28c40bf57a1ff0c5af1e304ff74317a10cfe8220abbdd54d7962e3', 'embedded_sha256': '7933d94f0c28c40bf57a1ff0c5af1e304ff74317a10cfe8220abbdd54d7962e3', 'packaging_changes': []}, {'module': 'tools.r11_io', 'original_file': '工作区/tools/r11_io.py', 'original_sha256': '69b2ff04d98f5e2c5c3cf80494ecb8258599421fe27197a77713324820c6aa04', 'embedded_sha256': '69b2ff04d98f5e2c5c3cf80494ecb8258599421fe27197a77713324820c6aa04', 'packaging_changes': []}, {'module': 'tools.r11_engine', 'original_file': '工作区/tools/r11_engine.py', 'original_sha256': '7e737ebe940d1767ff7d2ef427e4d142349529b26aeb23a8a4435469f9b4437e', 'embedded_sha256': 'ccc78232262a47e4653914228459f420cecbf6e5a1091157a3cb6fd9f0288213', 'packaging_changes': ['Replace a file read with the identical embedded frozen JSON resource; no decision contents changed.', 'Remove mutation of the host Python import path.']}, {'module': 'tools.r11_headings_v4', 'original_file': '工作区/tools/r11_headings_v4.py', 'original_sha256': '020f5c416dca01c994a24c6533fe6fef489b04e10b58155891552735ba2677e4', 'embedded_sha256': '020f5c416dca01c994a24c6533fe6fef489b04e10b58155891552735ba2677e4', 'packaging_changes': []}, {'module': 'tools.r11_policy_v2', 'original_file': '工作区/tools/r11_policy_v2.py', 'original_sha256': '552745856c2a317348cfeef4c21bd91a199789e9f03b1d1449f7096627bc5172', 'embedded_sha256': '552745856c2a317348cfeef4c21bd91a199789e9f03b1d1449f7096627bc5172', 'packaging_changes': []}, {'module': 'tools.r11_policy_v3', 'original_file': '工作区/tools/r11_policy_v3.py', 'original_sha256': 'dae4bd90fb022f093d1926cf11bd52f9c698c39e27e0073b264ee241fff5da19', 'embedded_sha256': 'dae4bd90fb022f093d1926cf11bd52f9c698c39e27e0073b264ee241fff5da19', 'packaging_changes': []}, {'module': 'tools.r11_policy_v4', 'original_file': '工作区/tools/r11_policy_v4.py', 'original_sha256': 'eb875a26e8f31d65622f006987a840a98355416c6a9a4907bfa39bece084b7bc', 'embedded_sha256': 'eb875a26e8f31d65622f006987a840a98355416c6a9a4907bfa39bece084b7bc', 'packaging_changes': []}, {'module': 'tools.r11_policy_v5', 'original_file': '工作区/tools/r11_policy_v5.py', 'original_sha256': '2fbd3088c4e58a82c6f6a8be3cd2416efbd612b296cefd7aee20f0c1c06d3a13', 'embedded_sha256': '2fbd3088c4e58a82c6f6a8be3cd2416efbd612b296cefd7aee20f0c1c06d3a13', 'packaging_changes': []}, {'module': 'tools.r11_verify_release', 'original_file': '工作区/tools/r11_verify_release.py', 'original_sha256': 'dd69ae64177824475ed3b4ac3508462c56195fc48e540e52f2af99c9fefe4417', 'embedded_sha256': '1799a6d1a9f8f062263660351765c8488fcb7fc33f30aa4d70c198ca1accb30a', 'packaging_changes': ['Only the unchanged pure replay() function is embedded; retired disk/database replay driver and Unix fcntl imports are not needed.']}, {'module': 'tools.r12_policy', 'original_file': '工作区/tools/r12_policy.py', 'original_sha256': 'a7f152c7f3d366b0ba4c6cb24d235e44e4864e4475615572bfd972867afcda2c', 'embedded_sha256': 'a7f152c7f3d366b0ba4c6cb24d235e44e4864e4475615572bfd972867afcda2c', 'packaging_changes': []}, {'module': 'tools.r12_policy_v2', 'original_file': '工作区/tools/r12_policy_v2.py', 'original_sha256': '380db6e2c14459d9b37c4038262e2b450ff0fced8313bab26260a269b1e94599', 'embedded_sha256': '380db6e2c14459d9b37c4038262e2b450ff0fced8313bab26260a269b1e94599', 'packaging_changes': []}, {'module': 'tools.r12_policy_v3', 'original_file': '工作区/tools/r12_policy_v3.py', 'original_sha256': 'e9f94516ac72b85e9ffbd43fa038dd01238146a5b90c3e4e41d3bb5fe08e1b63', 'embedded_sha256': 'e9f94516ac72b85e9ffbd43fa038dd01238146a5b90c3e4e41d3bb5fe08e1b63', 'packaging_changes': []}, {'module': 'tools.r12_policy_v4', 'original_file': '工作区/tools/r12_policy_v4.py', 'original_sha256': 'bdf279d3bcade6ddef27f996f202ced573f78a5c336c6f15f682afa58373cdba', 'embedded_sha256': 'bdf279d3bcade6ddef27f996f202ced573f78a5c336c6f15f682afa58373cdba', 'packaging_changes': []}, {'module': 'tools.r12_policy_v5', 'original_file': '工作区/tools/r12_policy_v5.py', 'original_sha256': 'bd00228b0fa3516951043ef9b24c3e81d7ddd71c9c053a0a7eb2d8c2a5b32448', 'embedded_sha256': 'c36cfdfdb58687a6a7060f869c2170b30504fa76850ec2d607fe2b4cebc0fede', 'packaging_changes': ['Replace a file read with the identical embedded frozen JSON resource; no decision contents changed.']}, {'module': 'tools.r12_policy_v6', 'original_file': '工作区/tools/r12_policy_v6.py', 'original_sha256': 'c01349c381bfd8a1caaa90a9d1b315b20c6397259c960e6441dc52cc699c117d', 'embedded_sha256': 'c01349c381bfd8a1caaa90a9d1b315b20c6397259c960e6441dc52cc699c117d', 'packaging_changes': []}, {'module': 'tools.r12_policy_v7', 'original_file': '工作区/tools/r12_policy_v7.py', 'original_sha256': 'bd972ae95653fda60749e9cb3f75d8f7d33ffb0f2afde3fa4ddcfeae321fcd55', 'embedded_sha256': '4c58e118de281da6d2bec1efff1c9e0f491dfeaa5dd114bd686e14a48031aff4', 'packaging_changes': ['Replace a file read with the identical embedded frozen JSON resource; no decision contents changed.']}]
EXPECTED = {'canonical_sha256': 'fcda9178d45a18c3f72516d08b073a1410a38ba239c326774a52dc299b0585d3', 'canonical_fields': ['record_id', 'stock_code', 'year', 'source', 'responsibility_text', 'raw_text_sha256'], 'records': 4073781, 'nonempty_records': 3754886, 'empty_records': 318895, 'input_sha256': 'dac38597ce68396fe0a06889b549e7f8a1a579fb443e38cadedbc5ee5870f620', 'source_release_manifest_sha256': '1e2d0d4a0a14aecf512e42f52e39e3b5ee0ccd7380868cae13c97e73959ed6f4'}
from pathlib import Path

ENGINE_SOURCE_PATHS = {'jdclean_unified.responsibility_repair_r11': 'engine_sources/jdclean_unified/responsibility_repair_r11.py', 'tools.r11_io': 'engine_sources/tools/r11_io.py', 'tools.r11_engine': 'engine_sources/tools/r11_engine.py', 'tools.r11_headings_v4': 'engine_sources/tools/r11_headings_v4.py', 'tools.r11_policy_v2': 'engine_sources/tools/r11_policy_v2.py', 'tools.r11_policy_v3': 'engine_sources/tools/r11_policy_v3.py', 'tools.r11_policy_v4': 'engine_sources/tools/r11_policy_v4.py', 'tools.r11_policy_v5': 'engine_sources/tools/r11_policy_v5.py', 'tools.r11_verify_release': 'engine_sources/tools/r11_verify_release.py', 'tools.r12_policy': 'engine_sources/tools/r12_policy.py', 'tools.r12_policy_v2': 'engine_sources/tools/r12_policy_v2.py', 'tools.r12_policy_v3': 'engine_sources/tools/r12_policy_v3.py', 'tools.r12_policy_v4': 'engine_sources/tools/r12_policy_v4.py', 'tools.r12_policy_v5': 'engine_sources/tools/r12_policy_v5.py', 'tools.r12_policy_v6': 'engine_sources/tools/r12_policy_v6.py', 'tools.r12_policy_v7': 'engine_sources/tools/r12_policy_v7.py'}
MODULE_SOURCES = {name: (Path(__file__).resolve().parent / relative).read_text(encoding='utf-8') for name, relative in ENGINE_SOURCE_PATHS.items()}

# ===== Standalone execution layer (the decision rules above are frozen) =====
import builtins, functools, hashlib, inspect, json, sys, types
from pathlib import Path

class EmbeddedEngine:
    """Each instance owns isolated rule globals; V5 cannot mutate V4."""
    def __init__(self, version, memo=True):
        self.modules = {}
        self.version = version
        self.policy = self.load('tools.r12_policy_v4' if version == 'V4' else 'tools.r12_policy_v7')
        self.v5 = None if version == 'V4' else self.load('tools.r12_policy_v5')
        self.v6 = None if version == 'V4' else self.load('tools.r12_policy_v6')
        self.predicates = []
        if memo:
            pure={'cleantext','strip_clause','is_task','qualification','personal','operational','operational_knowledge','current','decide','actual','modal','_without_connector'}
            state={'_context_br','_parent_norm','_nested_context','_source_entity_names','_parent_events','_source_has_br','_source_has_letter','_br_active','_removed_markers'}
            replacements={};slots=[]
            for name,module in tuple(self.modules.items()):
                if name!='jdclean_unified.responsibility_repair_r11' and not name.startswith(('tools.r11_policy_','tools.r12_policy')):continue
                for attr,fn in tuple(vars(module).items()):
                    if inspect.isfunction(fn) and fn.__name__ in pure:
                        assert not set(fn.__code__.co_names)&state
                        if fn not in replacements:replacements[fn]=functools.lru_cache(maxsize=4096)(fn)
                        slots.append((module,attr,fn))
            for module,attr,fn in slots:setattr(module,attr,replacements[fn])
            self.predicates=list(replacements.values())
        target=self.policy if version=='V4' else self.v5
        target._cached=functools.lru_cache(maxsize=256)(target._cached.__wrapped__)

    def load(self, name):
        if name in self.modules:return self.modules[name]
        module=types.ModuleType('embedded_'+self.version+'.'+name)
        module.__file__='/__r12_embedded__/workspace/'+name.replace('.','/')+'.py'
        module.__package__=module.__name__.rpartition('.')[0]
        self.modules[name]=module
        if name in {'tools','jdclean_unified'}:
            module.__path__=[]
        else:
            env=dict(vars(builtins));env['__import__']=self.import_module
            module.__dict__.update(__builtins__=env,BUNDLED_RESOURCES=BUNDLED_RESOURCES)
            exec(compile(MODULE_SOURCES[name],'<embedded:'+name+'>','exec'),module.__dict__)
        if '.' in name:
            parent,attr=name.rsplit('.',1);setattr(self.load(parent),attr,module)
        return module

    def import_module(self,name,globals=None,locals=None,fromlist=(),level=0):
        if level==0 and (name in MODULE_SOURCES or name in {'tools','jdclean_unified'}):
            module=self.load(name)
            for item in fromlist:
                if item!='*' and not hasattr(module,item) and name+'.'+item in MODULE_SOURCES:self.load(name+'.'+item)
            return module if fromlist else self.load(name.split('.')[0])
        return builtins.__import__(name,globals,locals,fromlist,level)

    def process(self,raw,stage):
        for fn in self.predicates:fn.cache_clear()
        row={'record_id':'SOURCE_ONLY','responsibility_text':''}
        policy=self.policy if stage in {'V4','V7'} else (self.v5 if stage=='V5' else self.v6)
        return policy.process(raw,row)

def code_fingerprint():
    """Fingerprint the runtime and every packaged semantic module for resume."""
    payload = {'runtime':file_sha(Path(__file__)), 'modules':{name:hashlib.sha256(text.encode('utf-8')).hexdigest() for name,text in sorted(MODULE_SOURCES.items())}}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()

def load_review_resources(path=None):
    """Load local adjudications; never distribute private originals in this repository."""
    global BUNDLED_RESOURCES
    if path is None:
        BUNDLED_RESOURCES = {'r10_reviews': [], 'v5_reviews': [], 'v7_reviews': []}
        return
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if set(data) != {'r10_reviews', 'v5_reviews', 'v7_reviews'}:
        raise ValueError('Unexpected review resource groups.')
    for rows in data.values():
        if not isinstance(rows, list):
            raise ValueError('Review resource groups must be lists.')
        for row in rows:
            if not isinstance(row, dict) or 'raw' not in row or 'raw_sha256' not in row:
                raise ValueError('Review resource schema is invalid.')
            if hashlib.sha256(row['raw'].encode('utf-8')).hexdigest() != row['raw_sha256']:
                raise ValueError('Local review raw-text checksum mismatch.')
    BUNDLED_RESOURCES = data

class Cleaner:
    def __init__(self,memo=True):
        self.base=EmbeddedEngine('V4',memo)
        self.later=EmbeddedEngine('V7',memo)
        self.cached=functools.lru_cache(maxsize=8192)(self._clean)
    def _clean(self,raw):
        p=self.base.process(raw,'V4');body=p['after'];stage='V4'
        if self.later.v5.applicability(raw,body):p=self.later.process(raw,'V5');body=p['after'];stage='V5'
        if self.later.v6.applicable(raw):p=self.later.process(raw,'V6');body=p['after'];stage='V6'
        if hashlib.sha256(raw.encode()).hexdigest() in self.later.policy.REVIEWS:p=self.later.process(raw,'V7');body=p['after'];stage='V7'
        return body,stage
    def clean(self,raw):return self.cached(raw)

import argparse, collections, concurrent.futures, csv, gzip, io, multiprocessing, os, platform, sqlite3, time

FIELDS=['record_id','stock_code','year','source','responsibility_text','raw_text_sha256']
RAW_COLUMNS=['关联股票代码','招聘发布年份','来源','职位描述']
_WORKER=None

def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def atomic_json(path,value):
    path=Path(path);temp=path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,path)

def canonical(row):
    return (json.dumps([row[k] for k in FIELDS],ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8')

def worker_init(review_resources=None):
    global _WORKER
    load_review_resources(review_resources)
    _WORKER=Cleaner()

def worker_batch(batch):
    answer=[]
    for sid,raw_sha,raw in batch:
        try:body,stage=_WORKER.clean(raw)
        except Exception as error:raise RuntimeError('Frozen cleaning failed for unique source '+str(sid)+' SHA256 '+raw_sha) from error
        answer.append((body,stage,sid))
    return answer

def progress(output,phase,**values):
    info={'phase':phase,'utc_time':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),**values}
    atomic_json(output/'progress.json',info)
    print(json.dumps(info,ensure_ascii=False),flush=True)

def existing_result(output):
    manifest=output/'manifest.json'
    if not manifest.exists():return None
    m=json.loads(manifest.read_text(encoding='utf-8'))
    if m.get('status') not in {'PASS_EXACT_R12_V7_REPRODUCTION','COMPLETE_OTHER_INPUT','PARTIAL_SMOKE_RUN'}:raise RuntimeError('Previous output did not pass; use a new output directory.')
    for e in m['files']:
        p=output/e['file']
        if not p.is_file() or file_sha(p)!=e['sha256']:raise RuntimeError('Existing output checksum failed: '+str(p))
    return m

def ingest(db,input_path,limit,output):
    try:
        csv.field_size_limit(sys.maxsize)
    except OverflowError:
        # CPython uses C long here; Windows may have a 32-bit C long.
        csv.field_size_limit(2**31-1)
    known={};count=0;start=time.monotonic();last=start
    with input_path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames is None or any(k not in reader.fieldnames for k in RAW_COLUMNS):raise ValueError('Missing required raw CSV columns: '+', '.join(RAW_COLUMNS))
        if len(reader.fieldnames)!=len(set(reader.fieldnames)):raise ValueError('Duplicate CSV column names are not accepted.')
        db.execute('BEGIN')
        for row in reader:
            if limit and count>=limit:break
            if None in row or any(row.get(k) is None for k in RAW_COLUMNS):raise ValueError('Malformed CSV record at ordinal '+str(count+1))
            raw=row['职位描述'];digest=hashlib.sha256(raw.encode('utf-8')).digest()
            sid=known.get(digest)
            if sid is None:
                sid=len(known)+1;known[digest]=sid
                db.execute('INSERT INTO sources(sid,raw_sha,raw) VALUES(?,?,?)',(sid,digest.hex(),raw))
            count+=1
            db.execute('INSERT INTO records(seq,stock_code,year,source,sid) VALUES(?,?,?,?,?)',(count,row['关联股票代码'],row['招聘发布年份'],row['来源'],sid))
            if count%50000==0:
                db.commit();db.execute('BEGIN')
                if time.monotonic()-last>=10:
                    progress(output,'INGEST_RAW_INPUT',records=count,elapsed_seconds=round(time.monotonic()-start,1));last=time.monotonic()
        db.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)',('ingest_complete','true'))
        db.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)',('records',str(count)));db.commit()
    return count

def classify(db,args,output):
    total=db.execute('SELECT count(*) FROM sources').fetchone()[0]
    done,last_sid=db.execute('SELECT count(*),coalesce(max(sid),0) FROM results').fetchone()
    if done!=last_sid:raise RuntimeError('Resume results are not a contiguous source prefix.')
    start=time.monotonic();last=start;pending=collections.deque();exhausted=False
    progress(output,'CLEAN_UNIQUE_ORIGINALS',unique_total=total,unique_done=done,workers=args.workers)
    context=multiprocessing.get_context('spawn')
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers,mp_context=context,initializer=worker_init,initargs=(args.review_resources,)) as pool:
        while pending or not exhausted:
            while not exhausted and len(pending)<2*args.workers:
                batch=db.execute('SELECT sid,raw_sha,raw FROM sources WHERE sid>? ORDER BY sid LIMIT ?',(last_sid,args.batch_size)).fetchall()
                if not batch:exhausted=True;break
                last_sid=batch[-1][0];pending.append(pool.submit(worker_batch,batch))
            if not pending:break
            result=pending.popleft().result()
            db.executemany('INSERT INTO results(body,stage,sid) VALUES(?,?,?)',result);db.commit();done+=len(result)
            if time.monotonic()-last>=10 or done==total:
                progress(output,'CLEAN_UNIQUE_ORIGINALS',unique_total=total,unique_done=done,elapsed_seconds=round(time.monotonic()-start,1));last=time.monotonic()
    if db.execute('SELECT count(*) FROM results').fetchone()[0]!=total:raise RuntimeError('Some sources were not cleaned; incomplete output is not published.')
    return total

def export(db,args,output,input_sha,code_sha,unique_count):
    dest=output/'cleaned';dest.mkdir(exist_ok=True)
    h=hashlib.sha256();counts=collections.Counter();files=[];writer=stream=binary=None;part=0;part_rows=0;temp=None
    def finish_part():
        if stream is None:return
        stream.close();binary.close();target=dest/f'part_{part:05d}.csv.gz';os.replace(temp,target)
        files.append({'file':str(target.relative_to(output)),'records':part_rows,'bytes':target.stat().st_size,'sha256':file_sha(target)})
    query='SELECT r.seq,r.stock_code,r.year,r.source,x.body,s.raw_sha,x.stage FROM records r JOIN sources s ON s.sid=r.sid JOIN results x ON x.sid=r.sid ORDER BY r.seq'
    try:
        for seq,stock,year,source,body,raw_sha,stage in db.execute(query):
            if part_rows==50000 or writer is None:
                finish_part();part+=1;part_rows=0;temp=dest/f'part_{part:05d}.csv.gz.partial';binary=temp.open('wb')
                gz=gzip.GzipFile(filename='',fileobj=binary,mode='wb',compresslevel=6,mtime=0)
                stream=io.TextIOWrapper(gz,encoding='utf-8-sig',newline='');writer=csv.DictWriter(stream,fieldnames=FIELDS+['cleaning_version','applied_stage'],lineterminator='\n');writer.writeheader()
            if seq!=counts['records']+1:raise RuntimeError('Raw record order changed.')
            row=dict(record_id=f'R2_{seq:010d}',stock_code=stock,year=year,source=source,responsibility_text=body,raw_text_sha256=raw_sha)
            h.update(canonical(row));writer.writerow(dict(row,cleaning_version='R12_V7_FROZEN' if args.review_resources else 'R12_V7_PUBLIC_RULES',applied_stage=stage));part_rows+=1
            counts.update(records=1,nonempty_records=int(bool(body.strip())),empty_records=int(not body.strip()));counts['stage_'+stage]+=1
            if seq%250000==0:progress(output,'EXPORT_IN_ORIGINAL_ORDER',records=seq)
        finish_part();stream=binary=None
    finally:
        if stream is not None:stream.close()
        if binary is not None:binary.close()
    digest=h.hexdigest();full_known=input_sha==EXPECTED['input_sha256'] and not args.limit
    exact=full_known and counts['records']==EXPECTED['records'] and digest==EXPECTED['canonical_sha256']
    status='PASS_EXACT_R12_V7_REPRODUCTION' if exact else ('PARTIAL_SMOKE_RUN' if args.limit else 'COMPLETE_OTHER_INPUT')
    if full_known and not exact:status='FAILED_REFERENCE_EQUIVALENCE'
    manifest={'status':status,'scope':'Raw CSV to frozen responsibility text; does not compute semantic-drift indicators.','version':'R12 V7','counts':dict(counts),'unique_originals_computed':unique_count,'input_sha256':input_sha,'script_sha256':code_sha,'review_resources_sha256':args.review_resources_sha256,'private_reviews_loaded':bool(args.review_resources),'canonical_fields':FIELDS,'canonical_sha256':digest,'expected_canonical_sha256':EXPECTED['canonical_sha256'] if full_known else None,'frozen_reference_match':exact,'used_saved_cleaned_text_as_input':False,'external_network_calls':0,'human_gold_standard':False,'files':files,'environment':{'python':sys.version,'platform':platform.platform(),'sqlite':sqlite3.sqlite_version},'parameters':{'workers':args.workers,'batch_size':args.batch_size,'limit':args.limit,'exact_source_deduplication_for_compute_only':True,'record_order_and_weights_preserved':True}}
    atomic_json(output/'manifest.json',manifest)
    if full_known and not exact:raise RuntimeError('Rebuilt output differs from frozen R12 V7. Failed output is preserved for diagnosis; it is NOT accepted.')
    return manifest

def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description='One-file frozen R12 V7 cleaning from the original recruitment CSV. No third-party packages or network required.')
    here=Path(__file__).resolve().parent
    parser.add_argument('--input',type=Path,default=here/'data/原始数据2.0版本.csv')
    parser.add_argument('--output-dir',type=Path,default=here/'output')
    parser.add_argument('--workers',type=int,default=min(6,max(1,(os.cpu_count() or 2)-2)))
    parser.add_argument('--batch-size',type=int,default=500)
    parser.add_argument('--limit',type=int,default=0,help='Smoke test only; a limited run is never marked as a full reproduction.')
    parser.add_argument('--review-resources',type=Path,help='Optional private local adjudications; needed for exact frozen-corpus reproduction.')
    parser.add_argument('--resume',action='store_true',help='Resume a complete raw-input index with identical code, input and limit.')
    parser.add_argument('--keep-work-db',action='store_true')
    parser.add_argument('--allow-other-input',action='store_true',help='Allow a different raw CSV; output is not certified as the research corpus.')
    args=parser.parse_args(argv)
    if sys.version_info[:2]!=(3,12):parser.error('Use CPython 3.12.x for the frozen research environment.')
    if args.workers<1 or args.batch_size<1 or args.limit<0:parser.error('Invalid workers, batch-size or limit.')
    args.input=args.input.resolve();output=args.output_dir.resolve()
    args.review_resources=args.review_resources.resolve() if args.review_resources else None
    load_review_resources(args.review_resources)
    args.review_resources_sha256=file_sha(args.review_resources) if args.review_resources else None
    if not args.input.is_file():parser.error('Raw input not found: '+str(args.input))
    if args.input.is_relative_to(output):parser.error('Output directory must not contain the raw input.')
    if output.exists() and any(output.iterdir()) and not args.resume:parser.error('Output directory is not empty; use a new directory or --resume.')
    output.mkdir(parents=True,exist_ok=True);start=time.monotonic();code_sha=code_fingerprint()
    progress(output,'CHECK_INPUT_SHA256',input=str(args.input));input_sha=file_sha(args.input)
    if input_sha!=EXPECTED['input_sha256'] and not args.allow_other_input:raise ValueError('Input SHA256 differs from the preserved original. No cleaning was performed. Use --allow-other-input only for a deliberately different dataset.')
    if input_sha==EXPECTED['input_sha256'] and not args.review_resources:
        raise ValueError('Frozen-corpus reproduction requires --review-resources with the separately held private local review JSON.')
    previous=existing_result(output) if args.resume else None
    if previous:
        if previous['script_sha256']!=code_sha or previous['input_sha256']!=input_sha or previous['parameters']['limit']!=args.limit or previous.get('review_resources_sha256')!=args.review_resources_sha256:raise RuntimeError('Existing output belongs to different code or input.')
        print('Existing output verified; no new reconstruction performed. Choose an empty output directory for a fresh run.',flush=True);return previous
    dbpath=output/'work.sqlite';new=not dbpath.exists();db=sqlite3.connect(dbpath)
    try:
        # The raw index is disposable and not resumable until complete. Avoid
        # writing each large original twice on removable storage. Cleaning
        # checkpoints switch to WAL after the complete raw index is flushed.
        db.execute('PRAGMA journal_mode='+('OFF' if new else 'WAL'))
        db.execute('PRAGMA synchronous='+('OFF' if new else 'NORMAL'))
        db.execute('PRAGMA temp_store=MEMORY');db.execute('PRAGMA cache_size=-131072')
        if new:
            db.executescript('CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT); CREATE TABLE sources(sid INTEGER PRIMARY KEY,raw_sha TEXT NOT NULL,raw TEXT NOT NULL); CREATE TABLE records(seq INTEGER PRIMARY KEY,stock_code TEXT NOT NULL,year TEXT NOT NULL,source TEXT NOT NULL,sid INTEGER NOT NULL); CREATE TABLE results(sid INTEGER PRIMARY KEY,body TEXT NOT NULL,stage TEXT NOT NULL);')
            db.executemany('INSERT INTO meta VALUES(?,?)',[('input_sha256',input_sha),('script_sha256',code_sha),('limit',str(args.limit)),('review_resources_sha256',args.review_resources_sha256 or '')]);db.commit()
            n=ingest(db,args.input,args.limit,output)
            with dbpath.open('r+b') as handle:os.fsync(handle.fileno())
            db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=NORMAL')
        else:
            m=dict(db.execute('SELECT key,value FROM meta'))
            if not args.resume or m.get('input_sha256')!=input_sha or m.get('script_sha256')!=code_sha or m.get('limit')!=str(args.limit) or m.get('review_resources_sha256')!=(args.review_resources_sha256 or ''):raise RuntimeError('Resume identity mismatch.')
            if m.get('ingest_complete')!='true':raise RuntimeError('Input indexing was interrupted; use a new empty output directory.')
            n=int(m['records'])
        if not args.limit and input_sha==EXPECTED['input_sha256'] and n!=EXPECTED['records']:raise RuntimeError('Original input row count differs from the frozen corpus.')
        unique_count=classify(db,args,output)
        manifest=export(db,args,output,input_sha,code_sha,unique_count)
        manifest['elapsed_seconds']=round(time.monotonic()-start,2);atomic_json(output/'manifest.json',manifest)
    finally:db.close()
    if not args.keep_work_db:
        dbpath.unlink()
        for suffix in ['-journal','-wal','-shm']:
            sidecar=Path(str(dbpath)+suffix)
            if sidecar.exists():sidecar.unlink()
    progress(output,manifest['status'],records=manifest['counts']['records'],canonical_sha256=manifest['canonical_sha256'],elapsed_seconds=manifest['elapsed_seconds'])
    return manifest

if __name__=='__main__':
    multiprocessing.freeze_support()
    try:main()
    except (Exception,KeyboardInterrupt) as error:
        print('FAILED: '+str(error),file=sys.stderr,flush=True);raise SystemExit(1)
