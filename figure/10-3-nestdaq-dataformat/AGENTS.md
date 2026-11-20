# データフォーマット付録の図と本文

- ユーザー指定：元のnestdaq-dataformatのSVG図を論文でも取り込み、SVG生成スクリプトをこのフォルダにまとめる。ROOTで描き直さない。この指定は親の一般的なROOT作図方針より優先する。
- 説明の原本コピーはarticle/index.html（元publish/site/index.html）。その説明・表・SVG図を付録に収録する。内容を別の要約へ置き換えない。
- build_format.pyは元の生成スクリプトを改変せずに保持。再生成はbuild.pyを使う。PDFはSVGのLaTeX取り込み用変換であり、論文全体のビルドではない。
- 元HTML・SVG・スクリプトの出典ハッシュはreference/origin.json。既存資料・公開履歴は保持する。wikiの変更・公開は別の指示に従う。
