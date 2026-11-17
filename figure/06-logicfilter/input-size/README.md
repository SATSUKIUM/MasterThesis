# LF入力サイズと処理時間

run000668、CPU/GPU各1 RUN。元の全TFプロファイルをdata/cpu.csvとgpu.csvへ固定コピー。
received=1を全件使用。input_bytes/1e6 [MB]、process_us/1000 [ms]。各72121 TF。
このフォルダで `root -l -b -q plot.C`。input-time.pdf, cpu-fit.pdf, gpu-fit.pdfを生成する。
表示範囲外を除外せず全TFから等重み一次回帰。結果はdata/fit-results.csvに保存。
