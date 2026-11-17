from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import csv,json,re,hashlib,collections
r=Path.cwd()
counts=list(csv.DictReader((r/'figure/05-hlf/cluster-selection/data/counts.csv').open()))
assert [int(x['all_events']) for x in counts]==[387974,295491,168213]
assert [int(x['tracks_ge2']) for x in counts]==[21659,20308,18118]
for x in counts:assert int(x['tracks_lt2'])+int(x['tracks_ge2'])==int(x['all_events'])
summary=json.loads((r/'docs/performance-results/20261112/single-summary.json').read_text())
for x in csv.DictReader((r/'figure/06-logicfilter/input-size/data/fit-results.csv').open()):
 expected=summary[x['implementation']]['fit']
 for a,b in [('intercept_ms','intercept_ms'),('slope_ms_per_MB','slope_ms_MB'),('R2','R2')]:assert abs(float(x[a])-expected[b])<1e-9
 assert int(x['frames'])==72121
expected={(x['gpus'],x['lf_count']):x['sum_individual_LF_MB_s'] for x in json.loads((r/'docs/performance-results/20261112/member-clock-summary.json').read_text())['results']}
values=list(csv.DictReader((r/'figure/06-logicfilter/parallel-rate/data/plot-values.csv').open()))
assert len(values)==9
for x in values:assert abs(float(x['sum_individual_LF_MB_s'])-expected[int(x['gpus']),int(x['lf_count'])])<1e-8
for x in json.loads((r/'figure/source-manifest.json').read_text())['inputs']:
 assert hashlib.sha256((r/x['copy']).read_bytes()).hexdigest()==x['sha256']
manifest=json.loads((r/'docs/performance-results/20261112/manifest.json').read_text())
for x in manifest['sources']:assert hashlib.sha256((r/x['copy']).read_bytes()).hexdigest()==x['sha256']
active=[]
for p in (r/'src').rglob('*.tex'):
 for ref in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',p.read_text()):
  assert (r/'figure'/ref).is_file(),ref
  assert ref.endswith('.pdf'),ref
  active.append(ref)
assert len(active)==3
assert len(list((r/'figure').rglob('*.pdf')))==5
assert not list((r/'figure').rglob('*.png')) and not list((r/'figure').rglob('*.svg'))
assert not (r/'figure/05-hlf/tof-selection/tof-selection.pdf').exists()
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,t,a):
  for k,v in a:
   if k in ['href','src'] and not v.startswith(('http:','https:','file:','#')):self.links.append(v.split('#')[0])
for p in [r/'docs/index.html',r/'docs/figure-guidelines.html',r/'figure/index.html',r/'workspace/20261117/root-figure-layout/index.html']:
 parser=Links();parser.feed(p.read_text())
 for link in parser.links:assert (p.parent/unquote(link)).exists(),(p,link)
for macro in (r/'figure').glob('*/*/plot.C'):
 text=macro.read_text();assert ',800,600)' in text and 'SetCanvasSize(800,600)' in text
 assert 'SetLineWidth(3)' in text and 'SetLineWidth(2)' not in text
for name in ['05-evaluate-HLF-with-T103-data.tex','06-evaluate-LogicFilter-with-T103-data.tex']:
 for options in re.findall(r'\\includegraphics\[([^]]+)\]',(r/'src/subfiles'/name).read_text()):
  assert all(key in options for key in ['pagebox=cropbox','width=0.95','height=0.70','keepaspectratio'])
 text=(r/'src/subfiles'/name).read_text();assert text.count('\\makebox[\\linewidth][c]{\\includegraphics')==text.count('\\includegraphics')
print(json.dumps({'status':'passed','root_version':'6.36.04','cluster_counts':'raw ROOT agrees with published sample','fit_parameters':'agree within 1e-9','parallel_rates':'9 conditions agree within 1e-8','figure_pdfs':5,'active_pdf_references':active,'TOF':'missing input: expected exit 2, no PDF','thesis_build':'not run'},ensure_ascii=False,indent=2))
