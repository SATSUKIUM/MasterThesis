#!/usr/bin/env python3
"""Generate ROOT macro and field tables using only the sibling JSON definitions."""
from pathlib import Path
import json
p=Path(__file__).resolve().parent
headers=json.loads((p/'data/headers-v1.json').read_text())
words=json.loads((p/'data/words-v3.json').read_text())
def q(s):return json.dumps(s)
cpp=r'''#include "pdf_output.hxx"
#include <TBox.h>
#include <TText.h>
#include <TStyle.h>
#include <TArrow.h>
#include <vector>
#include <string>
struct Field { const char* name; int start; int size; };
void text(double x,double y,const char* s,double size=.028,int align=12){auto t=new TText(x,y,s);t->SetTextFont(132);t->SetTextSize(size);t->SetTextAlign(align);t->Draw();}
void layout(const char* id,const char* title,std::vector<Field> fields,int total,bool bits=false){
 TCanvas c(id,title,800,600);c.Range(0,0,1,1);text(.06,.95,title,.036);
 text(.06,.89,bits?"Bit index (MSB on left)":"Byte offset from record start",.027);
 const int rowwidth=bits?64:16;int rows=(total+rowwidth-1)/rowwidth;
 double dy=rows>9?.72/rows:.072; double top=.83;
 int colors[]={TColor::GetColor("#DCE5F1"),TColor::GetColor("#F3E9CE"),TColor::GetColor("#DAE8DC"),TColor::GetColor("#E9DDE8")};
 for(int r=0;r<rows;r++){
  for(unsigned i=0;i<fields.size();i++){
   auto f=fields[i];int begin=std::max(f.start,r*rowwidth),end=std::min(f.start+f.size,(r+1)*rowwidth);if(begin>=end)continue;
   double x1=.08+.84*(begin-r*rowwidth)/rowwidth,x2=.08+.84*(end-r*rowwidth)/rowwidth;
   double y=top-r*dy;auto b=new TBox(x1,y-dy*.75,x2,y);b->SetFillColor(colors[i%4]);b->SetLineWidth(3);b->Draw();
   double font=std::min(.026,(x2-x1)*1.5/std::max(1,int(std::string(f.name).size())));
   if(bits && f.size<4){text((x1+x2)/2,y-dy*.38,"R",.022,22);}else text((x1+x2)/2,y-dy*.38,f.name,std::max(.016,font),22);
   text(x1,y+.009,std::to_string(bits?63-begin:begin).c_str(),.019,11);
  }
 }
 if(bits)text(.06,.17,"R: reserved; each word is 64 bits (8 bytes)",.026);
 else text(.06,.06,(std::string("Total: ")+std::to_string(total)+" bytes; field widths are defined in data/headers-v1.json").c_str(),.023);
 save_figure_pdf(c,(std::string("pdf/")+id+".pdf").c_str());
}
void plot(){gROOT->SetBatch(kTRUE);gStyle->SetLineWidth(3);
'''
# Split comments[256] visually into one summary row, while retaining exact offsets in JSON/table.
for h in headers:
 fields=h['fields']; total=h['size_bytes']
 if total==304:
  fields=[f for f in fields if f['offset']<48]+[{'name':'comments[256] (bytes 48-303)','offset':48,'bytes':16}]; total_draw=64
 else:total_draw=total
 cpp+='layout('+q(h['id'])+','+q(h['name']+f" ({h['size_bytes']} bytes)")+',{' + ','.join('{'+q(f['name'])+f",{f['offset']},{f['bytes']}"+'}' for f in fields)+f'}},{total_draw});\n'
for w in words:
 cpp+='layout('+q(w['id'])+','+q(w['name'])+ ',{'+','.join('{'+q(n)+f',{64-lo-width},{width}'+'}' for n,lo,width in w['fields'])+'},64,true);\n'
cpp+=r'''
 {TCanvas c("pipeline","Processing and serialization",800,600);c.Range(0,0,1,1);
 text(.06,.96,"NestDAQ processing and serialized records",.036);
 const char* names[]={"FEE / Sampler","STFBuilder / TFBuilder","LogicFilter","Slicer (per HBF j)","High-level filter / FileSink"};
 const char* a[]={"64-bit hit words + HBD pairs","TFH + [STFH + (HBFH + words + HBDs) x H] x S","TFH + FilterH + [TriggerH + trigger times] x H + STFs","META_j + SLICE_j,1 + ... + SLICE_j,n(j)","META_j + accepted SLICEs; run header / trailer at sink"};
 for(int i=0;i<5;i++){double y=.87-i*.16;auto b=new TBox(.05,y-.105,.95,y);b->SetFillColor(TColor::GetColor("#E5EBF3"));b->SetLineWidth(3);b->Draw();text(.075,y-.032,names[i],.028);text(.075,y-.078,a[i],.023);if(i<4){auto ar=new TArrow(.5,y-.112,.5,y-.15,.018,"|>");ar->SetLineWidth(3);ar->Draw();}}
 text(.06,.025,"H: HBFs per source; S: sources; n(j): triggers in HBF j",.024);
 save_figure_pdf(c,"pdf/pipeline.pdf");}
}
'''
# correct summary labels: the file envelope diagrams deliberately collapse 256B comment span.
cpp=cpp.replace('Total: ")+std::to_string(total)+" bytes;','Drawn span: ")+std::to_string(total)+" bytes;')
(p/'plot.C').write_text(cpp)
# Source-based compile checks: every byte offset, field width and record size.
incs=[]
for h in headers:
 if h['source'] not in incs:incs.append(h['source'])
check='#include <cstdint>\n#include <cstdio>\n#include <cstddef>\n#include <iostream>\n'
for src in incs:check+=f'#include "reference/source/{src}"\n#pragma pack()\n'
for h in headers:
 name=h['name']
 check+=f'static_assert(sizeof({name})=={h["size_bytes"]},"{h["id"]} size");\n'
 for f in h['fields']:
  check+=f'static_assert(offsetof({name},{f["name"]})=={f["offset"]},"{h["id"]}.{f["name"]} offset");\n'
  check+=f'static_assert(sizeof((({name}*)0)->{f["name"]})=={f["bytes"]},"{h["id"]}.{f["name"]} width");\n'
check+='int main(){std::cout << "8 records: sizeof, every field offset and width verified; time_t=" <<sizeof(time_t)<<" bytes\\n";}\n'
(p/'verify_layout.cxx').write_text(check)
for w in words:
 used=[]
 for _,lo,width in w['fields']:used.extend(range(lo,lo+width))
 assert sorted(used)==list(range(64)),w['id']
# JSON remains canonical; table rows are regenerated reproducibly.
def esc(s):return s.replace('_',r'\_').replace('&',r'\&').replace('#',r'\#')
tables=[]
for h in headers:
 tables.append(r'\subsubsection{'+esc(h['name'])+'}\n'+f"総長は{h['size_bytes']} byteである。"+(r'識別子は\texttt{'+h['magic']+'}である。' if h.get('magic') else '')+'\n')
 tables.append(r'\begin{longtable}{r r l p{0.40\linewidth}}'+'\n'+r'\caption{'+esc(h['name'])+r'のフィールド配置。}\label{tab:format-'+h['id']+r'}\\'+'\n'+r'\hline オフセット & byte数 & フィールド & 意味 \\ \hline\endfirsthead'+'\n'+r'\hline オフセット & byte数 & フィールド & 意味 \\ \hline\endhead'+'\n')
 for f in h['fields']:
  note=f.get('note','')
  tables.append(f"{f['offset']} & {f['bytes']} & "+r'\texttt{'+esc(f['name'])+'} & '+esc(note)+r' \\'+'\n')
 tables.append(r'\hline\end{longtable}'+'\n')
 tables.append(r'\begin{figure}[htbp]\centering\makebox[\linewidth][c]{\includegraphics[pagebox=cropbox,width=0.95\linewidth,height=0.55\textheight,keepaspectratio]{../figure/10-3-nestdaq-dataformat/pdf/'+h['id']+r'.pdf}}\caption{'+esc(h['name'])+'のバイト配置。'+('commentsは256 byteを1段に縮約して示す。' if h['size_bytes']==304 else '')+r'}\label{fig:format-'+h['id']+r'}\end{figure}'+'\n')
(p/'header-tables.tex').write_text(''.join(tables))
print('Generated plot.C, header-tables.tex, verify_layout.cxx; 4 word maps cover 64 bits without gaps or overlap.')
