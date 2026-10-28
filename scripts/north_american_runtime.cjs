const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const cp = require('node:child_process');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.resolve(ROOT,'..','expansion-research','runtime-output');
const total=fs.readdirSync(ROOT).filter(f=>f.endsWith('.html')&&f!=='index.html').length;
const focused=process.argv.includes('--focused');
fs.mkdirSync(OUT,{recursive:true});
const report = {schema:'old-oak-runtime-validation-v1',accepted_content_commit:cp.execFileSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8'}).trim(),
  functional_cases:[],responsive_cases:0,dossiers_rendered:0,index_rendered:false,console_errors:[],page_errors:[],network_errors:[],
  failures:[],limitations:['Chromium headless validation against an HTTP server serving exact checked-out repository bytes; external editorial/source websites are outside this rendering test.','Representative viewport widths tested: 390, 768 and 1440 CSS pixels. No physical-device, Safari or Firefox run.']};
const failures = report.failures;
let server, browser;
function check(label,fn){try{fn();report.functional_cases.push({case:label,status:'passed'});}catch(e){failures.push({kind:'runtime',case:label,error:e.message});report.functional_cases.push({case:label,status:'failed'});}}
function observe(page){
  page.on('console',msg=>{if(msg.type()==='error')report.console_errors.push({page:page.url(),message:msg.text()});});
  page.on('pageerror',e=>report.page_errors.push({page:page.url(),error:e.message}));
  page.on('requestfailed',r=>report.network_errors.push({url:r.url(),error:r.failure()?.errorText}));
  page.on('response',r=>{if(r.status()>=400)report.network_errors.push({url:r.url(),status:r.status()});});
}
async function functional(page,BASE){
  await page.goto(BASE,{waitUntil:'load'});
  // The badge is part of the published reader experience, not just JSON metadata.
  // Its primary percentage must represent the entire accepted development roadmap.
  const manifest=JSON.parse(fs.readFileSync(path.join(ROOT,'site-progress.json'),'utf8'));
  const overall=manifest.roadmap.gates.filter(g=>g.status==='accepted').reduce((n,g)=>n+g.weight,0);
  await page.locator('#project-progress-status summary').waitFor({state:'visible',timeout:20000});
  const badge=await page.locator('#project-progress-status summary').innerText();
  check('Homepage revision matches roadmap',()=>assert.ok(badge.includes('Rev '+manifest.revision),badge));
  check('Homepage overall progress is roadmap-weighted, not phase-only',()=>assert.ok(badge.includes('Roadmap '+overall+'%'),badge));
  await page.locator('#project-progress-status summary').click();
  const roadmapHref=await page.locator('#project-progress-status .p-detail a').getAttribute('href');
  check('Expanded status links authoritative development roadmap',()=>assert.ok(roadmapHref.endsWith('/DEVELOPMENT-ROADMAP.md'),roadmapHref));
  const expandedStatus=await page.locator('#project-progress-status .p-detail').innerText();
  const phase=JSON.parse(fs.readFileSync(path.join(ROOT,'north-american-expansion-checkpoint.json'),'utf8'));
  check('Expanded status distinguishes editorial checkpoint',()=>assert.ok(expandedStatus.includes('NA-'+phase.checkpoint),expandedStatus));
  // Close the fixed overlay before testing controls underneath it.
  await page.locator('#project-progress-status summary').click();
  const original=await page.locator('#bottles tr' ).evaluateAll(rs=>rs.map(r=>({id:r.id,dataset:{...r.dataset},text:r.textContent,mash:r.querySelector('td.mash').textContent,href:r.querySelector('a').getAttribute('href')})));
  check(total+' unique dossier rows and dossier targets',()=>{assert.equal(original.length,total);assert.equal(new Set(original.map(r=>r.id)).size,total);assert.equal(new Set(original.map(r=>r.href)).size,total);});
  check('Old Oak title and application metadata',()=>{assert.equal(fs.readFileSync(path.join(ROOT,'index.html'),'utf8').includes('<title>Old Oak Omnibus</title>'),true);});
  const visible=()=>page.locator('#bottles tr').evaluateAll(rs=>rs.filter(r=>!r.hidden).map(r=>r.id));
  const expectedSort=(key,descending)=>{
    return [...original].sort((a,b)=>{
      let av=key==='mash'?a.mash:a.dataset[key],bv=key==='mash'?b.mash:b.dataset[key];
      if(av===''||bv==='')return av===''?(bv===''?a.dataset.name.localeCompare(b.dataset.name):1):-1;
      let n;
      if(['name','category','mash'].includes(key)) n=av.localeCompare(bv);
      else if(key==='overall') n=Math.sqrt(Number(a.dataset.quality)*Number(a.dataset.value))-Math.sqrt(Number(b.dataset.quality)*Number(b.dataset.value));
      else n=Number(av)-Number(bv);
      return (descending?-n:n)||a.dataset.name.localeCompare(b.dataset.name);
    }).map(r=>r.id);
  };
  for(const key of ['name','category','mash','proof','cost','age','quality','value','overall']){
    for(let attempt=0;attempt<2;attempt++){
      await page.locator('th[data-key="'+key+'"] button').click();
      const direction=await page.locator('th[data-key="'+key+'"]').getAttribute('aria-sort');
      const actual=await visible();
      check('Sort '+key+' '+direction,()=>assert.deepEqual(actual,expectedSort(key,direction==='descending')));
    }
  }
  await page.locator('#search').fill('OGD 114');
  const ogd=await visible();
  check('OGD alias returns the canonical and named 114 single-barrel expressions',()=>assert.deepEqual([...ogd].sort(),['old-grand-dad-114','old-grand-dad-114-single-barrel-7-year-bourbon'].sort()));
  const scores=await page.locator('#old-grand-dad-114 td.score').allTextContents();
  check('Canonical Quality Value Overall displays',()=>assert.deepEqual(scores.map(s=>s.trim()),['6.2','8.8','7.4']));
  await page.locator('#search').fill('NO_MATCH_OLD_OAK_COMPLETION_TEST');
  const emptyVisible=await page.locator('#empty').isVisible();
  check('Empty state visible and zero rows',()=>{assert.equal(emptyVisible,true);});
  assert.equal((await visible()).length,0);
  await page.locator('#search').fill('');
  for(const [selector,field] of [['#category','category'],['#family','groups'],['#basis','basis'],['#period','period'],['#calibration','qualityCalibration']]){
    const values=await page.locator(selector).evaluate(e=>[...e.options].map(o=>o.value));
    for(const value of values){
      await page.locator(selector).selectOption(value);
      const actual=await visible();
      const expected=original.filter(r=>value==='all'||(field==='groups'?r.dataset.groups.split('|').includes(value):r.dataset[field]===value)).map(r=>r.id).sort();
      check('Filter '+selector+' '+value,()=>assert.deepEqual([...actual].sort(),expected));
      const count=await page.locator('#count').textContent();
      check('Filter count '+selector+' '+value,()=>assert.equal(count,actual.length+' of '+total+' dossiers'));
      if(['#family','#period','#calibration'].includes(selector)){
        const key=selector==='#family'?'family':selector==='#period'?'period':'calibration';
        const actualParam=new URL(page.url()).searchParams.get(key);
        check('Filter URL '+selector+' '+value,()=>assert.equal(actualParam,value==='all'?null:value));
      }
    }
    await page.locator(selector).selectOption('all');
  }
  await page.locator('#family').selectOption('OldGrandDad');
  const familyBefore=await visible();
  await page.reload({waitUntil:'load'});
  const familyAfter=await visible();
  check('Family filter membership survives URL reload',()=>assert.deepEqual([...familyAfter].sort(),[...familyBefore].sort()));
  await page.locator('#search').fill('OGD 114');
  const combined=await visible();
  check('Combined family and alias query',()=>assert.deepEqual([...combined].sort(),['old-grand-dad-114','old-grand-dad-114-single-barrel-7-year-bourbon'].sort()));
  await page.locator('#old-grand-dad-114 a').click();
  await page.waitForURL('**/old-grand-dad-114.html');
  const title=await page.title();
  check('Dossier navigation reaches canonical title',()=>assert.ok(title.includes('Old Grand-Dad 114')));
  const navLinks=await page.locator('a[href]').evaluateAll(as=>as.map(a=>a.getAttribute('href')).filter(h=>h==='index.html'||h.startsWith('index.html?')));
  check('Canonical return navigation exists',()=>assert.ok(navLinks.length>0));
  await page.goBack({waitUntil:'load'});
  check('Browser back returns to family catalogue',()=>assert.ok(page.url().includes('family=OldGrandDad')));
}
async function responsive(context,BASE,files,width,height){
  let cursor=0;
  const workers=Array.from({length:4},async()=>{
    const page=await context.newPage();observe(page);
    await page.setViewportSize({width,height});
    while(cursor<files.length){
      const filename=files[cursor++];
      try{
        const response=await page.goto(BASE+filename,{waitUntil:'load',timeout:45000});
        if(response.status()!==200)throw Error('HTTP '+response.status());
        await page.locator('img').evaluateAll(async imgs=>{for(const im of imgs){im.scrollIntoView();await Promise.race([im.decode().catch(()=>{}),new Promise(resolve=>setTimeout(resolve,10000))]);}}); await page.evaluate(()=>scrollTo(0,0));
        const state=await page.evaluate(()=>({
          width:innerWidth,documentWidth:document.documentElement.scrollWidth,
          main:!!document.querySelector('main'),title:document.title,
          badImages:[...document.images].filter(i=>!i.complete||i.naturalWidth===0||i.naturalHeight===0).map(i=>({src:i.getAttribute('src')?.slice(0,100),alt:i.alt})),
          overflowElements:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+2||r.left< -2)&&getComputedStyle(e).position!=='fixed';}).slice(0,8).map(e=>({tag:e.tagName,class:e.className}))
        }));
        report.responsive_cases++;
        if(!state.main||!state.title.includes('Old Oak Omnibus'))failures.push({kind:'rendering_structure',file:filename,width,state});
        if(state.documentWidth>width+2)failures.push({kind:'responsive_overflow',file:filename,width,documentWidth:state.documentWidth,elements:state.overflowElements});
        if(state.badImages.length)failures.push({kind:'rendered_image',file:filename,width,images:state.badImages});
        if(filename==='index.html')report.index_rendered=true;
        if(filename==='index.html'||filename==='old-grand-dad-114.html'||state.documentWidth>width+2||state.badImages.length){
          const shots=path.join(OUT,'screenshots');fs.mkdirSync(shots,{recursive:true});
          await page.screenshot({path:path.join(shots,filename.replace('.html','')+'-'+width+'.png'),fullPage:false});
        }
      }catch(e){failures.push({kind:'browser_navigation',file:filename,width,error:e.message});}
    }
    await page.close();
  });
  await Promise.all(workers);
}
(async()=>{
  server=http.createServer((req,res)=>{
    const url=new URL(req.url,'http://localhost');
    const filename=decodeURIComponent(url.pathname)==='/'?'index.html':decodeURIComponent(url.pathname).slice(1);
    if(filename==='favicon.ico'){res.writeHead(204);res.end();return;}
    const target=path.resolve(ROOT,filename);
    if(!target.startsWith(ROOT+path.sep)||!fs.existsSync(target)||!fs.statSync(target).isFile()){res.writeHead(404);res.end('Missing file');return;}
    const type=target.endsWith('.html')?'text/html; charset=utf-8':target.endsWith('.json')?'application/json':'text/plain; charset=utf-8';
    res.writeHead(200,{'Content-Type':type});fs.createReadStream(target).pipe(res);
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const BASE='http://127.0.0.1:'+server.address().port+'/';
  browser=await chromium.launch(process.env.OLD_OAK_CHROMIUM_EXECUTABLE?{executablePath:process.env.OLD_OAK_CHROMIUM_EXECUTABLE}:{ });
  report.browser_version=browser.version();
  const context=await browser.newContext();
  // No source link is followed during rendering. Any unexpected external resource is recorded explicitly.
  await context.route('**/*',async route=>{
    const url=new URL(route.request().url());
    if(url.origin===new URL(BASE).origin)await route.continue();
    else{report.limitations.push('External render request excluded: '+url.origin);await route.abort();}
  });
  const page=await context.newPage();observe(page);
  try{await functional(page,BASE);}catch(e){failures.push({kind:'runtime',case:'Functional sequence',error:e.message});}
  await page.close();
  const allfiles=fs.readdirSync(ROOT).filter(f=>f.endsWith('.html')).sort();
  const sagamorePath=path.join(ROOT,'sagamore-expansion-data.json');
  const sagamoreFiles=fs.existsSync(sagamorePath)?JSON.parse(fs.readFileSync(sagamorePath,'utf8')).map(m=>m.filename):[];
  const files=focused?['index.html',...JSON.parse(fs.readFileSync(path.join(ROOT,'north-american-expansion-checkpoint.json'))).added_dossiers,...sagamoreFiles]:allfiles;
  assert.equal(allfiles.length,total+1);
  for(const [width,height] of [[390,844],[768,1024],[1440,900]])await responsive(context,BASE,files,width,height);
  report.dossiers_rendered=report.responsive_cases===(files.length*3)?files.length-1:Math.min(total,Math.floor(report.responsive_cases/3));
  if(report.console_errors.length)failures.push({kind:'console_errors',count:report.console_errors.length});
  if(report.page_errors.length)failures.push({kind:'page_errors',count:report.page_errors.length});
  if(report.network_errors.length)failures.push({kind:'network_errors',count:report.network_errors.length});
  report.status=failures.length?'failed':'passed';
})().catch(e=>{failures.push({kind:'validation_environment',error:e.stack});report.status='failed';}).finally(async()=>{
  if(browser)await browser.close();
  if(server)await new Promise(resolve=>server.close(resolve));
  report.limitations=[...new Set(report.limitations)];
  fs.writeFileSync(path.join(OUT,'runtime-report.json'),JSON.stringify(report,null,2)+'\n');
  console.log('RUNTIME_VALIDATION_RESULT '+JSON.stringify(report));
  process.exitCode=failures.length?1:0;
});
