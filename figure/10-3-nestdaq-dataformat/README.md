# NestDAQデータフォーマット：元のHTML・SVGを収録した論文付録

## このフォルダの役割

Google Driveの `nestdaq-dataformat/publish/site/index.html` にある説明の1〜5節を、表とSVG図21点ごと付録へ収録しています。`docs/format-study/index.html` は形式検討の入口で、その先の `dataformat.html` が解説本文、`publish/site/index.html` が同じ本文の公開用HTMLです。作り直したROOT図への置換はしません。

- `article/index.html`：元の説明HTMLの保存コピー（本文58段落、表16点、図21点）。関連CSS、ソースの行番号付きHTML、ライセンスも保持
- `svg/`：このHTMLが使う既存のSVG図21点。初回収録時は元ファイルとSHA256一致
- `pdf/`：上記SVGからrsvg-convertで変換したLaTeX取り込み用のベクターPDF。図の内容を描き直さない
- `build_format.py`：元のSVG生成スクリプトそのもの（改変なし）
- `schema/`、`fonts/`、`packing-notes.html`、`pipeline-notes.html`、`format-notes.html`、`font-controls.js`：元スクリプトの入力一式
- `reference/source/`：参照コードとMITライセンス。コミットと各ファイルSHA256は `reference/manifest.json`
- `reference/origin.json`：取り込み元、元HTML・スクリプト・SVGのSHA256
- `build.py`：元スクリプトを期待されるディレクトリ構造の一時領域で実行し、SVGとPDFを生成する実行用スクリプト
- `article_to_tex.py`：保存した説明HTMLを `appendix-body.tex` へ移す。Webのナビゲーションなどだけ除き、段落・表・図を収録
- `article-mapping.json`：収録した段落数・表数・図一覧・説明HTMLの参照ソースアンカー

## 再生成

このフォルダを単体でコピーして使用できます。Python 3（標準ライブラリのみ）、clang++、librsvgのrsvg-convertが必要です。

```sh
# 既存SVGをそのままPDFへ変換し、説明HTMLから付録本文を生成
python3 build.py --from-existing-svg
# 元のスクリプト・JSON・フォントからSVG自体も再生成
python3 build.py
```

後者は `editable-svg/` に文字入りSVGも出力し、`svg/` にはNoto Serifを輪郭化した表示用SVGを生成します。元の `build_format.py` はプロジェクト内のパス構造を前提とするため、直接実行する代わりに `build.py` を使います。外部のGoogle Driveや元プロジェクトを参照せず、公開やZIP作成も行いません。論文全体のPDFビルドは別です。

初回収録は `--from-existing-svg` で元SVGのバイト列を保持してPDF変換しています。`article/` は元資料の保存用で、再生成後のSVGは `svg/`、付録本文は `appendix-body.tex` です。記事内容を更新する場合は `article/index.html` を編集して本文を再生成します。各図・表の元HTMLとの対応は `article-mapping.json` を参照してください。

## 引用

加島駿一『J-PARC チャームバリオン分光実験のためのリアルタイム事象識別プロセスの開発と評価』修士論文、付録「NestDAQデータフォーマットとデバイス間の構造変化」、該当図番号。

図のラベルは `fig:format-svg-<SVGの拡張子を除いたファイル名>`、付録のラベルは `sec:nestdaq-dataformat` です。提出年・公刊URL・最終図番号は論文の確定後に記入してください。現在は執筆中のため公刊年・DOIは付与していません。wikiの引用変更・公開は未実施です。既存資料の公開履歴と原図は保持しています。フォントと参照コードは同梱ライセンス、その他の図文は著者の利用条件に従います。

## 検証範囲

初回収録では元のHTML・生成スクリプト・表示SVG21点のハッシュを照合し、PDF21点を生成しました。原稿には元HTMLの全58段落、全16表、全21図を収録しています（Webナビ・SVG原寸リンク・末尾フォントライセンス案内を除く）。元の本文にある「現在のBySomethingは全SLICEを保持」は参照スナップショットのスケルトンに関する説明であり、ベンチマークで用いたTOF等の選別実装を意味しません。論文全体のPDFビルド・組版の目視確認は別途です。

再生成時のeditable-svg/はフォントを各SVGへ埋め込む重複出力のためGit対象外です。再生成入力・完成SVG・PDFはGitで保持します。

元スクリプトを別の一時フォルダで実行して全SVGを再生成し、title/descと整形用空白を除く全描画要素・属性が既存SVG21点と一致することを確認しました（validation.json）。同時に64項目のsizeof/offsetof検証も通過しています。
