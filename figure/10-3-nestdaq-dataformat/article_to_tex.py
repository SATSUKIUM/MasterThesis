#!/usr/bin/env python3
"""Typeset chapters 1-5 of the retained explanatory HTML, preserving its text and diagrams."""
from pathlib import Path
from html.parser import HTMLParser
import re,json,hashlib
P=Path(__file__).resolve().parent
class Node:
 def __init__(self,tag='',attrs=()):self.tag=tag;self.a=dict(attrs);self.children=[]
 def text(self):return ''.join(c if isinstance(c,str) else c.text() for c in self.children)
 def walk(self,tag):
  if self.tag==tag:yield self
  for c in self.children:
   if isinstance(c,Node):yield from c.walk(tag)
class Parse(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.root=Node('root');self.stack=[self.root]
 def handle_starttag(self,t,a):
  n=Node(t,a);self.stack[-1].children.append(n)
  if t not in ['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']:self.stack.append(n)
 def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:self.stack=self.stack[:i];break
 def handle_data(self,s):self.stack[-1].children.append(s)

def esc(s):
 table={'\\':r'\textbackslash{}','{':r'\{','}':r'\}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','~':r'\textasciitilde{}','^':r'\textasciicircum{}','µ':r'$\mu$','μ':r'$\mu$','Σ':r'$\sum$','≤':r'$\leq$','≥':r'$\geq$','×':r'$\times$','→':r'$\rightarrow$','₀':r'$_0$','₁':r'$_1$','₂':r'$_2$','⁶':r'$^6$'}
 return ''.join(table.get(c,c) for c in re.sub(r'\s+',' ',s))

def inline(n):
 if isinstance(n,str):return esc(n)
 t=n.tag
 if t=='br':return ' '
 if t in ['script','style','img']:return ''
 body=''.join(inline(c) for c in n.children)
 if t=='code':return r'\texttt{'+body.replace(r'\_',r'\_\allowbreak{}').replace('::',r'::\allowbreak{}')+'}'
 if t in ['b','strong']:return r'\textbf{'+body+'}'
 if t in ['i','em']:return r'\textit{'+body+'}'
 if t=='sub':return r'\textsubscript{'+body+'}'
 if t=='sup':return r'\textsuperscript{'+body+'}'
 if t=='a':
  href=n.a.get('href','')
  if body.strip() in ['SVG原寸','検証記録']:return ''
  # Source anchors are retained as exact filenames/line numbers in an appendix ledger.
  if href.startswith('sources.html#'):
   token=href.split('#',1)[1];anchors.add(token)
   return body
  if href.startswith('#') and href[1:] in ids:return body
  return body
 return body

parser=Parse();html=P/'article/index.html';parser.feed(html.read_text());main=next(parser.root.walk('main'))
ids={n.a['id'] for tag in ['section','h2','h3'] for n in main.walk(tag) if 'id' in n.a}
anchors=set();figure_names=[];table_count=0;paragraphs=[];headings=[]

def figure(n,caption=None):
 name=Path(n.a['src']).stem
 if name in figure_names:return ''
 figure_names.append(name)
 title=caption or n.a.get('alt',name)
 title=re.sub(r'^図\d+[：:]','',title).replace('SVG原寸','').strip()
 title=title.replace(' output structure','の構造').replace(' byte layout','のバイト配置').replace(' bit layout','のビット配置')
 return '\n図'+r'\ref{fig:format-svg-'+name+'}に示す。\n'+r'\begin{figure}[htbp]\centering'+'\n'+r'\makebox[\linewidth][c]{\includegraphics[pagebox=cropbox,width=0.95\linewidth,height=0.70\textheight,keepaspectratio]{../figure/10-3-nestdaq-dataformat/pdf/'+name+r'.pdf}}'+'\n'+r'\caption{'+esc(title)+r'}\label{fig:format-svg-'+name+r'}\end{figure}'+'\n'

def table(n):
 global table_count
 table_count+=1
 rows=list(n.walk('tr'));cells=[[c for c in row.children if isinstance(c,Node) and c.tag in ['th','td']] for row in rows]
 cols=max(map(len,cells));assert all(len(c)==cols for c in cells)
 widths={2:[.24,.66],3:[.30,.12,.48],4:[.10,.10,.29,.39],5:[.22,.06,.22,.17,.20]}[cols]
 # Header offset tables need space for 64-bit types and explanations.
 title=headings[-1] if headings else 'データ構造'
 out='\n'+r'{\footnotesize\setlength{\tabcolsep}{3pt}\begin{longtable}{'+''.join('p{'+str(w)+r'\linewidth}' for w in widths)+'}\n'+r'\caption{'+esc(re.sub(r'^\d+(?:\.\d+)*\s*','',title))+r'。}\label{tab:format-html-'+str(table_count)+r'}\\'+'\n'+r'\hline'+'\n'
 out+=' & '.join(inline(c) for c in cells[0])+r' \\ \hline\endfirsthead'+'\n'+r'\hline '+' & '.join(inline(c) for c in cells[0])+r' \\ \hline\endhead'+'\n'
 for row in cells[1:]:out+=' & '.join(inline(c) for c in row)+r' \\'+'\n'
 return out+r'\hline\end{longtable}}'+'\n'

def block(n):
 if isinstance(n,str):return '' if not n.strip() else esc(n)
 t=n.tag
 if t in ['nav','style','script','h1','footer']:return ''
 if t=='div' and 'flow' in n.a.get('class','').split():return ''
 if t in ['h2','h3','h4']:
  title=re.sub(r'^\d+(?:\.\d+)*[.]?\s*','',n.text()).strip();headings.append(title)
  cmd={'h2':'subsection','h3':'subsubsection','h4':'paragraph'}[t]
  ident=n.a.get('id','')
  return ('\n\\FloatBarrier\n' if t=='h2' else '\n')+'\\'+cmd+'{'+esc(title)+'}\n'+('\\label{sec:format-html-'+ident+'}\n' if ident else '')
 if t=='p':
  if 'フォントライセンス' in n.text():return ''
  # Production links are handled in the source ledger/README rather than main prose.
  paragraphs.append(n.text());return inline(n).strip()+'\n\n'
 if t in ['ul','ol']:
  env='itemize' if t=='ul' else 'enumerate';return '\n\\begin{'+env+'}\n'+''.join('\\item '+inline(c)+'\n' for c in n.children if isinstance(c,Node) and c.tag=='li')+'\\end{'+env+'}\n'
 if t=='table':return table(n)
 if t=='figure':
  imgs=list(n.walk('img'));cap=next(n.walk('figcaption'),None);h=next(n.walk('h4'),None)
  caption=h.text() if h else (cap.text() if cap else None)
  return ''.join(figure(img,caption) for img in imgs)
 if t=='img':return figure(n)
 if t in ['summary','figcaption']:return ''
 return ''.join(block(c) for c in n.children)

body=block(main)
body=body.replace('図2のHBFラップ','元資料の参考図2のHBFラップ')
# Source linkage is preserved without web-only navigation in the thesis text.
manifest=json.loads((P/'reference/manifest.json').read_text());paths=[x['path'] for x in manifest['files']]
source_rows=[]
for anchor in sorted(anchors):
 match=re.match(r'(.+)-L(\d+)$',anchor)
 if not match:continue
 ident,line=match.groups();name=next((x for x in paths if x.replace('/','-').replace('.','-')==ident),ident)
 source_rows.append((name,int(line)))
body+='\n\\FloatBarrier\n\\subsection{参照箇所}\n本付録の説明と定義の参照箇所を表\\ref{tab:format-source-lines}に示す。行番号は同梱したスナップショットに対するものである。\n'
body+=r'{\footnotesize\begin{longtable}{p{0.70\linewidth}r}\caption{説明HTMLから引き継いだ参照ソースの行番号。}\label{tab:format-source-lines}\\\hline ソース & 行 \\ \hline\endfirsthead\hline ソース & 行 \\ \hline\endhead'+'\n'
for name,line in sorted(set(source_rows)):body+=r'\texttt{'+esc(name)+r'} & '+str(line)+r' \\'+'\n'
body+=r'\hline\end{longtable}}'+'\n'
(P/'appendix-body.tex').write_text('% Generated from article/index.html by article_to_tex.py; edit the HTML snapshot for content changes.\n'+body)
expected=[Path(n.a['src']).stem for n in main.walk('img')]
assert set(expected)==set(figure_names) and len(figure_names)==21
report={'article_sha256':hashlib.sha256(html.read_bytes()).hexdigest(),'figures':figure_names,'tables_from_article':table_count,'paragraphs_from_article':len(paragraphs),'section_headings':headings,'source_anchors':sorted(anchors),'omitted_web_elements':['navigation links','flow navigation','SVG original-size links','font-license footer'],'renderer':'original SVG -> rsvg-convert PDF (no redraw)'}
(P/'article-mapping.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(f'Converted {len(paragraphs)} paragraphs, {table_count} tables, all 21 original SVG diagrams; retained source anchors.')
