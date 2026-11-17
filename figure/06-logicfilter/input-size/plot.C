#include <TCanvas.h>
#include <TGraph.h>
#include <TF1.h>
#include <TLegend.h>
#include <TLatex.h>
#include <TROOT.h>
#include <TStyle.h>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <stdexcept>
TGraph read_profile(const char* filename){
  std::ifstream f(filename);if(!f)throw std::runtime_error(filename);std::string line;std::getline(f,line);TGraph graph;
  while(std::getline(f,line)){
    std::vector<std::string> cells;std::stringstream ss(line);std::string cell;while(std::getline(ss,cell,','))cells.push_back(cell);
    if(cells.size()!=11)throw std::runtime_error("bad profile row");
    if(cells[1]=="1")graph.SetPoint(graph.GetN(),std::stod(cells[4])/1e6,std::stod(cells[8])/1000.);
  }
  if(graph.GetN()!=72121)throw std::runtime_error("expected 72121 TF");return graph;
}
void plot(){
  gROOT->SetBatch(kTRUE);gStyle->SetOptStat(0);auto cpu=read_profile("data/cpu.csv"),gpu=read_profile("data/gpu.csv");
  cpu.SetMarkerColor(kBlue+2);gpu.SetMarkerColor(kRed+1);cpu.SetMarkerStyle(20);gpu.SetMarkerStyle(20);cpu.SetMarkerSize(.22);gpu.SetMarkerSize(.22);
  const char* files[]={"input-time.pdf","cpu-fit.pdf","gpu-fit.pdf"};
  std::ofstream stats("data/fit-results.csv");stats<<"implementation,frames,intercept_ms,slope_ms_per_MB,R2\n";stats.precision(16);
  for(int mode=0;mode<3;++mode){
    TCanvas c(TString::Format("input_%d",mode),"",1100,700);c.SetLeftMargin(.14);c.SetBottomMargin(.14);c.SetRightMargin(.04);c.SetTopMargin(.10);
    auto frame=c.DrawFrame(0,0,1.3,mode==2?2:12);frame->SetTitle("run000668.dat / Monitor Off / 1 RUN;LF input size (MB/TF);Processing time (ms/TF)");
    TLegend legend(.18,.78,.47,.89);legend.SetBorderSize(0);legend.SetFillStyle(0);
    if(mode==0){cpu.Draw("P SAME");gpu.Draw("P SAME");legend.AddEntry(&cpu,"CPU","p");legend.AddEntry(&gpu,"GPU","p");legend.Draw();}
    else{
      TGraph &g=mode==1?cpu:gpu;g.Draw("P SAME");const char* name=mode==1?"CPU":"GPU";legend.AddEntry(&g,name,"p");legend.Draw();
      // Equal-weight regression: ALL TF, including points outside displayed axes.
      long double sx=0,sy=0,sxx=0,sxy=0,syy=0;for(int i=0;i<g.GetN();++i){double x,y;g.GetPoint(i,x,y);sx+=x;sy+=y;sxx+=x*x;sxy+=x*y;syy+=y*y;}
      auto n=g.GetN();double b=(n*sxy-sx*sy)/(n*sxx-sx*sx),a=(sy-b*sx)/n;double r2=(n*sxy-sx*sy)*(n*sxy-sx*sy)/((n*sxx-sx*sx)*(n*syy-sy*sy));
      TF1 fit("fit","[0]+[1]*x",0,1.3);fit.SetParameters(a,b);fit.SetLineColor(kBlack);fit.Draw("SAME");TLatex note;note.SetNDC();note.SetTextSize(.027);note.DrawLatex(.46,.83,TString::Format("a=%.4f, b=%.4f, R^{2}=%.4f",a,b,r2));
      stats<<name<<","<<n<<","<<a<<","<<b<<","<<r2<<"\n";c.SaveAs(files[mode]);continue;
    }
    c.SaveAs(files[mode]);
  }
}
