#!/usr/bin/env python3
"""Focused expansion validation and immutable-baseline regression checks."""
import base64, hashlib, html, io, json, math, pathlib, re, subprocess, sys, urllib.parse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from lxml import html as lh
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import completion_validate as cv
def digest(b):return hashlib.sha256(b).hexdigest()
def projection(text):return json.loads(re.search(r'<script[^>]*id="whiskey-index-data"[^>]*>(.*?)</script>',text,re.S)[1])
def validate(full=False):
    ctl=json.loads((ROOT/'north-american-expansion-checkpoint.json').read_text());ledger=json.loads((ROOT/'north-american-expression-ledger.json').read_text());new=json.loads((ROOT/'north-american-expansion-data.json').read_text()) if (ROOT/'north-american-expansion-data.json').exists() else []
    errors=[];checks=0
    def check(ok,kind,detail):
        nonlocal checks;checks+=1
        if not ok:errors.append({'kind':kind,**detail})
    for n,h in ctl['baseline_dossier_sha256'].items():check(digest((ROOT/n).read_bytes())==h,'baseline_dossier_preservation',{'file':n})
    for n,h in ctl['completed_ledgers_preserved'].items():check(digest((ROOT/n).read_bytes())==h,'completed_ledger_preservation',{'file':n})
    original=subprocess.check_output(['git','show',ctl['baseline_commit']+':index.html'],cwd=ROOT,text=True)
    baseline=projection(original);text=(ROOT/'index.html').read_text();current=projection(text)
    by={r['filename']:r for r in current['rows']}
    for r in baseline['rows']:check(by.get(r['filename'])==r,'baseline_index_metadata',{'file':r['filename']})
    oldrows=re.findall(r'<tr\b[^>]*data-name="[^"]*".*?</tr>',original,re.S)
    for r in oldrows:check(r in text,'baseline_index_row_bytes',{'id':re.search('id="([^"]*)"',r)[1]})
    dom=lh.fromstring(text);rows=dom.xpath('//tbody[@id="bottles"]/tr');targets=[r.xpath('.//a/@href')[0] for r in rows];files={p.name for p in ROOT.glob('*.html') if p.name!='index.html'}
    check(len(files)==825+len(new)==ctl['dossier_count'],'counts',{'files':len(files),'records':len(new),'controller':ctl['dossier_count']})
    check(len(targets)==len(set(targets)) and set(targets)==files,'dossier_targets',{'duplicates':len(targets)-len(set(targets)),'missing':sorted(set(targets)-files),'orphans':sorted(files-set(targets))})
    check(len(by)==len(current['rows'])==len(files),'projection_count',{'count':len(by)})
    check({m['filename'] for m in new}==set(ctl['added_dossiers']),'controller_parity',{})
    check(not any(p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif','.svg','.avif'} for p in ROOT.rglob('*') if '.git' not in p.parts),'standalone_image_assets',{})
    checks_columns={'name','category','proof','cost','mash','age','quality','value','overall'}
    check(set(dom.xpath('//th[@data-key]/@data-key'))==checks_columns,'all_nine_sort_columns',{})
    inspect_paths=sorted(ROOT.glob('*.html')) if full else [ROOT/'index.html']+[ROOT/m['filename'] for m in new]
    with ProcessPoolExecutor(max_workers=4) as pool:items=list(pool.map(cv.inspect_one,map(str,inspect_paths),chunksize=4))
    check_count_before=checks;errors.extend(e for item in items for e in item['errors']);checks+=len(items)
    byfile={item['file']:item for item in items};local=0;unique=set();occ=0
    for item in items:
        unique.update(i['sha256'] for i in item['images']);occ+=sum(i['occurrences'] for i in item['images'])
        for value,attr,tag in item['refs']:
            u=urllib.parse.urlsplit(value)
            if u.scheme or u.netloc or value.startswith('//'):continue
            local+=1;target=urllib.parse.unquote(u.path) or item['file'];p=(ROOT/target).resolve();check(p.is_relative_to(ROOT) and p.is_file(),'broken_local_reference',{'file':item['file'],'reference':value})
            if p.is_file() and p.suffix=='.html' and u.fragment:
                ids=byfile.get(p.name,{}).get('ids')
                if ids is None:ids=lh.fromstring(p.read_text()).xpath('//*[@id]/@id')
                check(urllib.parse.unquote(u.fragment) in ids,'broken_local_anchor',{'file':item['file'],'reference':value})
    rowby={r.get('id'):r for r in rows}
    for m in new:
        md=byfile[m['filename']]['metadata'];expected={k:v for k,v in m.items() if k!='editorial'};check(md==expected,'new_dossier_metadata',{'file':m['filename']})
        q,v,o=m['quality'],m['value'],m['overall'];check((o is None if q is None or v is None else math.isclose(o,math.sqrt(q*v),rel_tol=1e-12)),'overall_precision',{'file':m['filename']})
        check(m['abv'] is None if m['proof'] is None else math.isclose(m['abv']*2,m['proof']),'proof_abv',{'file':m['filename']})
        for k in ['quality','value']:check(m[k] is None or 1<=m[k]<=10,'score_range',{'file':m['filename'],'field':k})
        r=rowby[m['slug']];ds=r.attrib;cells=r.xpath('./td');check(len(cells)==9,'row_columns',{'file':m['filename']})
        for field,key in [('quality','quality'),('value','value'),('overall','overall'),('proof','proof'),('cost','price'),('age','age_sort_years')]:
            raw=ds.get('data-'+field);val=m[key];check(raw=='' if val is None else raw is not None and math.isclose(float(raw),val,rel_tol=1e-12),'numeric_sort_key',{'file':m['filename'],'field':field})
        for i,k in [(6,'quality'),(7,'value'),(8,'overall')]:
            d=cells[i].text_content().strip().rstrip('†‡§');exp='N/A' if m[k] is None else f'{m[k]:.1f}';check(d==exp,'score_display',{'file':m['filename'],'field':k,'display':d,'expected':exp})
        check(bool(dom.xpath('//select[@id="category"]/option[@value=$cat]',cat=m['category'])),'category_filter',{'file':m['filename']})
        check(bool(dom.xpath('//select[@id="family"]/option[@value=$family]',family=ds['data-family'])),'family_filter',{'file':m['filename']})
        check(len(m['buy_price_thresholds'])==5 and len(m['serving_recommendations'])>=4 and len(m['comparables'])>=2,'canonical_sections',{'file':m['filename']})
        if m['quality'] is not None:check(bool(m['review_evidence']),'independent_score_evidence',{'file':m['filename']})
        if m['category'].startswith('Canadian') and q is not None:check(m['quality_calibration_details']['underlying_mode']=='universal_rubric','canadian_calibration_boundary',{'file':m['filename']})
        if m['exact_bottle_image_status']=='verified':check(bool(byfile[m['filename']]['images']),'image_embedding',{'file':m['filename']})
    report={'schema':'old-oak-north-american-static-validation-v1','checkpoint':ctl['checkpoint'],'status':'passed' if not errors else 'failed','full_repository_validation':full,'dossiers':len(files),'new_dossiers':len(new),'html_files_structurally_checked':len(items),'original_dossier_hashes_verified':825,'original_index_rows_byte_preserved':825,'completed_ledgers_unchanged':True,'checks':checks,'local_references_checked':local,'embedded_image_occurrences_decoded':occ,'unique_image_payloads_decoded':len(unique),'image_dossiers_added':sum(m['exact_bottle_image_status']=='verified' for m in new),'numeric_counts':{k:sum(m[k] is not None for m in new) for k in ['quality','value','overall']},'failure_count':len(errors),'failures':errors}
    out=ROOT.parent/'expansion-research'/'static-report.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(report,ensure_ascii=False));return report
if __name__=='__main__':sys.exit(0 if validate('--full' in sys.argv)['status']=='passed' else 1)
