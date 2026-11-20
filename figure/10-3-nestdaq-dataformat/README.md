# NestDAQデータフォーマット：論文用図と再生成資料

本フォルダを単体でコピーして再作図できます。論文の節 `sec:nestdaq-dataformat`、図 `fig:format-*`、表 `tab:format-*` に対応します。図番号は論文のビルド時に確定するので、引用先を管理する際はラベルも記録してください。

## 引用

加島駿一『J-PARC チャームバリオン分光実験のためのリアルタイム事象識別プロセスの開発と評価』修士論文、付録「NestDAQデータフォーマット」、該当図番号。

提出年・公刊URL・最終図番号は論文確定後に追記してください。現在は執筆中のためDOI・公刊年を付与していません。wikiへ引用を移す際は、この論文の確定版を出典とし、図の改変の有無も示してください。利用許諾は論文・参照ソースそれぞれの権利条件に従います。本READMEで新たな再利用ライセンスを付与してはいません。

## 構成と生成

- `pdf/`: 論文用の完成図13点（すべてベクターPDF）
- `data/headers-v1.json`, `words-v3.json`: バイト・ビット配置の定義
- `data/pipeline.json`, `timeframe-v1.json`: 以前の調査で整理した構造定義。現行図のすべてを直接描画する入力ではなく、参照データとして保持
- `render.py`: 定義JSONから `plot.C`、`header-tables.tex`、`verify_layout.cxx` を生成
- `plot.C`, `pdf_output.hxx`: ROOT作図とpdfcropによるページ正規化
- `reference/source/`, `reference/manifest.json`: 参照実装19ファイルとコミット・SHA256
- `reference/original-notes.md`: 以前の調査メモの保存コピー
- `validation.txt`: 構造体サイズ・オフセット・幅の照合結果

必要環境：Python 3（標準ライブラリのみ）、ROOT 6、C++17コンパイラ、TeX Liveのpdfcrop。

```sh
python3 render.py
c++ -std=c++17 verify_layout.cxx -o /tmp/nestdaq-format-layout-check
/tmp/nestdaq-format-layout-check
root -l -b -q plot.C
```

ROOTはバッチ実行でPDFのみ生成します。論文PDFのビルドは別です。図は800×600、線幅3。FileSinkの図だけはcomments[256]を1段へ縮約しており、全体は304 byteです。ビット図のRは予約領域です。

## 出典・版・確認範囲

参照実装：SATSUKIUM/nestdaq-user-impl、コミット `3dd6b69f9b3c37eaa6b97f11c11d0b659c5ab064`。
https://github.com/SATSUKIUM/nestdaq-user-impl/tree/3dd6b69f9b3c37eaa6b97f11c11d0b659c5ab064

以前の `nestdaq-dataformat/docs/format-study/schema/` にある定義を保存して再作図しました。既存の公開記事・原図・元資料は保持しています。本フォルダの図は論文用に新たにROOTで生成したもので、以前の公開履歴がなかったことを意味しません。wiki自体の引用変更・公開は未実施です。

8レコードのsizeof・各フィールドのoffsetof・幅を参照C++ヘッダから静的検証し、4種のワードが64 bitを重複・欠落なく覆うことを検証しました。64 bit time_tを前提とします。Filter.lengthの宣言値が時刻レコードあたり4 byte、実格納が8 byteとなる実装差は本文に注記しています。TOTの時間換算は本付録で確定していません。全世代の形式の互換性を保証する資料ではありません。
