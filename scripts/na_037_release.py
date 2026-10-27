#!/usr/bin/env python3
"""Controlled NA-037 completion helpers. Operates only on locally checked-out worktree.

This script does NOT publish; the gated release workflow checks and commits
only after static and Chromium verification succeed.
"""
from __future__ import annotations
import json, pathlib, re, sys
from html import unescape

ROOT=pathlib.Path(__file__).resolve().parent.parent
CONTROLLER=ROOT/'north-american-expansion-checkpoint.json'
LEDGER=ROOT/'north-american-expression-ledger.json'
PROGRESS=ROOT/'site-progress.json'
ROADMAP=ROOT/'DEVELOPMENT-ROADMAP.md'
INDEX=ROOT/'index.html'
IDS=[
 'two-brewers-yukon-single-malt-release-22',
 'two-brewers-yukon-single-malt-release-33',
 'two-brewers-yukon-single-malt-release-35',
 'windsor-canadian-original',
 'windsor-canadian-reserve',
 'alberta-premium-20-year-2019',
 'alberta-springs-10-year',
]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def assert_eq(actual,expected,label):
    if actual!=expected:raise ValueError(f'{label}: expected {expected!r}, got {actual!r}')

def preflight():
    c,l=read(CONTROLLER),read(LEDGER)
    assert_eq(c['checkpoint'],36,'checkpoint')
    assert_eq(c['status'],'implementation_in_progress','phase status')
    assert_eq(c['dossier_count'],1043,'previous dossier count')
    assert_eq(l['counts']['accepted'],218,'previous accepted count')
    assert_eq(l['counts']['pending'],7,'previous pending count')
    assert_eq(c['prepared_batch_037']['ids'],IDS,'prepared-batch deterministic order')
    authors=read(ROOT/'research/na-037-authored.json')
    assert_eq([a['id'] for a in authors],IDS,'exact author order')
    by={r['id']:r for r in l['entries']}
    for i in IDS:
        assert_eq(by[i]['implementation_status'],'pending_research',i)
        if (ROOT/by[i]['filename']).exists():raise ValueError('Already published: '+i)
    print(json.dumps({'phase':'preflight','checkpoint':36,'ready_records':7}))

def normalize():
    """Sort all category/family/basis/period/calibration option labels, All first.

    Do not touch the original 825 tr bytes or underlying filter values.
    """
    text=INDEX.read_text(encoding='utf-8')
    report={}
    for field in ('category','family','basis','period','calibration'):
        pat=re.compile(r'(<select\\b[^>]*\\bid="'+re.escape(field)+r'"[^>]*>)(.*?)(</select>)',re.S)
        match=pat.search(text)
        if not match:raise ValueError('Selector not found: '+field)
        body=match.group(2)
        found=list(re.finditer(r'<option\\b[^>]*value="([^"]*)"[^>]*>.*?</option>',body,re.S))
        if not found:raise ValueError('Options missing: '+field)
        values=[x.group(1) for x in found]
        if len(values)!=len(set(values)):raise ValueError('Duplicate filter values: '+field)
        if values.count('all')!=1:raise ValueError('Expected exactly one All option: '+field)
        # Require the body to contain only option tags and whitespace.
        residual=re.sub(r'<option\\b[^>]*>.*?</option>','',body,flags=re.S)
        if residual.strip():raise ValueError('Unexpected selector markup: '+field)
        entries=[(x.group(1),x.group(0)) for x in found]
        def name(option):
            return re.sub(r'\\s*\\(\\d+\\)\\s*$','',unescape(re.sub(r'<[^>]+>','',option[1]))).strip().casefold()
        entries.sort(key=lambda pair:(pair[0]!='all',name(pair),pair[0]))
        normalized='\n'.join('  '+raw for _,raw in entries)
        text=text[:match.start(2)]+normalized+text[match.end(2):]
        report[field]={'options':len(entries),'sorted':True,'unique':True}
    INDEX.write_text(text,encoding='utf-8')
    print(json.dumps({'phase':'normalize','filters':report}))

def finalize():
    c,l=read(CONTROLLER),read(LEDGER)
    assert_eq(c['checkpoint'],37,'post-build checkpoint')
    assert_eq(c['dossier_count'],1050,'post-build dossier total')
    assert_eq(l['counts']['accepted'],225,'post-build accepted-pending count')
    assert_eq(l['counts']['pending'],0,'post-build pending count')
    by={x['id']:x for x in l['entries']}
    for i in IDS:
        assert_eq(by[i]['implementation_status'],'accepted_pending_validation',i)
    report_dir=ROOT.parent/'expansion-research'
    static=read(report_dir/'static-report.json')
    runtime=read(report_dir/'runtime-output'/'runtime-report.json')
    if static['status']!='passed' or static['failure_count']!=0 or static['dossiers']!=1050:
        raise ValueError('Static release gate incomplete or failed')
    if runtime['status']!='passed' or runtime['failures'] or runtime['responsive_cases']!=678:
        raise ValueError('Chromium release gate incomplete or failed')
    if not all(x['status']=='passed' for x in runtime['functional_cases']):
        raise ValueError('Chromium functional suite did not fully pass')
    if len(c['added_dossiers'])!=225:raise ValueError('Expansion list inconsistent with dossier count')
    for i in IDS:by[i]['implementation_status']='accepted'
    l['updated_date']='2026-10-27'
    c['status']='complete'
    c['updated_at']='2026-10-27'
    c['next_action']='North American Expansion NA-037 complete (all 238 decisions). Next: approved Sagamore Spirit discovery and finite expression inventory before implementation; honor DEVELOPMENT-ROADMAP.md R002. Preserve 825 baseline.'
    c['history'][-1].update(status='accepted',validation={
      'structural_data_link_image_checks':static['checks'],
      'functional_cases_passed':len(runtime['functional_cases']),
      'responsive_pages_rendered':runtime['responsive_cases'],
      'viewports':[390,768,1440],
      'failures':0
    })
    c['validation']['static']=static
    c['validation']['runtime']=runtime
    c['prepared_batch_037']['status']='published_accepted'
    c['prepared_batch_037']['accepted_date']='2026-10-27'
    c['final_ui_normalization']['status']='accepted'
    c['final_ui_normalization']['accepted_date']='2026-10-27'
    c['final_ui_normalization']['scope']+=' Completed by scripts/na_037_release.py and browser filter regression validation.'
    write(LEDGER,l);write(CONTROLLER,c)

    text=ROADMAP.read_text(encoding='utf-8')
    assert_eq(text.count('**Roadmap revision:** R001'),1,'roadmap revision marker')
    text=text.replace('**Roadmap revision:** R001','**Roadmap revision:** R002',1)
    old='| na-expansion | Close all 238 Widow Jane/Canadian expression decisions and publish validated dossiers | 11 | partial |'
    if old not in text:raise ValueError('Roadmap gate missing')
    text=text.replace(old,old.replace(' | partial |',' | accepted |'),1)
    oldpct='**Current baseline: 30% accepted (30/100 weighted points).**'
    if oldpct not in text:raise ValueError('Roadmap progress sentence missing')
    text=text.replace(oldpct,'**Current baseline: 41% accepted (41/100 weighted points).**',1)
    pattern=r'\\*\\*Stage A — Preserve and finish current commitments\\.\\*\\*[^\\n]+'
    newstage=("**Stage A — Preserve and finish current commitments.** Original 825 dossiers remain immutable. "
       "As of 2026-10-27, **NA-037, 1,050 dossiers** = 825 baseline + 28 Widow Jane + 197 Canadian; "
       "ledger **225 accepted, 11 excluded, 2 baseline-preserved, 0 pending** "
       "(238 of 238 decisions). The final seven Canadian dossiers are published and were tested "
       "with zero failures using full structural checking and focused Chromium at 390/768/1440. "
       "North American Expansion is complete; categorical filters have been alphabetized with All first. "
       "Do not replay accepted checkpoints 001–037. Advance to approved Sagamore research as Stage B.")
    text,n=re.subn(pattern,lambda _:newstage,text,count=1)
    assert_eq(n,1,'Stage A summary replacement')
    text=text.replace('**Stage B — Extend expression coverage deliberately.**','**Stage B — Extend expression coverage deliberately.**',1)
    marker='## 9. Revision history\n\n'
    if marker not in text:raise ValueError('Roadmap changelog missing')
    text=text.replace(marker,marker+'- **2026-10-27 — R002:** Accepted and validated NA-037: seven remaining Canadian dossiers; total 1,050, 238/238 decisions, all original 825 preserved. Normalized catalogue filters alphabetically. North American gate accepted (+11 weighted points); overall **41%**. Next authorized family: Sagamore.\n',1)
    ROADMAP.write_text(text,encoding='utf-8')
    p=read(PROGRESS)
    assert_eq(p['revision'],'R001','previous progress revision')
    p['revision']='R002';p['asOf']='2026-10-27'
    p['progress']['completed']=238;p['progress']['total']=238
    p['progress']['basis']='All 238 finite North American candidates disposed: 225 accepted, 11 excluded, 2 baseline-preserved; 0 pending.'
    p['roadmap']['gates']=read_roadmap_gates(text)
    p['roadmap']['note']='R002: final seven Canadian dossiers accepted; 41/100 full-vision delivery points earned. North American 238/238 is only one finished workstream.'
    write(PROGRESS,p)
    print(json.dumps({'phase':'finalize','checkpoint':37,'published_dossiers':1050,'expansion_dispositions':'238/238','roadmap_revision':'R002','accepted_roadmap_points':41}))

def read_roadmap_gates(text):
    lines=[x for x in text.splitlines() if re.match(r'^\\| [a-z][a-z0-9-]+ \\|',x)]
    gates=[]
    for line in lines:
        columns=[x.strip() for x in line.split('|')[1:-1]]
        if len(columns)!=5:raise ValueError('Unexpected roadmap gate columns')
        i,label,weight,status,evidence=columns
        gates.append(dict(id=i,label=label,weight=int(weight),status=status,evidence=evidence))
    if len(gates)!=15 or sum(x['weight'] for x in gates)!=100:
        raise ValueError('Roadmap must contain exactly 15 gates totaling 100 points')
    return gates

if __name__=='__main__':
    commands={'preflight':preflight,'normalize':normalize,'finalize':finalize}
    if len(sys.argv)!=2 or sys.argv[1] not in commands:sys.exit('Usage: python scripts/na_037_release.py preflight|normalize|finalize')
    commands[sys.argv[1]]()
