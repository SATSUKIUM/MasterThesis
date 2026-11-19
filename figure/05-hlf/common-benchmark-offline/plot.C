#include "../../pdf_output.hxx"
#include <TFile.h>
#include <TH1D.h>
#include <TH2.h>
#include <TStyle.h>
#include <TLegend.h>
#include <TBox.h>
#include <TGraphErrors.h>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
void plot(){
 gROOT->SetBatch();gStyle->SetOptStat(0);gStyle->SetLineWidth(3);gStyle->SetHistLineWidth(3);gStyle->SetTitleFontSize(.042);TFile f("hist.root");TCanvas c("c","",800,600);c.SetGrid();
 auto save=[&](std::string n){save_figure_pdf(c,(n+".pdf").c_str());};
 auto overlay=[&](std::string prefix,std::string name,double lo=0,double hi=0){c.Clear();c.SetGrid();c.SetLeftMargin(.13);c.SetRightMargin(.05);auto*a=f.Get<TH1>((prefix+"before").c_str());auto*b=f.Get<TH1>((prefix+"track").c_str());a->SetLineColor(kBlack);b->SetLineColor(kBlue+2);a->SetLineWidth(3);b->SetLineWidth(3);if(hi>lo)a->GetXaxis()->SetRangeUser(lo,hi);a->SetMinimum(0);a->SetMaximum(1.15*std::max(a->GetMaximum(),b->GetMaximum()));a->Draw("hist");b->Draw("hist same");TLegend l(.58,.77,.93,.90);l.AddEntry(a,"Before Track HLF","l");l.AddEntry(b,"After Track HLF","l");l.Draw();save(name);};
 for(std::string selection:{"tof","wide"}){c.Clear();c.SetGrid();auto*a=f.Get<TH1>("tof_before");auto*b=f.Get<TH1>(("tof_"+selection).c_str());a->SetLineColor(kBlack);b->SetLineColor(kBlue+2);a->SetMinimum(0);a->SetMaximum(1.1*a->GetMaximum());a->Draw("hist");double lo=selection=="tof"?124.5:122.,hi=selection=="tof"?128.5:129.;TBox box(lo,0,hi,a->GetMaximum());box.SetFillColorAlpha(kOrange,.20);box.Draw();a->Draw("hist same");b->Draw("hist same");TLegend l(.56,.76,.94,.91);l.AddEntry(a,"Before TOF HLF","l");l.AddEntry(b,"After TOF HLF (whole slices)","l");l.AddEntry(&box,Form("%.1f < TOF < %.1f ns",lo,hi),"f");l.Draw();save("tof-"+selection);}
 overlay("layers_","kldc-layers",5.5,8.5);overlay("chi_","kldc-reduced-chi2");overlay("chi_raw_","kldc-chi2");overlay("nt_","kldc-multiplicity",-.5,19.5);
 for(int l=1;l<=8;++l)overlay("res"+std::to_string(l)+"_","kldc-residual-l"+std::to_string(l));
 for(std::string n:{"before","track"})for(std::string p:{"xy_","xy6_","xy7_","xy8_","bft_"}){c.Clear();c.SetGrid();c.SetLeftMargin(.15);c.SetRightMargin(.19);c.SetBottomMargin(.12);c.SetTopMargin(.11);auto*h=f.Get<TH2>((p+n).c_str());if(!h)throw std::runtime_error(p+n);h->Draw("colz");c.SetFixedAspectRatio();c.Update(); // Square plotting frame: equal x/y ranges and square pad interior.
 c.SetCanvasSize(800,800);c.SetLeftMargin(.14);c.SetRightMargin(.20);c.SetBottomMargin(.14);c.SetTopMargin(.20);c.Modified();c.Update();save(p+n);c.SetFixedAspectRatio(false);c.SetCanvasSize(800,600);}
 // Every cluster-count histogram has 200 bins; unpopulated fractional bins retain integer values.
 std::vector<TH1D*> clusters;for(int l=1;l<=8;++l)clusters.push_back(new TH1D(Form("cluster%d",l),Form("KLDC layer %d;Clusters per slice;Slices",l),200,-.5,49.5));TH1D qualifying("qualifying",";Layers with >= 2 clusters;Slices",200,-.5,8.5);std::ifstream in("clusters.csv");std::string line;getline(in,line);while(getline(in,line)){for(char&ch:line)if(ch==',')ch=' ';std::istringstream s(line);long id;s>>id;int n,q=0;for(auto*h:clusters){s>>n;h->Fill(n);q+=n>=2;}qualifying.Fill(q);}
 for(int l=1;l<=8;++l){c.Clear();c.SetGrid();c.SetLeftMargin(.13);c.SetRightMargin(.05);c.SetBottomMargin(.12);c.SetTopMargin(.09);clusters[l-1]->SetLineWidth(3);clusters[l-1]->SetMinimum(0);clusters[l-1]->Draw("hist");save("clusters-l"+std::to_string(l));}
 c.Clear();c.SetGrid();qualifying.SetLineWidth(3);qualifying.SetMinimum(0);qualifying.Draw("hist");save("multiplicity-qualifying-layers");
 std::ifstream ef("efficiency-summary.csv");getline(ef,line);TGraphErrors gr;int i=0;while(getline(ef,line)){for(char&ch:line)if(ch==',')ch=' ';std::istringstream s(line);double layer,d,n,p,se;s>>layer>>d>>n>>p>>se;gr.SetPoint(i,layer,100*p);gr.SetPointError(i,0,100*se);++i;}c.Clear();c.SetGrid();gr.SetTitle("Conditional BFT-to-KLDC hit matching (not intrinsic efficiency);KLDC layer;Matched / reference tracks [%]");gr.SetMarkerStyle(20);gr.SetLineWidth(3);gr.SetMinimum(0);gr.SetMaximum(100);gr.Draw("AP");save("bft-kldc-conditional-matching");

 std::ifstream sf("selection-summary.csv");getline(sf,line);TGraph reduction,retention;int point=0;double beforeBytes=662535240.,beforeTracks=235093.;while(getline(sf,line)){for(char&ch:line)if(ch==',')ch=' ';std::istringstream s(line);std::string name;double ns,bytes,events,tracks,te,bft;s>>name>>ns>>bytes>>events>>tracks>>te>>bft;if(name.find("multiplicity_N")==0){int n=std::stoi(name.substr(14));reduction.SetPoint(point,n,beforeBytes/bytes);retention.SetPoint(point,n,100*tracks/beforeTracks);++point;}}
 for(int q=0;q<2;++q){auto*g=q?&retention:&reduction;c.Clear();c.SetGrid();g->SetTitle(q?"Common calibrated event population;Required layers with >=2 clusters;KLDC track retention [%]":"SliceData bytes only;Required layers with >=2 clusters;Before / after bytes");g->SetMarkerStyle(20);g->SetLineWidth(3);g->SetMinimum(0);g->Draw("APL");save(q?"multiplicity-track-retention":"multiplicity-reduction");}
 TFile counts("cluster-histograms.root","RECREATE");for(auto*h:clusters)h->Write();qualifying.Write();counts.Close();
}
