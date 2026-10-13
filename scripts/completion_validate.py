#!/usr/bin/env python3
"""Validate the accepted collection and reconstruct missing downloads from its metadata.
Recovery uploads immutable Git blobs only; it never changes a branch, dossier or score.
"""
import base64, csv, hashlib, io, json, os, re, subprocess, sys, urllib.parse, urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".completion-output"
BASELINE = "e3776f7db3e79ed4ae62a741d603ab41441152db"
DATA_RE = re.compile(r'<script\b(?=[^>]*\bid=["\']whiskey-data["\'])[^>]*>(.*?)</script>', re.I | re.S)
DATA_URI = re.compile(r'data:image/[A-Za-z0-9.+-]+(?:;[A-Za-z0-9=.+-]+)*,[^"\'\s<>)]*', re.I)
RECOVERY_TARGETS = ["whiskey-data.json", "whiskey-data.csv", "score-audit.json",
                    "value-review-audit.json", "quality-anchor-ledger.md",
                    "anchor-review-follow-up.md", "audit.md"]
def digest(b):
    return hashlib.sha256(b).hexdigest()
def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()
def metadata(path):
    match = DATA_RE.search(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError("Missing dossier metadata: " + path.name)
    return json.loads(match.group(1))
def accepted():
    files = sorted(ROOT.glob("*.html"))
    dossiers = [p for p in files if p.name != "index.html"]
    assert len(dossiers) == 825, len(dossiers)
    return dossiers, [metadata(p) for p in dossiers]
def recover():
    dossiers, records = accepted()
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    match = re.search(r'<script\b(?=[^>]*\bid=["\']whiskey-index-data["\'])[^>]*>(.*?)</script>', index, re.S)
    projection = json.loads(match.group(1))
    by_file = {r["filename"]: r for r in records}
    records = [by_file[r["filename"]] for r in projection["rows"]]
    assert len(records) == 825 and len(by_file) == 825
    generated = {}
    generated["whiskey-data.json"] = ("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",",":")) for r in records) + "\n]\n").encode()
    assert json.loads(generated["whiskey-data.json"]) == records
    fields = ["filename","slug","name","category","subcategory","producer","family","proof","abv",
              "age","age_display","age_sort_years","bottle_size_ml","price","nc_abc_price",
              "price_basis","price_period","price_effective","price_checked_date","price_url",
              "quality","value","overall","quality_score","value_score","overall_score",
              "quality_calibration_mode","quality_confidence","value_calibration_mode",
              "value_confidence","research_date","score_date","mash_bill_display"]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for r in records:
        writer.writerow({k: "" if r.get(k) is None else r[k] for k in fields})
    generated["whiskey-data.csv"] = stream.getvalue().encode()
    csv_rows = list(csv.DictReader(io.StringIO(generated["whiskey-data.csv"].decode())))
    assert len(csv_rows) == 825
    for exported, original in zip(csv_rows, records):
        for k in fields:
            assert exported[k] == ("" if original.get(k) is None else str(original[k])), (original["filename"],k)
    common = {"schema":"old-oak-recovered-reference-v1",
              "source":"Current accepted dossier metadata; navigation recovery, not new research or recalibration",
              "accepted_content_commit":git("rev-parse","HEAD"), "dossier_count":825}
    score_fields = ["filename","slug","name","category","quality","quality_score","value","value_score","overall","overall_score",
                    "quality_calibration_mode","quality_confidence","quality_anchor_category_id","quality_anchor_status",
                    "quality_anchor_references","quality_anchor_comparison","quality_calibration_details","score_date"]
    value_fields = ["filename","slug","name","category","price","nc_abc_price","bottle_price","bottle_size_ml","price_basis",
                    "price_period","price_effective","price_checked_date","price_url","quality","value","value_score",
                    "value_rationale","value_calibration_mode","value_confidence","value_comparison_basis",
                    "value_comparison_review","value_review_date","value_review_comparators","buy_price_thresholds"]
    for target, fields_out in [("score-audit.json",score_fields),("value-review-audit.json",value_fields)]:
        obj = {**common, "records":[{k:r[k] for k in fields_out if k in r} for r in records]}
        assert len(obj["records"]) == 825
        generated[target] = (json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode()
    slugs = {r["slug"]:r["filename"] for r in records}
    def refs(value):
        if isinstance(value, str):
            value = [value]
        if not value:
            return "No explicit reference recorded"
        return "; ".join("["+v+"]("+slugs[v]+")" if v in slugs else str(v) for v in value)
    profiles = defaultdict(list)
    for r in records:
        key = r.get("quality_anchor_category_id") or r.get("quality_scoring_category") or r["category"]
        profiles[key].append(r)
    lines = ["# Old Oak Omnibus — recovered native anchor ledger","",
             "This navigation target is reconstructed solely from the current accepted dossier metadata. It restores access to existing calibration references; it does not establish endpoints, change grades, or replace completed research.","",
             "The complete metadata is available in [whiskey-data.json](whiskey-data.json). The accepted hierarchy is in [calibration-hierarchy-v6.2.md](calibration-hierarchy-v6.2.md).",""]
    for category, group in sorted(profiles.items()):
        lines += ["## "+category,"", "Recorded anchor statuses: "+", ".join(sorted({str(r.get("quality_anchor_status","not recorded")) for r in group}))+".",""]
        seen = set()
        for r in group:
            anchor = r.get("quality_anchor_references") or {}
            identity = json.dumps(anchor,sort_keys=True)
            if identity in seen:
                continue
            seen.add(identity)
            if isinstance(anchor,dict):
                for label in ("worst","average","best"):
                    lines += ["- "+label.capitalize()+": "+refs(anchor.get(label))]
            else:
                lines += ["Recorded metadata: "+json.dumps(anchor,ensure_ascii=False)]
        lines += [""]
    generated["quality-anchor-ledger.md"] = ("\n".join(lines)+"\n").encode()
    hudson = [r for r in records if "hudson" in r["slug"] and "rye" in (r["slug"]+" "+r["category"]).lower()]
    lines = ["# Old Oak Omnibus — recovered anchor review follow-up","",
             "This page restores a missing navigation target from current accepted metadata. No new tasting investigation or recalibration was performed. The saved [Rye floor resolution](rye-floor-resolution-v5.1.md) remains the historical research reference.",""]
    for r in hudson:
        lines += ["## ["+r["name"]+"]("+r["filename"]+")",""]
        for k in ("quality_anchor_status","quality_rationale","quality_anchor_comparison","quality_calibration_basis"):
            if r.get(k):
                lines += [k+": "+str(r[k]),""]
        if r.get("quality_calibration_details"):
            lines += ["Accepted calibration details:","",json.dumps(r["quality_calibration_details"],ensure_ascii=False,indent=2),""]
    generated["anchor-review-follow-up.md"] = ("\n".join(lines)+"\n").encode()
    numeric = lambda k: sum(isinstance(r.get(k),(int,float)) and not isinstance(r.get(k),bool) for r in records)
    lines = ["# Old Oak Omnibus — recovered accepted-state audit","",
             "This missing download target is reconstructed from the current accepted repository. It is a validation snapshot, not the historical batch audit and not a new research pass.","",
             "- Dossiers: 825", "- Numeric Quality records: "+str(numeric("quality")),
             "- Numeric Value records: "+str(numeric("value")), "- Numeric Overall records: "+str(numeric("overall")),
             "- All dossier prose, expression identities, grades, prices and research dates remain as accepted.","",
             "[Landing page](index.html) · [Complete metadata](whiskey-data.json) · [CSV summary](whiskey-data.csv) · [Score snapshot](score-audit.json) · [Value snapshot](value-review-audit.json) · [Final validation record](final-validation-checkpoint.json)",""]
    generated["audit.md"] = ("\n".join(lines)+"\n").encode()
    OUT.mkdir(exist_ok=True)
    recovery = OUT/"recovered"
    recovery.mkdir(exist_ok=True)
    manifest = []
    for target in RECOVERY_TARGETS:
        if (ROOT/target).exists():
            continue
        b = generated[target]
        (recovery/target).write_bytes(b)
        request = urllib.request.Request("https://api.github.com/repos/"+os.environ["GITHUB_REPOSITORY"]+"/git/blobs",
            data=json.dumps({"content":base64.b64encode(b).decode(),"encoding":"base64"}).encode(),
            headers={"Authorization":"Bearer "+os.environ["GH_TOKEN"],"Accept":"application/vnd.github+json","Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(request,timeout=60) as response:
            uploaded = json.load(response)
        manifest.append({"file":target,"git_blob_sha":uploaded["sha"],"sha256":digest(b),"size_bytes":len(b),
                         "source":"Current accepted dossier metadata; explicitly labeled recovery",
                         "all_825_metadata_records_verified":target in ("whiskey-data.json","whiskey-data.csv","score-audit.json","value-review-audit.json")})
    print("RECOVERED_REFERENCE_BLOBS "+json.dumps({"accepted_content_commit":git("rev-parse","HEAD"),"files":manifest},separators=(",",":")))
    (OUT/"recovery-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")

def inspect_one(path_str):
    import html5lib
    from lxml import etree, html
    from PIL import Image
    path = Path(path_str)
    b = path.read_bytes()
    text = b.decode("utf-8")
    errors, uris, refs_local = [], [], []
    minimized = DATA_URI.sub("data:image/png;base64,AA==",text)
    parser = html5lib.HTMLParser(namespaceHTMLElements=False)
    parser.parse(minimized)
    errors += [{"kind":"structure","file":path.name,"position":pos,"code":code,"details":details} for pos,code,details in parser.errors]
    dom = html.document_fromstring(text)
    ids = [x.get("id") for x in dom.xpath("//*[@id]")]
    for key,count in Counter(ids).items():
        if count>1:
            errors.append({"kind":"duplicate_id","file":path.name,"id":key,"count":count})
    title = "".join(dom.xpath("//title/text()"))
    if "Old Oak Omnibus" not in title:
        errors.append({"kind":"branding","file":path.name,"title":title})
    if not dom.xpath("//head") or not dom.xpath("//body") or not dom.xpath("//main"):
        errors.append({"kind":"structure","file":path.name,"code":"missing-head-body-main"})
    for u in dict.fromkeys(DATA_URI.findall(text)):
        try:
            header,payload=u.split(",",1)
            raw=base64.b64decode(payload,validate=True) if ";base64" in header.lower() else urllib.parse.unquote_to_bytes(payload)
            if header.lower().startswith("data:image/svg+xml"):
                etree.fromstring(raw,parser=etree.XMLParser(resolve_entities=False,no_network=True))
                fmt="SVG"
                size=None
            else:
                with Image.open(io.BytesIO(raw)) as im:
                    im.load()
                    fmt=im.format
                    size=im.size
                expected={"image/png":"PNG","image/jpeg":"JPEG","image/webp":"WEBP","image/gif":"GIF","image/avif":"AVIF"}
                mime=header[5:].split(";")[0].lower()
                if mime in expected and fmt!=expected[mime]:
                    raise ValueError("MIME/image format mismatch")
            uris.append({"sha256":digest(raw),"format":fmt,"size":size,"occurrences":text.count(u)})
        except Exception as e:
            errors.append({"kind":"embedded_image","file":path.name,"error":str(e)})
    for node in dom.xpath("//*[@href or @src or @poster or @srcset]"):
        for attribute in ("href","src","poster"):
            value=node.get(attribute)
            if value:
                refs_local.append((value,attribute,node.tag))
        if node.get("srcset"):
            for candidate in node.get("srcset").split(","):
                value=candidate.strip().split()[0]
                if not value.startswith("data:"):
                    refs_local.append((value,"srcset",node.tag))
    for style in dom.xpath("//style/text() | //@style"):
        refs_local += [(m.strip(" \t\n'\""),"css","style") for m in re.findall(r"url\((.*?)\)",style,re.S)]
    data = metadata(path) if path.name!="index.html" else None
    if data and (data.get("filename")!=path.name or data.get("slug")!=path.stem):
        errors.append({"kind":"identity","file":path.name})
    return {"file":path.name,"sha256":digest(b),"bytes":len(b),"ids":ids,"refs":refs_local,"images":uris,"metadata":data,"errors":errors}

def validate():
    from lxml import html
    OUT.mkdir(exist_ok=True)
    paths=sorted(ROOT.glob("*.html"))
    assert len(paths)==826,len(paths)
    with ProcessPoolExecutor(max_workers=4) as executor:
        inspected=list(executor.map(inspect_one,map(str,paths),chunksize=4))
    errors=[e for item in inspected for e in item["errors"]]
    by_file={item["file"]:item for item in inspected}
    local_count=0
    for item in inspected:
        for value,attribute,tag in item["refs"]:
            parsed=urllib.parse.urlsplit(value)
            if parsed.scheme or parsed.netloc or value.startswith("//"):
                continue
            local_count+=1
            target=urllib.parse.unquote(parsed.path) or item["file"]
            file=(ROOT/target).resolve()
            if not file.is_relative_to(ROOT) or not file.is_file():
                errors.append({"kind":"broken_local_reference","file":item["file"],"reference":value,"attribute":attribute})
            elif file.suffix==".html" and parsed.fragment:
                target_item=by_file.get(file.name)
                if target_item and urllib.parse.unquote(parsed.fragment) not in target_item["ids"]:
                    errors.append({"kind":"broken_anchor","file":item["file"],"reference":value})
    index=html.document_fromstring((ROOT/"index.html").read_text())
    projection=json.loads(index.xpath('//script[@id="whiskey-index-data"]/text()')[0])
    rows=index.xpath('//tbody[@id="bottles"]/tr')
    targets=[row.xpath(".//a[@href]")[0].get("href") for row in rows]
    dossier_names=set(by_file)-{"index.html"}
    for name,values in (("rendered_index",targets),("projection",[r["filename"] for r in projection["rows"]])):
        if len(values)!=825 or set(values)!=dossier_names or len(set(values))!=825:
            errors.append({"kind":"dossier_navigation","source":name,"count":len(values),"duplicates":[k for k,n in Counter(values).items() if n>1],
                           "missing":sorted(dossier_names-set(values)),"nonexistent":sorted(set(values)-dossier_names)})
    md_by={f:item["metadata"] for f,item in by_file.items() if f!="index.html"}
    for p in projection["rows"]:
        m=md_by[p["filename"]]
        for key in ("name","category","proof","abv","price","bottle_size_ml","quality_score","value_score","overall_score",
                    "quality_calibration_mode","quality_confidence","research_date","price_checked_date","current_or_historical"):
            if p.get(key)!=m.get(key):
                errors.append({"kind":"index_metadata","file":p["filename"],"field":key,"index":p.get(key),"dossier":m.get(key)})
    ledger=json.loads((ROOT/"image-embedding-checkpoint.json").read_text())
    if ledger.get("status")!="complete" or len(ledger.get("inspected_articles",[]))!=825 or not ledger.get("validation",{}).get("all_dossiers_inspected"):
        errors.append({"kind":"completed_ledger","message":"The accepted completed ledger is not preserved"})
    tracked=git("ls-files").splitlines()
    assets=[p for p in tracked if Path(p).suffix.lower() in (".png",".jpg",".jpeg",".gif",".webp",".avif",".svg",".ico",".bmp")]
    if assets:
        errors.append({"kind":"standalone_image_asset","files":assets})
    record=json.loads((ROOT/"final-validation-checkpoint.json").read_text())
    changed=git("diff","--name-only",BASELINE,"HEAD","--","*.html").splitlines()
    repair_by={}
    for repair in record["repairs"]:
        for c in repair["changes"]:
            if c["file"].endswith(".html"):
                repair_by[c["file"]]=c
    if set(changed)!=set(repair_by):
        errors.append({"kind":"preservation","unexpected_or_missing_html_changes":sorted(set(changed)^set(repair_by))})
    for filename in changed:
        before=subprocess.check_output(["git","show",BASELINE+":"+filename],cwd=ROOT).decode()
        after=(ROOT/filename).read_text()
        c=repair_by.get(filename,{})
        restored=after
        if c.get("original_reference"):
            old=c["original_reference"]
            match=re.search(r'\bsrc=(["\'])(data:image/[^"\']+)\1',after)
            # Select the data URI whose decoded bytes match the recorded verified source.
            candidates=list(re.finditer(r'\bsrc=(["\'])(data:image/[^"\']+)\1',after))
            found=[]
            for match in candidates:
                uri=match.group(2)
                head,payload=uri.split(",",1)
                raw=base64.b64decode(payload) if ";base64" in head else urllib.parse.unquote_to_bytes(payload)
                if digest(raw)==c.get("source_member_sha256"):
                    found.append(match)
            # An accepted sibling inline figure can share bytes; restore the location that exactly reproduces baseline.
            for match in found:
                trial=after[:match.start(2)]+old+after[match.end(2):]
                if trial==before:
                    restored=trial
                    break
        elif filename=="old-grand-dad-114.html":
            restored=after.replace('<span>High</span>\n<div class="scoreline"><span>Sweetness</span>',
                                   '<span>High</span></div>\n<div class="scoreline"><span>Sweetness</span>',1)
        elif filename=="index.html":
            new="function sortValue(r){return sortKey==='overall'&&r.dataset.overall!==''?Math.sqrt(Number(r.dataset.quality)*Number(r.dataset.value)):r.dataset[sortKey];}\nfunction cmp(a,b){let av=sortValue(a),bv=sortValue(b);"
            old="function cmp(a,b){let av=a.dataset[sortKey],bv=b.dataset[sortKey];"
            restored=after.replace(new,old,1)
        else:
            if before.replace("</meta>","")==after:
                restored=before
        if restored!=before:
            errors.append({"kind":"preservation","file":filename,"message":"Changes exceed the recorded defect-only edit"})
    if git("rev-parse",BASELINE+":image-embedding-checkpoint.json")!=git("rev-parse","HEAD:image-embedding-checkpoint.json"):
        errors.append({"kind":"preservation","file":"image-embedding-checkpoint.json","message":"Completed ledger bytes changed"})
    if (ROOT/"whiskey-data.json").exists():
        exported=json.loads((ROOT/"whiskey-data.json").read_text())
        if {r["filename"]:r for r in exported}!=md_by:
            errors.append({"kind":"export_parity","file":"whiskey-data.json"})
    unique={im["sha256"] for item in inspected for im in item["images"]}
    report={"schema":"old-oak-static-validation-v1","accepted_content_commit":git("rev-parse","HEAD"),"dossiers_validated":825,"index_validated":True,
            "html_files_validated":826,"local_references_checked":local_count,"embedded_image_occurrences":sum(im["occurrences"] for item in inspected for im in item["images"]),
            "unique_embedded_payloads_decoded":len(unique),"standalone_image_assets_absent":not assets,
            "preservation_baseline":BASELINE,"completed_image_ledger_byte_identical":True,
            "dossier_index_count":len(rows),"missing_dossier_targets":0 if set(targets)==dossier_names else len(set(targets)-dossier_names),
            "orphan_dossiers":len(dossier_names-set(targets)),"duplicate_dossier_links":len(targets)-len(set(targets)),
            "failure_counts":dict(Counter(e["kind"] for e in errors)),"failures":errors,
            "file_manifest":[{k:item[k] for k in ("file","sha256","bytes")} for item in inspected],
            "timestamp":datetime.now(timezone.utc).isoformat(),"status":"passed" if not errors else "failed"}
    (OUT/"static-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("STATIC_VALIDATION_RESULT "+json.dumps({k:v for k,v in report.items() if k!="file_manifest"},ensure_ascii=False,separators=(",",":")))
    sys.exit(bool(errors))
if __name__=="__main__":
    {"recover":recover,"validate":validate}[sys.argv[1]]()
