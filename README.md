# MasterThesis

- `src/main.tex`：表紙、共通設定、章の読み込み
- `src/subfiles/*.tex`：章ごとの本文、参考文献、付録
- `figure/`：図の原本・画像
- `docs/`：参考資料・提出版PDF
- `misc/`：補助スクリプト・メモ
- `out/`：生成PDF・中間ファイル（Git対象外）
- `workspace/20261111/latex-git-setup/index.html`：準備の記録

## ビルド

TeX Live 等の `platex`, `latexmk`, `dvipdfmx` と原稿が読み込むパッケージを使用。
リポジトリのルートで `make` を実行すると `out/main.pdf` を生成する。
中間ファイルの削除は `make clean`（生成PDFを保持）。
<!-- 章のみのビルド例：

```sh
latexmk -r .latexmkrc -outdir=../../out/introduction src/subfiles/03-introduction.tex
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

## 表記検討メモ

`src/subfiles/01-notation-notes.tex` を表紙の前に表示する。
表は「現在使っている表記／迷っている表記／意図など」の3列。
長くなると自動的に改ページし、見出しを繰り返す。
現在の表記と候補、意図を記録する。統一方針の確定は前提としない。
目次・節番号・表番号には含めない。
提出時は `src/main.tex` の `\notationnotestrue` を
`\notationnotesfalse` に変更してから `make` する。

## 目次と付録

通常の目次に続き、図目次・表目次をそれぞれ別ページに表示する。
図・表が未登録の間も見出しを表示し、captionを追加すると自動で掲載する。
付録は `src/subfiles/10-appendix.tex` 内で `\appendix` に切り替え、
`\section` ごとに「付録A」「付録B」…と表示する。本文は未記入。

## コード表示

`/Users/kashima/LaTeX_personal/TEX/CUDA_get_started/texTemplate.tex` の
`listings,jvlisting` と `needspace` を継承。コードは上下罫線・左行番号・自動折り返し。
元設定の `\smallitshape` は `\small\itshape` に修正。
言語はブロックごとに指定する。

```tex
本文中では \lstinline|cudaDeviceSynchronize()| を使う。

\Needspace{8\baselineskip}
\begin{lstlisting}[language=C++,caption={同期処理の例},label={lst:sync}]
// ホスト側で完了を待つ
cudaDeviceSynchronize();
\end{lstlisting}
```

`\lstinline` の区切り文字はコード内に含まれない文字を使う。
`\Needspace` は必要な場合だけ指定し、短いブロックの直前で改ページを促す。

付録の後は `\clearpage` で改ページし、暫定の参考メモ
`src/subfiles/11-reference-notes.tex` を表示する。番号なしの参考ページに、インラインコード・コードブロック・参照・改ページ調整の入力例と表示例を掲載する。

概要は `src/subfiles/02-abstract.tex` に記述する。タイトルページの直後、
目次の前に独立ページとして表示する。本文は未記入。

## VSCodeの出力先（2026-11-12）

VSCodeでは **MasterThesisフォルダーを開く**。`.vscode/settings.json` の
`MasterThesis (latexmk)` レシピがユーザー共通のplatex→コピー設定を置き換え、
最初からリポジトリ直下の `out/` にPDFと中間ファイルを生成する。
`src/subfiles/` の単独ビルドでも出力先は同じ。成功後は `.out` のみ削除し、
差分ビルド・参照解決に必要な他の中間ファイルとSyncTeXは保持する。
`make clean` はPDFを保持して中間ファイルを削除する。
既存のsrc以下のPDFは削除せず `out/previous/src/` 以下へ移動した。
編集後のPDF再生成はユーザーの依頼時のみ行う。

subfilesのファイル名には、main.texでの読み込み順に01〜11の番号を付ける。
番号は文書内の章番号ではなく、執筆メモ・概要・付録などを含むファイルの表示順を表す。

## 付録Bの計測環境 (試作)

`src/subfiles/10-appendix.tex` の付録Bにmarq04〜07とe50server03の構成記録を整理。
出典の固定コピーとハッシュは `docs/measurement-environments/20261112/`、
判断・未確認事項は `workspace/20261112/appendix-b-environments/index.html` を参照。
構成調査日とベンチマーク実行日時は区別し、各測定系列との対応は未確認。

## 発表資料からの性能評価の取り込み (2026-11-12)

05にオンラインフィルタ、06に現行WG4のLogicFilter評価、10付録Aにchannel-map検索性能を追記。
07にT103の平均負荷換算、09に参考文献を追加。
出典・旧版との区別は `workspace/20261112/performance-results/index.html`、
集計値の固定コピーは `docs/performance-results/20261112/` を参照。
