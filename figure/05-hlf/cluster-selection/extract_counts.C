#include <TFile.h>
#include <TTree.h>
#include <fstream>
#include <stdexcept>
void extract_counts(const char* source="/Users/kashima/scp_landing_zone/20260314/data") {
  std::ofstream out("data/counts.csv");
  out << "min_layers,run,all_events,tracks_lt2,tracks_ge2\n";
  const int runs[]={611,610,609};
  for(int n=0;n<3;++n){
    TFile f(TString::Format("%s/run%06d_KLDCtrack.root",source,runs[n]),"READ");
    auto t=f.Get<TTree>("tree");if(f.IsZombie()||!t)throw std::runtime_error("missing tree");
    auto total=t->GetEntries();auto selected=t->GetEntries("nt>=2");
    const long long expectedTotal[]={387974,295491,168213},expectedSelected[]={21659,20308,18118};
    if(total!=expectedTotal[n]||selected!=expectedSelected[n])throw std::runtime_error("counts differ from published sample");
    out<<n<<","<<runs[n]<<","<<total<<","<<total-selected<<","<<selected<<"\n";
  }
}
