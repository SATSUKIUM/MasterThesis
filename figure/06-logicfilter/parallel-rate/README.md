# LF並列処理率

メンバー時刻V2、9条件・全35 LFの集計をdata/per-process.csvへ固定コピー。
各LFでinput_bytes/net_us_sumを求め、条件別に合算する。N倍pooled比でも実経過時間のスループットでもない。
このフォルダで `root -l -b -q plot.C`。parallel-rate.pdfのみ生成。再計算値はdata/plot-values.csvへ保存。
