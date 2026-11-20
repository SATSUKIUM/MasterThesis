"""Generate the reference HTML, nested SVGs and byte/bit diagrams from JSON.
Run: python3 docs/format-study/build_format.py [--verify-cpp]
Only Python's standard library is required. --verify-cpp additionally uses clang++.
"""
from pathlib import Path
from html import escape as esc
import base64
import hashlib
import json
import platform
import re
import subprocess
import sys
import tempfile
import textwrap
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SRC = REPO / 'resources/GitHub/nestdaq-user-impl'
HEADERS = json.loads((ROOT/'schema/headers-v1.json').read_text())
STAGES = json.loads((ROOT/'schema/pipeline.json').read_text())
WORDS = json.loads((ROOT/'schema/words-v3.json').read_text())
APPEARANCE = json.loads((ROOT/'schema/appearance.json').read_text())
FONT = APPEARANCE['embedded_font']
FONT_CHOICES = APPEARANCE['font_choices']
DEFAULT_FONT = next(c for c in FONT_CHOICES if c['id']==APPEARANCE['default_font_id'])
FONT_LICENSE = (ROOT/DEFAULT_FONT['license']).read_text()
def font_css(choice):
    rules=[]
    for face in choice['faces']:
        data=base64.b64encode((ROOT/face['path']).read_bytes()).decode('ascii')
        rules.append('@font-face{font-family:"'+choice['family']+'";src:url("data:font/ttf;base64,'+data+'") format("truetype");font-style:'+face['style']+';font-weight:'+face['weight']+';font-stretch:75% 100%;font-display:swap;}')
    return ''.join(rules)
FONT_CSS=font_css(DEFAULT_FONT)
HTML_FONT_CSS=''.join(font_css(choice) for choice in FONT_CHOICES)
COLORS = dict(tf='#b6d7a5',tfheader='#93c47d',stf='#f9cfa0',stfheader='#f6b466',
              hbf='#adb8c6',hbfheader='#687584',data='#43484d',filter='#a6c6cc',
              trigger='#76a5af',trgtime='#45818e',file='#a4c2f4',fileheader='#6d9eeb',
              transport='#e8edf1',ellipsis='#ffffff')
COLORS.update(APPEARANCE.get('colors',{}))
FIG=ROOT/'figures'
FIG.mkdir(exist_ok=True)

def save_svg(name,w,h,content,title):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title"><title id="title">{esc(title)}</title><metadata>{esc(FONT_LICENSE)}</metadata><style>{FONT_CSS}</style><rect width="100%" height="100%" fill="white"/><g font-family="{esc(APPEARANCE['svg_font_family'], quote=True)}" font-weight="{APPEARANCE['svg_font_weight']}" font-stretch="{APPEARANCE['svg_font_stretch']}" style="font-variation-settings:{esc(APPEARANCE['svg_font_variation_settings'], quote=True)}" fill="#142e42">'+''.join(content)+'</g></svg>'
    ET.fromstring(svg)
    (FIG/name).write_text(svg)

def math_text(value):
    # Italicize variables only, leaving Header names and configuration keys upright.
    out=[];offset=0
    for match in re.finditer(r'(?<![\w-])(?:n_j|k_j|H|S|j)(?![\w-])',str(value)):
        out.append(esc(str(value)[offset:match.start()]))
        var=match.group()
        if '_' in var:
            base,sub=var.split('_',1)
            content=base+'<tspan baseline-shift="sub" font-size="75%">'+sub+'</tspan>'
        else:content=var
        out.append('<tspan class="math-variable" font-style="italic">'+content+'</tspan>')
        offset=match.end()
    out.append(esc(str(value)[offset:]))
    return ''.join(out)

def text(x,y,value,size=16,fill='#142e42',anchor='start',weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" style="font-variation-settings:&quot;wght&quot; {weight}, &quot;wdth&quot; 100">{math_text(value)}</text>'

def rect(x,y,w,h,kind):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{COLORS[kind]}" stroke="#454e54" stroke-width="1.7"/>'

def font_size(node,depth):
    size=APPEARANCE['concept_font_size']-depth*APPEARANCE['depth_font_step']
    if node['role']!='concept':size-=2
    return max(APPEARANCE['min_font_size'],size)

def label_lines(node,depth,w):
    size=font_size(node,depth)
    limit=max(14,int((w-28)/(size*.55)))
    return textwrap.wrap(node['label'],width=limit,break_long_words=False,break_on_hyphens=False) or ['']

def band(node,depth,w):
    return len(label_lines(node,depth,w))*font_size(node,depth)*1.22+19

def height(node,depth=0,w=912):
    if node['kind']=='ellipsis':return band(node,depth,w)-7
    if 'children' not in node:return band(node,depth,w)
    return band(node,depth,w)+sum(height(n,depth+1,w-40)+8 for n in node['children'])+8

def draw(node,x,y,w,out,parent_kind=None,depth=0):
    h=height(node,depth,w);kind=node['kind'];size=font_size(node,depth)
    out.append(f'<g opacity="{node.get("opacity",1)}">')
    if kind!='ellipsis':
        box=rect(x,y,w,h,kind)
        if node.get('dashed'):box=box.replace('/>',' stroke-dasharray="8 5"/>')
        out.append(box)
    color='white' if kind in ('data','hbfheader','trgtime') else '#142e42'
    if kind=='ellipsis':color='white' if parent_kind=='data' else '#142e42'
    role=node['role'];assert role in ('concept','record','annotation'),role
    anchor='start' if role=='concept' else 'middle'
    tx=x+14 if role=='concept' else x+w/2
    for i,line in enumerate(label_lines(node,depth,w)):
        out.append(text(tx,y+size+8+i*size*1.22,line,size,color,anchor=anchor,weight=700 if node.get('changed') else 400))
    cy=y+band(node,depth,w)
    for child in node.get('children',[]):
        draw(child,x+20,cy,w-40,out,kind,depth+1)
        cy+=height(child,depth+1,w-40)+8
    out.append('</g>')

def render_stage(stage,filename,width=960):
    top=126 if stage.get('callout') else 90
    content_width=width-48
    h=top+26+sum(height(n,w=content_width)+12 for n in stage['nodes'])
    out=[text(24,32,stage['device'],25 if width>=900 else 21)]
    if width>=900:
        out.append(text(24,57,'Bold: added / changed from previous stage; left: concepts; centered: stored records',13))
    else:out.append(text(24,58,'Input reference / faded output slots = removed',12))
    if stage.get('callout'):
        out += [rect(24,77,content_width,36,'transport'),text(width/2,101,stage['callout'],16,anchor='middle')]
    y=top
    for node in stage['nodes']:
        draw(node,24,y,content_width,out)
        y+=height(node,w=content_width)+12
    save_svg(filename,width,h,out,stage['device']+' output structure')

for stage in STAGES:
    render_stage(stage,stage['id']+'.svg')
    for side,comparison in stage.get('comparison',{}).items():
        render_stage(comparison,stage['id']+'-'+side+'.svg',width=520)

for hdr in HEADERS:
    end=0
    for f in hdr['fields']:
        assert f['offset']==end,(hdr['id'],f)
        end+=f['bytes']
    assert end==hdr['size_bytes']
    # Show the long comments array in one collapsed row, explicitly labelled.
    byte_rows=6 if hdr['id'].startswith('file-') else (end+7)//8
    out=[text(24,32,hdr['name'],22),text(24,56,f'{end} bytes / increasing byte address: left to right, then top to bottom',13)]
    for r in range(byte_rows):
        y=92+r*68
        out.append(text(12,y+30,'+'+str(r*8),12))
        for col in range(8):out.append(text(60+col*108+54,y-8,r*8+col,11,anchor='middle'))
        for f in hdr['fields']:
            lo=max(r*8,f['offset']);hi=min(r*8+8,f['offset']+f['bytes'])
            if lo>=hi:continue
            x=60+(lo-r*8)*108;w=(hi-lo)*108
            out.append(rect(x,y,w,46,'transport'))
            out.append(text(x+w/2,y+28,f['name'],15,anchor='middle'))
    if hdr['id'].startswith('file-'):
        y=92+byte_rows*68
        out += [rect(60,y,864,46,'transport'),text(492,y+28,'comments[256] / offsets 48..303 / collapsed (not to scale)',15,anchor='middle')]
        byte_rows+=1
    save_svg(hdr['id']+'-bytes.svg',960,104+byte_rows*68,out,hdr['name']+' byte layout')

for word in WORDS:
    seen=set();out=[text(24,32,word['name']+' / 64 bits = 8 bytes',22),text(24,57,'Bit significance: MSB 63 at left, LSB 0 at right (not byte address order)',13)]
    for i,(name,lo,width) in enumerate(word['fields'],1):
        bits=set(range(lo,lo+width));assert not seen & bits;seen|=bits
        x=48+(64-lo-width)*13.5;w=width*13.5
        out+=[rect(x,90,w,50,'transport'),text(x+w/2,122,i,17,anchor='middle')]
        out.append(text(48+(i-1)%2*440,177+(i-1)//2*29,f'{i}: [{lo+width-1}:{lo}] {name} ({width} bit)',15))
    assert seen==set(range(64))
    out += [text(48,81,'63',12),text(912,81,'0',12,anchor='end')]
    save_svg(word['id']+'-bits.svg',960,198+((len(word['fields'])+1)//2)*29,out,word['name']+' bit layout')

# Stable line anchors and a source fingerprint make the basis of this document reviewable.
source_names=sorted(set(h['source'] for h in HEADERS)|{'STFBuilder.h','STFBuilder.cxx','AmQStrTdcSampler.cxx','AmQStrTdcSampler.h','TimeFrameBuilder.cxx','LogicFilter/LogicFilter.cxx','TimeFrameSlicerByLogicTiming.cxx','FilterTimeFrameSliceABC.icxx','FilterTimeFrameSliceBySomething.cxx','FrameContainer.h','FileSink.cxx','UnpackTdc.h','AmQStrTdcData.h'})
def sid(name):return name.replace('/','-').replace('.','-')
def ref(name,needle,label=None):
    lines=(SRC/name).read_text(errors='replace').splitlines()
    idx=next((i for i,s in enumerate(lines,1) if needle in s),None)
    assert idx,(name,needle)
    return f'<a href="sources.html#{sid(name)}-L{idx}">{esc(label or name+":"+str(idx))}</a>'
manifest={}
source_html=[]
for name in source_names:
    data=(SRC/name).read_bytes();manifest[name]=hashlib.sha256(data).hexdigest()
    source_html.append(f'<h2 id="{sid(name)}">{esc(name)}</h2><p>SHA-256: <code>{manifest[name]}</code></p><pre>')
    for i,line in enumerate(data.decode(errors='replace').splitlines(),1):
        source_html.append(f'<span id="{sid(name)}-L{i}"><a href="#{sid(name)}-L{i}">{i:4}</a> {esc(line)}</span>\n')
    source_html.append('</pre>')
(ROOT/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
style='''body{font:16px/1.85 -apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;color:#203746;background:#fbfcfd;max-width:1100px;margin:42px auto;padding:0 24px}h1{font-size:32px;line-height:1.45}h2{margin-top:2.5em;border-bottom:2px solid #cbdde5}h3{margin-top:2em}a{color:#08668e}code{background:#edf1f4;padding:2px 4px;font-size:0.9em}table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}th,td{border:1px solid #cbd6dc;padding:9px;text-align:left;vertical-align:top}th{background:#eaf1f5}img{display:block;max-width:100%;height:auto;margin:16px auto}figure{margin:24px 0}figcaption,.muted{font-size:14px;color:#5c707d}.lead,.note{border-left:5px solid #217c91;background:#edf5f7;padding:14px 22px}.note{border-color:#b58232;background:#fff6e7}nav{background:#eaf1f5;padding:18px 24px}.flow{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.flow a{background:#eaf1f5;padding:6px 12px;border-radius:4px}.diagram{max-width:880px}.details-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.details-grid img{max-height:700px}pre{overflow:auto;font:12px/1.6 monospace;background:#edf1f4;padding:12px}pre span:target{background:#ffe5a8;display:block}section:target,h3:target{scroll-margin-top:15px}details{margin:14px 0}summary{cursor:pointer;color:#08668e}@media(max-width:760px){.details-grid{display:block}body{padding:0 15px}table{display:block;overflow:auto}}@media print{body{background:white;margin:0;max-width:none}nav{display:none}h2,h3{break-after:avoid}figure{break-inside:avoid}a{color:inherit}.diagram{max-height:235mm;width:auto}details{display:block}}'''
style = HTML_FONT_CSS + style
style += 'svg{display:block;max-width:100%;height:auto;margin:16px auto}.filter-comparison{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;align-items:start}.filter-comparison figure{margin:0}.filter-comparison svg{width:100%}@media(max-width:760px){.filter-comparison{display:block}}'
style = style.replace('-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif', APPEARANCE['html_font_family'])

style += 'section:target,h3:target{scroll-margin-top:175px}:root{--figure-font:"NestDAQ Roboto",sans-serif}.font-tools{position:sticky;top:0;z-index:5;background:#f4f7f3;border:1px solid #b6c4b1;border-radius:6px;padding:12px 16px;margin:20px 0;box-shadow:0 2px 5px #0001}.font-tools label{font-weight:600}.font-tools select,.font-tools button{font:inherit;padding:4px 10px;margin:0 8px}.font-tools small{display:block;color:#52634c}.font-sample{font-size:20px;padding:4px 0}.font-sample svg{margin:4px 0}body svg text{font-family:var(--figure-font)!important;font-variation-settings:normal!important}@media print{.font-tools{position:static;box-shadow:none}}'

style=style.replace('\"NestDAQ Roboto\",sans-serif', '\"'+DEFAULT_FONT['family']+'\",serif')
if not APPEARANCE['show_font_selector']:
    style += 'section:target,h3:target{scroll-margin-top:15px}'

def page(title,body):return '<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+style+'</style></head><body>'+body+'</body></html>'
sample='TimeFrame Header / Heartbeat / DAQ words / 0123456789 / agR'
comparison='<h1>Robotoの比較見本</h1><p><a href="dataformat.html">資料へ戻る</a>。Google Slidesで同じ文字列・太さを選び、字形を比較するための見本。全例は32 CSS px。図の階層別サイズとは分けて比較する。</p>'
for label,family,weight in [('Roboto Regular (400)','NestDAQ Roboto',400),('Roboto Medium (500)','NestDAQ Roboto',500),('Roboto Bold (700)','NestDAQ Roboto',700),('Helvetica Regular (comparison)','Helvetica, Arial, sans-serif',400)]:
    comparison+='<h2>'+label+'</h2><p style="font-family:'+esc(family,quote=True)+';font-size:32px;font-weight:'+str(weight)+';font-stretch:100%;">'+sample+'</p>'
comparison+='<p>図はRoboto 3.015 / weight 400 / wdth 100を使用。Google Slidesが選んでいる版や太さの一致は未確認。PDFやPNGへ変換した際の描画差もあり得る。</p><details><summary>Roboto license</summary><pre>'+esc((ROOT/'fonts/OFL.txt').read_text())+'</pre></details>'
(ROOT/'font-comparison.html').write_text(page('Roboto フォント比較',comparison))
(ROOT/'sources.html').write_text(page('NestDAQ 参照ソース', '<h1>参照ソースと行番号</h1><p><a href="dataformat.html">資料へ戻る</a>。ローカルスナップショットから生成。ソースは変更していません。</p>'+''.join(source_html)))

if '--verify-cpp' in sys.argv:
    includes='\n'.join('#include "'+n+'"' for n in sorted(set(h['source'] for h in HEADERS)))
    checks=[]
    for h in HEADERS:
        checks.append(f'static_assert(sizeof({h["name"]}) == {h["size_bytes"]}, "{h["id"]} size");')
        for f in h['fields']:
            checks.append(f'static_assert(offsetof({h["name"]}, {f["name"]}) == {f["offset"]}, "{h["id"]} {f["name"]}");')
    code='#include <cstdio>\n#include <cstdint>\n#include <cstddef>\n'+includes+'\n'+'\n'.join(checks)+'\nint main(){return 0;}\n'
    (ROOT/'verify_layout.cpp').write_text(code)
    with tempfile.TemporaryDirectory(prefix='nestdaq-layout-') as temp:
        result=subprocess.run(['clang++','-std=c++17','-I',str(SRC),str(ROOT/'verify_layout.cpp'),'-o',str(Path(temp)/'verify')],capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stderr)
        subprocess.run([str(Path(temp)/'verify')],check=True)
    result=dict(platform=platform.platform(),command='clang++ -std=c++17 -I resources/GitHub/nestdaq-user-impl docs/format-study/verify_layout.cpp',status='passed',checks=len(checks),source_manifest=manifest,schema_sha256=hashlib.sha256((ROOT/'schema/headers-v1.json').read_bytes()).hexdigest())
    (ROOT/'layout-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

parts=['<h1>NestDAQ データフォーマットと<br>デバイス間の構造変化</h1><p class="muted">2026-10-23 · nestdaq-user-impl ローカルスナップショット · v1ヘッダ / V3 TDCを中心に整理</p>',
'<p class="lead">FEE → Sampler → STFBuilder → TimeFrameBuilder → LogicFilter → TimeFrameSlicerByLogicTiming → FilterTimeFrameBySomething → FileSink。各段階のデータを、既存のKeynote図と同じ色分けの入れ子図で示す。図中の並びは上から下がデータ順。箱の面積はbyte数に比例しない。<b>太字は前段から追加・変更された要素</b>を示す。</p>',
'<nav><a href="#pipeline">データの変化</a> / <a href="#headers">ヘッダとmagic</a> / <a href="#words">DAQ word・HBD</a> / <a href="#sizes">サイズの関係</a> / <a href="#implementation">実装上の注記</a> / <a href="#rebuild">編集・再生成</a> / <a href="#log">ログ</a></nav>',
'<h2>対象と読み方</h2><p>既存の <a href="../../pictures/keynote/figures.key">figures.key</a>、<a href="../../pictures/keynote/figures.pptx">figures.pptx</a>、数字.pngを参考に、実装コードで補足した。対象はこのディレクトリ内のコードであり、NestDAQ全運用・全世代を一律に規定する仕様ではない。元コードのSHA-256は<a href="source-manifest.json">manifest</a>に記録した。v0とv1、FEMの世代を混在させない。</p>',
'<p>緑：TF、橙：STF、灰青：HBF、濃灰：DAQ word/HBD、青緑：Filter/Trigger、濃い緑：同期したheartbeat group、ウォームグレー：FileSink。<i>S</i>＝TFのソース数、<i>H</i>＝1ソースのSTFに含むHBF数、<i>n<sub>j</sub></i>＝HBF jのtrigger数。概念上の枠の見出しは左揃え、実際に記録されるHeader・DAQ words・HBD・TrgTimeは中央揃え。DAQ wordsの下にHBDを別の箱で示す。代表例では複数の要素を描き、「× number of …」は図示分を含む総繰り返し数を表す。</p>',
'<h2 id="pipeline">1. デバイスを通るデータ構造</h2><div class="flow">']
options=''.join('<option value="'+esc(c['id'])+'"'+(' selected' if c['id']==DEFAULT_FONT['id'] else '')+'>'+esc(c['label'])+'</option>' for c in FONT_CHOICES)
sample_svg='<svg width="700" height="40" viewBox="0 0 700 40" role="img" aria-label="書体と変数の斜体の見本"><g>'+text(0,28,'TimeFrame Header / DAQ word / H = max-hbf / n_j, k_j, S',20)+'</g></svg>'
# Retain the comparison toolbar source; enable it via show_font_selector.
if APPEARANCE['show_font_selector']:
    parts.insert(1,'<div class="font-tools"><label for="figure-font">図のフォント</label><select id="figure-font">'+options+'</select><button id="font-reset" type="button">既定に戻す</button><span id="font-status" role="status" aria-live="polite">'+esc(DEFAULT_FONT['label'])+'</span><small>ページ内の全SVGを切替。太字・変数の斜体も保持。単独SVGリンクは生成時の既定フォント。</small><div class="font-sample">'+sample_svg+'</div></div>')
for i,s in enumerate(STAGES):parts.append(('<span>→</span>' if i else '')+f'<a href="#{s["id"]}">{esc(s["device"])}</a>')
parts.append('</div>')
parts.append((ROOT/'packing-notes.html').read_text())
STAGE_TEXT=(ROOT/'pipeline-notes.html').read_text().split('<!-- STAGE -->')
assert len(STAGE_TEXT)==8
for i,s in enumerate(STAGES):
    parts += [f'<section id="{s["id"]}"><h3>1.{i+1} {esc(s["device"])}</h3><p>{esc(s["caption"])}</p>',STAGE_TEXT[i]]
    if s.get('comparison'):
        parts.append('<p><b>選別動作の例：</b>左は入力、右は不採用SLICEを半透明・破線で示した説明図。不採用SLICEとFilter/Trigger情報は実際の出力byte列には存在しない。表示位置を揃えて消えた部分を比較するために描いている。現在のBySomethingのProcessSlice()はreturn trueなので、このSLICE除去はまだ行わない。</p><div class="filter-comparison">')
        for side,label in [('input','入力：3個のSLICE'),('output','選別例：SLICE #1を除去')]:
            name=s['id']+'-'+side+'.svg'
            parts.append(f'<figure><h4>{label}</h4><a href="figures/{name}"><img src="figures/{name}" alt="{label}"></a><figcaption><a href="figures/{name}">SVG原寸</a></figcaption></figure>')
        parts.append('</div>')
    else:
        parts.append(f'<figure><a href="figures/{s["id"]}.svg"><img class="diagram" src="figures/{s["id"]}.svg" alt="{esc(s["device"])}のデータの入れ子構造"></a><figcaption>図{i+1}：{esc(s["device"])}の出力。{esc(s.get("figure_note",""))}<a href="figures/{s["id"]}.svg">SVG原寸</a> / <a href="../../pictures/keynote/{s["reference"]}.png">参考図 {s["reference"]}.png</a></figcaption></figure>')
    parts.append('</section>')
parts.append('<h2 id="headers">2. ヘッダ・レコード定義とmagic</h2><p>magicはuint64_tの定数値と、<b>little-endianでメモリ／ファイルに並べた8 byteの文字表現</b>を示す。<code>\\0</code>は実byte 0x00。コードコメントの末尾空白と、実定数のNULは区別する。ASCII表現はC文字列として途中で打ち切らず8 byteで読む。</p><table><tr><th>構造体</th><th>size [B]</th><th>magic [hex]</th><th>8 byteの文字表現（LE）</th><th>実byte [hex]</th></tr>')
for h in HEADERS:
    if h['magic']:
        raw=int(h['magic'],16).to_bytes(8,'little');ascii_s=''.join('\\0' if b==0 else chr(b) for b in raw)
        cells=f'<code>{h["magic"]}</code></td><td><code>"{esc(ascii_s)}"</code></td><td><code>{raw.hex(" ")}</code>'
    else:cells='なし</td><td>なし</td><td>—'
    parts.append(f'<tr><td><a href="#header-{h["id"]}">{esc(h["name"])}</a></td><td>{h["size_bytes"]}</td><td>{cells}</td></tr>')
parts.append('</table>')
verification=json.loads((ROOT/'layout-verification.json').read_text()) if (ROOT/'layout-verification.json').exists() else None
verified=verification and verification['source_manifest']==manifest and verification.get('schema_sha256')==hashlib.sha256((ROOT/'schema/headers-v1.json').read_bytes()).hexdigest()
parts.append('<p>'+('この環境のclang++で全構造体のsizeofと全フィールドのoffsetofを検査済み（'+str(verification['checks'])+'項目）。<a href="layout-verification.json">検証記録</a>。' if verified else '配置は宣言から記述。対象ビルドでsizeof/offsetofを確認すること。')+'別のABIや旧版ファイルの配置まで保証するものではない。byte図はアドレス順、bit図はMSB→LSBで読む。</p>')
for h in HEADERS:
    parts.append(f'<section id="header-{h["id"]}"><h3>{esc(h["name"])} / {h["size_bytes"]} byte</h3><p>根拠：'+ref(h['source'],'struct '+('Trailer' if h['id']=='file-trailer' else 'TrgTimeHeader' if h['id']=='trigger' else 'TrgTime {' if h['id']=='trgtime' else 'Header') if h['id'] in ('trigger','trgtime','hbf') else 'namespace v1',h['source'])+('（v1を参照）。</p>' if h['id']!='hbf' else '。</p>'))
    parts.append('<ul>'+''.join('<li>'+esc(n)+'</li>' for n in h['notes'])+'</ul>')
    parts.append('<table><tr><th>offset [B]</th><th>size [B]</th><th>field / type</th><th>内容</th></tr>')
    for f in h['fields']:parts.append(f'<tr><td>{f["offset"]}</td><td>{f["bytes"]}</td><td><code>{f["name"]}</code><br><code>{f["type"]}</code></td><td>{esc(f["note"])}</td></tr>')
    parts.append(f'</table><details><summary>byte配置図を開く（SVG）</summary><a href="figures/{h["id"]}-bytes.svg"><img src="figures/{h["id"]}-bytes.svg" alt="{esc(h["name"])} byte配置"></a></details></section>')
parts.append('<h2 id="words">3. DAQ wordとHeartbeat Delimiter</h2><p>ここではSlicerが処理するTDC64H_V3 / TDC64L_V3を対象にする。hitは64 bit＝8 byte。hitのtypeは0x0b（[63:58]）。HBDは2 word＝16 byteで、ソフトウェアのHBF Header 16 byteとは別に存在する。bit抽出の根拠：'+ref('UnpackTdc.h','namespace TDC64H_V3')+'、'+ref('UnpackTdc.h','namespace TDC64L_V3')+'。HBD宣言：'+ref('AmQStrTdcData.h','// 1st heartbeat')+'（v1）。</p>')
for w in WORDS:
    parts.append(f'<h3>{esc(w["name"])}</h3><p>{esc(w["note"])}</p><a href="figures/{w["id"]}-bits.svg"><img src="figures/{w["id"]}-bits.svg" alt="{esc(w["name"])} bit配置"></a>')
    parts.append('<table><tr><th>bit範囲</th><th>幅</th><th>field</th></tr>'+''.join(f'<tr><td>[{lo+width-1}:{lo}]</td><td>{width}</td><td>{esc(name)}</td></tr>' for name,lo,width in w['fields'])+'</table>')
parts.append((ROOT/'format-notes.html').read_text())
# Replace evidence tokens with actual source links; tokens: {{file|needle|optional label}}
import re
body=''.join(parts)
body=re.sub(r'\{\{([^{}]+)\}\}',lambda m:ref(*m.group(1).split('|')),body)
def inline_figure(match):
    attrs,name=match.group(1),match.group(2)
    svg=(FIG/name).read_text()
    svg=re.sub(r'<style>.*?</style>|<metadata>.*?</metadata>','',svg,flags=re.S)
    unique='figure-'+name.replace('.svg','')
    svg=svg.replace('id="title"',f'id="{unique}"').replace('aria-labelledby="title"',f'aria-labelledby="{unique}"')
    klass='diagram' if 'class="diagram"' in attrs else 'byte-bit-diagram'
    return svg.replace('<svg ',f'<svg class="{klass}" ',1)
body=re.sub(r'<img([^>]*?)src="figures/([^"/]+\.svg)"[^>]*>',inline_figure,body)
for choice in FONT_CHOICES:
    body+='<details><summary>'+esc(choice['label'])+' / font license</summary><pre>'+esc((ROOT/choice['license']).read_text())+'</pre></details>'
script=(ROOT/'font-controls.js').read_text()
if APPEARANCE['show_font_selector']:
    body+='<script type="application/json" id="font-choices">'+json.dumps(FONT_CHOICES,ensure_ascii=False).replace('<','\u003c')+'</script><script>'+script+'</script>'
(ROOT/'dataformat.html').write_text(page('NestDAQ データフォーマットと構造変化',body))
print(f'Generated dataformat.html, sources.html, {len(STAGES)} nested SVGs + 2 filter comparison SVGs, {len(HEADERS)} header diagrams, {len(WORDS)} bit diagrams. C++ verification: {bool(verified)}')
