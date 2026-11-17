# TOF選別図 (未対応)

現在のスライド画像と一致する元ヒストグラム・選別条件は未特定。画像から分布を推定しない。
plot.Cはdata/bins.csvがない場合に終了コード2で停止し、PDFを出力しない。
必要なCSV列はbin_low_ns,bin_high_ns,all_counts,selected_counts。実データ確認後に作成する。
旧画像はdocs/figure-archive/20261117に保持し、本文からは一旦外した。

PDF出力は共通pdf_output.hxxを使用し、pdfcropでページ原点・回転・余白を正規化する (TeX LiveとGhostscriptが必要)。
