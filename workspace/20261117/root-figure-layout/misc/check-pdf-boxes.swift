import Foundation
import PDFKit
var records:[[String:Any]]=[]
for path in CommandLine.arguments.dropFirst(){
 guard let pdf=PDFDocument(url:URL(fileURLWithPath:path)),pdf.pageCount==1,let p=pdf.page(at:0) else{fatalError(path)}
 let media=p.bounds(for:.mediaBox),crop=p.bounds(for:.cropBox)
 guard p.rotation==0,media==crop,media.origin.x==0,media.origin.y==0,media.width>media.height else{fatalError("unnormalized: "+path)}
 records.append(["path":path,"width_pt":media.width,"height_pt":media.height,"rotation":p.rotation,"origin":[0,0]])
}
let d=try JSONSerialization.data(withJSONObject:records,options:[.prettyPrinted,.sortedKeys])
print(String(data:d,encoding:.utf8)!)
