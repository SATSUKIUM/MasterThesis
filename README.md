# MasterThesis

- `src/main.tex`：表紙、共通設定、章の読み込み
- `src/subfiles/*.tex`：章ごとの本文、参考文献、付録
- `figure/`：図の原本・画像
- `docs/`：参考資料・提出版PDF
- `misc/`：補助スクリプト・メモ
- `build/`：生成PDF・中間ファイル（Git対象外）
- `workspace/20261111/latex-git-setup/index.html`：準備の記録

## ビルド

TeX Live 等の `platex`, `latexmk`, `dvipdfmx` と原稿が読み込むパッケージを使用。
リポジトリのルートで `make` を実行すると `build/main.pdf` を生成する。
中間ファイルの削除は `make clean`（生成PDFを保持）。
<!-- 章のみのビルド例：

```sh
latexmk -r .latexmkrc -outdir=../../build/introduction src/subfiles/introduction.tex
``` -->

図は `\includegraphics{example.pdf}` のように `figure/` 内の名前を指定する。
表紙の題目・所属・氏名と章構成は仮置き。研究本文・数値・文献は未記入。

## 再利用元

`../2024B4Paper/TEX/TEX/main.tex`、参照コミット `9d59637`。
`jsarticle` の A4・片面・独立表紙、`times`、数式・図表パッケージ、
節単位の数式・表・図番号、青色リンク、`subfiles` 分割方式を継承。
旧論文の本文・図・著者一覧は転用していない。
共通パッケージは main.tex に集約し、日本語PDFしおり用の `pxjahyper` を追加。

## Git

`.DS_Store`・`.DS_STORE`、LaTeX中間ファイルとビルド出力は追跡しない。
必要な図・参考資料・提出版PDFは `figure/`・`docs/` に置いて管理する。
