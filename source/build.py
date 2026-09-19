from pathlib import Path
from learning_points import POINTS
import json,re,html,copy
from learning import ROUTE, CONTEXT, home
ROOT=Path(__file__).resolve().parent
curriculum=json.loads((ROOT/'curriculum.json').read_text())
EXERCISES=curriculum['exercises']; MISSIONS=curriculum['missions']
s=json.loads((ROOT/'spec.json').read_text()); out=ROOT.parent; esc=html.escape
for asset in (ROOT/'assets').glob('*.svg'): (out/asset.name).write_bytes(asset.read_bytes())
cats={'p1':('START','起步'),'p2':('WRITE','文字'),'p3':('DATA','資料'),'p4':('VIS','視覺'),'p5':('DOC','NotebookLM 專題'),'p6':('TOOL','工具'),'p7':('FLOW','工作流程'),'p8':('FLOW','工作流程'),'mat':('MAT','素材')}
cards=[]; mapping={}
for sec in s['sections']:
 for i,c in enumerate(sec['cards']):
  prefix,cat=cats[sec['id']]; n=i+1+(8 if sec['id']=='p8' else 0)
  old=('MAT_'+chr(65+i) if sec['id']=='mat' else sec['prefix']+str(i if sec['id'] in ('p7','p8') else i+1))
  id=f'{prefix}-{n:02}'
  mapping[old]=id;cards.append(dict(c,id=id,old=old,category=cat))
# Reuse the notebook setup card here so learners can start the topic directly.
notebook_setup=copy.deepcopy(next(c for c in cards if c['id']=='WRITE-13'))
notebook_setup.update(id='DOC-00',old='',category='NotebookLM 專題',title='建立骨鬆衛教資料筆記本')
cards.append(notebook_setup)
# Correct outdated editorial references before applying stable identifiers.
fixes={}
def tx(t):
 for a,b in fixes.items(): t=t.replace(a,b)
 t=re.sub(r'素材 ([A-H])',lambda m:mapping['MAT_'+m[1]],t)
 t=re.sub(r'(?<![A-Za-z0-9_])(?:MAT_[A-H]|[A-H]\d+)(?!\d)',lambda m:mapping.get(m[0],m[0]),t)
 return t
prompts={k:tx(v) for k,v in s['prompts'].items()}
prompts['A1']=prompts['A1'].replace('醫療院所衛教與病人溝通工作的 AI 助理。我是機構的內勤同仁','衛教與病人溝通工作的 AI 助理。我是內勤同仁')
payload={}; titles={c['id']:c['title'] for c in cards}
for c in EXERCISES: titles[c['id']]=c['title']
def button(text,label='複製提詞',style=''):
 key='copy'+str(len(payload));payload[key]=text
 return f'<button class="{style}" data-copy="{key}">{esc(label)}</button>'
def checks(items,id):
 return '<fieldset><legend>成果驗收</legend>'+''.join(f'<label><input type="checkbox" data-save="{id}-check-{i}">{tx(t)}</label>' for i,t in enumerate(items))+'</fieldset>'
def notes(id):
 return f'<details><summary>記錄成果與工作應用</summary><label>成果摘要／待確認事項<textarea data-save="{id}-notes" placeholder="記錄虛構練習成果，請勿輸入真實個資。"></textarea></label><label>回到我的工作：要替換的資料與保留的檢查<textarea data-save="{id}-transfer"></textarea></label></details>'
DISPLAY={'START':'起步','WRITE':'文字','DATA':'資料','VIS':'圖像','DOC':'文件','TOOL':'工具','FLOW':'流程','CASE':'任務','MAT':'素材','PIC':'圖片簡報','PRO':'專業簡報','SEARCH':'搜尋','READ':'讀圖','VOICE':'語音','ROLE':'演練'}
def chinese_labels(text):
 return re.sub(r'\b(START|WRITE|DATA|VIS|DOC|TOOL|FLOW|CASE|MAT|PIC|PRO|SEARCH|READ|VOICE|ROLE)-(\d+)',lambda m:DISPLAY[m[1]]+m[2],text)
def shell(title,body,page):
 # Translate visible labels only; stable link anchors and stored keys remain compatible.
 body=''.join(part if part.startswith('<') else chinese_labels(part) for part in re.split(r'(<[^>]+>)',body))

 nav=''.join(f'<a {"aria-current=page" if page==p else ""} href="{p}">{n}</a>' for p,n in [('index.html','學習入口'),('practice.html','基礎練習'),('missions.html','整合任務'),('materials.html','素材中心')])
 used=set(re.findall(r'data-copy="([^"]+)"',body))
 data=json.dumps({k:v for k,v in payload.items() if k in used},ensure_ascii=False).replace('<','\\u003c')
 return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light dark"><title>{title}｜嘉義醫院 AI 實作</title><style>{(ROOT/'style.css').read_text()}</style></head><body><a class="skip" href="#main">跳到內容</a><header><div class="brand">嘉義醫院 <span>骨鬆衛教 AI 實作</span></div><nav aria-label="主導覽">{nav}</nav></header><main id="main">{body}</main><footer>醫療人員教學版 · 虛構個案與理解測驗資料，非院內正式規範 · 衛教內容須臨床審閱<br>紀錄僅存在目前瀏覽器；清除瀏覽器資料可能遺失。<div class="actions"><button id="export">匯出練習紀錄</button><button id="reset">清除練習紀錄</button></div></footer><div id="toast" role="status" aria-live="polite"></div><dialog id="copyDialog"><h2>手動複製</h2><p>瀏覽器未允許自動複製，請選取以下內容。</p><textarea id="manual" aria-label="待複製內容" readonly></textarea><button id="selectAll">全選文字</button><button id="closeDialog">關閉</button></dialog><script>const COPY={data};\n{(ROOT/'app.js').read_text()}</script></body></html>'''
def filters(options, tabs=False):
 if tabs:
  names={'使用工具':'0、使用工具','起步':'一、起步體驗','文字':'二、文字練習','資料':'三、數據處理','視覺':'四、圖像設計','NotebookLM 專題':'五、NBLM應用','圖片簡報':'六、圖片簡報','專業簡報':'七、專業簡報','工具':'八、小工具製作','工作流程':'九、工作流程','搜尋查證':'十、搜尋查證','圖片理解':'十一、圖片理解','語音應用':'十二、語音應用','角色演練':'十三、角色演練'}
  return '<div class="category-bar"><p class="category-label">練習頁籤</p><div class="category-tabs" role="group" aria-label="基礎練習分類">'+''.join(f'<button type="button" data-category-tab="{x}" aria-pressed="false">{names.get(x,"全部練習")}</button>' for x in ['使用工具']+options)+'</div></div><div class="filters"><label>搜尋卡號或關鍵字<input id="search" type="search" placeholder="例如 文字08、會議紀錄、查錯"></label><label class="inline"><input type="checkbox" id="unfinished">只看未完成</label></div><p id="count" role="status"></p><p id="empty" hidden>此頁籤沒有符合的練習。請調整搜尋條件或切換頁籤。</p>'
 return '<div class="filters"><label>搜尋卡號或關鍵字<input id="search" type="search" placeholder="例如 B8、會議紀錄、查錯"></label><label>練習分類<select id="category"><option value="">全部分類</option>'+''.join(f'<option>{x}</option>' for x in options)+'</select></label><label class="inline"><input type="checkbox" id="unfinished">只看未完成</label></div><p id="count" role="status"></p><p id="empty" hidden>沒有符合的練習。請更換關鍵字或分類。</p>'
def article(id,title,cat,body,old='',minutes='',extra=''):
 point='<p class="learning-point">'+esc(POINTS[id])+'</p>' if cat!='素材' else ''
 info=next((e for e in EXERCISES+MISSIONS if e['id']==id),None)
 guidance=''
 if cat!='素材':
  use,avoid,finish=(info or {}).get('context',CONTEXT.get(cat,('需要整理工作資訊時','資訊不足卻要求確定結論','需人工核對的草稿')))
  outcome=(info or {}).get('goal','')
  if outcome: finish=outcome+' '+finish
  else: finish='完成「'+title+'」的練習成果；'+finish+'。'
  guidance='<dl class="use-guide">'+''.join('<div><dt>'+label+'</dt><dd>'+esc(value)+'</dd></div>' for label,value in [('何時用',use),('何時不適合',avoid),('完成到哪裡',finish)])+'</dl>'

 if id.startswith('CASE-'):
  return f'<article class="exercise mission-card" id="{id}" data-category="{cat}" data-search="{esc(id+" "+title+" "+cat,quote=True)}"><details class="mission-fold"><summary><span class="meta">{id} · {cat}<span>{minutes}</span></span><h2>{esc(title)}</h2>{point}<span class="mission-teaser">{esc((info or {}).get("skills",""))}</span><span class="fold-label" aria-hidden="true"></span></summary><div class="mission-content">{guidance}{body}<div class="completion"><label><input type="checkbox" data-save="{id}-done" data-done>已完成本題並核對成果</label><a href="#{id}">本題連結</a><button type="button" data-collapse-mission>收合任務</button></div></div></details></article>'
 bridge=id in ('WRITE-13','WRITE-13A','WRITE-13B','DOC-00')
 if bridge: extra='<p class="course-label">課程銜接・NotebookLM</p>'+extra
 return f'<article class="exercise" id="{id}" data-category="{cat}" data-search="{esc(id+" "+old+" "+title+" "+cat,quote=True)}"><div class="meta">{id}  <span>{minutes}</span></div><h2>{esc(title)}</h2>{point}{extra}{guidance}{body}<div class="completion"><label><input type="checkbox" data-save="{id}-done" data-done>已完成本題並核對成果</label><a href="#{id}">本題連結</a></div></article>'
def render(c):
 id=c['id']; parts=[];keys=[]
 for b in c['blocks']:
  typ=b['type']
  if typ in ['do','note','warn']:parts.append(f'<p class="{typ}">{tx(b["html"])}</p>')
  elif typ=='row':
   parts.append('<div class="actions">'+''.join((button(prompts[i['key']],tx(i['label'])) if 'key' in i else '<a href="'+esc(i['url'],quote=True)+'" target="_blank" rel="noopener">'+esc(i['label'])+'</a>') for i in b['items'])+'</div>'); keys.extend(i['key'] for i in b['items'] if 'key' in i)
  elif typ=='details':parts.append(f'<details><summary>{b["summary"]}</summary><pre>{esc(prompts[b["key"]])}</pre></details>')
  elif typ=='ask':parts.append('<details><summary>繼續追問</summary><div class="actions">'+''.join(button(prompts[i['key']],tx(i['label'])) if i.get('key') else '<p>'+tx(i['label'])+'</p>' for i in b['items'])+'</div></details>')
  elif typ=='checks':parts.append(checks(b['items'],id))
  elif typ=='table':parts.append('<div class="tablewrap"><table><caption>'+tx(b.get('summary',''))+'</caption><thead><tr>'+''.join('<th>'+tx(x)+'</th>' for x in b['header'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+tx(x)+'</td>' for x in r)+'</tr>' for r in b['rows'])+'</tbody></table></div>')
  elif typ=='workmap':
   for i in range(1,4):
    parts.append(f'<label>情境 {i}<input data-save="map-{i}-context" placeholder="例：每月部門月會紀錄"></label><label>使用的練習<select data-save="map-{i}-card"><option value="">選擇練習</option>'+''.join(f'<option value="{k}">{k}｜{esc(v)}</option>' for k,v in titles.items() if not k.startswith('MAT'))+'</select></label>')
   parts.append('<button id="copyMap">複製我的工作地圖</button>')
 if c['category']=='素材':
  parts.insert(0,f'<div class="actions"><a href="downloads/{id}.txt" download>下載素材文字檔</a></div>')
  # Recompute usage rather than retaining stale hand-written card references.
  users=[x['id'] for x in cards if any(b['type']=='row' and any(i.get('key')==c['old'] for i in b['items']) for b in x['blocks']) and x['category']!='素材']
  parts.insert(0,'<p>使用本素材的練習：'+ '、'.join(f'<a href="practice.html#{x}">{x}</a>' for x in users)+'</p>')
 elif len(set(keys))>1 and any(k.startswith('MAT_') for k in keys):
  bundle=list(dict.fromkeys(keys));parts.insert(0,button('\n\n'.join(prompts[k] for k in bundle),'複製完整練習包','primary'))
 return article(id,tx(c['title']),c['category'],''.join(parts)+notes(id),c['old'],c.get('minutes',''))
practice=[c for c in cards if c['category']!='素材'];materials=[c for c in cards if c['category']=='素材']
body='<p class="eyebrow">基礎練習・單項能力</p><h1>先練一項，再串成工作流程。</h1><p class="lead">以骨鬆衛教為簡報主題，練習查證、講稿、圖像、組頁與互動。</p>'+filters(['起步','文字','資料','視覺','NotebookLM 專題','圖片簡報','專業簡報','工具','工作流程','搜尋查證','圖片理解','語音應用','角色演練'], tabs=True)
body+='<section id="TOOLS-00" class="tool-panel" hidden><h2>使用工具</h2><p><a href="sources.html">骨鬆衛教來源與使用範圍</a></p><p>選擇課堂指定或慣用工具即可；所有連結以新分頁開啟。</p><div class="actions"><a href="https://chatgpt.com/" target="_blank" rel="noopener noreferrer">ChatGPT ↗</a><a href="https://gemini.google.com/" target="_blank" rel="noopener noreferrer">Gemini ↗</a><a href="https://claude.ai/" target="_blank" rel="noopener noreferrer">Claude ↗</a><a href="https://notebooklm.google.com/" target="_blank" rel="noopener noreferrer">NotebookLM ↗</a></div></section>'
body+='<div class="actions"><a href="index.html#beginner">入門十題路線</a><a href="index.html#capabilities">AI 應用地圖</a></div>'
for e in EXERCISES:
 p=e['prompt']+'\n\n【練習素材】\n'+e['material']; b=f'<details><summary>1 · 讀素材，先自己試</summary><pre>{esc(e["material"])}</pre></details><details><summary>2 · 需要一點提示</summary><p>{e["hint"]}</p></details><details class="guided"><summary>3 · 展開完整提詞</summary><pre>{esc(e["prompt"])}</pre>{button(p,"複製提詞＋素材")}</details><details><summary>4 · 挑戰變化題</summary><p>{e["change"]}</p>{button(e["change"],"複製變化題")}</details>'+checks(e['checks'],e['id'])+notes(e['id'])
 if e['id']=='PRO-07': b='<p class="route-intro">PPT路線：專業簡報07 → 08 → 09。先做樣稿，再擴充與驗收。</p>'+b
 if e['id']=='PRO-10': b='<p class="route-intro">HTML路線：專業簡報10 → 11 → 12。先能播放，再加互動與交付驗收。</p>'+b
 if e.get('course_bridge'):
  b+='<div class="actions"><a href="#WRITE-13A">大綱發想</a><a href="#WRITE-13B">查資料填內文</a><a href="#DOC-08">接續：文件08 簡報製作</a></div>'
 if e.get('workbook'): b='<div class="actions"><a href="'+e['workbook']+'" download>下載 Excel 練習檔</a></div>'+b
 if e.get('copy_top'):
  b=re.sub(r'<button class="" data-copy="[^"]+">複製提詞＋素材</button>', '', b)
  copy_note=e.get('copy_note') or ('先將Excel附到AI對話，再貼上提詞。' if e.get('workbook') else '複製後，在提詞最後貼上13A的大綱，再送出。')
  b='<div class="actions">'+button(p if e.get('copy_bundle') else e['prompt'],'複製完整提詞','primary')+'</div><p class="note">'+copy_note+'</p>'+b
 if e.get('material_keys'):
  bundle=e['prompt']+'\n\n'+ '\n\n'.join(prompts[k] for k in e['material_keys'])
  b='<div class="actions">'+button(bundle,'複製完整提詞＋三份素材','primary')+'</div>'+b
 if e.get('asset'): b='<div class="actions"><a href="'+e['asset']+'" target="_blank">開啟練習圖片</a><a href="'+e['asset']+'" download>下載練習圖片</a></div><p class="note">若 AI 不接受 SVG，開啟圖片後截圖，再將截圖附上。</p>'+b
 if e.get('prompt_steps'):
  b=re.sub(r'<button class="" data-copy="[^"]+">複製提詞＋素材</button>', '', b)
  b='<div class="actions">'+''.join(button(text,label,'primary') for label,text in e['prompt_steps'])+'</div><p class="note">先複製第一步並生成人物，確認後再複製第二步。完整提詞可在下方展開查看。</p>'+b
 if e.get('previous'): b='<p>接續練習：<a href="#'+e['previous']+'">'+e['previous']+'｜'+esc(titles[e['previous']])+'</a>。可沿用前題成果；若從本題開始，請先閱讀本題完整素材。</p>'+b
 if e.get('sources'): b+='<details><summary>設計原則與參考來源</summary><p>本題是依以下原則設計的課堂練習；數據及組織皆為虛構，時間為教學估計。</p><ul>'+''.join('<li><a target="_blank" rel="noopener" href="'+esc(url,quote=True)+'">'+esc(label)+'</a></li>' for label,url in e['sources'])+'</ul></details>'
 body+=article(e['id'],e['title'],e['category'],b,minutes=e['minutes'],extra='')
body+=''.join(render(c) for c in practice)
# Keep each category in stable numeric order, including newly added cards.
article_pattern=r'<article class="exercise".*?</article>'
ordered_articles=re.findall(article_pattern,body,re.S)
category_order=['START','WRITE','DATA','VIS','DOC','PIC','PRO','TOOL','FLOW','SEARCH','READ','VOICE','ROLE']
def article_order(markup):
 identifier=re.search(r' id="([A-Z]+)-(\d+)([A-Z]?)"',markup)
 return (category_order.index(identifier[1]),int(identifier[2]),identifier[3])
ordered_articles.sort(key=article_order)
article_iterator=iter(ordered_articles)
body=re.sub(article_pattern,lambda _:next(article_iterator),body,flags=re.S)
(out/'practice.html').write_text(shell('基礎練習',body,'practice.html'))
body='<p class="eyebrow">整合任務・跨能力應用</p><h1>完成一份骨鬆衛教簡報。</h1><p class="lead">從內容、視覺、互動或試講選一條路線，展開步驟開始練習。</p><label class="mode">練習方式<select id="mode"><option value="guided">引導版：提供提詞與提示</option><option value="challenge">挑戰版：先自行規劃，隱藏提示與提詞</option></select></label>'+filters([m['category'] for m in MISSIONS])
for m in MISSIONS:
 id=m['id'];b=f'<p class="lead">{m["skills"]}</p><p>{m["goal"]}</p><p>素材：'+ '、'.join(f'<a href="materials.html#{mapping[k]}">{mapping[k]}</a>' for k in m['materials'])+'</p>'
 if m.get('presentation'):
  bridge=m['presentation']
  b+='<div class="presentation-bridge"><h3>接到'+bridge['series']+'</h3><p>'+esc(bridge['input'])+' → '+esc(bridge['output'])+'</p><div class="actions">'+''.join('<a href="practice.html#'+x+'" target="_blank" rel="noopener">'+x+'｜'+esc(titles[x])+'</a>' for x in bridge['links'])+'</div><p class="note">參考方法會另開頁面；回到本任務，沿用已完成的資料製作簡報。</p></div>'
 mat='\n\n'.join(prompts[k] for k in m['materials'])
 b+=button(mat,'複製本題全部素材')+f'<details><summary>挑戰任務書：先自行設計步驟</summary><p>請交付：{m["goal"]}</p><p>自行決定工具、提詞與順序；必須保留來源、待確認資訊與修改紀錄。完成後使用下方成果驗收核對。</p></details>'
 for i,(name,prompt,hint) in enumerate(m['steps'],1):
  full=prompt+'\n\n【練習素材】\n'+mat+('\n\n【前一步已核對的成果，請自行貼在下方】\n' if i>1 else '')
  b+=f'<section class="step"><h3><span>0{i}</span> {name}</h3><p>{"先閱讀原始素材，建立可核對的第一份成果。" if i==1 else "帶入前一步已核對的成果，完成本步交付；未確認事項保留標記。"}</p><details class="guided"><summary>提示與本步提詞</summary><p>{hint}</p><pre>{esc(prompt)}</pre>{button(full,"複製本步提詞＋素材")}</details><label>本步成果／待確認事項<textarea data-save="{id}-step-{i}" placeholder="記錄成果；下一步請帶入已核對的內容。"></textarea></label></section>'
 b+=f'<details><summary>變化題：需求改變了</summary><p>{m["change"]}</p>{button(m["change"],"複製變化題")}</details>'+checks(m['checks'],id)+f'<details><summary>驗收依據：完成後再看</summary><p>{m["rubric"]}</p></details><p>可回頭練：'+'、'.join(f'<a href="practice.html#{x}">{x} {esc(titles[x])}</a>' for x in m['related'])+'</p>'+notes(id)
 body+=article(id,m['title'],m['category'],b,minutes=m['minutes'])
(out/'missions.html').write_text(shell('整合任務',body,'missions.html'))
body='<p class="eyebrow">素材中心・教學資料</p><h1>練習資料，集中取用。</h1><p class="lead">以下皆為虛構教材。以骨鬆衛教簡報為主軸；知識附來源，理解測驗數據為虛構示範。</p>'+filters(['素材'])+''.join(render(c) for c in materials)
(out/'materials.html').write_text(shell('素材中心',body,'materials.html'))
body=home(titles).replace('AI 工作坊','骨鬆衛教 AI 工作坊')
(out/'index.html').write_text(shell('學習入口',body,'index.html'))
(out/'downloads').mkdir(exist_ok=True)
for i,key in enumerate(['MAT_A','MAT_B','MAT_C','MAT_D','MAT_E','MAT_F','MAT_G','MAT_H'],1):
 (out/'downloads'/f'MAT-{i:02d}.txt').write_text(prompts[key])
(out/'numbering-v2.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
print('Built 4 pages; original cards:',len(practice),'new:',len(EXERCISES),'missions:',len(MISSIONS))

(out/'sources.html').write_text(shell('骨鬆衛教來源','<h1>骨鬆衛教來源</h1><p>查核日期：2026-09-19。以下為一般衛教依據，個別診療與院內規範仍須由臨床團隊確認。</p><pre>'+esc((ROOT/'骨鬆衛教來源.txt').read_text())+'</pre><div class="actions"><a href="materials.html#MAT-02">回到來源素材</a></div>','sources.html'))
