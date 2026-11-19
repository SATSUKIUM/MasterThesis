#include "../../pdf_output.hxx"
#include <TCanvas.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TLegend.h>
#include <TLatex.h>
#include <TStyle.h>
#include <TROOT.h>
#include <TSystem.h>
#include <array>
#include <vector>
#include <string>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <memory>
#include <cmath>
#include <cstdio>
#include <stdexcept>
struct RBSample {unsigned long long message,tf,bytes;double us;int keep;};
struct RBCase {std::string key,label,cond,slice;};
std::vector<std::string> rb_split(std::string s){std::vector<std::string> a;std::stringstream f(s);std::string x;while(std::getline(f,x,','))a.push_back(x);return a;}
double rb_q(std::vector<double> v,double q){std::sort(v.begin(),v.end());double x=(v.size()-1)*q;size_t i=x;return v[i]+(v[std::min(i+1,v.size()-1)]-v[i])*(x-i);}
void plot(){
 gROOT->SetBatch(kTRUE);gStyle->SetOptStat(0);gStyle->SetLineWidth(3);gStyle->SetHistLineWidth(3);gStyle->SetFrameLineWidth(3);gStyle->SetPaperSize(20,15);gStyle->SetPalette(kViridis);
 std::vector<RBCase> cases;std::ifstream cf("data/cases.csv");std::string line;std::getline(cf,line);while(std::getline(cf,line)){auto a=rb_split(line);if(a.size()!=4)throw std::runtime_error("case row");cases.push_back({a[0],a[1],a[2],a[3]});}if(cases.size()!=5)throw std::runtime_error("five environments expected");
 std::vector<unsigned long long> tfid(20001),nslice(20001);std::ifstream mf("data/messages.csv");std::getline(mf,line);unsigned long long m,t,n;int nm=0;while(std::getline(mf,line)){std::replace(line.begin(),line.end(),',',' ');std::istringstream s(line);if(!(s>>m>>t>>n)||m<1||m>20000)throw std::runtime_error("message ledger");tfid[m]=t;nslice[m]=n;++nm;}if(nm!=20000)throw std::runtime_error("ledger count");
 std::array<std::array<std::vector<RBSample>,2>,5> rows;
 for(int k=0;k<5;++k)for(int mode=0;mode<2;++mode){auto path=std::string("data/")+(mode?cases[k].slice:cases[k].cond);FILE* pipe=gSystem->OpenPipe(("gzip -dc \""+path+"\"").c_str(),"r");if(!pipe)throw std::runtime_error("gzip input");char buf[512];if(!fgets(buf,sizeof(buf),pipe))throw std::runtime_error("CSV header");while(fgets(buf,sizeof(buf),pipe)){RBSample x;if(sscanf(buf,"%llu,%llu,%llu,%lf,%d",&x.message,&x.tf,&x.bytes,&x.us,&x.keep)!=5)throw std::runtime_error("CSV sample");if(x.message<1||x.message>20000||x.tf!=tfid[x.message]||!(x.us>0))throw std::runtime_error("sample identity/time");if(mode&&nslice[x.message]==0)throw std::runtime_error("slice without coincidence");rows[k][mode].push_back(x);}if(gSystem->ClosePipe(pipe)!=0)throw std::runtime_error("gzip failed");if(rows[k][mode].size()!=size_t(mode?152880:20000))throw std::runtime_error("sample count");}
 std::ofstream audit("histogram-audit.csv");audit<<"file,environment,metric,mode,group,range,bins_x,bins_y,xmin,xmax,ymin,ymax,entries,underflow,overflow,logx,logy,gridx,gridy\n";audit<<std::setprecision(17);
 std::ofstream catalog("figures.csv");catalog<<"file,mode,group,metric,range,environment\n";
 std::string kind=gSystem->BaseName(gSystem->WorkingDirectory());
 TCanvas c("benchmark_root","",800,600);c.SetCanvasSize(800,600);
 auto setup=[&](bool two){c.Clear();c.cd();c.SetCanvasSize(800,600);c.SetLogx(0);c.SetLogy(0);c.SetLogz(0);c.SetGrid(1,1);c.SetLeftMargin(.15);c.SetBottomMargin(.14);c.SetTopMargin(.12);c.SetRightMargin(two?.15:.04);};
 auto title=[&](const std::string& text){TLatex a;a.SetNDC();a.SetTextSize(.032);a.DrawLatex(.15,.94,text.c_str());};
 auto selected=[&](const RBSample& r,int group){return group==0||(nslice[r.message]>0)==(group==1);};
 const char* modes[]={"cond","slice"};const char* groups[]={"all","has_slice","no_slice"};const char* modeLabel[]={"ConditionalRun (no communication)","ProcessSlice"};const char* groupLabel[]={"all messages","#geq1 slice per message","no slice per message"};int colors[]={kGray+2,kRed+1,kBlue+1,kGreen+2,kViolet+1};
 unsigned uid=0;
 for(int mode=0;mode<2;++mode)for(int group=0;group<3;++group){
  if(mode&&group!=1)continue; // all ProcessSlice calls belong to has_slice; no synthetic empty calls.
  std::array<std::vector<RBSample>,5> subset;std::vector<double> poolTime,poolRate;double maxSize=0,maxTime=0;
  for(int k=0;k<5;++k)for(const auto& r:rows[k][mode])if(selected(r,group)){subset[k].push_back(r);poolTime.push_back(r.us);poolRate.push_back(double(r.bytes)/r.us);maxTime=std::max(maxTime,r.us);maxSize=std::max(maxSize,double(r.bytes)/1000.);}
  if(poolTime.empty())throw std::runtime_error("empty scope");
  auto stem=std::string(modes[mode])+"-"+groups[group];auto caption=kind+" / "+modeLabel[mode]+" / "+groupLabel[group];
  for(int metric=0;metric<2;++metric)for(int zoom=0;zoom<2;++zoom){
   auto& pool=metric?poolRate:poolTime;double top=(zoom?rb_q(pool,.995):*std::max_element(pool.begin(),pool.end()))*(zoom?1.0000001:1.01);if(!(top>0))throw std::runtime_error("axis bound");
   setup(false);std::vector<std::unique_ptr<TH1D>> hs;double ymax=0;std::string outside;
   for(int k=0;k<5;++k){auto h=std::make_unique<TH1D>(("rb"+std::to_string(uid++)).c_str(),metric?";Input throughput [MB/s];Calls / bin":";Processing time [#mus];Calls / bin",200,0,top);h->SetDirectory(nullptr);h->SetStats(false);h->SetLineWidth(3);h->SetLineColor(colors[k]);h->SetLineStyle(k+1);h->GetYaxis()->SetTitleOffset(1.55);for(const auto& r:subset[k])h->Fill(metric?double(r.bytes)/r.us:r.us);ymax=std::max(ymax,h->GetMaximum());if(k)outside+=", ";outside+=std::to_string(int(h->GetBinContent(201)));hs.push_back(std::move(h));}
   for(int k=0;k<5;++k){hs[k]->SetMaximum(ymax*1.25);hs[k]->SetMinimum(0);hs[k]->Draw(k?"HIST SAME":"HIST");}TLegend legend(.60,.62,.95,.86);legend.SetBorderSize(0);legend.SetFillStyle(0);legend.SetTextSize(.030);for(int k=0;k<5;++k)legend.AddEntry(hs[k].get(),cases[k].label.c_str(),"l");legend.Draw();title(caption);
   if(zoom){TLatex a;a.SetNDC();a.SetTextSize(.024);a.DrawLatex(.17,.86,"Display: pooled 99.5% quantile; statistics use all calls");a.DrawLatex(.17,.82,("Overflow: "+outside+" (legend order)").c_str());}
   std::string file=stem+"-"+(metric?"throughput":"time")+"-"+(zoom?"zoom":"full")+".pdf";save_figure_pdf(c,file.c_str());catalog<<file<<','<<modes[mode]<<','<<groups[group]<<','<<(metric?"throughput":"time")<<','<<(zoom?"zoom":"full")<<",all\n";
   for(int k=0;k<5;++k){auto& h=*hs[k];if(!zoom&&(h.GetBinContent(0)||h.GetBinContent(201)))throw std::runtime_error("full-range overflow");if(c.GetLogx()||c.GetLogy()||!c.GetGridx()||!c.GetGridy()||h.GetNbinsX()!=200)throw std::runtime_error("plot settings");audit<<file<<','<<cases[k].key<<','<<(metric?"throughput":"time")<<','<<modes[mode]<<','<<groups[group]<<','<<(zoom?"zoom":"full")<<",200,0,0,"<<top<<",0,"<<ymax*1.25<<','<<h.GetEntries()<<','<<h.GetBinContent(0)<<','<<h.GetBinContent(201)<<",0,0,1,1\n";}
  }
  for(int k=0;k<5;++k){setup(true);TH2D h(("rb2"+std::to_string(uid++)).c_str(),";Input size [kB];Processing time [#mus]",200,0,maxSize*1.01,200,0,maxTime*1.01);h.SetDirectory(nullptr);h.SetStats(false);h.SetLineWidth(3);h.GetYaxis()->SetTitleOffset(1.55);for(const auto& r:subset[k])h.Fill(double(r.bytes)/1000.,r.us);h.Draw("COLZ");title(caption+" / "+cases[k].label);std::string file=stem+"-size-time-"+cases[k].key+".pdf";save_figure_pdf(c,file.c_str());catalog<<file<<','<<modes[mode]<<','<<groups[group]<<",size-time,full,"<<cases[k].key<<'\n';if(c.GetLogx()||c.GetLogy()||h.GetNbinsX()!=200||h.GetNbinsY()!=200||!c.GetGridx()||!c.GetGridy())throw std::runtime_error("2D settings");audit<<file<<','<<cases[k].key<<",size-time,"<<modes[mode]<<','<<groups[group]<<",full,200,200,0,"<<maxSize*1.01<<",0,"<<maxTime*1.01<<','<<h.GetEntries()<<",0,0,0,0,1,1\n";}
 }
 audit.close();catalog.close();if(!audit||!catalog)throw std::runtime_error("audit output");
}
