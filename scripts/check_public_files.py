"""Validate public package files; not a general data-loss-prevention system."""
import ast,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[]
    tracked=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True)
    paths=[ROOT/x.decode() for x in tracked.stdout.split(b'\0') if x] if tracked.returncode==0 and tracked.stdout else [p for p in ROOT.rglob('*') if p.is_file() and not any(x in {'.git','__pycache__','build','dist','.venv'} or x.endswith('.egg-info') for x in p.relative_to(ROOT).parts)]
    secrets=re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    private_paths=re.compile(r'/(?:Users|Volumes)/[A-Za-z0-9\u3400-\u9fff]')
    for path in paths:
        name=path.relative_to(ROOT).as_posix()
        if path.suffix in {'.gz','.zip','.sqlite','.db','.parquet','.dta','.xlsx','.pem','.key','.jsonl','.whl'} or any(x in {'private','private_resources','output','outputs','data'} for x in path.relative_to(ROOT).parts):errors.append(name+': excluded data path');continue
        if path.stat().st_size>1024*1024:errors.append(name+': unexpected large file');continue
        try:text=path.read_text(encoding='utf-8-sig')
        except UnicodeError:errors.append(name+': unexpected binary');continue
        if secrets.search(text) or private_paths.search(text):errors.append(name+': credential or developer path')
        if path.suffix=='.csv' and 'data_rules/' not in name:
            if name not in {'examples/input_synthetic.csv','research_input_synthetic.csv'}:errors.append(name+': unapproved CSV');continue
            with path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
            id_name='example_id' if name.startswith('examples/') else 'record_id'
            if not all(r[id_name].startswith('SYNTH') for r in rows):errors.append(name+': non-synthetic ID')
    manifest=json.loads((ROOT/'docs/source_manifest.json').read_text())
    if 'semantic_modules' in manifest:
        pkg=ROOT/'src/chinese_job_description_cleaning'
        for name,h in manifest['semantic_modules'].items():
            path=pkg/'engine_sources'/Path(name.replace('.','/')+'.py')
            if hashlib.sha256(path.read_bytes()).hexdigest()!=h:errors.append(str(path.relative_to(ROOT))+': frozen rule changed')
        tree=ast.parse((pkg/'_frozen.py').read_text())
        resources=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='BUNDLED_RESOURCES' for x in n.targets))
        if resources!={'r10_reviews':[],'v5_reviews':[],'v7_reviews':[]}:errors.append('private source adjudications embedded')
    else:
        pkg=ROOT/'src/chinese_job_title_cleaning'
        for folder,key in [('_lexical','lexical_public_hashes'),('_revision','revision_public_hashes')]:
            for name,h in manifest[key].items():
                if hashlib.sha256((pkg/folder/name).read_bytes()).hexdigest()!=h:errors.append(folder+'/'+name+': copied rule changed')
    if errors:raise SystemExit('\n'.join(errors))
    print('PASS_PUBLIC_FILES',len(paths),'files')

if __name__=='__main__':main()
