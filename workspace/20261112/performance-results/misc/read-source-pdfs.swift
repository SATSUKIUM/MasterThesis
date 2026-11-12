import Foundation
import PDFKit
let root = "/Users/kashima/codex-cli-workspace/master-thesis/workspace/20261031/K-project-interim-report/Keynote/output"
let specs:[(String,[Int])] = [("K-sys-symp2025",[8,12,13,14,19]),("JPS2026Spring",[8,10,11,12,23]),("JPS2026Autumn",[6,8,9]),("SPADI2026_kashima",[6,8,9,11,12])]
for (name,pages) in specs {
 guard let doc = PDFDocument(url: URL(fileURLWithPath: root+"/"+name+".pdf")) else { fatalError(name) }
 for num in pages { print("\nFILE \(name) PAGE \(num)\n\(doc.page(at:num-1)?.string ?? "[no text]")") }
}
