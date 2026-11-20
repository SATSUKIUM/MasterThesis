#include "../../pdf_output.hxx"
#include <TFile.h>
#include <TH1D.h>
#include <TGraph.h>
#include <TStyle.h>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
std::vector<std::vector<double>> read(const char*p){std::ifstream f(p);std::string l;getline(f,l);std::vector<std::vector<double>>r;while(getline(f,l)){for(char&c:l)if(c==',')c=' ';std::istringstream s(l);std::vector<double>a;double x;while(s>>x)a.push_back(x);r.push_back(a);}return r;}
void plot(){gROOT->SetBatch();gStyle->SetOptStat(0);gStyle->SetHistLineWidth(3);gStyle->SetLineWidth(3);gStyle->SetFrameLineWidth(3);auto rows=read("tf.csv"),win=read("windows.csv");TCanvas c("c","",800,600);c.SetLeftMargin(.14);c.SetBottomMargin(.14);c.SetGrid();TFile out("histograms.root","RECREATE");std::ofstream a("histogram-audit.csv");a<<"plot,entries,bins,underflow,overflow\n";for(int type=0;type<3;++type){double max=0;auto&r=type==2?win:rows;for(auto&v:r){if(type==2&&v[1]<.099999)continue;max=std::max(max,type==0?v[3]:type==1?v[4]*.001:v[3]*.001);}std::string name=type==0?"slice-count":type==1?"tf-trigger-rate":"100ms-trigger-rate";TH1D h(name.c_str(),type==0?";Slices per TF;TF count":type==1?";Triggers / TF duration [kHz];TF count":";Trigger rate [kHz];0.1 s window count",200,0,max*1.01);h.SetDirectory(nullptr);for(auto&v:r){if(type==2&&v[1]<.099999)continue;h.Fill(type==0?v[3]:type==1?v[4]*.001:v[3]*.001);}h.SetLineColor(kBlue+1);h.Draw("hist");save_figure_pdf(c,(name+".pdf").c_str());h.Write();a<<name<<','<<h.GetEntries()<<",200,"<<h.GetBinContent(0)<<','<<h.GetBinContent(201)<<'\n';}TGraph g;for(int i=0;i<(int)win.size();++i)g.SetPoint(i,win[i][0]+win[i][1]*.5,win[i][3]*.001);g.SetTitle(";Acquisition time from first HBF [s];Trigger rate [kHz]");g.SetLineWidth(3);g.SetLineColor(kBlue+1);g.SetMinimum(0);g.Draw("AL");save_figure_pdf(c,"trigger-time-series.pdf");g.Write("time-series");out.Close();}
