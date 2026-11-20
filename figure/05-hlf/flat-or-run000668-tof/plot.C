#include "../../pdf_output.hxx"
#include <TFile.h>
#include <TH2D.h>
#include <TStyle.h>
#include <TSystem.h>
#include <TLatex.h>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <array>
#include <cstdio>
#include <stdexcept>
struct Sample{unsigned long long m,tf,b;double us;int keep;};
void plot(){gROOT->SetBatch();gStyle->SetOptStat(0);gStyle->SetHistLineWidth(3);gStyle->SetLineWidth(3);gStyle->SetFrameLineWidth(3);std::vector<int> ns(20001);std::vector<unsigned long long> ids(20001);std::ifstream ledger("data/messages.csv");std::string line;getline(ledger,line);while(getline(ledger,line)){for(char&c:line)if(c==',')c=' ';std::istringstream s(line);int m;s>>m>>ids[m]>>ns[m];}const char*hosts[]={"e50server03","marq04","marq06","marq07"};std::array<std::array<std::vector<Sample>,2>,4> rows;double maxB[2]={},maxUs[2]={};
 for(int h=0;h<4;++h)for(int mode=0;mode<2;++mode){auto path=std::string("gzip -dc data/")+hosts[h]+(mode?"-slice.csv.gz":"-cond.csv.gz");FILE*f=gSystem->OpenPipe(path.c_str(),"r");char buf[512];fgets(buf,512,f);while(fgets(buf,512,f)){Sample a;if(sscanf(buf,"%llu,%llu,%llu,%lf,%d",&a.m,&a.tf,&a.b,&a.us,&a.keep)!=5||a.m<1||a.m>20000||a.tf!=ids[a.m]||a.us<=0)throw std::runtime_error("sample");rows[h][mode].push_back(a);maxB[mode]=std::max(maxB[mode],a.b*.001);maxUs[mode]=std::max(maxUs[mode],a.us);}if(gSystem->ClosePipe(f))throw std::runtime_error("gzip");}
 std::string folder=gSystem->BaseName(gSystem->WorkingDirectory());std::string filter=folder.substr(folder.rfind('-')+1);TCanvas c("c","",800,600);c.SetLeftMargin(.15);c.SetRightMargin(.16);c.SetBottomMargin(.14);c.SetTopMargin(.12);c.SetGrid();c.SetLogx(0);c.SetLogy(0);c.SetLogz(0);TFile out("histograms.root","RECREATE");std::ofstream audit("histogram-audit.csv");audit<<"file,entries,bins_x,bins_y,underflow,overflow\n";
 for(int h=0;h<4;++h)for(int mode=0;mode<2;++mode)for(int group=0;group<3;++group){if(mode&&group!=1)continue;std::string name=std::string(mode?"slice":"cond")+"-"+(group==0?"all":group==1?"has_slice":"no_slice")+"-size-time-"+hosts[h];double boundB=0,boundUs=0;for(int hh=0;hh<4;++hh)for(auto a:rows[hh][mode]){if(group&&bool(ns[a.m])!=(group==1))continue;boundB=std::max(boundB,a.b*.001);boundUs=std::max(boundUs,a.us);}TH2D hist(name.c_str(),";Input size [kB];Processing time [#mus]",200,0,boundB*1.01,200,0,boundUs*1.01);hist.SetDirectory(nullptr);int n=0;for(auto a:rows[h][mode]){if(group&&bool(ns[a.m])!=(group==1))continue;hist.Fill(a.b*.001,a.us);++n;}c.Clear();c.SetGrid();c.SetLogx(0);c.SetLogy(0);c.SetLogz(0);hist.Draw("colz");TLatex t;t.SetNDC();t.SetTextSize(.031);t.DrawLatex(.15,.94,(std::string("run000668 / ")+filter+" / "+hosts[h]+" / "+(mode?"ProcessSlice":"ConditionalRun")+" / "+(group==0?"all":group==1?"slice present":"no slice")).c_str());save_figure_pdf(c,(name+".pdf").c_str());hist.Write();double under=0,over=0;for(int ix=0;ix<=201;++ix)for(int iy=0;iy<=201;++iy){double bc=hist.GetBinContent(ix,iy);if(ix==0||iy==0)under+=bc;else if(ix==201||iy==201)over+=bc;}if(under||over||hist.GetEntries()!=n||c.GetLogx()||c.GetLogy()||c.GetLogz()||!c.GetGridx()||!c.GetGridy())throw std::runtime_error("plot properties or full-range entries");audit<<name<<".pdf,"<<n<<",200,200,"<<under<<","<<over<<"\n";}out.Close();}
