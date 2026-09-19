from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import json,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.copies=[];self.exercises=[];self.points=[];self.inpoint=False;self.point=''
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id'in a:self.ids.append(a['id'])
  if 'href'in a:self.links.append(a['href'])
  if 'data-copy'in a:self.copies.append(a['data-copy'])
  if t=='article' and 'exercise'in a.get('class',''):self.exercises.append((a['id'],a.get('data-category')))
  if t=='p' and a.get('class')=='learning-point':self.inpoint=True;self.point=''
 def handle_data(self,d):
  if self.inpoint:self.point+=d
 def handle_endtag(self,t):
  if t=='p' and self.inpoint:self.points.append(self.point);self.inpoint=False
pages={}
for file in ['index.html','practice.html','missions.html','materials.html','sources.html']:
 s=(ROOT/file).read_text();p=Page();p.feed(s);pages[file]=p
 assert len(p.ids)==len(set(p.ids)),file
 script=re.search(r'<script>(.*?)</script>',s,re.S).group(1)
 payload=json.loads(script[len('const COPY='):script.index(';\n')]);assert set(p.copies)==set(payload),file
 assert not re.search('寶佳|社福|捐款|兒少|暖冬|志工|世界展望',s),file
 with tempfile.NamedTemporaryFile('w',suffix='.js') as tmp:
  tmp.write(script);tmp.flush();subprocess.run(['node','--check',tmp.name],check=True)
 for point in p.points:assert len(point)<=25,(file,point)
for file,p in pages.items():
 for href in p.links:
  u=urlsplit(href)
  if u.scheme or u.netloc:continue
  target=unquote(u.path) or file
  assert (ROOT/target).exists(),(file,href)
  if u.fragment and target in pages:assert unquote(u.fragment) in pages[target].ids,(file,href)
assert len(pages['practice.html'].exercises)==115
assert len(pages['missions.html'].exercises)==8
assert len(pages['materials.html'].exercises)==8
assert len(pages['practice.html'].points)==115
assert 'TOOLS-00' in pages['practice.html'].ids
print('PASS: 115 exercises in 13 chapters; 8 missions; 8 materials; copy payloads; links; JavaScript; learning points.')
print(Counter(c for _,c in pages['practice.html'].exercises))

# Check delivered content, including hidden prompt payloads and downloadable sources.
import zipfile
for path in ROOT.rglob('*'):
 if path.suffix in ['.html','.txt','.svg']:
  text=path.read_text()
 elif path.suffix=='.xlsx':
  with zipfile.ZipFile(path) as z:
   text=' '.join(z.read(n).decode() for n in z.namelist() if n.endswith('.xml'))
 else:continue
 for term in ['活動企劃','活動預算','活動招募','活動成果','護骨行動','支援同仁','報名名單','簽到表','物資採購','衛教量統計','全年衛教量','季度骨鬆衛教接觸人次']:
  assert term not in text,(path.name,term)
print('PASS: all delivered pages, copy payloads, sources, SVGs and XLSX use the presentation curriculum.')
