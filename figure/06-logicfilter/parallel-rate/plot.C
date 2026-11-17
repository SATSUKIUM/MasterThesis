#include <TCanvas.h>
#include <TGraph.h>
#include <TLegend.h>
#include <TROOT.h>
#include <TStyle.h>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <stdexcept>
void plot(){
  gROOT->SetBatch(kTRUE);gStyle->SetOptStat(0);std::ifstream f("data/per-process.csv");if(!f)throw std::runtime_error("missing per-process.csv");std::string line;std::getline(f,line);
  std::map<std::pair<int,int>,double> rates;int rows=0;
  while(std::getline(f,line)){std::stringstream ss(line);std::string cell;std::vector<std::string> v;while(std::getline(ss,cell,','))v.push_back(cell);if(v.size()!=11)throw std::runtime_error("bad row");rates[{std::stoi(v[1]),std::stoi(v[2])}]+=std::stod(v[6])/std::stod(v[7]);++rows;}
  if(rows!=35||rates.size()!=9)throw std::runtime_error("expected 35 LF records / 9 conditions");
  TGraph one,two;std::ofstream table("data/plot-values.csv");table.precision(16);table<<"gpus,lf_count,sum_individual_LF_MB_s\n";
  for(const auto &r:rates){auto &g=r.first.first==1?one:two;g.SetPoint(g.GetN(),r.first.second,r.second);table<<r.first.first<<","<<r.first.second<<","<<r.second<<"\n";}
  TCanvas c("parallel","",1000,700);c.SetLeftMargin(.14);c.SetBottomMargin(.14);c.SetRightMargin(.04);c.SetTopMargin(.06);c.SetGrid();auto frame=c.DrawFrame(.5,0,8.5,2100);frame->SetTitle(";LF processes;Sum of individual LF processing rates (MB/s)");
  one.SetMarkerColor(kBlue+2);one.SetLineColor(kBlue+2);two.SetMarkerColor(kRed+1);two.SetLineColor(kRed+1);one.SetMarkerStyle(20);two.SetMarkerStyle(21);one.SetLineWidth(2);two.SetLineWidth(2);one.Draw("LP SAME");two.Draw("LP SAME");TLegend legend(.18,.75,.45,.9);legend.SetBorderSize(0);legend.SetFillStyle(0);legend.AddEntry(&one,"1 GPU","lp");legend.AddEntry(&two,"2 GPU","lp");legend.Draw();c.SaveAs("parallel-rate.pdf");
}
