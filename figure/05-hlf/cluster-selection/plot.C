#include "../../pdf_output.hxx"
#include <TCanvas.h>
#include <TGraph.h>
#include <TLegend.h>
#include <TLatex.h>
#include <TStyle.h>
#include <TROOT.h>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <stdexcept>
void plot(){
  gROOT->SetBatch(kTRUE);gStyle->SetLineWidth(3);gStyle->SetHistLineWidth(3);gStyle->SetFrameLineWidth(3);gStyle->SetPaperSize(20,15);gStyle->SetOptStat(0);
  std::ifstream f("data/counts.csv");if(!f)throw std::runtime_error("missing data/counts.csv");
  std::string line;std::getline(f,line);TGraph all,low,high;int i=0;
  while(std::getline(f,line)){std::replace(line.begin(),line.end(),',',' ');std::istringstream s(line);int n,run;double a,l,h;if(!(s>>n>>run>>a>>l>>h))throw std::runtime_error("bad count row");all.SetPoint(i,n,a);low.SetPoint(i,n,l);high.SetPoint(i,n,h);++i;}
  if(i!=3)throw std::runtime_error("expected three cuts");
  TCanvas c("cluster","",800,600);c.SetCanvasSize(800,600);c.SetLeftMargin(.14);c.SetBottomMargin(.14);c.SetTopMargin(.06);c.SetRightMargin(.04);
  auto frame=c.DrawFrame(-.1,0,2.1,450000);frame->SetTitle(";Minimum layers (N_{cluster} #geq 2);Events");
  TGraph* graphs[]={&all,&low,&high};int colors[]={kGray+2,kTeal+2,kOrange+7};const char* labels[]={"All events","Tracks < 2","Tracks #geq 2"};
  TLegend legend(.57,.72,.93,.93);legend.SetBorderSize(0);legend.SetFillStyle(0);
  for(int k=0;k<3;++k){graphs[k]->SetLineColor(colors[k]);graphs[k]->SetMarkerColor(colors[k]);graphs[k]->SetMarkerStyle(20);graphs[k]->SetLineWidth(3);graphs[k]->Draw("LP SAME");legend.AddEntry(graphs[k],labels[k],"lp");}
  legend.Draw();TLatex text;text.SetTextSize(.032);for(int j=0;j<3;++j){double x,y,xa,ya;high.GetPoint(j,x,y);all.GetPoint(j,xa,ya);text.DrawLatex(x-(j==2?.20:.07),y+16000,TString::Format("%.1f%%",100*y/ya));}save_figure_pdf(c, "cluster-selection.pdf");
}
