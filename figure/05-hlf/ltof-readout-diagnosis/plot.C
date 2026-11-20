#include "../../pdf_output.hxx"
#include <TFile.h>
#include <TH1D.h>
#include <TGraph.h>
#include <TLegend.h>
#include <TLatex.h>
#include <TStyle.h>
#include <fstream>
#include <sstream>
#include <map>
#include <array>
#include <memory>
#include <vector>
std::vector<std::vector<std::string>> csv(const std::string&p){std::ifstream f(p);std::string l;getline(f,l);std::vector<std::vector<std::string>>r;while(getline(f,l)){std::stringstream ss(l);std::vector<std::string>a;std::string x;while(getline(ss,x,','))a.push_back(x);r.push_back(a);}return r;}
void plot(){gROOT->SetBatch();gStyle->SetOptStat(0);gStyle->SetHistLineWidth(3);gStyle->SetLineWidth(3);gStyle->SetFrameLineWidth(3);TCanvas c("c","",800,600);c.SetLeftMargin(.14);c.SetBottomMargin(.14);c.SetTopMargin(.13);c.SetGrid();TFile root("histograms.root","RECREATE");std::ofstream audit("histogram-audit.csv");audit<<"run,plot,bins,entries,underflow,overflow\n";
 for(int run:{400,668}){std::map<std::string,std::unique_ptr<TH1D>>h;auto rows=csv("data/run"+std::to_string(run)+"-hist.csv");for(auto&a:rows){std::string name=a[0];int b=std::stoi(a[1]);double lo=std::stod(a[2]),hi=std::stod(a[3]);if(!h.count(name)){double width=hi-lo,xlo=lo-(b-1)*width;bool tot=name.find("tot")!=std::string::npos;double unit=tot?1024.:1.;h[name]=std::make_unique<TH1D>((std::to_string(run)+name).c_str(),"",200,xlo/unit,(xlo+200*width)/unit);h[name]->SetDirectory(nullptr);}h[name]->SetBinContent(b,std::stod(a[4]));}
 for(auto&kv:h){auto&x=*kv.second;double n=x.Integral(0,201);x.SetEntries(n);audit<<run<<','<<kv.first<<",200,"<<n<<','<<x.GetBinContent(0)<<','<<x.GetBinContent(201)<<'\n';x.Write();}
 for(int seg=1;seg<=6;++seg)for(int mode=0;mode<4;++mode){std::string p="seg"+std::to_string(seg),stem="run"+std::to_string(run)+"-"+p+(mode==0?"-time":mode==1?"-lr":mode==2?"-tot":"-tot-tight");std::vector<std::string>names;std::vector<const char*>labels;
 if(mode==0){names={p+"_L_time",p+"_R_time"};labels={"Left","Right"};}else if(mode==1){names={p+"_lr",p+"_tight_lr"};labels={"Prompt [-72,168) ns","Peak [20,80) ns"};}else{std::string k=p+(mode==3?"_tight":"");names={k+"_L_tot_only",k+"_L_tot_both",k+"_R_tot_only",k+"_R_tot_both"};labels={"L: L-only anchor","L: both-side anchor","R: R-only anchor","R: both-side anchor"};}
 c.Clear();c.SetGrid();c.SetLogx(0);c.SetLogy(0);c.SetLogz(0);int cols[]={kBlue+1,kRed+1,kGreen+2,kMagenta+1};std::vector<std::unique_ptr<TH1D>>v;double ymax=0;for(int i=0;i<(int)names.size();++i){v.emplace_back((TH1D*)h.at(names[i])->Clone());auto&x=*v.back();x.SetDirectory(nullptr);x.SetLineColor(cols[i]);x.SetLineStyle(i>=2?2:1);x.SetLineWidth(3);if(mode>=2&&x.Integral(0,201)>0)x.Scale(1./x.Integral(0,201));ymax=std::max(ymax,x.GetMaximum());}
 v[0]->SetTitle(mode==0?";LTOF side - UTOF LR mean [ns];Hit-anchor combinations":mode==1?";LTOF L - R [ns];All LR-pair-anchor combinations":";Decoded TOT [ns];Fraction per 4 ns bin");v[0]->SetMaximum(ymax*1.2);v[0]->Draw("hist");for(int i=1;i<(int)v.size();++i)v[i]->Draw("hist same");TLegend leg(.56,mode>=2?.64:.73,.89,.87);leg.SetTextSize(.026);for(int i=0;i<(int)v.size();++i)leg.AddEntry(v[i].get(),labels[i],"l");leg.Draw();TLatex t;t.SetNDC();t.SetTextSize(.031);t.DrawLatex(.14,.94,("run"+std::to_string(run)+" / LTOF segment "+std::to_string(seg)+" / raw merged data").c_str());save_figure_pdf(c,(stem+".pdf").c_str());}
 auto a=csv("data/run"+std::to_string(run)+"-trigger-tf.csv");double dt=.002097152;std::array<std::vector<double>,3>bin;for(auto&b:bin)b.resize(420);std::array<TGraph,3>g;double max=0;for(auto&r:a){int i=std::stoi(r[0])-1,b=int((i*dt+dt/2)/.1);for(int j=0;j<3;++j)bin[j][b]+=std::stod(r[j+2]);}int col[]={kBlue+1,kGreen+2,kRed+1};for(int j=0;j<3;++j){for(int b=0;b<420;++b){double duration=b==419?.04304:.1;double y=bin[j][b]/duration/1000.;g[j].SetPoint(b,b*.1+duration/2,y);max=std::max(max,y);}g[j].SetLineColor(col[j]);g[j].SetLineWidth(3);g[j].Write(("run"+std::to_string(run)+"-trigger-"+std::to_string(j)).c_str());}c.Clear();c.SetGrid();g[2].SetTitle(";Acquisition time [s];Trigger rate [kHz]");g[2].SetMinimum(0);g[2].SetMaximum(max*1.15);g[2].Draw("AL");g[0].Draw("L same");g[1].Draw("L same");TLegend leg(.51,.72,.89,.88);leg.SetTextSize(.026);leg.AddEntry(&g[0],"marq04 adjacent-channel AND","l");leg.AddEntry(&g[1],"Physical same-segment LR AND","l");leg.AddEntry(&g[2],"Individual-readout Flat OR","l");leg.Draw();save_figure_pdf(c,("run"+std::to_string(run)+"-trigger-time.pdf").c_str());
 }root.Close();}
