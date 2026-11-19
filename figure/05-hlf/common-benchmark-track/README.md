# 共通ベンチマーク ROOT 図

`root -l -b -q plot.C`でPDFのみ生成する。ROOT 6.36.04、pdfcrop、Ghostscriptを使用。

- 2026-11-19の各20,000 TF、各段1プロセス、各条件1回。e50はconservative/performance、他3台performance。
- condは送受信を除くConditionalRun、sliceはProcessSliceのみ。steady_clockのdouble µs、関数末尾のメンバーvector、PostRun出力。両計時は別実行。
- condのslice有無は、同じ条件のslice実行とmessage/TF IDで対応付けて再構成した。messages.csvにslice数を保存。全5環境で台帳が同一であり、12864-byteのMETAのみパケットとの独立照合も一致。
- has_sliceは9734メッセージ、no_sliceは10266メッセージ。sliceには152880呼び出しがある。sliceなしではProcessSliceは呼ばれないので図を作らずN/Aとする。採用されたsliceの有無とは区別する。
- TH1は200 bins、TH2は200×200 bins。XY・Zとも線形、SetGrid、線幅3、800×600。
- fullは全サンプルを含む範囲。zoomは表示のみをプールしたp99.5までに拡大し、overflow件数を図とhistogram-audit.csvへ記録。平均・統計量は表示範囲によらず全サンプルから計算する。
- plot.Cと共通PDF正規化ヘルパー ../../pdf_output.hxxを使う。原本の保存済み測定CSV.gzをdata/へ同梱し、再測定は行わない。
- Trackは0d7bbf6＋現行channel-map API互換移植・KLDC番号名前解決・ROOT診断無効化の参照版。発表版一致、物理トラックパラメータ一致は未確認。
