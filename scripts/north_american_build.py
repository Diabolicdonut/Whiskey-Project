#!/usr/bin/env python3
"""Render explicitly authored expansion records; never rebuild a baseline dossier."""
import base64, csv, hashlib, html, io, json, math, pathlib, re, subprocess, sys
from decimal import Decimal, ROUND_HALF_UP
ROOT=pathlib.Path(__file__).resolve().parent.parent
DATA=ROOT/'north-american-expansion-data.json'
DATE='2026-10-14'
esc=lambda s:html.escape(str(s),quote=True)
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def half(x):return float(Decimal(str(x)).quantize(Decimal('.1'),rounding=ROUND_HALF_UP))
def display(x):return 'N/A' if x is None else f'{x:.1f}'
def family_id(name):return re.sub('[^A-Za-z0-9]','',name)
CSS=''' :root{--ink:#261e17;--muted:#70604f;--paper:#f6f0e7;--card:#fffaf3;--line:#d6c6b2;--accent:#865024}*{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--paper);font:17px/1.65 Georgia,serif}a{color:var(--accent);overflow-wrap:anywhere}a:focus-visible{outline:3px solid #bc7b38;outline-offset:3px}.topbar{background:#17120e;color:#e9dfd1;padding:.8rem 4%;display:flex;gap:1.1rem;flex-wrap:wrap;font:600 .76rem/1.4 system-ui}.topbar a{color:inherit}.hero{background:linear-gradient(120deg,#21170f,#4a3120);color:#f9f0e4;padding:4rem 0 3.5rem}.wrap{width:min(1180px,92%);margin:auto}.eyebrow{font:700 .75rem/1.5 system-ui;text-transform:uppercase;letter-spacing:.12em;color:#d9b890}h1{font-size:clamp(2.5rem,6vw,5rem);line-height:1.04;letter-spacing:-.04em;margin:.7rem 0 1.3rem;overflow-wrap:anywhere}.dek{font-size:1.25rem;color:#e9d7c3;max-width:880px}.meta{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1.5rem}.pill{border:1px solid #b39b81;border-radius:99px;padding:.4rem .7rem;font:600 .8rem system-ui}main{padding:3rem 0 4rem}.grid{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:2.5rem}article,aside{min-width:0}section{padding:1.2rem 0 2rem;border-top:1px solid var(--line)}h2{font-size:clamp(1.7rem,3vw,2.4rem);line-height:1.13;margin:.4rem 0 1.1rem}h3{font-size:1.1rem;margin:.4rem 0 .7rem}p{margin:.8rem 0}.bottle{display:block;width:100%;max-height:560px;object-fit:contain;background:#eee7dc;border-radius:12px;margin:0 0 2.2rem}.sidebar-card,.review-card,.serve-card,.band{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:1.1rem;margin:0 0 1rem}.sidebar-card{font:.88rem/1.55 system-ui}.sidebar-card h3{font:800 .75rem system-ui;letter-spacing:.08em;text-transform:uppercase}dl{margin:0}dt{font-weight:700;margin-top:.7rem}dd{margin:.2rem 0 .6rem;overflow-wrap:anywhere}.score{font:800 2rem/1.1 Georgia}.note{background:#eee1cf;border-left:4px solid #a26b34;padding:.9rem 1rem;font:.9rem/1.6 system-ui}.serve-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}.comparison-wrap{overflow:auto}table{width:100%;border-collapse:collapse;font:.85rem/1.45 system-ui}th,td{text-align:left;padding:.7rem;border-bottom:1px solid var(--line)}th{background:#2b2119;color:#fffaf3}.comparison-wrap table{min-width:560px}.bands{display:grid;gap:.7rem}.band{margin:0}.current-band{border:2px solid #435447;background:#edf2e9}.band p{font-size:.98rem;margin:.4rem 0}.sources{padding-left:1.3rem;font:.87rem/1.65 system-ui}.sources li{padding:.5rem 0}.small{font:.8rem/1.6 system-ui;color:var(--muted)}footer{padding:1.5rem 4%;border-top:1px solid var(--line);font:.8rem/1.6 system-ui}@media(max-width:800px){.grid{grid-template-columns:1fr}.hero{padding:3rem 0 2.5rem}.bottle{max-height:440px}}@media(max-width:520px){.serve-grid{grid-template-columns:1fr}.wrap{width:94%}h1{font-size:2.6rem}.hero .dek{font-size:1.1rem}.comparison-wrap table{min-width:480px}}'''
def make_metadata(e,a):
    q=a.get('quality');v=a.get('value'); dims=a.get('dimensions')
    if q is not None:assert a.get('reviews') and a.get('quality_rationale')
    if v is not None:assert q is not None and a.get('pricing') and a.get('value_rationale')
    category=a.get('category',e['whisky_category'])
    mode=a.get('calibration_mode','evidence_limited_provisional' if q is not None else 'unscored')
    underlying='universal_rubric' if category.startswith('Canadian') or category in ['Flavored whiskey','American whiskey'] else 'native_anchored'
    detail={'underlying_mode':underlying,'reviewed_date':DATE,'limitations':a.get('evidence_limit','Scores summarize the matched published tasting evidence; variation and conflicting judgments remain explicit.')}
    if q is not None and underlying=='universal_rubric':
        assert dims and len(dims)==7,'Universal assessments need seven documented dimension judgments'
        weights=[25,20,15,15,10,10,5];base=sum(x*w for x,w in zip(dims,weights))/100
        adj=round(q-base,4);assert abs(adj)<=.5001,(q,base,adj)
        detail.update(universal_dimensions=dict(zip(['integration','flavor_development','finish','technical_cleanliness','texture','maturity_wood_management','distinctiveness'],dims)),weights=weights,diagnostic_baseline=base,editorial_adjustment=adj,adjustment_reason=a['quality_rationale'])
    elif q is not None:
        detail['anchor_references']={'worst':['cleveland-black-reserve-early-2013-2014'],'average':['makers-mark','bulleit-bourbon'],'best':['michters-20-year-bourbon-2024']} if category=='Bourbon' else {'worst':['hudson-maple-cask-rye-2014-batch-1-bottle-2338'],'average':['old-overholt-bottled-in-bond','high-west-double-rye-current'],'best':['redemption-ancients-18-year-rye-2017']}
        if category=='Rye':detail['native_anchor_status']='provisional; unresolved floor retained'
    price=a.get('pricing') or {};currency=price.get('currency','USD');amount=price.get('amount');size=price.get('size_ml',750)
    usd=round(amount*750/size,2) if amount is not None and currency=='USD' else price.get('usd_750_reference')
    proof=a.get('proof',e['proof']);age=a.get('age',e['age_statement_years']);age_display=a.get('age_display',f'{age:g} Years' if age is not None else 'NAS / label age not established')
    overall=math.sqrt(q*v) if q is not None and v is not None else None
    reviews=a.get('reviews',[]);sources=a.get('sources',[]);assert sources,'Every published dossier needs identified sources'
    m={'slug':e['id'],'filename':e['filename'],'name':e['canonical_expression_name'],'family':e['brand_family'],'portfolio':None,'category':category,'subcategory':a.get('subcategory',category),'producer':a.get('producer',e['producer']),
      'proof':proof,'abv':proof/2 if proof is not None else None,'age':age_display,'age_display':age_display,'age_sort_years':age,
      'mash_bill_display':a.get('grain',e['grain_information']),'mash_bill_confidence':a.get('grain_confidence','Matched expression documentation; no undisclosed ratios inferred.'),
      'quality':q,'quality_score':q,'value':v,'value_score':v,'overall':overall,'overall_score':overall,
      'quality_calibration_mode':mode,'quality_calibration_details':detail,'quality_calibration_basis':a.get('calibration_basis',('Canadian execution within its intended category, using the universal rubric; American bourbon and straight-rye endpoints are not applied.' if category.startswith('Canadian') else 'The established project hierarchy applies to the exact expression category.')),
      'quality_rationale':a.get('quality_rationale','N/A: no sufficient matched independent tasting record was authenticated.'),'quality_confidence':a.get('quality_confidence','Low–medium; matched published sample' if q is not None else 'Unscored'),
      'quality_na_reason':None if q is not None else a.get('na_reason','Genuinely insufficient exact-expression independent sensory evidence.'),
      'value_rationale':a.get('value_rationale','N/A: a reliable sensory assessment and matched dated price are both required.'),'value_confidence':a.get('value_confidence','Dated price context and exact sensory scope' if v is not None else 'Unscored'),
      'value_na_reason':None if v is not None else 'Insufficient matched sensory evidence and/or defensible price context.',
      'price':usd,'price_basis':price.get('basis','Price not established'),'price_url':price.get('url'),'price_period':price.get('date'),
      'price_effective':price.get('effective'),'price_checked_date':DATE,'price_currency':currency,'bottle_size_ml':size,'bottle_price':amount,'price_normalized_to_ml':750,
      'nc_abc_price':amount if price.get('nc_code') else None,'nc_code':price.get('nc_code'),'nc_listing_status':price.get('nc_status','No authenticated current NC listing for this exact historical identity.'),
      'current_or_historical':'current' if e['status']=='current' else 'historical','period_filter':'current' if e['status']=='current' else 'historical',
      'release_year':a.get('release_year'),'release_scope':a['identity'],'availability_note':a.get('availability','Dated listings and original prices do not guarantee stock; collector premiums do not improve drinking Value.'),
      'research_date':DATE,'score_date':DATE,'review_sources':[r['url'] for r in reviews],'review_publishers':list(dict.fromkeys(r['publisher'] for r in reviews)),
      'critical_source_count':len(set(r['publisher'] for r in reviews)),'review_evidence':reviews,'source_urls':list(dict.fromkeys([s['url'] for s in sources]+[r['url'] for r in reviews])),
      'production_summary':a['production'],'finishing_information':a.get('finish',e['finishing_information']),'identity_note':a.get('identity_note'),'history':a['history'],
      'comparables':a.get('comparables',[]),'buy_price_thresholds':a['bands'],'serving_recommendations':a['serving'],'review_video_sources':a.get('videos',[]),
      'image_credits':[],'exact_bottle_image_status':'unavailable','exact_bottle_image_scope':a['identity'],'image_limitation':a.get('image_limitation','No exact-expression image authenticated; sibling, generic or mismatched bottles are omitted.'),
      'canonical_complete':True,'canonical_format_version':'north-american-expansion-v1','assessment_checkpoint':'NA-001','editorial':a}
    return m
def render(m,image_uri=None):
    a=m['editorial'];quality=display(m['quality']);value=display(m['value']);overall=display(m['overall'])
    proof='Proof N/A' if m['proof'] is None else f'{m["proof"]:g} proof · {m["abv"]:g}% ABV'
    short=a['short_version'];price=a.get('pricing') or {};amount=price.get('amount');currency=price.get('currency','USD');size=price.get('size_ml',750)
    price_text=(f'{currency} {amount:.2f} / {size:g} mL' if amount is not None else 'No defensible price established')
    body=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(m['name'])} | Old Oak Omnibus</title><style>{CSS}</style></head><body><nav class="topbar"><a href="index.html">Old Oak Omnibus</a><a href="index.html?family={family_id(m['family'])}">{esc(m['family'])} family</a><a href="#review">Critical synthesis</a><a href="#value">Buying decision</a><a href="#sources">Sources</a></nav><header class="hero"><div class="wrap"><p class="eyebrow">{esc(m['category'])} dossier · researched {DATE}</p><h1>{esc(m['name'])}</h1><p class="dek">{esc(short)}</p><div class="meta"><span class="pill">{esc(proof)}</span><span class="pill">{esc(m['age_display'])}</span><span class="pill">Quality {quality}</span><span class="pill">Value {value}</span><span class="pill" data-canonical-overall="true">Overall {overall}</span></div></div></header><main class="wrap"><div class="grid"><article>'''
    if image_uri:body+=f'<img class="bottle" src="{image_uri}" width="{m["image_credits"][0]["width"]}" height="{m["image_credits"][0]["height"]}" alt="{esc(m["name"])} — verified expression photograph" decoding="async">'
    else:body+=f'<p class="note">{esc(m["image_limitation"])}</p>'
    def section(id,title,content):return f'<section id="{id}"><h2>{title}</h2>{content}</section>'
    body+=section('short-version','The short version',f'<p>{esc(short)}</p><p><strong>Exact identity:</strong> {esc(a["identity"])}</p>')
    body+=section('history','Background and history',''.join('<p>'+esc(p)+'</p>' for p in a['history'])+(('<p>For the shared historical context, read <a href="north-american-history.md">Canadian whisky, cross-border trade and the American market</a>. The release chronology above distinguishes the current bottle from its brand’s earlier history.</p>') if m['category'].startswith('Canadian') or m['family']!='Widow Jane' else ''))
    body+=section('production','Producer, grains, aging and finishing',f'<p>{esc(a["production"])}</p><dl><dt>Producer / source</dt><dd>{esc(m["producer"])}</dd><dt>Grain / mash composition</dt><dd>{esc(m["mash_bill_display"])}</dd><dt>Strength</dt><dd>{esc(proof)}</dd><dt>Age statement</dt><dd>{esc(m["age_display"])}</dd><dt>Finishing</dt><dd>{esc(m["finishing_information"])}</dd></dl>'+(f'<p class="note">{esc(a["identity_note"])}</p>' if a.get('identity_note') else ''))
    rev=''
    for r in m['review_evidence']:
        rev+=f'<div class="review-card"><h3>{esc(r["reviewer"])} · <a href="{esc(r["url"])}">{esc(r["publisher"])}</a></h3><p>{esc(r["summary"])}</p><p class="small">Scope: {esc(r["scope"])}</p></div>'
    rev+=f'<p class="note">{esc(a.get("evidence_limit","Published judgments are attributed to their reviewers. This dossier does not claim first-person tasting, and a sample review does not establish every batch."))}</p>'
    if not m['review_evidence']:rev+='<p>No authenticated independent tasting record supports a sensory synthesis for this exact release. Producer descriptions and related-bottle reviews do not fill that gap.</p>'
    rev+='<h3>Community sentiment</h3><p>'+esc(a.get('community','No separate representative community consensus is claimed. A handful of ratings or a video title is not treated as a sensory review.'))+'</p>'
    body+=section('review','Critical review synthesis',rev)
    comparison='<div class="comparison-wrap"><table><thead><tr><th scope="col">Whisky</th><th scope="col">Useful comparison</th></tr></thead><tbody>'
    for c in a['comparables']:comparison+=f'<tr><td><a href="{esc(c["url"])}">{esc(c["name"])}</a></td><td>{esc(c["reason"])}</td></tr>'
    comparison+='</tbody></table></div><p class="small">Comparisons explain recipe, style and purchasing choices. They do not merge the whiskies into one scoring category.</p>'
    body+=section('comparables','Comparable whiskies',comparison)
    calib=f'<p><strong>Quality {quality} / 10.</strong> {esc(m["quality_rationale"])}</p><p>{esc(m["quality_calibration_basis"])}</p><p><strong>Calibration mode:</strong> {esc(m["quality_calibration_mode"])}. {esc(m["quality_confidence"])}</p>'
    if m['quality_calibration_details'].get('universal_dimensions'):
        d=m['quality_calibration_details'];calib+='<table><thead><tr><th scope="col">Execution dimension</th><th scope="col">Weight</th><th scope="col">Diagnostic judgment</th></tr></thead><tbody>'
        for (k,v),w in zip(d['universal_dimensions'].items(),d['weights']):calib+=f'<tr><td>{esc(k.replace("_"," "))}</td><td>{w}%</td><td>{v:.1f}</td></tr>'
        calib+=f'</tbody></table><p class="small">Weighted diagnostic baseline {d["diagnostic_baseline"]:.3f}; editorial adjustment {d["editorial_adjustment"]:+.3f}. Dimension numbers are cautious editorial judgments of the published evidence. They are not measurements or new tasting observations.</p>'
    calib+='<p class="small">Scale: 1 catastrophic; 2 poor; 3 bad/flawed; 4 below average; 5 average/competent; 6 good; 7 very good; 8 excellent; 9 exceptional; 10 reference-class. Price and scarcity are excluded from Quality.</p>'
    body+=section('quality','Quality and calibration',calib)
    val=f'<p><strong>{esc(price_text)}</strong> · {esc(m["price_basis"])} · price context {esc(m["price_period"] or "not established")}; checked {DATE}.</p><p>{esc(m["nc_listing_status"])}</p><p><strong>Value {value} / 10.</strong> {esc(m["value_rationale"])}</p><p><strong>Overall {overall} / 10.</strong> Overall = √(Quality × Value). The index displays one decimal and sorts on the unrounded result. If either component lacks sufficient evidence, Overall is N/A.</p><p class="small">{esc(m["availability_note"])}</p>'
    if currency!='USD':val+='<p class="note">This is a Canadian-dollar price context. It is not a current NC ABC price or a U.S.-dollar quote; no unsourced currency conversion is used. The USD Cost sort has no numeric key for this record.</p>'
    body+=section('value','Price, Value and Overall',val)
    bands='<div class="bands">'
    for b in a['bands']:
        limits=(('Below '+str(b['maximum_exclusive'])) if b.get('minimum')==0 and b.get('maximum_exclusive') is not None else (str(b['minimum'])+' and above') if b.get('maximum_exclusive') is None and b.get('minimum') is not None else (str(b.get('minimum'))+' to below '+str(b.get('maximum_exclusive')))) if b.get('minimum') is not None else 'Conditional guidance; no numeric threshold established'
        bands+=f'<div class="band{ " current-band" if b.get("current_band") else ""}"><h3>{esc(b["label"])}</h3><p><strong>{esc(currency+" "+limits if b.get("minimum") is not None else limits)}</strong></p><p>{esc(b["reason"])}</p></div>'
    body+=section('buy-guidance','Five-band buy guidance',bands+'</div>')
    serving='<div class="serve-grid">'
    for s in a['serving']:serving+=f'<div class="serve-card"><h3>{esc(s["name"])}</h3><p>{esc(s["recommendation"])}</p></div>'
    body+=section('serving','Serving recommendations',serving+'</div><p class="small">Serving suggestions are editorial starting points, grounded in documented strength and style; adjust to your taste.</p>')
    videos=''.join(f'<p><a href="{esc(v["url"])}">{esc(v["title"])}</a> · {esc(v.get("scope","Further viewing; not silently counted as scored sensory evidence."))}</p>' for v in a.get('videos',[])) or '<p>No expression-matched viewing link was authenticated for inclusion. The written sources below are the review record.</p>'
    body+=section('viewing','Further viewing',videos)
    src='<ol class="sources">'
    for s in a['sources']:src+=f'<li><a href="{esc(s["url"])}">{esc(s["title"])}</a> — {esc(s["role"])}</li>'
    if m['image_credits']:
        im=m['image_credits'][0];src+=f'<li><a href="{esc(im["source_url"])}">Verified expression photograph</a> — {esc(im["scope"])}; embedded directly in this HTML.</li>'
    src+='</ol><p class="small">Specifications, historical claims, sensory reviews and prices have distinct evidence roles. Where a source’s typo or identity mismatch matters, it is stated above. Research date: '+DATE+'.</p>'
    body+=section('sources','Sources and scope',src)
    body+='</article><aside><div class="sidebar-card"><h3>At a glance</h3><dl>'
    for k,v in [('Family',m['family']),('Category',m['category']),('Proof / ABV',proof),('Age',m['age_display']),('Recipe',m['mash_bill_display']),('Price context',price_text),('Quality',quality),('Value',value),('Overall',overall)]:body+=f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>'
    body+='</dl></div><div class="sidebar-card"><h3>Confidence and scope</h3><p>'+esc(m['release_scope'])+'</p><p>'+esc(m['quality_confidence'])+'</p></div></aside></div></main><footer>Old Oak Omnibus · North American Expansion · Researched '+DATE+' · <a href="index.html">Return to the catalogue</a></footer>'
    body+='<script type="application/json" id="whiskey-data">'+json.dumps({k:v for k,v in m.items() if k!='editorial'},ensure_ascii=False,separators=(',',':')).replace('</','<'+chr(92)+'/')+'</script></body></html>\n'
    return body
def row(m):
    a=m['editorial']; price=a.get('pricing') or {};p=price.get('amount');c=price.get('currency','USD');ps='N/A' if p is None else ('$' if c=='USD' else c+' ')+f'{p:.2f}'
    if p is not None and price.get('size_ml',750)!=750:ps+=f' / {price["size_ml"]} mL'
    marker={'native_anchored':'','parent_anchored':'†','universal_rubric':'‡','evidence_limited_provisional':'§','unscored':''}[m['quality_calibration_mode']]
    attrs={'id':m['slug'],'data-name':m['name'],'data-family':family_id(m['family']),'data-portfolio':'','data-groups':family_id(m['family']),'data-category':m['category'],'data-proof':m['proof'],'data-cost':m['price'],'data-age':m['age_sort_years'],'data-quality':m['quality'],'data-value':m['value'],'data-basis':'nc' if m['nc_code'] else 'alternate','data-quality-calibration':m['quality_calibration_mode'],'data-overall':m['overall'],'data-period':m['period_filter']}
    out='<tr '+' '.join(f'{k}="{esc(v if v is not None else "")}"' for k,v in attrs.items())+'>'
    proof_text='N/A' if m['proof'] is None else f"{m['proof']:g}"
    out+=f'<td class="name"><a href="{m["filename"]}">{esc(m["name"])}</a></td><td>{esc(m["category"])}</td><td>{esc(proof_text)}</td>'
    out+=f'<td title="{esc(m["price_basis"])}"><b>{esc(ps)}</b><small>{esc("NC regular retail" if m["nc_code"] else (c+" · "+(m["price_period"] or "undated")))}</small></td><td class="mash">{esc(m["mash_bill_display"])}</td><td class="age">{esc(m["age_display"])}</td><td class="score" title="{esc(m["quality_rationale"])}">{display(m["quality"])}{marker}</td><td class="score" title="{esc(m["value_rationale"])}">{display(m["value"])}</td><td class="score overall">{display(m["overall"])}</td></tr>'
    return out
def projection(m):
    keys=['slug','filename','name','category','proof','abv','price','price_basis','bottle_price','bottle_size_ml','age_display','age_sort_years','mash_bill_display','quality_score','value_score','overall_score','quality_calibration_mode','quality_confidence','research_date','price_checked_date','current_or_historical','family','portfolio','period_filter']
    return {k:m.get(k) for k in keys}
def integrate(new):
    text=(ROOT/'index.html').read_text();mt=re.search(r'(<script[^>]*id="whiskey-index-data"[^>]*>)(.*?)(</script>)',text,re.S);p=json.loads(mt[2]);p['rows'].extend(projection(m) for m in new);p['dossier_count']=len(p['rows']);p['expansion_dataset']='north-american-expansion-data.json'
    text=text[:mt.start(2)]+json.dumps(p,ensure_ascii=False,separators=(',',':'))+text[mt.end(2):]
    # Preserve all accepted 825 raw row strings; insert only new rows before their alphabetic successor.
    for m in sorted(new,key=lambda m:m['name'].casefold()):
        matches=list(re.finditer(r'<tr\b[^>]*data-name="([^"]*)".*?</tr>',text,re.S));pos=next((x.start() for x in matches if html.unescape(x[1]).casefold()>m['name'].casefold()),text.index('</tbody>'))
        text=text[:pos]+row(m)+'\n'+text[pos:]
    cats=re.search(r'<select id="category">(.*?)</select>',text,re.S);current=set(re.findall(r'value="([^"]+)"',cats[1]));extra=''.join(f'<option value="{esc(c)}">{esc(c)}</option>' for c in sorted({m['category'] for m in new}-current))
    text=text[:cats.end(1)]+extra+text[cats.end(1):]
    fm=re.search(r'<select id="family">(.*?)</select>',text,re.S);fm_text=fm[1]
    for f in sorted({m['family'] for m in new}):
        fid=family_id(f);count=sum(r['family']==f for r in p['rows']);op=f'<option value="{fid}">{esc(f)} ({count})</option>'
        pat=rf'<option value="{fid}">.*?</option>'
        fm_text=re.sub(pat,lambda _:op,fm_text) if re.search(pat,fm_text) else fm_text+op
    text=text[:fm.start(1)]+fm_text+text[fm.end(1):]
    # The accepted baseline has a plain Mash Bill header with no sort control. Repair only this missing behavior.
    text=text.replace('<th scope="col">Mash Bill</th>','<th scope="col" data-key="mash" aria-sort="none"><button type="button" aria-label="Sort by Mash Bill">Mash Bill</button></th>')
    text=text.replace("function sortValue(r){return sortKey===", "function sortValue(r){if(sortKey==='mash')return r.querySelector('td.mash').textContent;return sortKey===")
    text=text.replace("['name','category'].includes(sortKey)","['name','category','mash'].includes(sortKey)")
    (ROOT/'index.html').write_text(text)
def publish_input(path):
    authored=json.loads(pathlib.Path(path).read_text());ledger=json.loads((ROOT/'north-american-expression-ledger.json').read_text());ctl=json.loads((ROOT/'north-american-expansion-checkpoint.json').read_text());existing=json.loads(DATA.read_text()) if DATA.exists() else []
    ids={r['slug'] for r in existing};new=[];by={e['id']:e for e in ledger['entries']};assert 1<=len(authored)<=10
    for a in authored:
        e=by[a['id']];assert e['implementation_status']=='pending_research';assert e['id'] not in ids;assert not (ROOT/e['filename']).exists();m=make_metadata(e,a);uri=None
        if a.get('image_file'):
            from PIL import Image
            b=pathlib.Path(a['image_file']).read_bytes()
            with Image.open(io.BytesIO(b)) as im:im.load();fmt=im.format;width,height=im.size
            mime={'JPEG':'image/jpeg','PNG':'image/png','WEBP':'image/webp','AVIF':'image/avif'}[fmt];uri='data:'+mime+';base64,'+base64.b64encode(b).decode()
            m['image_credits']=[{'source_url':a['image_source'],'image_url':a['image_url'],'scope':a['identity'],'sha256':hashlib.sha256(b).hexdigest(),'image_embedded':True,'width':width,'height':height}];m['exact_bottle_image_status']='verified';m['image_limitation']=None
        m['assessment_checkpoint']=f'NA-{ctl["checkpoint"]+1:03d}'
        (ROOT/e['filename']).write_text(render(m,uri));new.append(m);e.update(implementation_status='accepted_pending_validation',decision='include',warrants_own_dossier=True,proof=m['proof'],abv=m['abv'],age_statement_years=m['age_sort_years'],age_information=m['age_display'],grain_information=m['mash_bill_display'],finishing_information=m['finishing_information'],whisky_category=m['category'],independent_review_record={'status':'matched_verified' if m['review_evidence'] else 'insufficient','scoring_allowed':m['quality'] is not None,'reviews':m['review_evidence']},exact_image_status=m['exact_bottle_image_status'],image_limitation=m['image_limitation'],assessment_checkpoint=m['assessment_checkpoint'],publication_sources=a['sources'])
    integrate(new);existing.extend(new);DATA.write_text(dump(existing));ledger['updated_date']=DATE;ledger['counts'].update(accepted=sum(e['implementation_status'].startswith('accepted') for e in ledger['entries']),pending=sum(e['implementation_status']=='pending_research' for e in ledger['entries']),excluded=sum(e['decision']=='exclude' for e in ledger['entries']));(ROOT/'north-american-expression-ledger.json').write_text(dump(ledger))
    ctl['checkpoint']+=1;ctl['status']='implementation_in_progress';ctl['added_dossiers'].extend(m['filename'] for m in new);ctl['widow_jane_added']=sum(m['family']=='Widow Jane' for m in existing);ctl['canadian_added']=sum(m['family']!='Widow Jane' for m in existing);ctl['dossier_count']=825+len(existing);ctl['last_parent_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();ctl['updated_at']=DATE;ctl['history'].append({'checkpoint':ctl['checkpoint'],'files':[m['filename'] for m in new],'parent_commit':ctl['last_parent_commit'],'status':'awaiting_validation'});ctl['next_action']='Validate current batch, record acceptance and push immediately; then research next pending entries in deterministic order.';(ROOT/'north-american-expansion-checkpoint.json').write_text(dump(ctl));print(json.dumps({'checkpoint':ctl['checkpoint'],'new_files':[m['filename'] for m in new],'total':ctl['dossier_count']}))
if __name__=='__main__':publish_input(sys.argv[1])
