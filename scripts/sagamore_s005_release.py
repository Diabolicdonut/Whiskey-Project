#!/usr/bin/env python3
"""Guarded Sagamore S005: 3 published pages only after full static/Chromium validation."""
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
AUTHORED=ROOT/'research/sagamore-s005-authored.json'
IDS=['sagamore-rum-cask-finish','sagamore-rye-ale-finish','sagamore-vintners-finish']
TITLES={
 'sagamore-rum-cask-finish':'Sagamore Rum Cask Finish Rye (2022 Reserve Series)',
 'sagamore-rye-ale-finish':"Sagamore Brewer's Select Rye Ale Finish (2020)",
 'sagamore-vintners-finish':"Sagamore Vintner's Finish Rye (2018)",
}
DATE='2026-10-28'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def req(ok,msg):
    if not ok:raise ValueError(msg)
def preflight():
    c=read(ROOT/'north-american-expansion-checkpoint.json')
    req(c['checkpoint']==37 and c['status']=='complete' and c['dossier_count']==1050,'NA-037 authority changed')
    req(read(PROGRESS)['revision']=='R007','Only S004 R007 accepted state may release S005')
    l=read(LEDGER)
    req(l['counts']=={'existing_published':15,'accepted_published':9,'pending_research':12,'excluded_pending_liquid_distinction':3,'total':39} and l['last_accepted_checkpoint']=='S004','S004 disposition changed')
    existing=read(DATA)
    req(len(existing)==9 and [x['slug'] for x in existing[-3:]]==['sagamore-double-oak-current','sagamore-manhattan-finish-2024','sagamore-manhattan-finish-2025'],'S004 metadata changed')
    a=read(AUTHORED);req([x['id'] for x in a]==IDS,'Wrong source order')
    by={e['id']:e for e in l['entries']}
    for x in a:
        e=by[x['id']]
        req(e['decision']=='pending_research' and not (ROOT/e['filename']).exists(),'Already accepted or existing candidate: '+x['id'])
        req(x['category']=='Rye' and len(x['bands'])==5 and sum(bool(z.get('current_band')) for z in x['bands'])==1 and len(x['comparables'])>=2 and len(x['serving'])>=4 and len(x['sources'])>=2,'Incomplete dossier '+x['id'])
        req(x['quality'] is None or bool(x['reviews']),'No score without matched reviewers')
        req(x['value'] is None or (x['quality'] is not None and x.get('pricing')),'No Value without Quality and price')
    print(json.dumps({'stage':'S005 preflight','preserved':1059,'ids':IDS}))
def stage():
    preflight();by={e['id']:e for e in read(LEDGER)['entries']};new=[]
    for a in read(AUTHORED):
        e=by[a['id']]
        b={'id':e['id'],'filename':e['filename'],'canonical_expression_name':TITLES[a['id']],
            'brand_family':'Sagamore Spirit','producer':a['producer'],'whisky_category':'Rye','proof':a['proof'],
            'age_statement_years':a['age'],'grain_information':a['grain'],
            'finishing_information':a['finish'],
            'status':'historical'}
        m=builder.make_metadata(b,a)
        m['assessment_checkpoint']='S005';m['canonical_format_version']='sagamore-expansion-v1'
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
    req(len(read(DATA))==12,'Expected exactly twelve accepted Sagamore metadata rows')
    print(json.dumps({'stage':'S005 staged','catalogue':1062,'ids':IDS}))
def finalize():
    c=read(ROOT/'north-american-expansion-checkpoint.json')
    req(c['checkpoint']==37 and c['status']=='complete' and c['dossier_count']==1050,'NA controller protection failed')
    req(len(read(DATA))==12 and [x['slug'] for x in read(DATA)[-3:]]==IDS,'S005 data unexpected')
    st=read(ROOT.parent/'expansion-research'/'static-report.json')
    rt=read(ROOT.parent/'expansion-research'/'runtime-output'/'runtime-report.json')
    req(st['status']=='passed' and st['failure_count']==0 and st['full_repository_validation'] and st['dossiers']==1062 and st['original_dossier_hashes_verified']==825 and st['original_index_rows_byte_preserved']==825,'Full static and original 825 baseline not validated')
    req(rt['status']=='passed' and not rt['failures'] and rt['responsive_cases']==714 and rt['index_rendered'] and not rt['page_errors'] and not rt['network_errors'] and all(x['status']=='passed' for x in rt['functional_cases']),'714 responsive browser cases not accepted')
    l=read(LEDGER);by={e['id']:e for e in l['entries']}
    for key in IDS:
        req(by[key]['decision']=='pending_research','Already accepted '+key)
        by[key]['decision']='accepted_published';by[key]['accepted_date']=DATE
        by[key]['validation']='Full static 1062 dossiers; Chromium 714 responsive views; zero failures'
    l['counts']={'existing_published':15,'accepted_published':12,'pending_research':9,'excluded_pending_liquid_distinction':3,'total':39}
    l['updated_at']=DATE;l['last_accepted_checkpoint']='S005'
    l['next_action']=('S006: research remaining Barleywine, standard Ale Cask and Moscatel finished releases; preserve 15 original and 12 newly accepted Sagamore dossiers. Do not conflate 90-proof Rye Ale with 98-proof Ale Cask or invent historical price and review evidence.')
    write(LEDGER,l)
    md=ROADMAP.read_text(encoding='utf-8')
    req('**Roadmap revision:** R007' in md and '**Updated:** 2026-10-28' in md,'Expected R007 authority')
    md=md.replace('**Roadmap revision:** R007','**Roadmap revision:** R008',1)
    anchor='## 9. Revision history\n\n';req(anchor in md,'Revision history missing')
    md=md.replace(anchor,anchor+'- **2026-10-28 — R008:** Sagamore S005 accepted individually sourced 2022 Rum Cask, 2020 Sierra Nevada Rye Ale and 2018 Vintner’s Finish dossiers. The Vintner’s exact price is not verified and its Value and Overall remain N/A. Full 1,062 dossier static sweep and 714 responsive Chromium cases passed, 825 originals unchanged. **27 Sagamore published**, **30/39** dispositions (9 pending), roadmap strict **41%**.\n',1)
    previous='**S004 accepted publication (2026-10-28):**'
    req(previous in md,'S004 history missing')
    md=md.replace(previous,'**S005 accepted publication (2026-10-28):** Three historical cask-finish dossiers with authentic release differences: 2022 two-region rum instead of 2019 single-rum; 2020 Sierra Nevada 90-proof Rye Ale instead of 98-proof Ale Cask; 2018 98.4-proof Vintner’s with no unsupported Value score. Validated catalogue **1,062**, Sagamore **30/39** resolved, nine pending; NA-037 and all 825 originals preserved. Strict roadmap remains **41/100** until whole family gate acceptance.\n\n'+previous,1)
    ROADMAP.write_text(md,encoding='utf-8')
    p=read(PROGRESS);req(p['revision']=='R007','R007 progress needed')
    p['revision']='R008';p['asOf']=DATE;p['progress']['completed']=30;p['progress']['total']=39
    p['progress']['basis']='15 existing Sagamore dossiers + 12 accepted new expressions + 3 excluded or held; 9 pending.'
    p['progress']['note']='Family disposition progress, not full roadmap percentage. 27 Sagamore dossiers published.'
    p['roadmap']['note']='R008: 1,062 dossiers and 30/39 Sagamore dispositions; whole family remains partial and 41% accepted full-roadmap weight.'
    write(PROGRESS,p)
    agents=ROOT/'AGENTS.md';t=agents.read_text(encoding='utf-8')
    t=t.replace('R007, not the historical','R008, not the historical')
    t=t.replace('S004 cover the 2024','S004 cover the 2024')
    t=t.replace('Keep the strict roadmap percentage at 41 until a whole gate is accepted.','S005 accepted three historical finishes (2022 Rum, 2020 Rye Ale, 2018 Vintner); S006 is next. Keep the strict roadmap percentage at 41 until a whole gate is accepted.')
    agents.write_text(t,encoding='utf-8')
    print(json.dumps({'checkpoint':'S005','catalogue':1062,'sagamore_published':27,'resolved':'30/39','roadmap':'R008','overall_percent':41}))
if __name__=='__main__':
    commands={'preflight':preflight,'stage':stage,'finalize':finalize}
    if len(sys.argv)!=2 or sys.argv[1] not in commands:sys.exit('Usage: preflight|stage|finalize')
    commands[sys.argv[1]]()
