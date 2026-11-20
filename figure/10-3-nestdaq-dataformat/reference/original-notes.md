DAQ word: ヒット情報。TDCとTimeOverThreshold、そして読み出し基盤のCH番号。現状8 byte
Heart Beat Delimiter: 一定周期で挿入される区切り。524.288 usごとに入る。現状8*2 byte。上記TDCはHBDからの相対時刻。
HeartBeatFrame Header: 16 byte
どんどん太っていきます
幾つのHeartBeatFrameを一つのSubTimeFrameにまとめるかはユーザーが決めることができる
SubTimeFrame Header: 48 byte。読み出し基盤のTDCモジュールの種類やUNIX時間が記録されている。
TFBでは各STFBのデータを同じ時間軸で統合する
⇨ ので、SubTimeFrameの数は読み出し基盤の数と一致
TimeFrame Header: 24 byte。TimeFrameのIDや、読み出し基盤の数が記録されている。のちの解析で使用するTFのtypeも記録されている。
単一のFilter Header
Trigger Time Headerの数はHBF in STFの数と同じ
TrgTimeはコインシデンスの数と同じ
Filter Header: 56 byte。コインシデンスの数など...
Trigger Time Header: 16 byte。
TrgTime: 8 byte。4 ns精度のコインシデンスTDCが記録されている。
オリジナルのTFが、HBF in STFの数だけ分割される(右図のMETA TFの数はそれと一致)
META TF直下のSTFはHBDを含むが、DAQ wordはコピーされない
TrgTimeの数だけSLICE TFがオリジナルのTFから切り出されて付属する
右図のような生データをFilterTimeFrameSliceABC.icxx/ParseMessages(FairMQParts& inParts)がデコードしてFrameContainer.hで定義されるコンテナにパースします。
データサイズとしては、痩せます
フィルター関連のデータは消えてます
SLICE TFは取捨選択されます
ファイルの最初と最後にFileSink　HeaderとFileSink Trailerがつきます
それぞれ304 byte。内容は同じで、MAGICのみが違う。
