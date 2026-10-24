"""Offline regressions; every mutable database is in a temporary directory."""
from pathlib import Path
from contextlib import closing
import json,sqlite3,sys,tempfile,time,unittest
from unittest.mock import patch
PACKAGE=next(p for p in Path(__file__).resolve().parents if (p/'scripts/scale_ingest.py').is_file() and (p/'server.py').is_file())
sys.path.insert(0,str(PACKAGE))
from scripts import scale_ingest as scale,bulk_ingest as bulk
from server import ValidationError,initialize


def video(n=1,**extra):
    return {'id':f'fixture{n:04}','title':'Comment changer les essuie-glaces de sa voiture — TEST SYNTHETIQUE',
            'channel':'Synthetic fixture','language':'fr',**extra}


def social(**extra):
    return {'webpage_url':'https://www.tiktok.com/@fixture/video/1234567890123456789',
            'title':'Comment changer les essuie-glaces de sa voiture ? #école',
            '_collection':{'provider':'yt-dlp','evidence_scope':'public_video_metadata'},**extra}


class StageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.stage=self.root/'stage';self.output=self.root/'prepared'
    def tearDown(self):
        for attempt in range(4):
            try:self.temp.cleanup();return
            except OSError as error:
                if getattr(error,'winerror',None) not in {32,145} or attempt==3:raise
                time.sleep(.05*(attempt+1))
    def rows(self,rows,name='records.jsonl'):
        path=self.root/name
        with path.open('w',encoding='utf-8',newline='\n') as stream:
            for row in rows:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
        return path
    def accepted(self):
        return [r for p in sorted(self.output.glob('batch-*/accepted.json')) for r in json.loads(p.read_text(encoding='utf-8'))]
    def rejected(self):
        rows=[]
        for path in sorted(self.output.glob('batch-*/quarantine.jsonl')):
            with path.open(encoding='utf-8') as stream:rows.extend(json.loads(line) for line in stream)
        return rows
    def test_resume_cursor_and_idempotence(self):
        file=self.rows([video(i) for i in range(9)])
        first=scale.stage([file],self.stage,max_records=4,commit_every=2)
        self.assertEqual(first['source_records'],4);self.assertFalse(first['complete'])
        second=scale.stage([file],self.stage,max_records=10,resume=True)
        self.assertEqual(second['source_records'],9);self.assertTrue(second['complete'])
        third=scale.stage([file],self.stage,resume=True)
        self.assertEqual(third['processed_this_run'],0);self.assertEqual(third['source_records'],9)
    def test_global_negative_variant_in_later_source_quarantines_identity(self):
        first=self.rows([social()],name='one.jsonl');second=self.rows([social(isPrivate=True)],name='two.jsonl')
        scale.stage([first],self.stage);scale.stage([second],self.stage)
        report=scale.prepare(self.stage,self.output,batch_size=1)
        self.assertEqual(report['accepted_candidates'],0);self.assertEqual(report['quarantined'],1)
        self.assertIn('Private or access-restricted record',self.rejected()[0]['reasons'])
    def test_duplicate_renamed_tiktok_author_not_split_across_batches(self):
        rows=[social(),social(webpage_url='https://www.tiktok.com/@renamed/video/1234567890123456789')]+[video(i) for i in range(3)]
        file=self.rows(rows);report=scale.stage([file],self.stage)
        self.assertEqual(report['unique_media_identities'],4);self.assertEqual(report['duplicate_identity_variants'],1)
        scale.prepare(self.stage,self.output,batch_size=1)
        records=self.accepted();self.assertEqual(len(records),4)
        self.assertEqual(len(next(r for r in records if r['platform']=='tiktok')['bulk_sources']),2)
    def test_prepare_resume_has_exact_coverage_no_repeat_ids(self):
        file=self.rows([video(i) for i in range(7)]);scale.stage([file],self.stage)
        first=scale.prepare(self.stage,self.output,batch_size=2,max_batches=1)
        self.assertFalse(first['complete']);self.assertEqual(first['source_records'],2)
        second=scale.prepare(self.stage,self.output,batch_size=2,resume=True)
        self.assertTrue(second['complete']);self.assertEqual(second['source_records'],7)
        ids=[r['id'] for r in self.accepted()];self.assertEqual(len(ids),len(set(ids)))
        third=scale.prepare(self.stage,self.output,batch_size=2,resume=True)
        self.assertEqual(second['batches'],third['batches'])
    def test_pending_source_prevents_any_candidate_export(self):
        file=self.rows([video(i) for i in range(5)]);scale.stage([file],self.stage,max_records=1)
        with self.assertRaisesRegex(ValidationError,'Complete all'):scale.prepare(self.stage,self.output)
        self.assertFalse(self.output.exists())
    def test_source_mutation_rejected_at_resume_and_preparation(self):
        file=self.rows([video()]);scale.stage([file],self.stage)
        file.write_text(json.dumps(video(2))+'\n',encoding='utf-8')
        with self.assertRaisesRegex(ValidationError,'Source bytes changed'):scale.stage([file],self.stage,resume=True)
        with self.assertRaisesRegex(ValidationError,'Archived source hash'):scale.prepare(self.stage,self.output)
    def test_prepared_tamper_is_rejected(self):
        file=self.rows([video()]);scale.stage([file],self.stage);scale.prepare(self.stage,self.output)
        (self.output/'batch-000000/accepted.json').write_text('[]',encoding='utf-8')
        with self.assertRaisesRegex(ValidationError,'batch file changed'):scale.prepare(self.stage,self.output,resume=True)
    def test_prepared_campaign_is_sealed_against_later_negative_variants(self):
        file=self.rows([video()]);scale.stage([file],self.stage);scale.prepare(self.stage,self.output)
        new=self.rows([video(isPrivate=True)],name='new.jsonl')
        with self.assertRaisesRegex(ValidationError,'sealed'):scale.stage([new],self.stage)
        self.assertTrue(scale.stage([file],self.stage,resume=True)['complete'])
    def test_exact_raw_hash_unicode_and_social_tokens(self):
        row=social(description='Tutoriel essuie-glaces.\u2028Texte réel de fixture. #école #fypシ゚viral')
        file=self.rows([row]);scale.stage([file],self.stage);scale.prepare(self.stage,self.output)
        result=self.accepted()[0]
        self.assertEqual(result['provenance']['source_record_sha256'],bulk.digest(row))
        self.assertIn('#école',result['social_content']['hashtags'])
        self.assertIn('\u2028',result['social_content']['original_caption'])
    def test_comments_media_and_unknown_private_fields_are_not_persisted(self):
        row=social(comments=[{'text':'UNRELATED_PRIVATE_COMMENT'}],api_token='SECRET_SENTINEL',video_url='https://media.test/video.mp4')
        file=self.rows([row]);scale.stage([file],self.stage)
        with closing(sqlite3.connect(self.stage/'stage.sqlite3')) as conn:
            record=conn.execute('SELECT record_json FROM entries').fetchone()[0]
        for value in ('SECRET_SENTINEL','UNRELATED_PRIVATE_COMMENT','https://media.test/video.mp4'):
            self.assertNotIn(value,record)
    def test_index_body_cannot_prove_language_or_teaching(self):
        row=social(title='Car clip',description='Comment changer les essuie-glaces tutoriel mécanique',
            _collection={'provider':'exa-public-mcp','evidence_scope':'public_video_metadata'})
        file=self.rows([row]);scale.stage([file],self.stage);scale.prepare(self.stage,self.output)
        self.assertEqual(self.accepted(),[])
        result=self.rejected()[0]['record'];self.assertEqual(result['language'],'und')
        self.assertEqual(result['verification_scope'],'indexed_search_metadata');self.assertEqual(result['description'],'')
    def test_language_conflict_and_promo_variants_remain_quarantined(self):
        file=self.rows([video(1),video(1,language='en'),video(2),video(2,description='BUY NOW promo code EXAMPLE')])
        scale.stage([file],self.stage);scale.prepare(self.stage,self.output)
        self.assertEqual(self.accepted(),[]);self.assertEqual(len(self.rejected()),2)
        self.assertTrue(any('conflicting_video_language_metadata' in r['reasons'] for r in self.rejected()))
    def test_reconciliation_matches_existing_bulk_prepare(self):
        rows=[video(1),video(1,language='en'),video(2),social(),social(isPrivate=True),
              social(webpage_url='https://www.tiktok.com/@fixture/video/1234567890123456790',title='Car clip',
                     _collection={'provider':'exa-public-mcp','evidence_scope':'indexed_search_metadata'}),
              social(webpage_url='https://www.tiktok.com/@fixture/video/1234567890123456790')]
        file=self.rows(rows);scale.stage([file],self.stage);scale.prepare(self.stage,self.output)
        old=self.root/'bulk';bulk.prepare([file],old,db=None)
        oldaccepted=json.loads((old/'accepted.json').read_text(encoding='utf-8'))
        oldrejected=[json.loads(s) for s in (old/'quarantine.jsonl').read_text(encoding='utf-8').split('\n') if s]
        self.assertEqual({r['id'] for r in self.accepted()},{r['id'] for r in oldaccepted})
        self.assertEqual({r['id']:r['reasons'] for r in self.rejected()},{r['id']:r['reasons'] for r in oldrejected})
    def test_output_is_compatible_with_existing_apply_dry_run(self):
        file=self.rows([video()]);scale.stage([file],self.stage);scale.prepare(self.stage,self.output)
        database=initialize(self.root/'fixture-catalog.sqlite3')
        result=bulk.apply_prepared(self.output/'batch-000000',db=database)
        self.assertEqual(result['selected'],1);self.assertFalse(result['database_modified'])
        with self.assertRaisesRegex(ValidationError,'approval'):bulk.apply_prepared(self.output/'batch-000000',db=database,execute=True)
    def test_foreign_database_is_not_modified(self):
        self.stage.mkdir();database=self.stage/'stage.sqlite3'
        with closing(sqlite3.connect(database)) as conn:conn.execute('CREATE TABLE important(value TEXT)');conn.commit()
        before=bulk.file_digest(database)
        with self.assertRaisesRegex(ValidationError,'not a scale'):scale.stage([self.rows([video()])],self.stage)
        self.assertEqual(before,bulk.file_digest(database))
    def test_explicit_resume_and_provider_pin(self):
        file=self.rows([video()]);scale.stage([file],self.stage)
        with self.assertRaisesRegex(ValidationError,'--resume'):scale.stage([file],self.stage)
        with self.assertRaisesRegex(ValidationError,'same provider'):scale.stage([file],self.stage,resume=True,provider='yt-dlp')
    def test_malformed_json_keeps_only_committed_rows(self):
        file=self.rows([video(1),video(2)]);file.write_bytes(file.read_bytes()+b'{broken}\n')
        with self.assertRaisesRegex(ValidationError,'Invalid JSONL'):scale.stage([file],self.stage,commit_every=1)
        with scale.staging(self.stage) as (conn,_):
            self.assertEqual(scale.counts(conn)['source_records'],2);self.assertFalse(scale.counts(conn)['complete'])
    def test_unexpected_failure_resumes_at_last_atomic_commit(self):
        file=self.rows([video(i) for i in range(6)]);original=bulk.adapt;calls=0
        def fail(row,*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==4:raise RuntimeError('Simulated interruption')
            return original(row,*args,**kwargs)
        with patch.object(bulk,'adapt',fail):
            with self.assertRaisesRegex(RuntimeError,'Simulated'):scale.stage([file],self.stage,commit_every=2)
        with scale.staging(self.stage) as (conn,_):self.assertEqual(scale.counts(conn)['source_records'],2)
        result=scale.stage([file],self.stage,resume=True,commit_every=2)
        self.assertEqual(result['source_records'],6);self.assertEqual(result['processed_this_run'],4)
    def test_changed_source_during_staging_is_permanently_invalid_after_restore(self):
        file=self.rows([video(1),video(2),video(3)]);original_bytes=file.read_bytes()
        original=bulk.adapt;calls=0
        def change_source(row,*args,**kwargs):
            nonlocal calls
            calls+=1
            result=original(row,*args,**kwargs)
            if calls==2:
                file.write_bytes(original_bytes+b'\n')
            return result
        with patch.object(bulk,'adapt',change_source):
            with self.assertRaisesRegex(ValidationError,'Input changed during staging'):
                scale.stage([file],self.stage,commit_every=1)
        # Restoring the original SHA must not rehabilitate committed entries.
        file.write_bytes(original_bytes)
        with self.assertRaisesRegex(ValidationError,'invalidated'):
            scale.stage([file],self.stage,resume=True)
        with self.assertRaisesRegex(ValidationError,'invalidated'):
            scale.prepare(self.stage,self.output)
        self.assertFalse(self.output.exists())
    def test_interrupted_batch_write_replays_without_losing_variants(self):
        file=self.rows([video(i) for i in range(4)]);scale.stage([file],self.stage)
        original=bulk.atomic_json
        def fail(path,value):
            if Path(path).name=='report.json' and Path(path).parent.name=='batch-000001':raise OSError('Simulated disk failure')
            return original(path,value)
        with patch.object(bulk,'atomic_json',fail):
            with self.assertRaisesRegex(OSError,'Simulated'):scale.prepare(self.stage,self.output,batch_size=2)
        checkpoint=json.loads((self.output/'checkpoint.json').read_text(encoding='utf-8'))
        self.assertEqual(len(checkpoint['batches']),1)
        report=scale.prepare(self.stage,self.output,batch_size=2,resume=True)
        self.assertEqual(report['source_records'],4);self.assertEqual(len(self.accepted()),4)
        self.assertEqual(len({row['id'] for row in self.accepted()}),4)
    def test_mutated_source_parse_failures_still_invalidate_committed_rows(self):
        for name,trailer in [('json',b'{broken}\n'),('unicode',b'\xff\n'),('oversize',b'x'*(scale.MAX_LINE+1)+b'\n')]:
            with self.subTest(name=name):
                file=self.rows([video(1),video(2)],name=name+'.jsonl')
                original_bytes=file.read_bytes();original=bulk.adapt;calls=0
                stage=self.root/('stage-'+name)
                def mutate(row,*args,**kwargs):
                    nonlocal calls
                    calls+=1
                    result=original(row,*args,**kwargs)
                    if calls==2:file.write_bytes(original_bytes+trailer)
                    return result
                with patch.object(bulk,'adapt',mutate):
                    with self.assertRaisesRegex(ValidationError,'Input changed during staging'):
                        scale.stage([file],stage,commit_every=1)
                file.write_bytes(original_bytes)
                with self.assertRaisesRegex(ValidationError,'invalidated'):
                    scale.stage([file],stage,resume=True)
                with self.assertRaisesRegex(ValidationError,'invalidated'):
                    scale.prepare(stage,self.root/('prepared-'+name))
    def test_stage_and_output_cannot_overlap(self):
        file=self.rows([video()]);scale.stage([file],self.stage)
        with self.assertRaisesRegex(ValidationError,'separate'):scale.prepare(self.stage,self.stage/'prepared')
    def test_missing_title_never_gets_invented(self):
        file=self.rows([video(title='')]);scale.stage([file],self.stage);scale.prepare(self.stage,self.output)
        self.assertEqual(self.accepted(),[]);self.assertIsNone(self.rejected()[0]['record'])


if __name__=='__main__':unittest.main(verbosity=2)
