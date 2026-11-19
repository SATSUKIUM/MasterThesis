# 共通ベンチマークの表とガバナー比較

stats.csv/JSONは表示範囲で切らない全サンプルの統計。各ケース・群のn、bytes、us、算術平均B/t、合算比ΣB/Σt、時間平均・分位点を収録。data/provenance.jsonに原CSV.gzの所在とSHA-256を保存した。図用原CSV.gzは隣のcommon-benchmark-{tof,multiplicity,track}/dataへ同梱。

C=conservative、P=performance。ConditionalRunはall/has_slice/no_slice、ProcessSliceはhas_sliceのみ（no_sliceには呼び出しがなくN/A）。分類は別実行のmessage/TF IDを使う再構成で、metadata-onlyの12864 bytesとも照合済み。

plot.CはROOTのTGraphでガバナー速度比を描く。フレームは200ビン、6点はヒストグラムの度数ではなくカテゴリ別の値。PDFのみ生成する。make_tables.pyでdata/stats.jsonからtables.texを再生成可能。thesis全体のビルドは行わない。
