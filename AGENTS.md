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
