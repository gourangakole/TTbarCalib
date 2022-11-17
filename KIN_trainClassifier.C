#include <cstdlib>
#include <iostream>
#include <map>
#include <string>

#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TObjString.h"
#include "TSystem.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TSystemDirectory.h"
#include "TMVA/Config.h"

#if not defined(__CINT__) || defined(__MAKECINT__)
#include "TMVA/Factory.h"
#include "TMVA/Tools.h"
#include "TMVA/MethodCategory.h"
#include "TMVA/DataLoader.h"
#endif

using namespace std;

enum JETRANK{LEAD,SUBLEAD,OTHER, INCLUSIVE=10000};

void KIN_trainClassifier( TString inputFile="", Int_t jetRank=LEAD)
{
  gSystem->ExpandPathName(inputFile);
  TString wgtsDir_name = "${CMSSW_BASE}/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/data/KIN_MVA_UL16_BDT_HIPM";
  TString wgtsDir(wgtsDir_name);
  gSystem->ExpandPathName(wgtsDir);
  TMVA::gConfig().GetIONames().fWeightFileDir = wgtsDir;
  if(jetRank==LEAD)         TMVA::gConfig().GetIONames().fWeightFileDir += "/leading/";
  else if(jetRank==SUBLEAD) TMVA::gConfig().GetIONames().fWeightFileDir += "/subleading/";
  else if(jetRank==OTHER)   TMVA::gConfig().GetIONames().fWeightFileDir += "/others/";
  else                      TMVA::gConfig().GetIONames().fWeightFileDir += "/inclusive/";
  cout << "Output dir set to: " << TMVA::gConfig().GetIONames().fWeightFileDir << endl;
  gSystem->Exec("mkdir -p "+TMVA::gConfig().GetIONames().fWeightFileDir);

  // This loads the library
  TMVA::Tools::Instance();
  std::cout << std::endl;
  std::cout << "==> Start TMVAClassification" << std::endl;

  // Create a ROOT output file where TMVA will store ntuples, histograms, etc.
  TString outfileName( "TMVA_BDT_UL16_HIPM.root" );
  TFile* outputFile = TFile::Open( outfileName, "RECREATE" );
  cout << "Create Factory" << endl;
  TMVA::Factory *factory = new TMVA::Factory("TMVAClassification", outputFile, "!V:!Silent:Color:DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Classification");
  cout << "Create DataLoader" << endl;
  TMVA::DataLoader *dataloader=new TMVA::DataLoader("");
  // You can add so-called "Spectator variables", which are not used in the MVA training
  // factory->AddSpectator( "spec1 := var1*2",  "Spectator 1", "units", 'F' );

  // Open and load input files from TTbarEventAnalysis step
  TFile *inF=TFile::Open(inputFile);
  // The 'kin' ttree we will load has one entry per jet (so don't think in terms of events)
  TTree *t=(TTree *)inF->Get("kin");
  cout << "Number of events in input file \'kin\' tree: " << t->GetEntries() << endl;

  // Loading the ttree and printing branch information can help understand what is sotred in the ttrees
  // and whether the information is correct.
  typedef struct MyEventInfoBranches_t
  {
    Float_t Jet_pt[100];
    Int_t Jet_flavour[100];
    Int_t Jet_rank[100];
    Int_t nJet;
  } evinit;
  MyEventInfoBranches_t ev;
  t->SetBranchAddress("jetpt",          ev.Jet_pt);
  t->SetBranchAddress("flavour",          ev.Jet_flavour);
  t->SetBranchAddress("jetrank",          ev.Jet_rank);
  // Each entry in the ttree is for a single jet in the event
  for(int i=0; i<t->GetEntries(); ++i){
    t->GetEntry(i);
    //cout << "i: " << i << " , pT: " << ev.Jet_pt[0] << " , flavour: " << ev.Jet_flavour[0] << " , jetrank: " << ev.Jet_rank[0] << endl;
  }
  outputFile->cd();

  // Divide input into signal and background
  TString jetRankCut("");
  if(jetRank!=OTHER)      {
    jetRankCut += "&& jetrank==";
    jetRankCut += jetRank;
  }
  else if(jetRank==OTHER) {
    jetRankCut += "&& jetrank>=";
    jetRankCut += jetRank;
  }
  // Require event passes nominal preselection (weight[0]>0) and eµ ttbar channel
  // "flavour" branch is filled with the flavour of the selected jet in the event with the lowest pT
  TCut sigCut("abs(flavour)==5 && weight[0]>0 && abs(ttbar_chan)==143" + jetRankCut);
  TCut bkgCut("abs(flavour)!=5 && weight[0]>0 && abs(ttbar_chan)==143" + jetRankCut);
  cout << "sigCut: " << sigCut << endl;
  cout << "bkgCut: " << bkgCut << endl;
  dataloader->SetInputTrees(t,sigCut,bkgCut);
  dataloader->GetDataSetInfo();

  //use common weight in the events
  dataloader->SetSignalWeightExpression("weight[0]");
  dataloader->SetBackgroundWeightExpression("weight[0]");

  //define variables for the training
  dataloader->AddVariable( "close_mlj[0]",   "M(close lepton,jet)"                            "GeV", 'F' );
  dataloader->AddVariable( "close_dphi",  "#Delta#phi(close lepton,jet)"                   "rad", 'F' );
  dataloader->AddVariable( "close_deta",  "#Delta#eta(close lepton,jet)"                   "",    'F' );
  dataloader->AddVariable( "close_lj2ll_dphi",    "#Delta#phi(close lepton+jet,dilepton)"                     "rad", 'F' );
  dataloader->AddVariable( "close_lj2ll_deta",    "#Delta#eta(close lepton+jet,dilepton)"                     "",    'F' );

  dataloader->AddVariable( "far_mlj",     "M(far lepton,jet)"                              "GeV", 'F' );
  dataloader->AddVariable( "far_dphi",    "#Delta#phi(far lepton,jet)"                     "rad", 'F' );
  dataloader->AddVariable( "far_deta",    "#Delta#eta(far lepton,jet)"                     "",    'F' );
  dataloader->AddVariable( "far_lj2ll_dphi",    "#Delta#phi(far lepton+jet,dilepton)"                     "rad", 'F' );
  dataloader->AddVariable( "far_lj2ll_deta",    "#Delta#eta(far lepton+jet,dilepton)"                     "",    'F' );

  dataloader->AddVariable( "j2ll_dphi",     "#Delta#phi(dilepton,jet)",                      "rad", 'F' );
  dataloader->AddVariable( "j2ll_deta",     "#Delta#eta(dilepton,jet)",                      "",    'F' );

  // Apply additional cuts on the signal and background samples (can be different)
  TCut mycuts = "";
  TCut mycutb = "";
  std::stringstream SplitOptionString;
  SplitOptionString <<":SplitMode=Random:NormMode=NumEvents:!V";
  cout << "MVA options: " << SplitOptionString.str() << endl;
  dataloader->PrepareTrainingAndTestTree( mycuts, mycutb, SplitOptionString.str() );

  cout << "Booking MVA methods . . . " << endl;

  // ---- Book MVA methods
  factory->BookMethod(dataloader, TMVA::Types::kBDT, "BDT","NTrees=1000:BoostType=Grad:MinNodeSize=5%:MaxDepth=3:Shrinkage=1.0:NegWeightTreatment=Pray");

  // ---- Now you can optimize the setting (configuration) of the MVAs using the set of training events
  // factory->OptimizeAllMethods("SigEffAt001","Scan");
  // factory->OptimizeAllMethods("ROCIntegral","FitGA");

  cout << "Training . . . . " << endl;
  factory->TrainAllMethods();
  cout << "Testing . . . . " << endl;
  factory->TestAllMethods();
  cout << "Evaluating . . . . " << endl;
  factory->EvaluateAllMethods();

  // Save the output
  outputFile->Close();

  std::cout << "==> Wrote root file: " << outputFile->GetName() << std::endl;
  std::cout << "==> TMVAClassification is done!" << std::endl;
  std::cout << " ==> Weights are stored in " << TMVA::gConfig().GetIONames().fWeightFileDir << std::endl;
  delete factory;
  delete dataloader;
  cout << "deleted factory and dataloader" << endl;
  return;
}
