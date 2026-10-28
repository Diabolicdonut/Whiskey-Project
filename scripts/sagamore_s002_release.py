#!/usr/bin/env python3
"""Sagamore S002 three-expression release; no North American controller mutation.

Gate design: preflight -> publish (local working tree) -> full static and
Chromium -> finalize only on pass -> atomic GitHub commit in workflow.
"""
from __future__ import annotations
import datetime
import json
import pathlib
import sys
from collections import Counter

ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import north_american_build as builder
import na_037_release
DATA=ROOT/'sagamore-expansion-data.json'
LEDGER=ROOT/'sagamore-expression-ledger.json'
ROADMAP=ROOT/'DEVELOPMENT-ROADMAP.md'
PROGRESS=ROOT/'site-progress.json'
AUTHORED=ROOT/'research/sagamore-s002-authored.json'
IDS=['sagamore-bib-7-year-2024','sagamore-bib-8-year-2026','sagamore-rye-9-year-2024']
DATE='2026-10-27'

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def require(cond,desc):
    if not cond:raise ValueError(desc)

def entries():
    lg=read(LEDGER)
    return lg,{r['id']:r for r in lg['entries']}

def preflight():
    c=read(ROOT/'north-american-expansion-checkpoint.json')
    require(c['checkpoint']==37 and c['status']=='complete' and c['dossier_count']==1050,
            'Must recover accepted NA-037 before Sagamore phase')
    lg,by=entries()
    require(lg['counts']=={'existing_published':15,'pending_research':21,
             'excluded_pending_liquid_distinction':3,'total':39},'S001 ledger changed')
    docs=read(AUTHORED)
    require([a['id'] for a in docs]==IDS,'Incorrect S002 author list/order')
    require(not DATA.exists(),'S002 Sagamore data already exists: never replay')
    for a in docs:
        e=by[a['id']]
        require(e['decision']=='pending_research' and not (ROOT/e['filename']).exists(),
                'Already published or changed: '+a['id'])
        require(a['category']=='Rye' and a['age']>=7 and a['quality'] is not None
               and len(a['reviews'])>0 and len(a['bands'])==5
               and len(a['comparables'])>=2 and len(a['serving'])>=4
               and any(s['name']=='Manhattan' for s in a['serving']),
                'Incomplete authored dossier '+a['id'])
        require(sum(bool(b.get('current_band')) for b in a['bands'])==1,
                'Expected exactly one current price band: '+a['id'])
    print(json.dumps({'phase':'preflight','ids':IDS,'protected_articles':1050}))

def publish():
    preflight()
    lg,by=entries(); new=[]
    for a in read(AUTHORED):
        entry=by[a['id']]
        e={'id':entry['id'],'filename':entry['filename'],
            'canonical_expression_name':a['identity'].split(',')[0] if False else next(
                {'sagamore-bib-7-year-2024':'Sagamore Bottled in Bond Straight Rye 7 Year (2024)',
                 'sagamore-bib-8-year-2026':'Sagamore Bottled in Bond Straight Rye 8 Year (2026)',
                 'sagamore-rye-9-year-2024':'Sagamore 9 Year Straight Rye Reserve Batch 1A (2024)'}[a['id']] for _ in [0]),
            'brand_family':'Sagamore Spirit','producer':a['producer'],
            'whisky_category':'Rye','proof':a['proof'],'age_statement_years':a['age'],
            'grain_information':a['grain'],'finishing_information':a['finish'],
            'status':'historical' if a['id']=='sagamore-rye-9-year-2024' else 'current'}
        m=builder.make_metadata(e,a)
        m['assessment_checkpoint']='S002'
        m['canonical_format_version']='sagamore-expansion-v1'
        m['image_limitation']=a['image_limitation']
        (ROOT/e['filename']).write_text(builder.render(m,None),encoding='utf-8')
        new.append(m)
    # Reuses the canonical NA index integrator but does not mutate its
    # 225-record metadata array, NA-037 controller, or 825 baseline dossiers.
    builder.integrate(new)
    na_037_release.normalize()
    write(DATA,new)
    print(json.dumps({'phase':'publication_staged_locally','new_pages':[x['filename'] for x in new],
                      'total_preview':1053}))

def finalize():
    lg,by=entries();c=read(ROOT/'north-american-expansion-checkpoint.json')
    require(c['checkpoint']==37 and c['dossier_count']==1050 and c['status']=='complete',
            'NA-037 controller unexpectedly altered')
    batch=read(DATA);require(len(batch)==3 and [m['slug'] for m in batch]==IDS,
                            'S002 metadata batch mismatch')
    static=read(ROOT.parent/'expansion-research'/'static-report.json')
    runtime=read(ROOT.parent/'expansion-research'/'runtime-output'/'runtime-report.json')
    require(static['status']=='passed' and static['dossiers']==1053
            and static['full_repository_validation'] and static['failure_count']==0,
            'Full 1053-page structural acceptance missing')
    require(runtime['status']=='passed' and not runtime['failures']
            and runtime['responsive_cases']==687 and runtime['index_rendered']
            and not runtime['page_errors'] and not runtime['network_errors'],
            'Focused Chromium 687 responsive views did not pass')
    for i in IDS:
        require(by[i]['decision']=='pending_research','S002 candidate already decided '+i)
        by[i]['decision']='accepted_published'
        by[i]['accepted_date']=DATE
        by[i]['filename']=i+'.html'
        by[i]['validation']='Full static 1053 dossiers; Chromium 687 responsive views; zero failures'
    lg['counts']={'existing_published':15,'accepted_published':3,'pending_research':18,
                  'excluded_pending_liquid_distinction':3,'total':39}
    lg['status']='implementation_in_progress'
    lg['updated_at']=DATE
    lg['last_accepted_checkpoint']='S002'
    lg['next_action']='Research next priority Sagamore gaps from deterministic ledger; prefer the 6-year BiB 2023, 8-year rye reserve, current Small Batch and Double Oak. Do not replay S002 or regenerate preserved articles.'
    write(LEDGER,lg)
    md=ROADMAP.read_text(encoding='utf-8')
    require('**Roadmap revision:** R004' in md,'Expected R004 roadmap')
    md=md.replace('**Roadmap revision:** R004','**Roadmap revision:** R005',1)
    h='## 9. Revision history\n\n'
    require(h in md,'Roadmap changelog missing')
    md=md.replace(h,h+'- **2026-10-27 — R005:** Sagamore S002 published three independently researched editions (2024 7-year BiB, 2026 8-year BiB, 2024 9-year Rye), reaching **1,053 published dossiers**. Preserved accepted NA-037 and initial 825, full static and 390/768/1440 Chromium acceptance zero failures; Sagamore 21/39 dispositions (18 pending). The whole Sagamore family gate stays partial and overall strict roadmap completion **41%**.\n',1)
    needle='**S001 active-phase display:**'
    if needle not in md:raise ValueError('Roadmap S001 phase section missing')
    md=md.replace(needle,'**S002 accepted publication (2026-10-27):** Three source-matched Sagamore dossiers added without altering the previously accepted 1,050; 15 preexisting and 3 newly published (18 total Sagamore articles), 3 exclusions/holds and 18 pending. Active disposition display **21/39**; no entire Sagamore gate acceptance yet. Validation: full structural sweep of 1,053 dossiers and focused Chromium 687 page/viewport renders.\n\n'+needle,1)
    ROADMAP.write_text(md,encoding='utf-8')
    p=read(PROGRESS)
    require(p['revision']=='R004','Progress revision changed')
    p['revision']='R005';p['asOf']=DATE
    p['progress']['completed']=21;p['progress']['total']=39
    p['progress']['source']['fields']=['existing_published','accepted_published',
                                      'excluded_pending_liquid_distinction']
    p['progress']['basis']='15 preexisting published Sagamore dossiers plus 3 new accepted published expressions and 3 exclusion/holds; 18 further candidates pending research.'
    p['progress']['note']='21/39 discovery decisions resolved, including only 3 newly published dossiers; strict full-vision gate acceptance remains 41/100.'
    p['roadmap']['note']='R005: 1,053 published dossiers and accepted S002 three-release Sagamore batch. Sagamore full-family gate remains partial; strict overall stays 41%.'
    write(PROGRESS,p)
    print(json.dumps({'checkpoint':'S002','published_dossiers':1053,
                      'sagamore_published':18,'sagamore_decisions':'21/39',
                      'roadmap_revision':'R005','accepted_points':41}))

if __name__=='__main__':
    f={'preflight':preflight,'publish':publish,'finalize':finalize}
    if len(sys.argv)!=2 or sys.argv[1] not in f:sys.exit('preflight|publish|finalize')
    f[sys.argv[1]]()
