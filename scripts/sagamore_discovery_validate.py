#!/usr/bin/env python3
"""Check the finite Sagamore inventory against preserved published content."""
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
LEDGER=ROOT/'sagamore-expression-ledger.json'
def main():
    data=json.loads(LEDGER.read_text(encoding='utf-8'))
    entries=data['entries'];counts=data['counts'];errors=[]
    if data.get('schema')!='old-oak-sagamore-discovery-ledger-v1':errors.append('Unknown inventory schema')
    if len({e['id'] for e in entries})!=len(entries):errors.append('Duplicate expression IDs')
    if [e['order'] for e in entries]!=list(range(1,len(entries)+1)):errors.append('Non-deterministic ordering')
    for key in ('existing_published','accepted_published','pending_research','excluded_pending_liquid_distinction'):
        if sum(e['decision']==key for e in entries)!=counts.get(key):errors.append('Wrong '+key+' count')
    if len(entries)!=counts['total']:errors.append('Wrong total')
    if data['baseline_publication']['north_american_checkpoint']!=37:errors.append('Expected accepted NA-037')
    if len(list(ROOT.glob('sagamore-*.html')))!=counts['existing_published']+counts.get('accepted_published',0):
        errors.append('Unexpected Sagamore article count: review this new batch and update inventory')
    for e in entries:
        if not e['producer_source'].startswith('https://'):
            errors.append('No source URL: '+e['id'])
        if e['decision'] in ('existing_published','accepted_published') and not (ROOT/e['filename']).is_file():
            errors.append('Missing preserved article: '+e['filename'])
        if e['decision']=='pending_research' and (ROOT/e['filename']).exists():
            errors.append('Unaccepted candidate file exists: '+e['filename'])
        if e['decision']=='excluded_pending_liquid_distinction' and e['filename'] is not None:
            errors.append('Excluded candidate has filename: '+e['id'])
    current=json.loads((ROOT/'north-american-expansion-checkpoint.json').read_text(encoding='utf-8'))
    if current['checkpoint']!=37 or current['status']!='complete':
        errors.append('Sagamore phase requires accepted NA-037 closure')
    report={'schema':'sagamore-discovery-validation-v1','existing':counts['existing_published'],
            'accepted_new':counts.get('accepted_published',0),
            'pending':counts['pending_research'],'excluded':counts['excluded_pending_liquid_distinction'],
            'status':'passed' if not errors else 'failed','errors':errors}
    print(json.dumps(report))
    return 0 if not errors else 1
if __name__=='__main__':sys.exit(main())
