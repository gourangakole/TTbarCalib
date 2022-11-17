#include "TTbarSFbFitTools.h"
#include <iostream>
#include <map>
#include <string>
#include "TMath.h"
#include "TCanvas.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TLine.h"
#include "RooHist.h"
#include "RooRealVar.h"
#include "RooDataHist.h"
#include "RooHistPdf.h"
#include "RooAddPdf.h"
#include "RooCategory.h"
#include "RooSimultaneous.h"
#include "RooPlot.h"
#include "RooMinuit.h"
#include "RooFitResult.h"
#include "RooWorkspace.h"


using namespace std;
int_char_map workingPoint_labels;
int_char_map jetptRange_labels;

//
TTbarFracFitter::TTbarFracFitter()
{
  using namespace RooFit;

  RooMsgService::instance().setSilentMode(true);
  RooMsgService::instance().getStream(0).removeTopic(Minimization);
  RooMsgService::instance().getStream(1).removeTopic(Minimization);
  RooMsgService::instance().getStream(1).removeTopic(ObjectHandling);
  RooMsgService::instance().getStream(1).removeTopic(DataHandling);
  RooMsgService::instance().getStream(1).removeTopic(Fitting);
  RooMsgService::instance().getStream(1).removeTopic(Plotting);
  RooMsgService::instance().getStream(0).removeTopic(InputArguments);
  RooMsgService::instance().getStream(1).removeTopic(InputArguments);
  RooMsgService::instance().getStream(0).removeTopic(Eval);
  RooMsgService::instance().getStream(1).removeTopic(Eval);
  RooMsgService::instance().getStream(1).removeTopic(Integration);
  RooMsgService::instance().getStream(1).removeTopic(NumIntegration);
  RooMsgService::instance().getStream(1).removeTopic(NumIntegration);

  workingPoint_labels[1] = "Loose";
  workingPoint_labels[2] = "Medium";
  workingPoint_labels[3] = "Tight";

  jetptRange_labels[0] = "(30 < p_{T} < 50 GeV)";
  jetptRange_labels[1] = "(50 < p_{T} < 70 GeV)";
  jetptRange_labels[2] = "(70 < p_{T} < 100 GeV)";
  jetptRange_labels[3] = "(100 < p_{T} < 140 GeV)";
  jetptRange_labels[4] = "(140 < p_{T} < 200 GeV)";
  jetptRange_labels[5] = "(200 < p_{T} < 300 GeV)";
  jetptRange_labels[6] = "(300 < p_{T} < 600 GeV)";
}

//
TTbarFracFitterResult_t TTbarFracFitter::fit(TObjArray &expTemplates, TH1F *dataH,Int_t idxOfInterest,TString saveResultIn)
{
  using namespace RooFit;

  TTbarFracFitterResult_t result;

  //variable to fit
  RooRealVar x("x",dataH->GetXaxis()->GetTitle(),dataH->GetXaxis()->GetXmin(),dataH->GetXaxis()->GetXmax());
  x.setBins(dataH->GetXaxis()->GetNbins());

  //data
  RooDataHist *data=new RooDataHist("data","data", RooArgSet(x), Import(*dataH) );

  //Total events expected
  Float_t totalExp(0);
  std::vector<Float_t> nExp,nExpUnc;
  for(int i=0; i<expTemplates.GetEntriesFast(); i++)
  {
    TH1 *h=((TH1 *)expTemplates.At(i));
    Double_t unc(0);
    nExp[i]=h->IntegralAndError(1,h->GetNbinsX(),unc);
    nExpUnc[i]=unc;
    totalExp += nExp[i];
  }

  //build the pdf components
  RooArgSet expPDFs,expFracs,nonPOIPDFs;
  TString poiName("v"); poiName+=idxOfInterest;
  for(int i=0; i<expTemplates.GetEntriesFast(); i++)
  {
    TH1 *h=(TH1 *)expTemplates.At(i);
    TString title(h->GetTitle());
    TString name("v"); name+= i;

    if(i<(expTemplates.GetEntriesFast()-1))
    {
      float frac(nExp[i]/totalExp);
      RooRealVar *fracVar = new RooRealVar(name,name,frac,0.5*frac,TMath::Min((float)1.0,(float)2*frac));
      fracVar->SetTitle(title);
      expFracs.add(*fracVar);
    }

    //PDF
    RooDataHist *itempl = new RooDataHist(name+"_hist",name+"_hist", RooArgList(x), Import(*h));
    RooHistPdf *ipdf    = new RooHistPdf (name+"_pdf", name+"_pdf",  RooArgSet(x), *itempl);
    ipdf->SetTitle(title);
    expPDFs.add(*ipdf);
    if(i!=idxOfInterest) nonPOIPDFs.add(*ipdf);
  }


  //create the final pdf
  RooAddPdf *pdf=new RooAddPdf("pdf","pdf", expPDFs, expFracs);

  //fit (using minos has the same behavior of profiling all variables except the parameter of interest)
  RooAbsReal *ll = pdf->createNLL(*data);
  RooMinuit minuit(*ll);
  minuit.setErrorLevel(0.5);
  minuit.migrad();
  minuit.hesse();
  RooArgSet poi(*expFracs.find(poiName));
  result.minuitStatus = minuit.minos(poi);

  //save result
  RooRealVar *fracVar=(RooRealVar *)expFracs.find(poiName);

  result.effExp=nExp[idxOfInterest]/totalExp;
  result.effExpUnc=nExpUnc[idxOfInterest]/totalExp;
  Float_t nObs    = fracVar->getVal()*totalExp;
  Float_t nObsUnc = fracVar->getError()*totalExp;
  result.sf      = nObs/nExp[idxOfInterest];
  result.sfUnc   = TMath::Sqrt(TMath::Power(nObs*nExpUnc[idxOfInterest],2)+TMath::Power(nObsUnc*nExp[idxOfInterest],2))/TMath::Power(nExp[idxOfInterest],2);
  result.eff=result.sf*result.effExp;
  result.effUnc=result.sfUnc*result.effExp;

  //
  if(saveResultIn!="")
  {
    TCanvas *canvas=new TCanvas("c","c",500,500);
    TPad *p1 = new TPad("p1","p1",0.0,0.95,1.0,0.0);
    p1->SetRightMargin(0.05);
    p1->SetLeftMargin(0.12);
    p1->SetTopMargin(0.01);
    p1->SetBottomMargin(0.1);
    p1->Draw();
    p1->cd();
    RooPlot *frame=x.frame();
    data->plotOn(frame,RooFit::Name("data"));
    pdf->plotOn(frame,
      RooFit::Name("totalexp"),
      RooFit::ProjWData(*data),
      RooFit::LineColor(1),
      RooFit::LineWidth(1),
      RooFit::MoveToBack());


      pdf->plotOn(frame,
        RooFit::Name("nonpoifit"),
        RooFit::ProjWData(*data),
        RooFit::Components(nonPOIPDFs),
        RooFit::FillColor(kGray),
        RooFit::LineColor(kGray),
        RooFit::FillStyle(1001),
        RooFit::DrawOption("f"),
        RooFit::MoveToBack());
        frame->Draw();
        frame->GetYaxis()->SetTitleOffset(1.5);
        frame->GetXaxis()->SetTitle(x.GetTitle());
        frame->GetYaxis()->SetRangeUser(0,dataH->GetMaximum()*2.0);

        TLatex *label= new TLatex();
        label->SetNDC();
        label->SetTextFont(42);
        label->SetTextSize(0.04);
        //label->DrawLatex(0.18,0.94,"#bf{CMS} #it{simulation}");

        TLegend *leg=new TLegend(0.18,0.7,0.35,0.9);
        leg->AddEntry("data",      "data",                             "p");
        leg->AddEntry("totalexp",  expFracs.find(poiName)->GetTitle(), "l");
        leg->AddEntry("nonpoifit", "others",                           "f");
        leg->SetFillStyle(0);
        leg->SetTextFont(42);
        leg->SetBorderSize(0);
        leg->SetTextSize(0.035);
        leg->Draw();

        canvas->cd();
        TPad *p2 =new TPad("p2","p2",0.0,0.95,1.0,1.0);
        p2->SetBottomMargin(0.05);
        p2->SetRightMargin(0.05);
        p2->SetLeftMargin(0.12);
        p2->SetTopMargin(0.05);
        p2->Draw();
        p2->cd();
        // The following line needs to be fixed to account for the correlation
        // between data and the fitted prediction. Currently the error to which
        // the residual histogram is normalised to is just the error on the data hist.
        RooHist *hpull = frame->pullHist();
        RooPlot *pullFrame = x.frame();
        //hpull->plotOn(pullFrame);
        pullFrame->addPlotable((RooPlotable *)hpull,"P") ;
        pullFrame->Draw();
        pullFrame->GetYaxis()->SetTitle("Pull");
        pullFrame->GetYaxis()->SetTitleSize(0.2);
        pullFrame->GetYaxis()->SetLabelSize(0.2);
        pullFrame->GetXaxis()->SetTitleSize(0);
        pullFrame->GetXaxis()->SetLabelSize(0);
        pullFrame->GetYaxis()->SetTitleOffset(0.15);
        pullFrame->GetYaxis()->SetNdivisions(4);
        pullFrame->GetYaxis()->SetRangeUser(-3.1,3.1);
        pullFrame->GetXaxis()->SetTitleOffset(0.8);

        canvas->cd();
        TPad *p3 = new TPad("p3","p3",0.7,0.57,0.95,0.82);
        p3->SetRightMargin(0.05);
        p3->SetLeftMargin(0.12);
        p3->SetTopMargin(0.008);
        p3->SetBottomMargin(0.2);
        p3->Draw();
        p3->cd();
        RooPlot *frame2=((RooRealVar *)expFracs.find(poiName))->frame();
        ll->plotOn(frame2,RooFit::ShiftToZero());
        frame2->Draw();
        frame2->GetYaxis()->SetRangeUser(0,12);
        frame2->GetXaxis()->SetRangeUser(165,180);
        frame2->GetYaxis()->SetNdivisions(3);
        frame2->GetXaxis()->SetNdivisions(3);
        frame2->GetXaxis()->SetTitle(expFracs.find(poiName)->GetTitle() + TString(" fraction"));
        frame2->GetYaxis()->SetTitle("LL");
        frame2->GetYaxis()->SetTitleOffset(1.5);
        frame2->GetXaxis()->SetTitleSize(0.08);
        frame2->GetXaxis()->SetLabelSize(0.08);
        frame2->GetYaxis()->SetTitleSize(0.08);
        frame2->GetYaxis()->SetLabelSize(0.08);

        canvas->Modified();
        canvas->Update();
        canvas->SaveAs(saveResultIn+".png");
        canvas->SaveAs(saveResultIn+".pdf");
        canvas->Delete();
      }


      //free memory
      delete ll;

      //all done
      return result;
    }


    //
    TTbarFracFitterResult_t TTbarFracFitter::fit(TObjArray &passTemplates, TH1F *passDataH, TObjArray &failTemplates, TH1F *failDataH, TString tagger, Int_t idxOfInterest, Int_t workingPoint, Int_t jetptRange, Int_t NomSysupSysdown, TString saveResultIn, Float_t lumi){
        using namespace RooFit;

        TTbarFracFitterResult_t result;

        //variable to fit
        RooRealVar x("x",passDataH->GetXaxis()->GetTitle(),passDataH->GetXaxis()->GetXmin(),passDataH->GetXaxis()->GetXmax());
        x.setBins(passDataH->GetXaxis()->GetNbins());

        //categories
        RooCategory status("status","status") ;
        status.defineType("pass") ;
        status.defineType("fail");

        //Fix mass values and create a mapped data hist
        std::map<std::string,TH1 *> dataH;
        dataH["pass"]=passDataH;
        dataH["fail"]=failDataH;
        RooDataHist* data = new RooDataHist("data","data",x,status,dataH);

        //compute the expected efficiency
        std::vector<float> expEff(passTemplates.GetEntriesFast(),0.);
        std::vector<float> expEffUnc(passTemplates.GetEntriesFast(),0.);
        for(int i=0; i<passTemplates.GetEntriesFast(); i++)
        {
          TH1 *passH=(TH1 *)passTemplates.At(i);
          TH1 *failH=(TH1 *)failTemplates.At(i);
          if(passH==0 || failH==0) continue;

          Double_t nPassUnc(0);
          Float_t nPass(passH->IntegralAndError(1,passH->GetNbinsX(),nPassUnc)), nFail(failH->Integral());
          Float_t total(nPass+nFail);
          if(total==0) continue;

          expEff[i]=nPass/total;
          expEffUnc[i]=nPassUnc/total;
        }

        //Take the central value of the bin corresponding to a given pt range, according to the bin step in Templated_btagEffFitter.py
        //(30,50),(50,70),(70,100),(100,140),(140,200),(200,300),(300,600)
        float jetptbins[8] = {30,50,70,100,140,200,300,600};
        float m            = (jetptbins[jetptRange+1]+jetptbins[jetptRange])/2;

        //Mistag rates and uncertainties from negative tag method (contact analyst for .csv files)
        BTagCalibration calib_deepCSV("deepcsv", "data/DeepCSV_2018.out");
        BTagCalibration calib_deepJet("deepjet", "data/DeepFlavour_2018.out");

        BTagCalibrationReader DeepCSV_mistag_reader_loose(BTagEntry::OP_LOOSE,// operating point
                             "central",                               // central sys type
                             {"up", "down"});                         // other sys

        BTagCalibrationReader DeepCSV_mistag_reader_medium(BTagEntry::OP_MEDIUM,"central",{"up", "down"});
        BTagCalibrationReader DeepCSV_mistag_reader_tight(BTagEntry::OP_TIGHT,"central",{"up", "down"});

        BTagCalibrationReader DeepJet_mistag_reader_loose(BTagEntry::OP_LOOSE,"central",{"up", "down"});
        BTagCalibrationReader DeepJet_mistag_reader_medium(BTagEntry::OP_MEDIUM,"central",{"up", "down"});
        BTagCalibrationReader DeepJet_mistag_reader_tight(BTagEntry::OP_TIGHT,"central",{"up", "down"});

        DeepCSV_mistag_reader_loose.load(calib_deepCSV,BTagEntry::FLAV_UDSG,"incl");
        DeepCSV_mistag_reader_medium.load(calib_deepCSV,BTagEntry::FLAV_UDSG,"incl");
        DeepCSV_mistag_reader_tight.load(calib_deepCSV,BTagEntry::FLAV_UDSG,"incl");

        DeepJet_mistag_reader_loose.load(calib_deepJet,BTagEntry::FLAV_UDSG,"incl");
        DeepJet_mistag_reader_medium.load(calib_deepJet,BTagEntry::FLAV_UDSG,"incl");
        DeepJet_mistag_reader_tight.load(calib_deepJet,BTagEntry::FLAV_UDSG,"incl");

        float mistagrate = 1;
        if(tagger=="DeepCSVBDisc"){
          if(workingPoint==1){
            if(NomSysupSysdown==0) mistagrate = DeepCSV_mistag_reader_loose.eval_auto_bounds("central",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==1) mistagrate = DeepCSV_mistag_reader_loose.eval_auto_bounds("up",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==2) mistagrate = DeepCSV_mistag_reader_loose.eval_auto_bounds("down",BTagEntry::FLAV_UDSG,1.0,m);
          }
          if(workingPoint==2){
            if(NomSysupSysdown==0) mistagrate = DeepCSV_mistag_reader_medium.eval_auto_bounds("central",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==1) mistagrate = DeepCSV_mistag_reader_medium.eval_auto_bounds("up",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==2) mistagrate = DeepCSV_mistag_reader_medium.eval_auto_bounds("down",BTagEntry::FLAV_UDSG,1.0,m);
          }
          if(workingPoint==3){
            if(NomSysupSysdown==0) mistagrate = DeepCSV_mistag_reader_tight.eval_auto_bounds("central",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==1) mistagrate = DeepCSV_mistag_reader_tight.eval_auto_bounds("up",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==2) mistagrate = DeepCSV_mistag_reader_tight.eval_auto_bounds("down",BTagEntry::FLAV_UDSG,1.0,m);
          }
        }
        if(tagger=="DeepFlavourBDisc"){
          if(workingPoint==1){
            if(NomSysupSysdown==0) mistagrate = DeepJet_mistag_reader_loose.eval_auto_bounds("central",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==1) mistagrate = DeepJet_mistag_reader_loose.eval_auto_bounds("up",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==2) mistagrate = DeepJet_mistag_reader_loose.eval_auto_bounds("down",BTagEntry::FLAV_UDSG,1.0,m);
          }
          if(workingPoint==2){
            if(NomSysupSysdown==0) mistagrate = DeepJet_mistag_reader_medium.eval_auto_bounds("central",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==1) mistagrate = DeepJet_mistag_reader_medium.eval_auto_bounds("up",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==2) mistagrate = DeepJet_mistag_reader_medium.eval_auto_bounds("down",BTagEntry::FLAV_UDSG,1.0,m);
          }
          if(workingPoint==3){
            if(NomSysupSysdown==0) mistagrate = DeepJet_mistag_reader_tight.eval_auto_bounds("central",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==1) mistagrate = DeepJet_mistag_reader_tight.eval_auto_bounds("up",BTagEntry::FLAV_UDSG,1.0,m);
            if(NomSysupSysdown==2) mistagrate = DeepJet_mistag_reader_tight.eval_auto_bounds("down",BTagEntry::FLAV_UDSG,1.0,m);
          }
        }

        //cout << "Reader: " << tagger << " variation " << NomSysupSysdown << " working point " << workingPoint << " mistagsf = " << mistagrate << endl;

        /*mistagrate = 1;
        if(tagger=="DeepCSVBDisc"){
          if(workingPoint==1){
            if(NomSysupSysdown==0) mistagrate = 1.41852+-0.00040383*m+2.89389e-07*m*m+-3.55101e-11*m*m*m;
            if(NomSysupSysdown==1) mistagrate = (1.41852+-0.00040383*m+2.89389e-07*m*m+-3.55101e-11*m*m*m)*(1-(0.0559259+1.96455e-05*m+-3.60571e-08*m*m));
            if(NomSysupSysdown==2) mistagrate = (1.41852+-0.00040383*m+2.89389e-07*m*m+-3.55101e-11*m*m*m)*(1+(0.0559259+1.96455e-05*m+-3.60571e-08*m*m));
          }
          if(workingPoint==2){
            if(NomSysupSysdown==0) mistagrate = 1.6329+-0.00160255*m+1.9899e-06*m*m+-6.72613e-10*m*m*m;
            if(NomSysupSysdown==1) mistagrate = (1.6329+-0.00160255*m+1.9899e-06*m*m+-6.72613e-10*m*m*m)*(1-(0.122811+0.000162564*m+-1.66422e-07*m*m));
            if(NomSysupSysdown==2) mistagrate = (1.6329+-0.00160255*m+1.9899e-06*m*m+-6.72613e-10*m*m*m)*(1+(0.122811+0.000162564*m+-1.66422e-07*m*m));
          }
          if(workingPoint==3){
            if(NomSysupSysdown==0) mistagrate = 0.870921+5.90958/sqrt(m);
            if(NomSysupSysdown==1) mistagrate = (0.870921+5.90958/sqrt(m))*(1-(0.207667+0.000165081*m+-1.45307e-07*m*m));
            if(NomSysupSysdown==2) mistagrate = (0.870921+5.90958/sqrt(m))*(1+(0.207667+0.000165081*m+-1.45307e-07*m*m));
          }
        }
        if(tagger=="DeepFlavourBDisc"){
          if(workingPoint==1){
            if(NomSysupSysdown==0) mistagrate = 1.61341+-0.000566321*m+1.99464e-07*m*m+-5.09199/m;
            if(NomSysupSysdown==1) mistagrate = (1.61341+-0.000566321*m+1.99464e-07*m*m+-5.09199/m)*(1-(0.0631436+7.87525e-05*m+-1.10405e-07*m*m));
            if(NomSysupSysdown==2) mistagrate = (1.61341+-0.000566321*m+1.99464e-07*m*m+-5.09199/m)*(1+(0.0631436+7.87525e-05*m+-1.10405e-07*m*m));
          }
          if(workingPoint==2){
            if(NomSysupSysdown==0) mistagrate = 1.59373+-0.00113028*m+8.66631e-07*m*m+-1.10505/m;
            if(NomSysupSysdown==1) mistagrate = (1.59373+-0.00113028*m+8.66631e-07*m*m+-1.10505/m)*(1-(0.142253+0.000227323*m+-2.71704e-07*m*m));
            if(NomSysupSysdown==2) mistagrate = (1.59373+-0.00113028*m+8.66631e-07*m*m+-1.10505/m)*(1+(0.142253+0.000227323*m+-2.71704e-07*m*m));
          }
          if(workingPoint==3){
            if(NomSysupSysdown==0) mistagrate = 1.77088+-0.00371551*m+5.86489e-06*m*m+-3.01178e-09*m*m*m;
            if(NomSysupSysdown==1) mistagrate = (1.77088+-0.00371551*m+5.86489e-06*m*m+-3.01178e-09*m*m*m)*(1-(0.223324+0.000231341*m+-2.34362e-07*m*m));
            if(NomSysupSysdown==2) mistagrate = (1.77088+-0.00371551*m+5.86489e-06*m*m+-3.01178e-09*m*m*m)*(1+(0.223324+0.000231341*m+-2.34362e-07*m*m));
          }
        }
        cout << "Hard-coded: " << tagger << " variation " << NomSysupSysdown << " working point " << workingPoint << " mistagsf = " << mistagrate << endl;*/

        RooArgSet passPDFs,passCounts,passNonPOIPDFs,failPDFs,failCounts,sfVars,failNonPOIPDFs;
        for(int i=0; i<passTemplates.GetEntriesFast(); i++)
        {
          //build the pass PDF
          TH1 *h=(TH1 *)passTemplates.At(i);
          TString title(h->GetTitle());
          TString name("passv"); name+= i;
          Float_t nExp=h->Integral();

          //b-tag efficiency scale factor
          RooRealVar *sfVar;
          if(i==0) sfVar = new RooRealVar(Form("sf%d",i),title,1,0,2);
          if(i==1) sfVar = new RooRealVar(Form("sf%d",i),title,mistagrate,0,2);
          sfVars.add(*sfVar);
          if(i!=idxOfInterest) sfVar->setConstant(true);

          //npass expected
          RooRealVar *npassVar=new RooRealVar(name,name,nExp,nExp,nExp);
          npassVar->setConstant(true);
          name.ReplaceAll("v","fv");


          //re-scaling of the number of passing jets
          RooFormulaVar *npassFormulaVar = new RooFormulaVar(name,
            "@0*@1",
            RooArgSet(*npassVar,*sfVar)
          );
          passCounts.add( *npassFormulaVar );
          RooDataHist *itempl = new RooDataHist(name+"_hist",name+"_hist", RooArgList(x), Import(*h));
          RooHistPdf *ipdf    = new RooHistPdf (name+"_pdf", name+"_pdf",  RooArgSet(x), *itempl);
          ipdf->SetTitle(title);
          passPDFs.add(*ipdf);
          if(i!=idxOfInterest) passNonPOIPDFs.add(*ipdf);

          //build the fail PDF
          h=(TH1 *)failTemplates.At(i);
          title=h->GetTitle();
          name="failfv"; name+= i;
          nExp=h->Integral();
          RooFormulaVar *nFailFormulaVar = new RooFormulaVar(name,
            Form("@1*%f >=0 ? @0*(1-@1*%f)/(@1*%f) : 0",expEff[i],expEff[i],expEff[i]),
            RooArgSet(*npassFormulaVar,*sfVar)
          );
          failCounts.add( *nFailFormulaVar );
          itempl = new RooDataHist(name+"_hist",name+"_hist", RooArgList(x), Import(*h));
          ipdf    = new RooHistPdf (name+"_pdf", name+"_pdf",  RooArgSet(x), *itempl);
          ipdf->SetTitle(title);
          failPDFs.add(*ipdf);
          if(i!=idxOfInterest) failNonPOIPDFs.add(*ipdf);
        }

        //create the final pdfs
        RooSimultaneous *pdf = new RooSimultaneous("pdf","pdf",status);
        RooAddPdf *finalPassPDF = new RooAddPdf("passpdf","passpdf", passPDFs, passCounts);
        pdf->addPdf(*finalPassPDF,"pass");
        RooAddPdf *finalFailPDF = new RooAddPdf("failpdf","failpdf", failPDFs, failCounts);
        pdf->addPdf(*finalFailPDF,"fail");

        //fit (using minos has the same behavior of profiling all variables except the parameter of interest)
        RooRealVar *sfVar=(RooRealVar *)sfVars.find(Form("sf%d",idxOfInterest));
        RooAbsReal *ll = pdf->createNLL(*data,Extended(true));
        RooMinuit minuit(*ll);
        minuit.setErrorLevel(0.5);
        minuit.migrad();
        minuit.hesse();
        RooArgSet poi(*sfVar);
        result.minuitStatus = minuit.minos(poi);

        //save result
        result.effExp    = expEff[idxOfInterest];
        result.effExpUnc = expEffUnc[idxOfInterest];
        result.sf        = sfVar->getVal();
        result.sfUnc     = sfVar->getError();
        result.eff       = result.sf*result.effExp;
        result.effUnc    = TMath::Sqrt( TMath::Power(result.sfUnc*result.effExp,2)+TMath::Power(result.sf*result.effExpUnc,2) );

        //
        if(saveResultIn!="")
        {
          TCanvas *canvas=new TCanvas("c","c",1100,500);
          canvas->SetTopMargin(0);
          canvas->SetBottomMargin(0);
          canvas->SetRightMargin(0);
          canvas->SetLeftMargin(0);
          canvas->Divide(2,1);

          for(int i=0; i<2; i++)
          {
            std::string statusName(i==0 ? "pass" : "fail");

            TPad *c=(TPad *)canvas->cd(i+1);
            c->SetTopMargin(0);
            c->SetBottomMargin(0);
            c->SetRightMargin(0);
            c->SetLeftMargin(0);

            TPad *p1 = new TPad("p1","p1",0.0,0.85,1.0,0.0);
            p1->SetRightMargin(0.05);
            p1->SetLeftMargin(0.12);
            p1->SetTopMargin(0.01);
            p1->SetBottomMargin(0.1);
            p1->Draw();
            p1->cd();
            RooPlot *frame=x.frame();
            data->plotOn(frame,RooFit::Name("data"),RooFit::Cut(("status==status::"+statusName).c_str()));
            pdf->plotOn(frame,
              RooFit::Slice(status,statusName.c_str()),
              RooFit::Name("totalexp"),
              RooFit::ProjWData(*data),
              RooFit::LineColor(1),
              RooFit::LineWidth(1),
              RooFit::FillStyle(1001),
              RooFit::FillColor(0),
              RooFit::MoveToBack());
              pdf->plotOn(frame,
                RooFit::Slice(status,statusName.c_str()),
                RooFit::Name("nonpoifit"),
                RooFit::ProjWData(*data),
                RooFit::Components(i==0 ? passNonPOIPDFs : failNonPOIPDFs),
                RooFit::FillColor(kGray),
                RooFit::LineColor(kGray),
                RooFit::FillStyle(1001),
                RooFit::DrawOption("f"),
                RooFit::MoveToBack());
                frame->Draw();
                frame->GetYaxis()->SetTitleOffset(1.5);
                frame->GetXaxis()->SetTitle("Kinematic discriminator");
                frame->GetYaxis()->SetTitle("Events");
                Float_t ymax(TMath::Max(passDataH->GetMaximum(),failDataH->GetMaximum())*1.5);
                Float_t xmin(frame->GetXaxis()->GetXmin()),xmax(frame->GetXaxis()->GetXmax());
                frame->GetYaxis()->SetRangeUser(0,ymax);

                TLatex *label= new TLatex();
                label->SetNDC();
                label->SetTextFont(42);
                label->SetTextSize(0.04);

                TString tagger_label = tagger;
                TString wp_lable = workingPoint_labels[workingPoint];
                TString jpt_label = i==0 ? "tagged jets " : "vetoed jets ";
                jpt_label += jetptRange_labels[jetptRange];
                label->DrawLatex(0.54,0.94, Form("#scale[0.95]{%.2f fb^{-1} (13 TeV)}",lumi));
                label->DrawLatex(0.18,0.94, "#bf{CMS}");
                label->DrawLatex(0.54,0.90, tagger_label);
                label->DrawLatex(0.54,0.86, wp_lable);
                label->DrawLatex(0.54,0.82, jpt_label);

                TLine *line=new TLine();
                line->SetLineStyle(9);
                for(Int_t k=1; k<=3; k++)
                {
                  if(k<3)
                  line->DrawLine(xmin+k*(xmax-xmin)/3.,0,xmin+k*(xmax-xmin)/3.,ymax/1.5);
                  label->DrawLatex((2*(k-1)+1.)/6.,0.7,Form("#scale[1.0]{#it{=%d jets}}",k+1));
                }

                TLegend *leg=new TLegend(0.18,0.76,0.6,0.86);
                leg->SetNColumns(3);
                leg->AddEntry("data",      "Data",            "p");
                leg->AddEntry("totalexp",  sfVar->GetTitle(), "f");
                leg->AddEntry("nonpoifit", "udsg+c",          "f");
                leg->SetFillStyle(0);
                leg->SetTextFont(42);
                leg->SetBorderSize(0);
                leg->SetTextSize(0.035);
                leg->Draw();

                c->cd();
                TPad *p2 =new TPad("p2","p2",0.0,0.85,1.0,1.0);
                p2->SetBottomMargin(0.05);
                p2->SetRightMargin(0.05);
                p2->SetLeftMargin(0.12);
                p2->SetTopMargin(0.05);
                p2->SetGrid();
                p2->Draw();
                p2->cd();

                RooHist *hpull = frame->pullHist();
                RooPlot *pullFrame = x.frame();
                //hpull->plotOn(pullFrame);
                pullFrame->addPlotable((RooPlotable *)hpull,"P") ;
                pullFrame->Draw();
                pullFrame->GetYaxis()->SetTitle("Pull");
                pullFrame->GetYaxis()->SetTitleSize(0.2);
                pullFrame->GetYaxis()->SetLabelSize(0.2);
                pullFrame->GetXaxis()->SetTitleSize(0);
                pullFrame->GetXaxis()->SetLabelSize(0);
                pullFrame->GetYaxis()->SetTitleOffset(0.15);
                pullFrame->GetYaxis()->SetNdivisions(4);
                pullFrame->GetYaxis()->SetRangeUser(-3.1,3.1);
                pullFrame->GetXaxis()->SetTitleOffset(0.8);

                TLatex *label2= new TLatex();
                label2->SetNDC();
                label2->SetTextFont(42);
                label2->SetTextSize(0.04);
              }

              canvas->Modified();
              canvas->Update();
              canvas->SaveAs(saveResultIn+".png");
              canvas->SaveAs(saveResultIn+".pdf");
              canvas->Delete();
            }


            //free memory
            delete ll;

            //all done
            return result;
          }

          //
          TTbarFracFitter::~TTbarFracFitter()
          {

          }
