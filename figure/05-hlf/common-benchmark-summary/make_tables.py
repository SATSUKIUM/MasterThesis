from pathlib import Path
import json,csv
d=Path(__file__).resolve().parent
rows=json.loads((d/'data/stats.json').read_text());lookup={(r['kind'],r['environment'],r['mode'],r['group']):r for r in rows}
envs=[('e50-conservative','e50server03 (C)'),('e50-performance','e50server03 (P)'),('marq04','marq04 (P)'),('marq06','marq06 (P)'),('marq07','marq07 (P)')]
comp=[]
for group in ['all','has_slice','no_slice']:
 for kind in ['tof','multiplicity','track']:
  for mode in ['cond','slice']:
   if mode=='slice' and group=='no_slice':continue
   g='has_slice' if mode=='slice' else group
   a=lookup[kind,'e50-conservative',mode,g];b=lookup[kind,'e50-performance',mode,g]
   comp.append({'kind':kind,'mode':mode,'group':group,'conservative_MB_s':a['aggregate_MB_s'],'performance_MB_s':b['aggregate_MB_s'],'ratio':b['aggregate_MB_s']/a['aggregate_MB_s']})
with (d/'data/governor-group-comparison.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(comp[0]),lineterminator='\n');w.writeheader();w.writerows(comp)
tex=[]
for mode,group,caption,label in [('cond','all','ConditionalRunの全受信メッセージ','cond-all'),('cond','has_slice','sliceを1つ以上含むConditionalRun','cond-has'),('cond','no_slice','sliceを含まないConditionalRun','cond-none'),('slice','has_slice','ProcessSliceの全呼び出し','slice')]:
 tex+=['\\begin{table}[htbp]','  \\centering','  \\small','  \\caption{共通条件で測定した'+caption+'のスループット。値は総入力データ量と総処理時間の比$\\sum_i B_i/\\sum_i t_i$で、単位はMB/s。Cはconservative、Pはperformanceを表す。}','  \\label{tab:common-hlf-'+label+'}','  \\begin{tabular}{lrrr}','    \\hline','    環境 & TOF & Multiplicity & Track \\\\','    \\hline']
 for key,name in envs:
  vals=[]
  for kind in ['tof','multiplicity','track']:
   x=lookup[kind,key,mode,group]
   vals += [format(x['aggregate_MB_s'],'.1f')]
  tex.append('    '+name+' & '+' & '.join(vals)+' \\\\')
 tex+=['    \\hline','  \\end{tabular}','\\end{table}','']
tex+=['\\begin{table}[htbp]','  \\centering','  \\small','  \\caption{sliceを含む受信メッセージでの平均処理時間。C列はConditionalRunの1受信メッセージ、S列はProcessSliceの1呼び出しに対する平均であり、処理単位が異なる。単位は$\\upmu$s。}','  \\label{tab:common-hlf-time}','  \\begin{tabular}{lrrrrrr}','    \\hline','    & \\multicolumn{2}{c}{TOF} & \\multicolumn{2}{c}{Multiplicity} & \\multicolumn{2}{c}{Track} \\\\','    環境 & C & S & C & S & C & S \\\\','    \\hline']
for key,name in envs:
 vals=[format(lookup[kind,key,mode,'has_slice']['mean_us'],'.2f') for kind in ['tof','multiplicity','track'] for mode in ['cond','slice']]
 tex.append('    '+name+' & '+' & '.join(vals)+' \\\\')
tex+=['    \\hline','  \\end{tabular}','\\end{table}','']
# pLaTeX source already uses siunitx; avoid introducing upgreek dependencies.
(d/'tables.tex').write_text('\n'.join(tex).replace(chr(92)+'upmu',chr(92)+'mu')+'\n')
(d/'README.md').write_text('''# 共通ベンチマークの表とガバナー比較

stats.csv/JSONは表示範囲で切らない全サンプルの統計。各ケース・群のn、bytes、us、算術平均B/t、合算比ΣB/Σt、時間平均・分位点を収録。data/provenance.jsonに原CSV.gzの所在とSHA-256を保存した。図用原CSV.gzは隣のcommon-benchmark-{tof,multiplicity,track}/dataへ同梱。

C=conservative、P=performance。ConditionalRunはall/has_slice/no_slice、ProcessSliceはhas_sliceのみ（no_sliceには呼び出しがなくN/A）。分類は別実行のmessage/TF IDを使う再構成で、metadata-onlyの12864 bytesとも照合済み。

plot.CはROOTのTGraphでガバナー速度比を描く。フレームは200ビン、6点（sliceなしは3点）はヒストグラムの度数ではなくカテゴリ別の値。PDFのみ生成する。make_tables.pyでdata/stats.jsonからtables.texを再生成可能。thesis全体のビルドは行わない。
''')
print('generated tables.tex')
