#include <TROOT.h>
#include <TCanvas.h>
#include <TH1D.h>
#include <TLegend.h>
#include <TSystem.h>
#include <fstream>
#include <sstream>
#include <vector>
#include <algorithm>
#include <stdexcept>
// Schema: bin_low_ns,bin_high_ns,all_counts,selected_counts.
// No digitization or guessed distribution is supplied.
void plot(){
  gROOT->SetBatch(kTRUE);std::ifstream f("data/bins.csv");if(!f){Error("plot","TOF source histogram is not identified; data/bins.csv is required. No PDF produced.");gSystem->Exit(2);return;}
  std::string line;std::getline(f,line);std::vector<double> edges,a,b;
  while(std::getline(f,line)){std::replace(line.begin(),line.end(),',',' ');std::istringstream ss(line);double lo,hi,x,y;if(!(ss>>lo>>hi>>x>>y)||hi<=lo||x<0||y<0)throw std::runtime_error("invalid bin");if(!edges.empty()&&lo!=edges.back())throw std::runtime_error("non-contiguous bins");if(edges.empty())edges.push_back(lo);edges.push_back(hi);a.push_back(x);b.push_back(y);}
  if(a.empty())throw std::runtime_error("empty histogram");TH1D all("all",";TOF (ns);Counts",a.size(),edges.data()),selected("selected","",a.size(),edges.data());for(int i=0;i<(int)a.size();++i){all.SetBinContent(i+1,a[i]);selected.SetBinContent(i+1,b[i]);}all.SetStats(false);all.SetLineColor(kBlue+2);selected.SetLineColor(kRed+1);TCanvas c("tof","",1000,700);all.Draw("HIST");selected.Draw("HIST SAME");TLegend legend(.65,.75,.9,.9);legend.AddEntry(&all,"All","l");legend.AddEntry(&selected,"Selected","l");legend.Draw();c.SaveAs("tof-selection.pdf");
}
