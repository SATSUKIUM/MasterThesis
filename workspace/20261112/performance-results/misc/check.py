from pathlib import Path
import re,json,hashlib,subprocess,collections
root=Path.cwd();snap=root/'docs/performance-results/20261112';manifest=json.loads((snap/'manifest.json').read_text())
for f in manifest['sources']:
 p=root/f['copy'];assert p.is_file();assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
changed=['05-evaluate-HLF-with-T103-data.tex','06-evaluate-LogicFilter-with-T103-data.tex','07-apply-to-E50.tex','09-references.tex','10-appendix.tex']
for name in changed:
 s=(root/'src/subfiles'/name).read_text();s=re.sub(r'(?m)(?<!\\)%.*','',s)
 stack=[]
 for op,env in re.findall(r'\\(begin|end)\{([^}]+)\}',s):
  if op=='begin':stack.append(env)
  else:assert stack and stack.pop()==env,(name,env,stack)
 assert not stack,(name,stack)
 for f in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',s):assert (root/'figure'/f).is_file(),f
 assert '（' not in s and '）' not in s,name
 # Inline-code segments can contain underscores and TeX-like syntax; leave them literal.
 braces=re.sub(r'\\lstinline(.).*?\1','',s)
 depth=0
 for c in re.findall(r'(?<!\\)[{}]',braces):
  depth+=1 if c=='{' else -1
  assert depth>=0,name
 assert depth==0,(name,depth)
alltex='\n'.join((root/'src/subfiles'/n).read_text() for n in changed)
bibs=set(re.findall(r'\\bibitem\{([^}]+)\}',alltex))
for cite in re.findall(r'\\cite\{([^}]+)\}',alltex):assert set(cite.split(','))<=bibs,cite
labels=re.findall(r'\\label\{([^}]+)\}',alltex);assert len(labels)==len(set(labels))
for ref in re.findall(r'\\ref\{([^}]+)\}',alltex):assert ref in labels,ref
single=json.loads((snap/'single-summary.json').read_text());lf=(root/'src/subfiles/06-evaluate-LogicFilter-with-T103-data.tex').read_text()
for typ in ['CPU','GPU']:
 r=single[typ];assert abs(r['input_bytes']/r['process_us_sum']-r['process_MB_s'])<1e-9
 assert f"{r['process_MB_s']:.2f}" in lf and f"{r['mean_process_ms']:.3f}" in lf
 for key in ['intercept_ms','slope_ms_MB','R2']:assert f"{r['fit'][key]:.4f}" in lf
parallel=json.loads((snap/'member-clock-summary.json').read_text())
assert len(parallel['results'])==9
for r in parallel['results']:
 expected=sum(p['input_bytes']/p['net_us_sum'] for p in r['processes']);assert abs(expected-r['sum_individual_LF_MB_s'])<1e-8
 assert sum(p['received_frames'] for p in r['processes'])==288484
 assert sum(p['input_bytes'] for p in r['processes'])==102798031744
 assert f"{r['gpus']} & {r['lf_count']} & {expected:.1f}" in lf
 assert abs(expected-r['actual_wall_input_MB_s'])>1
base=subprocess.check_output(['git','show','HEAD:src/subfiles/10-appendix.tex'],text=True)
actual=(root/'src/subfiles/10-appendix.tex').read_text();marker='\\section{計測環境の詳細}'
assert base.split(marker,1)[1]==actual.split(marker,1)[1]
basehlf=subprocess.check_output(['git','show','HEAD:src/subfiles/05-evaluate-HLF-with-T103-data.tex'],text=True)
hlf=(root/'src/subfiles/05-evaluate-HLF-with-T103-data.tex').read_text()
for box in re.findall(r'\\begin\{tcolorbox\}.*?\\end\{tcolorbox\}',basehlf,re.S):assert box in hlf
assert 4*2**19/1e6==2.097152
for key,value in [('594.9',594.9),('442.9',442.9),('123.4',123.4)]:assert key in hlf
print(json.dumps({'source_hashes':len(manifest['sources']),'changed_tex_files':len(changed),'parallel_cases':len(parallel['results']),'per_process_records':sum(len(r['processes']) for r in parallel['results']),'bibliography_entries':len(bibs),'all_checks':'passed','pdf_build':'not run'},ensure_ascii=False,indent=2))
