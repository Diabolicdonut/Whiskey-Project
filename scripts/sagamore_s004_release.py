#!/usr/bin/env python3
"""Guarded Sagamore S004: 3 published pages only after full static/Chromium validation."""
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
AUTHORED=ROOT/'research/sagamore-s004-authored.json'
IDS=['sagamore-double-oak-current','sagamore-manhattan-finish-2024','sagamore-manhattan-finish-2025']
TITLES={
 'sagamore-double-oak-current':'Sagamore Double Oak Rye (current 96.6 proof)',
 'sagamore-manhattan-finish-2024':'Sagamore Manhattan Finish Rye (2024 second release)',
 'sagamore-manhattan-finish-2025':'Sagamore Manhattan Finish Rye (2025 30-month release)',
}
DATE='2026-10-28'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def req(ok,msg):
    if not ok:raise ValueError(msg)
def preflight():
    c=read(ROOT/'north-american-expansion-checkpoint.json')
    req(c['checkpoint']==37 and c['status']=='complete' and c['dossier_count']==1050,'NA-037 authority changed')
    req(read(PROGRESS)['revision']=='R006','Only S003 R006 accepted state may release S004')
    l=read(LEDGER)
    req(l['counts']=={'existing_published':15,'accepted_published':6,'pending_research':15,'excluded_pending_liquid_distinction':3,'total':39} and l['last_accepted_checkpoint']=='S003','S003 disposition changed')
    existing=read(DATA)
    req(len(existing)==6 and [x['slug'] for x in existing[-3:]]==['sagamore-bib-6-year-2023','sagamore-rye-8-year','sagamore-small-batch-current'],'S003 metadata changed')
    a=read(AUTHORED);req([x['id'] for x in a]==IDS,'Wrong source order')
    by={e['id']:e for e in l['entries']}
    for x in a:
        e=by[x['id']]
        req(e['decision']=='pending_research' and not (ROOT/e['filename']).exists(),'Already accepted or existing candidate: '+x['id'])
        req(x['category']=='Rye' and len(x['bands'])==5 and sum(bool(z.get('current_band')) for z in x['bands'])==1 and len(x['comparables'])>=2 and len(x['serving'])>=4 and len(x['sources'])>=2,'Incomplete dossier '+x['id'])
        req(x['quality'] is None or bool(x['reviews']),'No score without matched reviewers')
        req(x['value'] is None or (x['quality'] is not None and x.get('pricing')),'No Value without Quality and price')
    print(json.dumps({'stage':'S004 preflight','preserved':1056,'ids':IDS}))
def stage():
    preflight();by={e['id']:e for e in read(LEDGER)['entries']};new=[]
    for a in read(AUTHORED):
        e=by[a['id']]
        b={'id':e['id'],'filename':e['filename'],'canonical_expression_name':TITLES[a['id']],
            'brand_family':'Sagamore Spirit','producer':a['producer'],'whisky_category':'Rye','proof':a['proof'],
            'age_statement_years':a['age'],'grain_information':a['grain'],
            'finishing_information':a['finish'],
            'status':'current' if a['id']=='sagamore-double-oak-current' else 'historical'}
        m=builder.make_metadata(b,a)
        m['assessment_checkpoint']='S004';m['canonical_format_version']='sagamore-expansion-v1'
        m['image_limitation']=a['image_limitation']
        page=builder.render(m,None)
        canada=('For the shared historical context, read <a href="north-american-history.md">'
                'Canadian whisky, cross-border trade and the American market</a>. '
                'The release chronology above distinguishes the current bottle from its brand’s earlier history.')
        page=page.replace(canada,'').replace('Old Oak Omnibus · North American Expansion ·','Old Oak Omnibus · Sagamore Spirit Expansion ·')
        (ROOT/e['filename']).write_text(page,encoding='utf-8')
        new.append(m)
    builder.integrate(new);na_037_release.normalize()
    write(DATA,read(DATA)+new)
    req(len(read(DATA))==9,'Expected exactly nine published Sagamore metadata rows')
    print(json.dumps({'stage':'S004 staged','catalogue':1059,'ids':IDS}))
def finalize():
    c=read(ROOT/'north-american-expansion-checkpoint.json')
    req(c['checkpoint']==37 and c['status']=='complete' and c['dossier_count']==1050,'NA controller protection failed')
    req(len(read(DATA))==9 and [x['slug'] for x in read(DATA)[-3:]]==IDS,'S004 data unexpected')
    st=read(ROOT.parent/'expansion-research'/'static-report.json')
    rt=read(ROOT.parent/'expansion-research'/'runtime-output'/'runtime-report.json')
    req(st['status']=='passed' and st['failure_count']==0 and st['full_repository_validation'] and st['dossiers']==1059 and st['original_dossier_hashes_verified']==825 and st['original_index_rows_byte_preserved']==825,'Full static and original 825 baseline not validated')
    req(rt['status']=='passed' and not rt['failures'] and rt['responsive_cases']==705 and rt['index_rendered'] and not rt['page_errors'] and not rt['network_errors'] and all(x['status']=='passed' for x in rt['functional_cases']),'705 responsive browser cases not accepted')
    l=read(LEDGER);by={e['id']:e for e in l['entries']}
    for key in IDS:
        req(by[key]['decision']=='pending_research','Already accepted '+key)
        by[key]['decision']='accepted_published';by[key]['accepted_date']=DATE
        by[key]['validation']='Full static 1059 dossiers; Chromium 705 responsive views; zero failures'
    l['counts']={'existing_published':15,'accepted_published':9,'pending_research':12,'excluded_pending_liquid_distinction':3,'total':39}
    l['updated_at']=DATE;l['last_accepted_checkpoint']='S004'
    l['next_action']=('S005: verify Rum Cask, Barleywine, Ale, Rye Ale, Vintner and Moscatel finish identities with dated independent evidence; preserve original 15 and nine newly accepted Sagamore pages. The 2025 Manhattan remains unscored until edition-matched review is authenticated.')
    write(LEDGER,l)
    md=ROADMAP.read_text(encoding='utf-8')
    req('**Roadmap revision:** R006' in md and '**Updated:** 2026-10-28' in md,'Expected R006 authority')
    md=md.replace('**Roadmap revision:** R006','**Roadmap revision:** R007',1)
    anchor='## 9. Revision history\n\n';req(anchor in md,'Revision history missing')
    md=md.replace(anchor,anchor+'- **2026-10-28 — R007:** Sagamore S004 accepted current 96.6-proof Double Oak and distinct 2024 20-month and 2025 30-month Manhattan Finish dossiers. The latter is deliberately unscored pending matching independent criticism. Full static and 705 Chromium responsive cases passed; original 825 preserved. **1,059 dossiers**, **24 Sagamore published**, **27/39** dispositions (12 pending); strict vision completion **41%**, Sagamore gate partial.\n',1)
    previous='**S003 accepted publication (2026-10-28):**'
    req(previous in md,'S003 history missing')
    md=md.replace(previous,'**S004 accepted publication (2026-10-28):** Three canonical expression-specific articles; standard Double Oak is not Batch 9A, 2024 Manhattan is not 2025 Manhattan, and unsupported 2025 Quality/Value remain N/A. Catalogue **1,059** and Sagamore **27/39** resolved, 12 pending; NA-037 and 825 original dossiers preserved. Roadmap **41/100** until full Sagamore gate acceptance.\n\n'+previous,1)
    ROADMAP.write_text(md,encoding='utf-8')
    p=read(PROGRESS);req(p['revision']=='R006','R006 progress needed')
    p['revision']='R007';p['asOf']=DATE;p['progress']['completed']=27;p['progress']['total']=39
    p['progress']['basis']='15 existing Sagamore dossiers + 9 accepted new expressions + 3 excluded or held; 12 pending.'
    p['progress']['note']='Family disposition progress, not full roadmap percentage. 24 Sagamore dossiers published.'
    p['roadmap']['note']='R007: 1,059 dossiers and 27/39 Sagamore dispositions; whole family remains partial and 41% accepted full-roadmap weight.'
    write(PROGRESS,p)
    agents=ROOT/'AGENTS.md';t=agents.read_text(encoding='utf-8')
    t=t.replace('R006, not the historical','R007, not the historical')
    t=t.replace('S003 cover the 2024','S003 cover the 2024')
    t=t.replace('Keep the strict roadmap percentage at 41 until a whole gate is accepted.','S004 accepted three further editions (Double Oak core, 2024 and unscored 2025 Manhattan); S005 is next. Keep the strict roadmap percentage at 41 until a whole gate is accepted.')
    agents.write_text(t,encoding='utf-8')
    print(json.dumps({'checkpoint':'S004','catalogue':1059,'sagamore_published':24,'resolved':'27/39','roadmap':'R007','overall_percent':41}))
if __name__=='__main__':
    commands={'preflight':preflight,'stage':stage,'finalize':finalize}
    if len(sys.argv)!=2 or sys.argv[1] not in commands:sys.exit('Usage: preflight|stage|finalize')
    commands[sys.argv[1]]()
