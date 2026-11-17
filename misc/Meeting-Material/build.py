#!/usr/bin/env python3
"""Build title + draft abstract + current TOC in an isolated temporary copy."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,tempfile
root=Path(__file__).resolve().parents[2]
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y%m%d')
output=root/'misc/Meeting-Material'/f'{stamp}-kashima-MasterThesis.pdf'
work=Path(tempfile.mkdtemp(prefix='master-thesis-meeting-'))
if output.exists():shutil.copy2(output,work/'previous-output.pdf')
shutil.copytree(root/'src',work/'src');shutil.copyfile(root/'.latexmkrc',work/'.latexmkrc')
(work/'figure').symlink_to(root/'figure',target_is_directory=True)
abstract=work/'src/subfiles/02-abstract.tex';text=abstract.read_text()
start=text.index('\\begin{tcolorbox}');assert 'title=draft abstract' in text[start:start+120]
# Environments inside the draft box are nested: locate its actual matching end.
tokens=list(re.finditer(r'\\(begin|end)\{tcolorbox\}',text[start:]));depth=0;end=None
for token in tokens:
 depth+=1 if token.group(1)=='begin' else -1
 if depth==0:end=start+token.end();break
assert end is not None
abstract.write_text(text[:end]+'\n\\end{document}\n')
main=work/'src/main.tex';text=main.read_text().replace('\\notationnotestrue','\\notationnotesfalse')
main.write_text(text)
# First build all chapters solely to generate a complete, current table of contents.
with (work/'full-build.log').open('w') as log:
 subprocess.run(['latexmk','-r','.latexmkrc','src/main.tex'],cwd=work,stdout=log,stderr=subprocess.STDOUT,check=True)
toc=(work/'out/main.toc').read_bytes()
# Reuse that TOC without opening/replacing it; omit figure/table lists and chapters.
end=text.index('\\tableofcontents')+len('\\tableofcontents')
front=text[:end]+'\n\\clearpage\n\\end{document}\n'
front=front.replace('\\begin{document}','\\nofiles\n\\hypersetup{linktoc=none}\n\\begin{document}',1)
# Full-document bookmarks/labels point to excluded pages; do not import them.
for suffix in ['out','aux']:
 stale=work/f'out/main.{suffix}'
 if stale.exists():stale.unlink()
main.write_text(front)
with (work/'front-build.log').open('w') as log:
 subprocess.run(['platex','-kanji=utf8','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory=../out','main.tex'],cwd=work/'src',stdout=log,stderr=subprocess.STDOUT,check=True)
 subprocess.run(['dvipdfmx','-o',str(output),str(work/'out/main.dvi')],cwd=work/'src',stdout=log,stderr=subprocess.STDOUT,check=True)
assert toc==(work/'out/main.toc').read_bytes()
manifest={'date_jst':stamp,'output':str(output.relative_to(root)),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'temporary_workspace':str(work),'includes':['title','draft abstract box only','complete current table of contents'],'excludes':['notation notes','past thesis abstract notes','figure list','table list','body','appendices'],'source_files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root/'src').rglob('*.tex'))},'original_out_main_pdf_modified':False}
output.with_suffix('.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(output);print('Temporary logs:',work)
