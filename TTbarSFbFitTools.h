#ifndef _TTbarSFbFitTools_h_
#define _TTbarSFbFitTools_h_

#include <vector>
#include <map>

#include "TH1F.h"
#include "TObjArray.h"
#include "TString.h"

struct TTbarFracFitterResult_t
{
  float eff,effUnc,sf,sfUnc,effExp,effExpUnc;
  int minuitStatus;
};

typedef std::map<int,std::string> int_char_map;

class TTbarFracFitter
{
 public:
  TTbarFracFitter();
  TTbarFracFitterResult_t fit(TObjArray &fracTempl, TH1F *data, Int_t idxOfInterest=0, TString saveResultIn="");
  TTbarFracFitterResult_t fit(TObjArray &passTemplates, TH1F *passDataH,
                              TObjArray &failTemplates, TH1F *failDataH,
                              TString tagger="",
                              Int_t idxOfInterest=0,
                              Int_t workingPoint=0,
                              Int_t jetptRange=0,
                              Int_t NomSysupSysdown=0,
                              TString saveResultIn="",
                              Float_t lumi=41.8);
  ~TTbarFracFitter();

};

#endif
