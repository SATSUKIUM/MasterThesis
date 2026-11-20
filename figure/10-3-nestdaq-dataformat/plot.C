#include "pdf_output.hxx"
#include <TBox.h>
#include <TText.h>
#include <TStyle.h>
#include <TArrow.h>
#include <vector>
#include <string>
struct Field { const char* name; int start; int size; };
void text(double x,double y,const char* s,double size=.028,int align=12){auto t=new TText(x,y,s);t->SetTextFont(132);t->SetTextSize(size);t->SetTextAlign(align);t->Draw();}
void layout(const char* id,const char* title,std::vector<Field> fields,int total,bool bits=false){
 TCanvas c(id,title,800,600);c.Range(0,0,1,1);text(.06,.95,title,.036);
 text(.06,.89,bits?"Bit index (MSB on left)":"Byte offset from record start",.027);
 const int rowwidth=bits?64:16;int rows=(total+rowwidth-1)/rowwidth;
 double dy=rows>9?.72/rows:.072; double top=.83;
 int colors[]={TColor::GetColor("#DCE5F1"),TColor::GetColor("#F3E9CE"),TColor::GetColor("#DAE8DC"),TColor::GetColor("#E9DDE8")};
 for(int r=0;r<rows;r++){
  for(unsigned i=0;i<fields.size();i++){
   auto f=fields[i];int begin=std::max(f.start,r*rowwidth),end=std::min(f.start+f.size,(r+1)*rowwidth);if(begin>=end)continue;
   double x1=.08+.84*(begin-r*rowwidth)/rowwidth,x2=.08+.84*(end-r*rowwidth)/rowwidth;
   double y=top-r*dy;auto b=new TBox(x1,y-dy*.75,x2,y);b->SetFillColor(colors[i%4]);b->SetLineWidth(3);b->Draw();
   double font=std::min(.026,(x2-x1)*1.5/std::max(1,int(std::string(f.name).size())));
   if(bits && f.size<4){text((x1+x2)/2,y-dy*.38,"R",.022,22);}else text((x1+x2)/2,y-dy*.38,f.name,std::max(.016,font),22);
   text(x1,y+.009,std::to_string(bits?63-begin:begin).c_str(),.019,11);
  }
 }
 if(bits)text(.06,.17,"R: reserved; each word is 64 bits (8 bytes)",.026);
 else text(.06,.06,(std::string("Drawn span: ")+std::to_string(total)+" bytes; field widths are defined in data/headers-v1.json").c_str(),.023);
 save_figure_pdf(c,(std::string("pdf/")+id+".pdf").c_str());
}
void plot(){gROOT->SetBatch(kTRUE);gStyle->SetLineWidth(3);
layout("tf","TimeFrame::v1::Header (24 bytes)",{{"magic",0,8},{"length",8,4},{"hLength",12,2},{"type",14,2},{"timeFrameId",16,4},{"numSource",20,4}},24);
layout("stf","SubTimeFrame::v1::Header (48 bytes)",{{"magic",0,8},{"length",8,4},{"hLength",12,2},{"type",14,2},{"timeFrameId",16,4},{"femType",20,4},{"femId",24,4},{"numMessages",28,4},{"timeSec",32,8},{"timeUSec",40,8}},48);
layout("hbf","HeartbeatFrame::Header (16 bytes)",{{"magic",0,8},{"length",8,4},{"hLength",12,2},{"type",14,2}},16);
layout("filter","Filter::v1::Header (56 bytes)",{{"magic",0,8},{"length",8,4},{"hLength",12,2},{"type",14,2},{"timeFrameId",16,4},{"numTrigs",20,4},{"workerId",24,4},{"numMessages",28,4},{"elapseTime",32,4},{"reserve",36,4},{"timeSec",40,8},{"timeUSec",48,8}},56);
layout("trigger","Filter::v1::TrgTimeHeader (16 bytes)",{{"magic",0,8},{"length",8,4},{"hLength",12,2},{"type",14,2}},16);
layout("file-header","FileSinkHeader::v1::Header (304 bytes)",{{"magic",0,8},{"length",8,4},{"hLength",12,2},{"type",14,2},{"fairMQDeviceType",16,8},{"runNumber",24,8},{"startUnixtime",32,8},{"stopUnixtime",40,8},{"comments[256] (bytes 48-303)",48,16}},64);
layout("file-trailer","FileSinkTrailer::v1::Trailer (304 bytes)",{{"magic",0,8},{"length",8,4},{"hLength",12,2},{"type",14,2},{"fairMQDeviceType",16,8},{"runNumber",24,8},{"startUnixtime",32,8},{"stopUnixtime",40,8},{"comments[256] (bytes 48-303)",48,16}},64);
layout("trgtime","Filter::v1::TrgTime (8 bytes)",{{"time",0,4},{"type",4,4}},8);
layout("hr-v3","TDC64H_V3 / hit",{{"type",0,6},{"ch",6,7},{"TOT",13,22},{"TDC",35,29}},64,true);
layout("lr-v3","TDC64L_V3 / hit",{{"type",0,6},{"ch",6,8},{"TOT",14,16},{"TDC",30,19},{"zero / reserved",49,15}},64,true);
layout("hbd1","Heartbeat Delimiter / 1st word",{{"type=0x1c",0,6},{"reserved",6,2},{"flag",8,16},{"time offset",24,16},{"HB frame ID",40,24}},64,true);
layout("hbd2","Heartbeat Delimiter / 2nd word",{{"type=0x1e",0,6},{"reserved",6,2},{"userReg",8,16},{"generated size",24,20},{"transferred size",44,20}},64,true);

 {TCanvas c("pipeline","Processing and serialization",800,600);c.Range(0,0,1,1);
 text(.06,.96,"NestDAQ processing and serialized records",.036);
 const char* names[]={"FEE / Sampler","STFBuilder / TFBuilder","LogicFilter","Slicer (per HBF j)","High-level filter / FileSink"};
 const char* a[]={"64-bit hit words + HBD pairs","TFH + [STFH + (HBFH + words + HBDs) x H] x S","TFH + FilterH + [TriggerH + trigger times] x H + STFs","META_j + SLICE_j,1 + ... + SLICE_j,n(j)","META_j + accepted SLICEs; run header / trailer at sink"};
 for(int i=0;i<5;i++){double y=.87-i*.16;auto b=new TBox(.05,y-.105,.95,y);b->SetFillColor(TColor::GetColor("#E5EBF3"));b->SetLineWidth(3);b->Draw();text(.075,y-.032,names[i],.028);text(.075,y-.078,a[i],.023);if(i<4){auto ar=new TArrow(.5,y-.112,.5,y-.15,.018,"|>");ar->SetLineWidth(3);ar->Draw();}}
 text(.06,.025,"H: HBFs per source; S: sources; n(j): triggers in HBF j",.024);
 save_figure_pdf(c,"pdf/pipeline.pdf");}
}
