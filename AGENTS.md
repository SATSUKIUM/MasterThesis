# MasterThesis の作業方針

- 原稿は src/main.tex と src/subfiles/*.tex、図は figure/、参考資料は docs/、補助処理は misc/ に置く。
- 2024B4Paper由来の jsarticle / pLaTeX / dvipdfmx 様式を基本とする。表紙・章見出しは未確定。
- 未確認の研究成果・数値・引用文献を作らない。出典と測定条件を記録する。
- 作業ログは開始日の workspace/YYYYMMDD/作業名/index.html に日本語で残す。
- ビルドはルートで make。out/ は生成物でGit対象外。原本の図・資料PDFは保持する。
- 作業に必要なGit初期化・対象を明示したadd・ローカルコミットは逐次行う。既存変更を破棄しない。
- GitHubのURL共有後に初期プッシュを行う。URL共有前のリモート登録・pushは行わない。

- ユーザーの指定により、編集後のPDF再生成は依頼時のみ行う。設定の確認でも無断でビルドしない。
- VSCodeはMasterThesisをフォルダーとして開き、専用latexmkレシピでout/へ出力する。

- 日本語本文の句読点はユーザー指定の「、。」を使う。「，．」へ統一しない。文章中の半角カンマ・ピリオドはユーザー判断で例外的に使用することがある。コード・URL・TeX構文・小数点は別扱い。
- 表記点検の再開時は src/subfiles/01-notation-notes.tex のチェック項目と検討中の用語表を参照する。

- 表記チェックリストは外側itemizeに項目名、内側itemizeに説明・確認結果を置く。ソースのインデントも揃え、太字見出しと段落分割の形式へ戻さない。

- 付録Bの仕様表はセル末尾に句点を付けず、列挙の区切りは半角カンマと空白を使う。表外の本文は「、。」の方針を維持する。

- 論文の仕様表には機種・数量・規格・容量・設定を簡潔に記載する。Codexからユーザーへの取得報告、検出状況、未取得・要確認の作業案内は作業ログへ置く。搭載規格と実測値、公称値と設定値は区別する。

- 付録Bでは1CPU構成のNUMAノード数は省略する。メモリの搭載内訳は総容量の後に半角括弧で示す (例：128 GiB (32 GiB × 4))。内訳が不明なら補わない。

## 図の管理 (2026-11-17)

- docs/index.htmlを資料の入口とし、docs/figure-guidelines.htmlの図制作方針に従う。
- figure/は章別、その中を原則図別に分ける。写真等は章フォルダへ直接配置してよい。
- 完成図のコピーではなく、再作図用データとROOTマクロを同じ図フォルダへ置く。原本と集計条件を記録し、不明な分布を画像から推定しない。
- ROOTバッチモードでPDFのみ生成する。make figuresは図の生成だけを行い、論文PDFは依頼時のみ生成する。
- 元データがない図は未対応として記録し、旧画像を現行図として掲載しない。原本はdocsの参照アーカイブへ保持する。

- ROOT図は線幅3、横800・縦600を基本とする。includegraphicsはpagebox=cropboxと幅・高さの上限、keepaspectratioを指定し、図とキャプションをページ内に収める。現在の上限は0.95\linewidth・0.70\textheight。

- 図の左右ずれを避けるため、ROOT出力後にfigure/pdf_output.hxxでpdfcropを行いページ座標・回転・余白を正規化する。本文ではmakebox[\linewidth][c]で中央配置し、サイズ上限も保持する。

## 図表配置（2026-11-20 ユーザー合意）

- 文脈優先。短い表・小図は説明段落の直後、大きな比較図は短い説明と同じページにまとめた図表中心のページにする。run・評価項目・章の境界を越えさせない。
- 短い表はH、通常の小図はhtbp、大きな比較図はNeedspaceで説明と図の空きを確保してHでまとめる。全図を一律の強制固定にはしない。章境界はplaceins[section]、run/評価境界はFloatBarrier、通常フロートの先回りはflafterで抑える。
- 図のcaptionは下、表のcaptionは上。本文から番号で参照する。詳細はdocs/figure-guidelines.html#context-first-placement。論文PDFは依頼時だけ生成・確認する。

## 分割subfileの枝番号（2026-11-20）

- 同じ章のファイルを分割する場合は、章の入口を05-0-…、そこから読み込む追加部分を05-1-…のように付け、ファイル名順と読み込み順を揃える。
- 第5章は05-0-evaluate-HLF-with-T103-data.texが入口、05-1-common-flat-or.texが結果部分。ファイル名を変えたらmain.texとinput参照、現行の原稿リンクを更新する。本文は保持し、PDFは依頼なしにビルドしない。

- 付録は読み込み順に10-0-appendix.tex → 10-1-appendix-physical-lr.tex → 10-2-appendix-ltof-readout.tex → 10-3-appendix-nestdaq-dataformat.tex。10-3はmainから10-0の後に直接読み込む。
