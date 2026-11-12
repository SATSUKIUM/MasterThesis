# SPADI-A WG4：追加の現行指示（2026-11-11）

親ディレクトリのAGENTS.mdと併せて適用する。以下はユーザーの追加指定で、以前の表示確認・PDF名の指定に優先する。

- HTMLスライド・図表・PDFの表示確認は省略する。ユーザーが閲覧時に指摘した点を適宜修正する。リンク・構造・生成コマンドの完了等の通常の確認は継続する。
- HTMLスライド編集後は従来どおりPDFを生成する。現行の印刷用PDF名は `slides/20261111_Kashima.pdf`（指定日のYYYYMMDD_Kashima.pdf）。
- PDF生成は `misc/render-vector-slides.swift` に `slides/index.html` と上記PDFのパスを渡す。
- `slides/印刷用-A4横.pdf` は現行名への互換シンボリックリンク。`slides/試作版-A4横.pdf` はその旧名への既存リンク。保存版のHTML/PDFは更新しない。

- PDFの再生成・更新に都度の許可確認は不要（2026-11-11ユーザー再指定）。HTML編集と併せて自律的に更新する。実行環境が必須とする権限手続きのみ従う。

## メイン版の採用（2026-11-11）

- ユーザーがrun000668.dat版（p8/p9拡大・p10のHTML/SVG描画・補足SVG表示を反映した35ページ）を正式なメイン版に採用した。今後の編集対象は引き続き `slides/index.html` と `slides/20261111_Kashima.pdf`。各条件1 RUN・共有mmap入力という測定条件を維持して記載する。
- run000400.dat版は `variants/run000400/slides/index.html` と同ディレクトリの `20261111_Kashima.pdf` に保存。リンク再配置前のHTMLを `source-original.html` に完全保存し、元のSHA-256を保持する。これらを通常の編集対象にしない。
- `variants/run000668/slides/index.html` はメインHTMLへの転送、同PDF名はメインPDFへの互換リンク。二重編集しない。スライドの生成・検証コードは `measurements/20261111-run000668/misc/`。測定と採用のログは同測定ディレクトリの `index.html`、切替記録は `data/misc/main-promotion.json`。
- 旧スタイル保存版・過去の原資料・公開サイトはこの切替では更新しない。PDF生成はメインのパスを用い、表示確認は引き続き省略する。

## 操作案内と表紙（2026-11-11）

- 操作案内はRegular-Meeting/workspace/20261109/zst-compression/slides/index.htmlと同様、画面下部の独立した操作バーに置く。スライドへのオーバーレイはしない。表示時は下部に最低64 px（折返し時は操作バー実高＋16 px）の領域を確保してスライドを拡縮・配置する。Hで操作バー全体を表示／非表示にし、その都度再配置する。
- 表紙・ブラウザーのタイトルにrun000668.dat等の入力ファイル名を付けない。入力ファイル名は測定条件のページ・ログに記載する。
- 再生成時はmeasurements/20261111-run000668/misc/update-controls.pyのapplyを使い、操作バー・表紙の指定を維持する。

## 表記（2026-11-11）

- 現行スライドの括弧は半角の `(` `)` を使用する。
- プロセス構成の数は名称の前へ置き、`1×リプレイヤー → 1×LF → 4×Sink` のように表す。

## p10の測定系列（2026-11-12）

- ユーザー指定により、p10は補足B15と同じsix-clockの7条件を使う。値はsix/data/misc/six-clock-summary.jsonのnet_lf_count_scaled_MB_s (N × Σinput_bytes / ΣT_net)。実経過時間による総スループットと混同しない。1 GPUはLF1〜5、2 GPUはLF2/4。2 GPU LF6/8は保留。p10のHTML/SVG切り替え・ホバー・測定値表もこの系列に揃える。

## LF処理率の集計（2026-11-12改訂）

- p10・補足B15右図は、全LFの個別CSVを使い、各LF iでB_i / T_iを求めた和を表示する。N × pooled比のLF数倍換算へ戻さない。出典はmeasurements/20261111-run000668/six/data/misc/six-clock-individual-sum.json。従来のN倍換算値は履歴として保持する。
- 11月11日の旧six-clock値は、ローカル整数ns時刻と関数終了ガードによる旧実装の測定。既存プロファイル更新・Send試行ログ・1秒ごとの進捗ファイル更新がT_net内に含まれる。この制約を隠さない。メンバーtime_pointと、終了時刻より後のvector追加・PostRunでのCSV出力に統一した新計測とは区別する。
- 2 GPU LF6/8は2026-11-12にユーザーが保留解除・新方式で各1 RUNの追加測定を承認した。LF10は省略を維持する。

## メンバー時刻方式を採用（2026-11-12）

- 現行p10・補足B14/B15はmeasurements/20261112-member-clock/のV2・全9条件を使う。1 GPU LF1〜5、2 GPU LF2/4/6/8を各1 RUN、全35 LFの個別CSVから処理率を求めた和を表示する。LF10は省略。旧系列は保持するが混ぜない。
- 主計測はsteady_clock::time_pointのメンバー6個。メッセージの後片付け後に終了時刻を取り、新旧プロファイルの差分演算・RUN全体の測定vector追加・進捗出力は終了時刻の後に行う。net µsはstd::vector<double>へ保持し、PostRunでLF別の測定CSVへ保存する。Send再試行の時刻は一時バッファへ保持し、全Send時間を差し引く。
- 旧局所ns/終了ガード方式と開発V1は保存版。V1の開発確認とLF2中断は採用データに含めない。
- 再生成にはmeasurements/20261112-member-clock/misc/update-slides.pyを使う。従来clone-slides.pyも採用マーカーがあれば最後に新方式を適用する。現行の採用元はdata/misc/member-clock-summary.json、LF別数値はmember-clock-per-process.csv。

- p11の並列処理率の要約は、p10と同じ新方式の各LF処理率合計に必ず同期する。旧測定の実経過スループットを代入しない。単一LFのCPU/GPU比較は1リプレイヤー・process_usであり、4リプレイヤー・T_netのp10と区別して記載する。

## 発表スライドの文体（2026-11-12）

- 「補足に整理した」等、Codex CLIから依頼主への作業報告・編集内容の説明を発表スライドに載せない。作業報告はログへ置き、スライドには発表内容・結果・測定条件を記載する。

## p10のGPU使用率切り替え（2026-11-12）

- 図枠右上の「GPU使用率」で、同じメンバー時刻V2・9 RUNの平均GPU使用率へ切り替える。2 GPU時のGPU 0/1を別々に表示し、既存の構成タブ・値表示・測定値表も維持する。初期表示はスループット。
- 「点にカーソルを合わせると測定値を表示」の案内文は載せない。実際のホバー・フォーカス値表示は保持する。
- 使用率の出典はmeasurements/20261112-member-clock/data/misc/gpu-utilization-summary.json。生成コードadd-p10-gpu-toggle.pyをclone-slides.pyの最後に適用する。

- 数量と名称を結ぶ×の前後は空けず、`1×リプレイヤー`、`4×Sink`、`8×LF with 2×GPU`のように詰める (2026-11-12追加指定)。
