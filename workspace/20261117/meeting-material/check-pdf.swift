import Foundation
import PDFKit
import AppKit
let url=URL(fileURLWithPath:CommandLine.arguments[1])
guard let doc=PDFDocument(url:url) else{fatalError("Cannot open PDF")}
var all=""
for i in 0..<doc.pageCount{
 let p=doc.page(at:i)!;let text=p.string ?? "";all+=text
 print("PAGE \(i+1)\n\(text)\n")
 let image=p.thumbnail(of:NSSize(width:850,height:1200),for:.cropBox)
 let rep=NSBitmapImageRep(data:image.tiffRepresentation!)!
 try rep.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:"/tmp/meeting-material-page-\(i+1).png"))
}
guard all.contains("draft abstract"),all.contains("目次"),!all.contains("過去の修論の切り口"),!all.contains("表記チェック項目") else{fatalError("Unexpected content")}
print("VERIFIED \(doc.pageCount) pages")
