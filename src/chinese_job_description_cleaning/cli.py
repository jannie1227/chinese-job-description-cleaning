"""Stream caller-owned CSV locally; never print or send record contents."""
from .api import DescriptionCleaner
import argparse
import csv
import gzip
import io
import json
import os
from pathlib import Path
import sys
import tempfile


def _cell(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')) if isinstance(value, (list,dict)) else value


def process_csv(input_path, output_path, cleaner, text_column, id_column, category_columns=None):
    # 临时文件与目标同目录；已存在目标一律拒绝，不覆盖调用者的数据。
    source=Path(input_path).resolve(strict=True);target=Path(output_path).absolute()
    if source==target.resolve() or target.exists() or target.is_symlink():
        raise ValueError('Output must be a new file separate from the input.')
    target.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.clean-',suffix='.partial',dir=target.parent)
    temp=Path(name);rows=0
    try:
        try:csv.field_size_limit(sys.maxsize)
        except OverflowError:csv.field_size_limit(2**31-1)
        opener=gzip.open if source.suffix=='.gz' else Path.open
        with os.fdopen(fd,'w',encoding='utf-8-sig',newline='') as outgoing,opener(source,'rt' if source.suffix=='.gz' else 'r',encoding='utf-8-sig',newline='') as incoming:
            reader=csv.DictReader(incoming,strict=True)
            if reader.fieldnames is None or len(reader.fieldnames)!=len(set(reader.fieldnames)) or text_column not in reader.fieldnames:
                raise ValueError('CSV has missing, duplicate or ambiguous required columns.')
            if id_column and id_column not in reader.fieldnames:
                raise ValueError('Requested ID column is missing.')
            for col in (category_columns or {}).values():
                if col and col not in reader.fieldnames:raise ValueError('Requested metadata column is missing.')
            def records():
                for number,row in enumerate(reader,1):
                    if None in row or any(value is None for value in row.values()):raise ValueError('Malformed CSV row at ordinal '+str(number))
                    result={'description':row[text_column]}
                    if id_column:result['record_id']=row[id_column]
                    for key,col in (category_columns or {}).items():result[key]=row[col] if col else ''
                    yield result
            headers=list(cleaner.clean_record('').keys())
            writer=csv.DictWriter(outgoing,fieldnames=headers,lineterminator='\n');writer.writeheader()
            for result in cleaner.iter_clean_records(records()):
                writer.writerow({key:_cell(value) for key,value in result.items()});rows+=1
            outgoing.flush();os.fsync(outgoing.fileno())
        # hard-link publication fails if another process created the output;
        # unlike replacement it cannot silently overwrite an existing file.
        os.link(temp,target)
        return {'rows':rows,'output':str(target)}
    finally:
        if temp.exists():temp.unlink()


def main(argv=None):
    parser=argparse.ArgumentParser(description='Extract responsibilities from caller-owned descriptions with R12 V7 public rules.')
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--text-column',default='description',help='Column containing caller-owned input text.')
    parser.add_argument('--id-column',help='Optional unique string ID column; otherwise IDs are generated in row order.')
    parser.add_argument('--review-resources',type=Path,help='Optional caller-owned private adjudications; not needed for normal use.')
    args=parser.parse_args(argv)
    try:
        result=process_csv(args.input,args.output,DescriptionCleaner(args.review_resources),args.text_column,args.id_column)
    except (ValueError,TypeError,RuntimeError,OSError):
        # 只返回简明输入/运行错误；不把底层的原文断言打印到终端。
        parser.exit(2,'CSV cleaning failed; check columns, IDs, input types and the output path. No input text was logged.\n')
    print(json.dumps(result,ensure_ascii=False))
