"""Offline, resumable metadata staging. No network and no production import.

JSONL records are qualified by bulk_ingest.adapt unchanged. All variants of an
identity are reconciled before bounded, reviewable bulk-ingest batches are made.
The only database written is DIRECTORY/stage.sqlite3 with this tool's marker.
"""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import contextmanager, closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from scripts import bulk_ingest as bulk
from server import ValidationError, language_confidence, utcnow

VERSION='1.0.2'
APPLICATION_ID=0x524C5333
MAX_LINE=bulk.MAX_LINE_BYTES
NEGATIVES={'Private or access-restricted record',
           'Not an evidenced video; images and mixed carousels are not imported'}


def engine_hash():
    return bulk.digest({name:bulk.file_digest(BASE/name) for name in
        ('scripts/scale_ingest.py','scripts/bulk_ingest.py','scripts/social_metadata.py','automotive.py','server.py')})


@contextmanager
def staging(directory, *, create=False):
    directory=Path(directory).resolve()
    if not directory.exists():
        if not create: raise ValidationError('Staging directory does not exist')
        directory.mkdir(parents=True)
    database=directory/'stage.sqlite3'
    lock=directory/'.scale.lock'
    try: descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError: raise ValidationError('Staging is locked; verify the prior process before removing a stale lock') from None
    os.close(descriptor)
    connection=None
    try:
        if database.exists():
            # Validate before any write or PRAGMA that can modify an existing DB.
            with closing(sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)) as probe:
                if probe.execute('PRAGMA application_id').fetchone()[0]!=APPLICATION_ID:
                    raise ValidationError('This is not a scale-ingest staging database')
                if probe.execute("SELECT 1 FROM metadata WHERE key='invalidated_at'").fetchone():
                    raise ValidationError('Stage was invalidated by a source integrity failure; use a new stage')
                marker=probe.execute("SELECT value FROM metadata WHERE key='engine_hash'").fetchone()
                if not marker or marker[0]!=engine_hash():
                    raise ValidationError('Qualification engine changed; use a new stage to preserve provenance')
        elif not create: raise ValidationError('Staging database is missing')
        elif any(p.name!='.scale.lock' for p in directory.iterdir()):
            raise ValidationError('A new stage requires an empty directory')
        connection=sqlite3.connect(database)
        connection.row_factory=sqlite3.Row
        if connection.execute('PRAGMA application_id').fetchone()[0]==0:
            connection.executescript(f'''
                PRAGMA application_id={APPLICATION_ID};
                CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                CREATE TABLE sources(id INTEGER PRIMARY KEY,path TEXT UNIQUE NOT NULL,name TEXT NOT NULL,
                    sha256 TEXT NOT NULL,bytes INTEGER NOT NULL,next_offset INTEGER NOT NULL DEFAULT 0,
                    next_line INTEGER NOT NULL DEFAULT 1,status TEXT NOT NULL DEFAULT 'pending');
                CREATE TABLE entries(seq INTEGER PRIMARY KEY,source_id INTEGER NOT NULL,line INTEGER NOT NULL,
                    raw_sha256 TEXT NOT NULL,group_key TEXT NOT NULL,media_id TEXT,
                    record_json TEXT,decision_json TEXT,rejection_json TEXT,
                    UNIQUE(source_id,line));
                CREATE INDEX entries_group ON entries(group_key,seq);
            ''')
            connection.executemany('INSERT INTO metadata VALUES(?,?)',
                [('engine_hash',engine_hash()),('version',VERSION),('created_at',utcnow())])
            connection.commit()
        yield connection,directory
    finally:
        if connection is not None: connection.close()
        lock.unlink(missing_ok=True)


def counts(connection):
    total=connection.execute('SELECT count(*) FROM entries').fetchone()[0]
    unique=connection.execute('SELECT count(DISTINCT media_id) FROM entries').fetchone()[0]
    known=connection.execute('SELECT count(*) FROM entries WHERE media_id IS NOT NULL').fetchone()[0]
    pending=connection.execute("SELECT count(*) FROM sources WHERE status!='complete'").fetchone()[0]
    return {'source_records':total,'unique_media_identities':unique,'duplicate_identity_variants':known-unique,
            'unresolved_records':total-known,'pending_sources':pending,'complete':pending==0,
            'production_database_modified':False,'network_requests':0}


@contextmanager
def source_integrity(connection,path,source):
    """Check a source even if parsing/opening it fails after partial commits."""
    try:
        yield
    finally:
        try:changed=bulk.file_digest(path)!=source['sha256']
        except OSError:changed=True
        if changed:
            connection.rollback()
            connection.execute('INSERT OR REPLACE INTO metadata VALUES(?,?)',('invalidated_at',utcnow()))
            connection.execute('INSERT OR REPLACE INTO metadata VALUES(?,?)',('invalidation_reason','source_changed_during_staging'))
            connection.execute("UPDATE sources SET status='invalid' WHERE id=?",(source['id'],))
            connection.commit()
            raise ValidationError('Input changed during staging; snapshot cannot be exported') from None


def stage(inputs, directory, *, provider='auto', max_records=25000, commit_every=500, resume=False):
    if provider not in bulk.PROVIDERS or not 1<=max_records<=1000000 or not 1<=commit_every<=5000:
        raise ValidationError('Invalid provider or bounded row/commit limits')
    inputs=[Path(p).resolve() for p in inputs]
    if not inputs: raise ValidationError('Explicit JSONL input files are required')
    processed=0
    with staging(directory,create=True) as (conn,folder):
        sealed=conn.execute("SELECT value FROM metadata WHERE key='sealed_at'").fetchone()
        if sealed and any(not conn.execute('SELECT 1 FROM sources WHERE path=?',(str(path),)).fetchone() for path in inputs):
            raise ValidationError('Prepared stage is sealed; new source variants require a new campaign and review')
        old=conn.execute("SELECT value FROM metadata WHERE key='provider'").fetchone()
        if old and old[0]!=provider: raise ValidationError('Resume must use the same provider')
        conn.execute('INSERT OR IGNORE INTO metadata VALUES(?,?)',('provider',provider))
        for path in inputs:
            if path.suffix.lower() not in {'.jsonl','.ndjson'} or path.is_relative_to(folder):
                raise ValidationError('Use explicit JSONL files outside the staging directory')
            source_hash=bulk.file_digest(path)
            source=conn.execute('SELECT * FROM sources WHERE path=?',(str(path),)).fetchone()
            if source:
                if source['sha256']!=source_hash: raise ValidationError('Source bytes changed; use a new immutable snapshot and stage')
                if not resume: raise ValidationError('Existing source requires --resume')
            else:
                conn.execute('INSERT INTO sources(path,name,sha256,bytes) VALUES(?,?,?,?)',
                             (str(path),path.name,source_hash,path.stat().st_size))
        conn.commit()
        for path in inputs:
            source=conn.execute('SELECT * FROM sources WHERE path=?',(str(path),)).fetchone()
            if source['status']=='complete' or processed>=max_records: continue
            with source_integrity(conn,path,source),path.open('rb') as stream:
                stream.seek(source['next_offset']); line_number=source['next_line']; uncommitted=0
                while processed<max_records:
                    raw=stream.readline(MAX_LINE+1)
                    if not raw:
                        conn.execute("UPDATE sources SET status='complete' WHERE id=?",(source['id'],));break
                    if len(raw)>MAX_LINE: raise ValidationError(f'JSONL line {line_number} exceeds 2 MiB')
                    if raw.strip():
                        try: row=json.loads(raw.decode('utf-8-sig' if line_number==1 else 'utf-8'))
                        except (UnicodeError,json.JSONDecodeError): raise ValidationError(f'Invalid JSONL on line {line_number}') from None
                        if not isinstance(row,dict) or any(isinstance(row.get(k),list) for k in ('items','entries','videos','latestPosts','latestIgtvVideos')):
                            raise ValidationError('One media object per physical JSONL line is required; flatten containers upstream')
                        raw_hash=bulk.digest(row); record=decision=rejection=None; media_id=None
                        try:
                            record,decision=bulk.adapt(row,provider,source_label=source['name'],index=line_number)
                            media_id=record['id']
                        except (ValidationError,ValueError,TypeError) as error:
                            reason=bulk.short(str(error),250)
                            if reason in NEGATIVES: media_id=bulk.rejected_media_identity(row,provider)
                            rejection={'source':source['name'],'record_index':line_number,'source_record_sha256':raw_hash,
                                       'reasons':[reason],'record':None}
                            if media_id: rejection['id']=media_id
                        group_key=media_id or f'~unresolved:{source["id"]:09}:{line_number:012}'
                        dump=lambda value:json.dumps(value,ensure_ascii=False,separators=(',',':')) if value is not None else None
                        conn.execute('INSERT INTO entries(source_id,line,raw_sha256,group_key,media_id,record_json,decision_json,rejection_json) VALUES(?,?,?,?,?,?,?,?)',
                            (source['id'],line_number,raw_hash,group_key,media_id,dump(record),dump(decision),dump(rejection)))
                        processed+=1;uncommitted+=1
                    line_number+=1
                    conn.execute('UPDATE sources SET next_offset=?,next_line=? WHERE id=?',(stream.tell(),line_number,source['id']))
                    if stream.tell()==source['bytes']:
                        conn.execute("UPDATE sources SET status='complete' WHERE id=?",(source['id'],))
                    if uncommitted>=commit_every: conn.commit();uncommitted=0
                conn.commit()
        report={'tool':'scale_ingest','version':VERSION,'mode':'staging_only','created_at':utcnow(),
                'processed_this_run':processed,'engine_sha256':engine_hash(),**counts(conn)}
        bulk.atomic_json(folder/'stage-report.json',report)
        return report


def reconcile(identifier, entries):
    """Same conservative variant policy as bulk_ingest.prepare, tested for parity."""
    variants=[(json.loads(e['record_json']),json.loads(e['decision_json'])) for e in entries if e['record_json']]
    negatives=[json.loads(e['rejection_json']) for e in entries if e['rejection_json']]
    if not variants:
        reasons=list(dict.fromkeys(r for entry in negatives for r in entry['reasons']))
        return None,{'id':identifier,'record':None,'reasons':reasons,'source_variants':negatives}
    languages={r['language'].split('-')[0] for r,_ in variants if r['language_status']=='platform_metadata'}
    direct=any(r['verification_scope']=='public_video_metadata' and not d['reasons'] for r,d in variants)
    indexed=any(r['verification_scope']=='indexed_search_metadata' and not d['reasons'] for r,d in variants)
    reasons=[];waived=[];missing={'no_explicit_learning_signal','no_supported_automotive_or_motorsport_topic'}
    for record,decision in variants:
        for reason in decision['reasons']:
            if (direct or indexed) and record['verification_scope']=='indexed_search_metadata' and reason in missing:
                waived.append({'reason':reason,'scope':'indexed_search_metadata','source_record_sha256':record['provenance']['source_record_sha256']})
            else: reasons.append(reason)
    reasons.extend(r for entry in negatives for r in entry['reasons'])
    reasons=list(dict.fromkeys(reasons))
    if len(languages)>1: reasons.append('conflicting_video_language_metadata')
    record=max((r for r,_ in variants),key=lambda r:(
        language_confidence(r['language'],r['language_status'])=='platform_declared',
        {'public_video_metadata':3,'public_listing_metadata':2,'indexed_search_metadata':1}.get(r['verification_scope'],0),
        r['bulk_qualification']['status']=='candidate',len(r['description'])))
    record['bulk_sources']=[{**r['provenance'],**({'collection':r['collection_provenance']} if r.get('collection_provenance') else {})} for r,_ in variants]
    if negatives: record['bulk_rejected_variants']=negatives
    if waived:
        record['bulk_reconciliation']={'basis':'qualified_direct_metadata_over_index_missing_evidence' if direct else 'qualified_index_title_over_index_missing_evidence',
            'ignored_missing_evidence':waived,'explicit_negative_flags_preserved':True,'selected_scope':record['verification_scope'],'rules_version':bulk.VERSION}
    return (None,{'id':identifier,'reasons':reasons,'record':record}) if reasons else (record,None)


def prepare(directory, output, *, batch_size=1000, max_batches=10, resume=False):
    if not 1<=batch_size<=5000 or not 1<=max_batches<=1000:
        raise ValidationError('Bound batch-size to 1–5000 and max-batches to 1–1000')
    output=Path(output).resolve()
    with staging(directory) as (conn,folder):
        if output==folder or output.is_relative_to(folder) or folder.is_relative_to(output):
            raise ValidationError('Prepared output must be separate from the stage')
        if counts(conn)['pending_sources']: raise ValidationError('Complete all staged source files before global reconciliation')
        sources=[dict(s) for s in conn.execute('SELECT * FROM sources ORDER BY id')]
        for source in sources:
            if bulk.file_digest(source['path'])!=source['sha256']: raise ValidationError('Archived source hash changed')
        # Freeze the full source universe before producing the first candidate
        # packet. Later variants cannot invalidate an already reviewed packet.
        conn.execute('INSERT OR IGNORE INTO metadata VALUES(?,?)',('sealed_at',utcnow()))
        conn.commit()
        snapshot=bulk.digest({'engine':engine_hash(),'sources':sources,'counts':counts(conn),'batch_size':batch_size})
        checkpoint={'snapshot_sha256':snapshot,'after_key':'','batches':[],'complete':False}
        if output.exists() and any(output.iterdir()):
            if not resume or not (output/'checkpoint.json').is_file(): raise ValidationError('Use an empty output or --resume')
            checkpoint=json.loads((output/'checkpoint.json').read_text(encoding='utf-8'))
            if checkpoint['snapshot_sha256']!=snapshot: raise ValidationError('Stage changed after preparation; use a new output')
            for index,batch in enumerate(checkpoint['batches']):
                if batch['directory']!=f'batch-{index:06}': raise ValidationError('Invalid checkpoint batch path')
                for name,digest in batch['files'].items():
                    if name not in {'accepted.json','quarantine.jsonl','report.json','approval.template.json'} or bulk.file_digest(output/batch['directory']/name)!=digest:
                        raise ValidationError('Prepared batch file changed after checkpoint')
        output.mkdir(parents=True,exist_ok=True)
        bulk.atomic_json(output/'checkpoint.json',checkpoint)
        for _ in range(max_batches):
            groups=list(conn.execute('SELECT group_key,count(*) AS n FROM entries WHERE group_key>? GROUP BY group_key ORDER BY group_key LIMIT ?',
                                     (checkpoint['after_key'],batch_size)))
            if not groups: checkpoint['complete']=True;break
            accepted=[];quarantine=[];raw_count=0
            for group in groups:
                if group['n']>10000: raise ValidationError('An identity has over 10000 variants; review this anomaly separately')
                entries=list(conn.execute('SELECT * FROM entries WHERE group_key=? ORDER BY seq',(group['group_key'],)))
                record,rejected=reconcile(entries[0]['media_id'],entries)
                if record: accepted.append(record)
                else: quarantine.append(rejected)
                raw_count+=len(entries)
            target=output/f'batch-{len(checkpoint["batches"]):06}'
            target.mkdir(exist_ok=True)
            bulk.atomic_json(target/'accepted.json',accepted)
            temp=target/'quarantine.jsonl.tmp'
            with temp.open('w',encoding='utf-8',newline='\n') as stream:
                for row in quarantine: stream.write(json.dumps(row,ensure_ascii=False)+'\n')
            os.replace(temp,target/'quarantine.jsonl')
            accepted_hash=bulk.file_digest(target/'accepted.json')
            provenance=[]
            for source in sources:
                provenance.append({'name':source['name'],'sha256':source['sha256'],'bytes':source['bytes']})
            report={'adapter':'scale_ingest','version':VERSION,'adapter_version':bulk.VERSION,'mode':'dry_run',
                    'created_at':utcnow(),'database_modified':False,'production_database_modified':False,'network_requests':0,
                    'accepted_sha256':accepted_hash,'source_records':raw_count,'accepted_candidates':len(accepted),
                    'quarantined':len(quarantine),'snapshot_sha256':snapshot,'engine_sha256':engine_hash(),
                    'source_files':provenance,'candidate_counts':{key:dict(Counter(r[key] for r in accepted)) for key in ('platform','language','language_status','category_slug','verification_scope')}}
            bulk.atomic_json(target/'report.json',report)
            bulk.atomic_json(target/'approval.template.json',{'accepted_sha256':accepted_hash,'approved_ids':[],
                'reviewer':'','reason':'','note':'Candidates only. Review exact IDs; existing bulk apply requires explicit authorization.'})
            names=('accepted.json','quarantine.jsonl','report.json','approval.template.json')
            checkpoint['batches'].append({'directory':target.name,'files':{name:bulk.file_digest(target/name) for name in names},
                                         'accepted_candidates':len(accepted),'quarantined':len(quarantine),'source_records':raw_count})
            checkpoint['after_key']=groups[-1]['group_key']
            checkpoint['complete']=not bool(conn.execute('SELECT 1 FROM entries WHERE group_key>? LIMIT 1',(checkpoint['after_key'],)).fetchone())
            bulk.atomic_json(output/'checkpoint.json',checkpoint)
            if checkpoint['complete']:break
        bulk.atomic_json(output/'checkpoint.json',checkpoint)
        summary={'tool':'scale_ingest','version':VERSION,'mode':'dry_run','created_at':utcnow(),
                 'snapshot_sha256':snapshot,'complete':checkpoint['complete'],'batches':len(checkpoint['batches']),
                 **{key:sum(b[key] for b in checkpoint['batches']) for key in ('source_records','accepted_candidates','quarantined')},
                 'database_modified':False,'network_requests':0,'approval_required_per_batch':True}
        if summary['complete'] and summary['source_records']!=counts(conn)['source_records']:
            raise ValidationError('Completed preparation does not cover every staged record')
        bulk.atomic_json(output/'report.json',summary)
        return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    ingest=sub.add_parser('stage');ingest.add_argument('inputs',nargs='+',type=Path)
    ingest.add_argument('--stage',required=True,type=Path);ingest.add_argument('--provider',choices=bulk.PROVIDERS,default='auto')
    ingest.add_argument('--max-records',type=int,default=25000);ingest.add_argument('--commit-every',type=int,default=500)
    ingest.add_argument('--resume',action='store_true')
    prepared=sub.add_parser('prepare');prepared.add_argument('--stage',required=True,type=Path)
    prepared.add_argument('--output',required=True,type=Path);prepared.add_argument('--batch-size',type=int,default=1000)
    prepared.add_argument('--max-batches',type=int,default=10);prepared.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    try:
        if args.command=='stage': result=stage(args.inputs,args.stage,provider=args.provider,max_records=args.max_records,commit_every=args.commit_every,resume=args.resume)
        else:result=prepare(args.stage,args.output,batch_size=args.batch_size,max_batches=args.max_batches,resume=args.resume)
        print(json.dumps(result,ensure_ascii=True))
    except (ValidationError,OSError,sqlite3.Error) as error:
        parser.exit(2,f'SCALE_INGEST: {type(error).__name__}: {str(error).encode("ascii",errors="backslashreplace").decode()}\n')


if __name__=='__main__':main()
