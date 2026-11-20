図・データ・再作図マクロ

2026-11-20。条件: UTOF LR AND LTOF individual-readout OR。測定入力は各runの結合先頭20,000TF。4台各条件1回、計時はsteady_clock double µs、CRとPSは別実行、各段1プロセス、performance前後確認、sink=/dev/null。

PDF・plot.C・data/（元CSV.gz、メタデータ、コマンド、TF分類台帳）を同梱。統計表の正本は各summary/stats.csvとtables.tex。ヒストグラム200ビン、二次元200×200、軸は線形、グリッド、線幅3。時系列は取得HBF基準。生LTOF診断は独立のUTOF参照、固有検出効率ではない。

再作図はこのディレクトリでroot -l -b -q plot.C（summaryは表のみ）。再集計・原稿生成はcommon-benchmark/scripts/thesis-trigger-cleanup/prepare.pyとreport.py。論文全体PDFは依頼なしにビルドしない。
