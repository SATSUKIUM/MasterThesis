#include "../../pdf_output.hxx"
#include <TROOT.h>
#include <TStyle.h>
#include <TGraph.h>
#include <TH1D.h>
#include <TLine.h>
#include <TLatex.h>
#include <fstream>
#include <sstream>
#include <vector>
#include <algorithm>
struct RBComparison{std::string kind,mode,group;double ratio;};
void plot(){
 gROOT->SetBatch(kTRUE);gStyle->SetOptStat(0);gStyle->SetLineWidth(3);gStyle->SetHistLineWidth(3);gStyle->SetFrameLineWidth(3);gStyle->SetPaperSize(20,15);
 std::ifstream f("data/governor-group-comparison.csv");std::string line;std::getline(f,line);std::vector<RBComparison> rows;
 while(std::getline(f,line)){std::vector<std::string>a;std::stringstream s(line);std::string x;while(std::getline(s,x,','))a.push_back(x);if(a.size()!=6)throw std::runtime_error("comparison row");rows.push_back({a[0],a[1],a[2],std::stod(a[5])});}
 for(auto group:{"all","has_slice","no_slice"}){
  std::vector<double> y;std::vector<std::string> labels;
  for(auto r:rows)if(r.group==group){y.push_back(r.ratio);labels.push_back((r.kind=="tof"?"TOF":r.kind=="multiplicity"?"Multiplicity":"Track")+std::string(r.mode=="cond"?" CR":" PS"));}
  int n=y.size();if(n!=(std::string(group)=="no_slice"?3:6))throw std::runtime_error("comparison count");
  TCanvas c(("governor_"+std::string(group)).c_str(),"",800,600);c.SetCanvasSize(800,600);c.SetLeftMargin(.14);c.SetRightMargin(.04);c.SetBottomMargin(.19);c.SetTopMargin(.10);c.SetLogx(0);c.SetLogy(0);c.SetGrid(1,1);
  double top=std::max(1.,*std::max_element(y.begin(),y.end()))*1.2;TH1D frame(("gov_frame_"+std::string(group)).c_str(),";Filter / timing scope;Speed ratio (performance / conservative)",200,0,n);frame.SetMinimum(0);frame.SetMaximum(top);frame.GetXaxis()->SetLabelSize(0);frame.GetXaxis()->SetTitleOffset(1.8);frame.GetYaxis()->SetTitleOffset(1.4);frame.Draw("AXIS");
  TLine one(0,1,n,1);one.SetLineStyle(2);one.SetLineWidth(3);one.Draw();TGraph graph;graph.SetMarkerStyle(20);graph.SetMarkerSize(1.3);graph.SetMarkerColor(kBlue+1);graph.SetLineWidth(3);TLatex txt;txt.SetTextAlign(21);txt.SetTextSize(.031);
  for(int i=0;i<n;++i){graph.SetPoint(i,i+.5,y[i]);txt.DrawLatex(i+.5,-top*.055,labels[i].c_str());txt.DrawLatex(i+.5,y[i]+top*.04,TString::Format("%.3f",y[i]));}graph.Draw("P SAME");TLatex title;title.SetNDC();title.SetTextSize(.030);title.DrawLatex(.14,.94,("e50server03 / 20,000 TF / "+std::string(group)).c_str());
  if(std::string(group)=="no_slice"){title.SetTextSize(.026);title.DrawLatex(.17,.25,"ProcessSlice: N/A (not called)");}
  auto file=std::string(group)=="all"?"governor-comparison.pdf":"governor-"+std::string(group)+".pdf";save_figure_pdf(c,file.c_str());
 }
}
