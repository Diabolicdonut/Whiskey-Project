#!/usr/bin/env python3
"""Guarded Sagamore S003: 2023 bonded 6Y, 2023 reserve 8Y and current Small Batch.

preflight -> stage locally -> full static + Chromium -> finalize -> commit by CI.
Never alter or regenerate any accepted 1,053 dossiers.
"""
from __future__ import annotations
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import north_american_build as builder
import na_037_release

DATA=ROOT/'sagamore-expansion-data.json'
LEDGER=ROOT/'sagamore-expression-ledger.json'
ROADMAP=ROOT/'DEVELOPMENT-ROADMAP.md'
PROGRESS=ROOT/'site-progress.json'
AUTHORED=ROOT/'research/sagamore-s003-authored.json'
IDS=['sagamore-bib-6-year-2023','sagamore-rye-8-year','sagamore-small-batch-current']
TITLES={
 'sagamore-bib-6-year-2023':'Sagamore Bottled in Bond Straight Rye 6 Year (2023)',
 'sagamore-rye-8-year':'Sagamore Reserve Series 8 Year Rye (2023)',
 'sagamore-small-batch-current':'Sagamore Small Batch Rye (current Maryland-made core)',
}
DATE='2026-10-28'

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def req(check,msg):
    if not check:raise ValueError(msg)

def preflight():
    c=read(ROOT/'north-american-expansion-checkpoint.json')
    req(c['checkpoint']==37 and c['status']=='complete' and c['dossier_count']==1050,
        'NA-037 authority must remain accepted and byte-preserved')
    p=read(PROGRESS)
    req(p['revision']=='R005','Expected accepted roadmap R005')
    l=read(LEDGER)
    expected={'existing_published':15,'accepted_published':3,'pending_research':18,
              'excluded_pending_liquid_distinction':3,'total':39}
    req(l['counts']==expected and l['last_accepted_checkpoint']=='S002',
        'S002 counts changed; do not replay or overwrite newer work')
    already=read(DATA)
    req(len(already)==3 and [x['slug'] for x in already]==
        ['sagamore-bib-7-year-2024','sagamore-bib-8-year-2026','sagamore-rye-9-year-2024'],
        'Preserve existing three accepted Sagamore metadata entries')
    a=read(AUTHORED)
    req([x['id'] for x in a]==IDS,'Authored source order differs from S003 work plan')
    by={r['id']:r for r in l['entries']}
    for x in a:
        key=x['id'];e=by[key]
        req(e['decision']=='pending_research' and not (ROOT/e['filename']).exists(),
            'Candidate already published or not pending: '+key)
        req(x['category']=='Rye' and len(x['bands'])==5 and
            sum(bool(b.get('current_band')) for b in x['bands'])==1 and
            len(x['comparables'])>=2 and len(x['serving'])>=4 and len(x['sources'])>=2,
            'Incomplete canonical input for '+key)
        req(x['value'] is None or (x['quality'] is not None and bool(x['reviews'])),
            'Cannot score Value without exact matched tasting evidence')
        req(x['quality'] is None or bool(x['reviews']),
            'Quality requires independent matched critical source')
    print(json.dumps({'stage':'S003 preflight','protected_published':1053,'candidate_ids':IDS}))

def stage():
    preflight()
    l=read(LEDGER);by={e['id']:e for e in l['entries']}
    new=[]
    for a in read(AUTHORED):
        e=by[a['id']]
        e_for_builder={
            'id':e['id'],'filename':e['filename'],
            'canonical_expression_name':TITLES[a['id']],
            'brand_family':'Sagamore Spirit','producer':a['producer'],
            'whisky_category':'Rye','proof':a['proof'],
            'age_statement_years':a['age'],'grain_information':a['grain'],
            'finishing_information':a['finish'],
            'status':'current' if a['id']=='sagamore-small-batch-current' else 'historical'
        }
        m=builder.make_metadata(e_for_builder,a)
        m['assessment_checkpoint']='S003'
        m['canonical_format_version']='sagamore-expansion-v1'
        m['image_limitation']=a['image_limitation']
        html=builder.render(m,None)
        canada=('For the shared historical context, read <a href="north-american-history.md">'
                'Canadian whisky, cross-border trade and the American market</a>. '
                'The release chronology above distinguishes the current bottle from its brand’s earlier history.')
        html=html.replace(canada,'')
        html=html.replace('Old Oak Omnibus · North American Expansion ·',
                          'Old Oak Omnibus · Sagamore Spirit Expansion ·')
        (ROOT/e['filename']).write_text(html,encoding='utf-8')
        new.append(m)
    builder.integrate(new)
    na_037_release.normalize()
    existing=read(DATA)
    write(DATA,existing+new)
    print(json.dumps({'stage':'S003 staged locally','new':IDS,'preview_catalogue':1056}))

def finalize():
    l=read(LEDGER);c=read(ROOT/'north-american-expansion-checkpoint.json')
    req(c['checkpoint']==37 and c['status']=='complete' and c['dossier_count']==1050,
        'North American authoritative controller was modified')
    batch=read(DATA)
    req(len(batch)==6 and [x['slug'] for x in batch[-3:]]==IDS,'S003 metadata mismatch')
    static=read(ROOT.parent/'expansion-research'/'static-report.json')
    runtime=read(ROOT.parent/'expansion-research'/'runtime-output'/'runtime-report.json')
    req(static['status']=='passed' and static['failure_count']==0 and
        static['full_repository_validation'] and static['dossiers']==1056 and
        static['original_dossier_hashes_verified']==825 and
        static['original_index_rows_byte_preserved']==825,
        'Full static + original 825 baseline validation did not pass')
    req(runtime['status']=='passed' and not runtime['failures'] and
        runtime['responsive_cases']==696 and runtime['index_rendered'] and
        not runtime['page_errors'] and not runtime['network_errors'] and
        all(x['status']=='passed' for x in runtime['functional_cases']),
        'Chromium 390/768/1440 release acceptance incomplete or failed')
    by={e['id']:e for e in l['entries']}
    for key in IDS:
        req(by[key]['decision']=='pending_research','Unexpected double-accept: '+key)
        by[key]['decision']='accepted_published'
        by[key]['accepted_date']=DATE
        by[key]['validation']='Full static 1056 dossiers; Chromium 696 responsive views; zero failures'
    l['counts']={'existing_published':15,'accepted_published':6,'pending_research':15,
                 'excluded_pending_liquid_distinction':3,'total':39}
    l['updated_at']=DATE;l['last_accepted_checkpoint']='S003'
    l['next_action']=('Proceed with S004 in bounded independently sourced expressions; '
                      'prioritize current Double Oak 96.6, 2024/2025 Manhattan finish and '
                      'named cask-finish releases. Preserve 15 baseline and six accepted Sagamore files. '
                      'Do not relabel 2023 six-year BiB as independently scored without matched evidence.')
    write(LEDGER,l)

    md=ROADMAP.read_text(encoding='utf-8')
    req('**Roadmap revision:** R005' in md,'R005 roadmap required')
    md=md.replace('**Roadmap revision:** R005','**Roadmap revision:** R006',1)
    # Date and revision must advance together; strip Markdown hard-break spaces on changed line.
    req('**Updated:** 2026-10-27' in md,'Expected roadmap review date 2026-10-27')
    md=md.replace('**Updated:** 2026-10-27  ','**Updated:** 2026-10-28',1)
    h='## 9. Revision history\n\n'
    req(h in md,'Roadmap revision history missing')
    md=md.replace(h,h+
       '- **2026-10-28 — R006:** Sagamore S003 accepted three further dossiers (2023 bonded 6-year unscored, 2023 Reserve 8-year, current Maryland Small Batch) without changing 825 baseline or NA-037. Now **1,056 dossiers**, **24/39** Sagamore dispositions (15 pending), full static plus Chromium 696 responsive views zero failures; Sagamore gate remains partial and strict overall **41%**.\n',1)
    key='**S002 accepted publication (2026-10-27):**'
    req(key in md,'S002 accepted history missing')
    md=md.replace(key,
       '**S003 accepted publication (2026-10-28):** Three additional Sagamore expressions added: '
       'a conservatively unscored 2023 six-year bonded edition, the independently reviewed '
       '2023 111.4-proof Reserve 8-year, and the ongoing 93-proof Maryland Small Batch core. '
       'This brings the catalogue to **1,056** and Sagamore to **21 published** '
       '(15 existing + 6 new), with **24/39** discovery dispositions resolved '
       'and 15 still pending. **41%** overall strict accepted gates until the whole Sagamore '
       'gate is validated complete.\n\n'+key,1)
    ROADMAP.write_text(md,encoding='utf-8')
    p=read(PROGRESS)
    req(p['revision']=='R005','Expected current R005 progress projection')
    p['revision']='R006';p['asOf']=DATE
    p['progress']['completed']=24;p['progress']['total']=39
    p['progress']['basis']='15 existing Sagamore dossiers + 6 accepted new editions + 3 exclusion/hold decisions; 15 pending.'
    p['progress']['note']='Sagamore family disposition count, not percent of full-vision development. 21 Sagamore dossiers published.'
    p['roadmap']['note']='R006: Sagamore S003 accepted, 1,056 total dossiers; 24/39 family dispositions; overall 41% until the full family gate is accepted.'
    write(PROGRESS,p)
    agents=ROOT/'AGENTS.md'
    rules=agents.read_text(encoding='utf-8')
    rules=rules.replace('DEVELOPMENT-ROADMAP.md\x60 R005','DEVELOPMENT-ROADMAP.md\x60 R006',1)
    rules=rules.replace('First bounded target: 7-year BiB 2024, 8-year BiB 2026, and 9-year Reserve 2024; verify exact sources, independent tasting scope, time/currency/size of prices and calibrated scores.',
      'Accepted S002 and S003 cover the 2024 7-year bonded, 2026 8-year bonded, 2024 9-year reserve, 2023 6-year bonded (unscored), 2023 8-year reserve and current standard Small Batch. Never replay these.')
    rules=rules.replace('The accepted project scope remains governed by \x60DEVELOPMENT-ROADMAP.md\x60 R005',
                        'The accepted project scope remains governed by \x60DEVELOPMENT-ROADMAP.md\x60 R006')
    agents.write_text(rules,encoding='utf-8')
    print(json.dumps({'checkpoint':'S003','dossiers':1056,'sagamore_published':21,
                      'disposition':'24/39','roadmap':'R006','accepted_roadmap_points':41}))

if __name__=='__main__':
    options={'preflight':preflight,'stage':stage,'finalize':finalize}
    if len(sys.argv)!=2 or sys.argv[1] not in options:sys.exit('Usage: preflight|stage|finalize')
    options[sys.argv[1]]()
