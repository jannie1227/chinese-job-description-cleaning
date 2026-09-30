import csv
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from chinese_job_description_cleaning import DescriptionCleaner, clean_description, clean_record, clean_records

ROOT=Path(__file__).resolve().parents[1]
TEXT='岗位职责：负责设备安装与维护。\n任职要求：大专以上学历。'


class InstalledDescriptionAPI(unittest.TestCase):
    def test_plain_string_runs_offline_without_private_configuration(self):
        with patch('socket.create_connection',side_effect=AssertionError('Network not allowed')):
            self.assertEqual(clean_description(TEXT),'负责设备安装与维护')
            self.assertEqual(clean_description('任职要求：本科以上学历，熟悉 Python。'),'')
            self.assertEqual(clean_description(''),'')

    def test_record_retains_raw_text_identity_and_quality_limits(self):
        row=clean_record(TEXT,record_id='00001')
        self.assertEqual(row['description_raw'],TEXT)
        self.assertEqual(row['record_id'],'00001')
        self.assertEqual(row['raw_text_sha256'],hashlib.sha256(TEXT.encode()).hexdigest())
        self.assertEqual(row['rule_scope'],'R12_V7_PUBLIC_RULES')
        self.assertFalse(row['human_gold_standard'])
        json.dumps(row,ensure_ascii=False)

    def test_batch_preserves_duplicate_and_empty_records(self):
        rows=clean_records([{'description':TEXT},{'description':TEXT},{'description':''}])
        self.assertEqual(len(rows),3)
        self.assertNotEqual(rows[0]['record_id'],rows[1]['record_id'])
        self.assertEqual(rows[2]['responsibility_text'],'')
        with self.assertRaises(ValueError):
            clean_records([{'record_id':'same','description':TEXT},{'record_id':'same','description':TEXT}])
        with self.assertRaises(TypeError):
            clean_description(None)

    def test_shared_instance_is_safe_for_parallel_python_calls(self):
        cleaner=DescriptionCleaner()
        with ThreadPoolExecutor(max_workers=4) as executor:
            out=list(executor.map(cleaner.clean_description,[TEXT,'']*4))
        self.assertEqual(out,['负责设备安装与维护','']*4)

    def test_installed_cli_accepts_normal_csv_and_preserves_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'cleaned.csv'
            args=[sys.executable,'-m','chinese_job_description_cleaning','--input',str(ROOT/'examples/input_synthetic.csv'),'--output',str(output),'--id-column','example_id']
            result=subprocess.run(args,cwd=directory,text=True,capture_output=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stderr)
            with output.open(encoding='utf-8-sig',newline='') as handle:rows=list(csv.DictReader(handle))
            self.assertEqual(len(rows),4)
            self.assertEqual(rows[0]['responsibility_text'],'负责设备安装与维护')
            self.assertEqual(rows[3]['responsibility_text'],'')
            data=output.read_bytes()
            self.assertNotEqual(subprocess.run(args,cwd=directory,capture_output=True).returncode,0)
            self.assertEqual(output.read_bytes(),data)

    def test_optional_local_resources_do_not_contaminate_default_instance(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'caller_resources.json'
            path.write_text(json.dumps({'r10_reviews':[],'v5_reviews':[],'v7_reviews':[]}),encoding='utf-8')
            private=DescriptionCleaner(path)
            public=DescriptionCleaner()
            self.assertEqual(private.clean_description(TEXT),public.clean_description(TEXT))
            self.assertEqual(private.clean_record(TEXT)['rule_scope'],'R12_V7_WITH_LOCAL_REVIEWS')
            self.assertEqual(public.clean_record(TEXT)['rule_scope'],'R12_V7_PUBLIC_RULES')


if __name__ == '__main__':
    unittest.main()
