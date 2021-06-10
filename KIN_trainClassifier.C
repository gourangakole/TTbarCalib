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

void KIN_trainClassifier( TString myMethodList = "", TString inputFile="", Int_t jetRank=LEAD)
{
  gSystem->ExpandPathName(inputFile);
  TString wgtsDir_name = "${CMSSW_BASE}/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/data/KIN_MVA_UL18_v6_" + myMethodList;
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

  // Default MVA methods to be trained + tested
  std::map<std::string,int> Use;
  Use["Cuts"]            = 0;
  Use["CutsD"]           = 0;
  Use["CutsPCA"]         = 0;
  Use["CutsGA"]          = 0;
  Use["CutsSA"]          = 0;
  Use["Likelihood"]      = 0;
  Use["LikelihoodD"]     = 0; // the "D" extension indicates decorrelated input variables (see option strings)
  Use["LikelihoodPCA"]   = 0; // the "PCA" extension indicates PCA-transformed input variables (see option strings)
  Use["LikelihoodKDE"]   = 0;
  Use["LikelihoodMIX"]   = 0;
  Use["PDERS"]           = 0;
  Use["PDERSD"]          = 0;
  Use["PDERSPCA"]        = 0;
  Use["PDEFoam"]         = 0;
  Use["PDEFoamBoost"]    = 0; // uses generalised MVA method boosting
  Use["KNN"]             = 0; // k-nearest neighbour method
  Use["LD"]              = 0; // Linear Discriminant identical to Fisher
  Use["Fisher"]          = 0;
  Use["FisherCat"]       = 0;//added by loic
  Use["FisherG"]         = 0;
  Use["BoostedFisher"]   = 0; // uses generalised MVA method boosting
  Use["HMatrix"]         = 0;
  Use["FDA_GA"]          = 0; // minimisation of user-defined function using Genetics Algorithm
  Use["FDA_SA"]          = 0;
  Use["FDA_MC"]          = 0;
  Use["FDA_MT"]          = 0;
  Use["FDA_GAMT"]        = 0;
  Use["FDA_MCMT"]        = 0;
  Use["MLP"]             = 0; // Recommended ANN
  Use["MLPBFGS"]         = 0; // Recommended ANN with optional training method
  Use["MLPBNN"]          = 0; // Recommended ANN with BFGS training method and bayesian regulator
  Use["CFMlpANN"]        = 0; // Depreciated ANN from ALEPH
  Use["TMlpANN"]         = 0; // ROOT's own ANN
  Use["SVM"]             = 0;
  Use["BDT"]             = 0; // uses Adaptive Boost
  Use["BDTG"]            = 0; // uses Gradient Boost
  Use["BDTB"]            = 0; // uses Bagging
  Use["BDTD"]            = 0; // decorrelation + Adaptive Boost
  Use["BDTF"]            = 0; // allow usage of fisher discriminant for node splitting
  Use["RuleFit"]         = 0;
  std::cout << std::endl;
  std::cout << "==> Start TMVAClassification" << std::endl;

  if (myMethodList != "") {
    for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) it->second = 0;
    cout << "Using MVA method = " << myMethodList << endl;
    std::vector<TString> mlist = TMVA::gTools().SplitString( myMethodList, ',' );
    for (UInt_t i=0; i<mlist.size(); i++) {
      std::string regMethod(mlist[i]);

      if (Use.find(regMethod) == Use.end()) {
        std::cout << "Method \"" << regMethod << "\" not known in TMVA under this name. Choose among the following:" << std::endl;
        for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) std::cout << it->first << " ";
        std::cout << std::endl;
        return;
      }
      Use[regMethod] = 1;
    }
  }

  // Create a ROOT output file where TMVA will store ntuples, histograms, etc.
  TString outfileName( "TMVA_BDT_UL18_v6.root" );
  TFile* outputFile = TFile::Open( outfileName, "RECREATE" );
  cout << "Create Factory" << endl;
  TMVA::Factory *factory = new TMVA::Factory("TMVAClassification", outputFile, "!V:!Silent:Color:DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Classification");
  cout << "Create DataLoader" << endl;
  TMVA::DataLoader *dataloader=new TMVA::DataLoader("");
  // You can add so-called "Spectator variables", which are not used in the MVA training
  // factory->AddSpectator( "spec1 := var1*2",  "Spectator 1", "units", 'F' );
  cout << "Open input files" << endl;
  TFile *inF=TFile::Open(inputFile);
  TTree *t=(TTree *)inF->Get("kin");
  cout << "Number of events in input file \'kin\' tree: " << t->GetEntries() << endl;
  outputFile->cd();

  //b-jets are saved as 5, require that the event passes nominal preselection (weight[0]>0)
  TString jetRankCut("");
  if(jetRank!=OTHER)      {
    jetRankCut += "&& jetrank=="; jetRankCut += jetRank;
  }
  else if(jetRank==OTHER) {
    jetRankCut += "&& jetrank>="; jetRankCut += jetRank;
  }
  TCut sigCut("abs(flavour)==5 && weight[0]>0 && abs(ttbar_chan)<230000" + jetRankCut);
  TCut bkgCut("abs(flavour)!=5 && weight[0]>0 && abs(ttbar_chan)<230000" + jetRankCut);
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
  //
  // Please lookup the various method configuration options in the corresponding cxx files, eg:
  // src/MethoCuts.cxx, etc, or here: http://tmva.sourceforge.net/optionRef.html
  // it is possible to preset ranges in the option string in which the cut optimisation should be done:
  // "...:CutRangeMin[2]=-1:CutRangeMax[2]=1"...", where [2] is the third input variable

  // Cut optimisation
  if (Use["Cuts"]){
    factory->BookMethod(dataloader, TMVA::Types::kCuts, "Cuts",
			 "!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart" );
     }
  if (Use["CutsD"]){
    factory->BookMethod(dataloader, TMVA::Types::kCuts, "CutsD",
			 "!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart:VarTransform=Decorrelate" );
     }
  if (Use["CutsPCA"]){
    factory->BookMethod(dataloader, TMVA::Types::kCuts, "CutsPCA",
			 "!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart:VarTransform=PCA" );
     }
  if (Use["CutsGA"]){
    factory->BookMethod(dataloader, TMVA::Types::kCuts, "CutsGA",
			 "H:!V:FitMethod=GA:CutRangeMin[0]=-10:CutRangeMax[0]=10:VarProp[1]=FMax:EffSel:Steps=30:Cycles=3:PopSize=400:SC_steps=10:SC_rate=5:SC_factor=0.95" );
     }
  if (Use["CutsSA"]){
    factory->BookMethod(dataloader, TMVA::Types::kCuts, "CutsSA",
			 "!H:!V:FitMethod=SA:EffSel:MaxCalls=150000:KernelTemp=IncAdaptive:InitialTemp=1e+6:MinTemp=1e-6:Eps=1e-10:UseDefaultScale" );
     }
  // Likelihood ("naive Bayes estimator")
  if (Use["Likelihood"]){
    factory->BookMethod(dataloader, TMVA::Types::kLikelihood, "Likelihood",
			 "H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmoothBkg[1]=10:NSmooth=1:NAvEvtPerBin=50" );
     }
  // Decorrelated likelihood
  if (Use["LikelihoodD"]){
    factory->BookMethod(dataloader, TMVA::Types::kLikelihood, "LikelihoodD",
			 "!H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=50:VarTransform=Decorrelate" );
     }
  // PCA-transformed likelihood
  if (Use["LikelihoodPCA"]){
    factory->BookMethod(dataloader, TMVA::Types::kLikelihood, "LikelihoodPCA",
			 "!H:!V:!TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=50:VarTransform=PCA" );
     }
  // Use a kernel density estimator to approximate the PDFs
  if (Use["LikelihoodKDE"]){
    factory->BookMethod(dataloader, TMVA::Types::kLikelihood, "LikelihoodKDE",
			 "!H:!V:!TransformOutput:PDFInterpol=KDE:KDEtype=Gauss:KDEiter=Adaptive:KDEFineFactor=0.3:KDEborder=None:NAvEvtPerBin=50" );
     }
  // Use a variable-dependent mix of splines and kernel density estimator
  if (Use["LikelihoodMIX"]){
    factory->BookMethod(dataloader, TMVA::Types::kLikelihood, "LikelihoodMIX",
			 "!H:!V:!TransformOutput:PDFInterpolSig[0]=KDE:PDFInterpolBkg[0]=KDE:PDFInterpolSig[1]=KDE:PDFInterpolBkg[1]=KDE:PDFInterpolSig[2]=Spline2:PDFInterpolBkg[2]=Spline2:PDFInterpolSig[3]=Spline2:PDFInterpolBkg[3]=Spline2:KDEtype=Gauss:KDEiter=Nonadaptive:KDEborder=None:NAvEvtPerBin=50" );
     }
  // Test the multi-dimensional probability density estimator
  // here are the options strings for the MinMax and RMS methods, respectively:
  //      "!H:!V:VolumeRangeMode=MinMax:DeltaFrac=0.2:KernelEstimator=Gauss:GaussSigma=0.3" );
  //      "!H:!V:VolumeRangeMode=RMS:DeltaFrac=3:KernelEstimator=Gauss:GaussSigma=0.3" );
  if (Use["PDERS"]){
    factory->BookMethod(dataloader, TMVA::Types::kPDERS, "PDERS",
			 "!H:!V:NormTree=T:VolumeRangeMode=Adaptive:KernelEstimator=Gauss:GaussSigma=0.3:NEventsMin=400:NEventsMax=600" );
     }
  if (Use["PDERSD"]){
    factory->BookMethod(dataloader, TMVA::Types::kPDERS, "PDERSD",
			 "!H:!V:VolumeRangeMode=Adaptive:KernelEstimator=Gauss:GaussSigma=0.3:NEventsMin=400:NEventsMax=600:VarTransform=Decorrelate" );
     }
  if (Use["PDERSPCA"]){
    factory->BookMethod(dataloader, TMVA::Types::kPDERS, "PDERSPCA",
			 "!H:!V:VolumeRangeMode=Adaptive:KernelEstimator=Gauss:GaussSigma=0.3:NEventsMin=400:NEventsMax=600:VarTransform=PCA" );
     }

  // Multi-dimensional likelihood estimator using self-adapting phase-space binning
  if (Use["PDEFoam"]){
    factory->BookMethod(dataloader, TMVA::Types::kPDEFoam, "PDEFoam",
			 "!H:!V:SigBgSeparate=F:TailCut=0.001:VolFrac=0.0666:nActiveCells=500:nSampl=2000:nBin=5:Nmin=100:Kernel=None:Compress=T" );
     }

  if (Use["PDEFoamBoost"]){
    factory->BookMethod(dataloader, TMVA::Types::kPDEFoam, "PDEFoamBoost",
			 "!H:!V:Boost_Num=30:Boost_Transform=linear:SigBgSeparate=F:MaxDepth=4:UseYesNoCell=T:DTLogic=MisClassificationError:FillFoamWithOrigWeights=F:TailCut=0:nActiveCells=500:nBin=20:Nmin=400:Kernel=None:Compress=T" );
     }

  // K-Nearest Neighbour classifier (KNN)
  if (Use["KNN"]){
    factory->BookMethod(dataloader, TMVA::Types::kKNN, "KNN",
			 "H:nkNN=20:ScaleFrac=0.8:SigmaFact=1.0:Kernel=Gaus:UseKernel=F:UseWeight=T:!Trim" );
     }

  // H-Matrix (chi2-squared) method
  if (Use["HMatrix"]){
    factory->BookMethod(dataloader, TMVA::Types::kHMatrix, "HMatrix", "!H:!V:VarTransform=None" );
  }

  // Linear discriminant (same as Fisher discriminant)
  if (Use["LD"]){
    factory->BookMethod(dataloader, TMVA::Types::kLD, "LD", "H:!V:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10" );
  }

  // Fisher discriminant (same as LD)
  if (Use["Fisher"]){
    factory->BookMethod(dataloader, TMVA::Types::kFisher, "Fisher", "H:!V:Fisher:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10" );
  }

  // Fisher with Gauss-transformed input variables
  if (Use["FisherG"]){
    factory->BookMethod(dataloader, TMVA::Types::kFisher, "FisherG", "H:!V:VarTransform=Gauss" );
  }

  // Composite classifier: ensemble (tree) of boosted Fisher classifiers
  if (Use["BoostedFisher"]){
    factory->BookMethod(dataloader, TMVA::Types::kFisher, "BoostedFisher",
			 "H:!V:Boost_Num=20:Boost_Transform=log:Boost_Type=AdaBoost:Boost_AdaBoostBeta=0.2:!Boost_DetailedMonitoring" );
     }

  // Function discrimination analysis (FDA) -- test of various fitters - the recommended one is Minuit (or GA or SA)
  if (Use["FDA_MC"]){
    factory->BookMethod(dataloader, TMVA::Types::kFDA, "FDA_MC",
			 "H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=MC:SampleSize=100000:Sigma=0.1" );
     }

  if (Use["FDA_GA"]){ // can also use Simulated Annealing (SA) algorithm (see Cuts_SA options])
    factory->BookMethod(dataloader, TMVA::Types::kFDA, "FDA_GA",
			 "H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=GA:PopSize=300:Cycles=3:Steps=20:Trim=True:SaveBestGen=1" );
     }

  if (Use["FDA_SA"]){ // can also use Simulated Annealing (SA) algorithm (see Cuts_SA options])
    factory->BookMethod(dataloader, TMVA::Types::kFDA, "FDA_SA",
			 "H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=SA:MaxCalls=15000:KernelTemp=IncAdaptive:InitialTemp=1e+6:MinTemp=1e-6:Eps=1e-10:UseDefaultScale" );
     }

  if (Use["FDA_MT"]){
    factory->BookMethod(dataloader, TMVA::Types::kFDA, "FDA_MT",
			 "H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=MINUIT:ErrorLevel=1:PrintLevel=-1:FitStrategy=2:UseImprove:UseMinos:SetBatch" );
     }

  if (Use["FDA_GAMT"]){
    factory->BookMethod(dataloader, TMVA::Types::kFDA, "FDA_GAMT",
			 "H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=GA:Converger=MINUIT:ErrorLevel=1:PrintLevel=-1:FitStrategy=0:!UseImprove:!UseMinos:SetBatch:Cycles=1:PopSize=5:Steps=5:Trim" );
     }

  if (Use["FDA_MCMT"]){
    factory->BookMethod(dataloader, TMVA::Types::kFDA, "FDA_MCMT",
			 "H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=MC:Converger=MINUIT:ErrorLevel=1:PrintLevel=-1:FitStrategy=0:!UseImprove:!UseMinos:SetBatch:SampleSize=20" );
     }

  // TMVA ANN: MLP (recommended ANN) -- all ANNs in TMVA are Multilayer Perceptrons
  if (Use["MLP"]){
    factory->BookMethod(dataloader, TMVA::Types::kMLP, "MLP","H:!V:NeuronType=tanh:NCycles=200:HiddenLayers=N+1,N:TestRate=5");
    //"H:!V:NeuronType=tanh:VarTransform=N:NCycles=600:HiddenLayers=N+5:TestRate=5:!UseRegulator" );
  }


  if (Use["MLPBFGS"]){
    factory->BookMethod(dataloader, TMVA::Types::kMLP, "MLPBFGS", "H:!V:NeuronType=tanh:VarTransform=N:NCycles=600:HiddenLayers=N+5:TestRate=5:TrainingMethod=BFGS:!UseRegulator" );
  }
  if (Use["MLPBNN"]){
    factory->BookMethod(dataloader, TMVA::Types::kMLP, "MLPBNN", "H:!V:NeuronType=tanh:VarTransform=N:NCycles=600:HiddenLayers=N+5:TestRate=5:TrainingMethod=BFGS:UseRegulator" ); // BFGS training with bayesian regulators
  }

  // CF(Clermont-Ferrand)ANN
  if (Use["CFMlpANN"]){
    factory->BookMethod(dataloader, TMVA::Types::kCFMlpANN, "CFMlpANN", "!H:!V:NCycles=2000:HiddenLayers=N+1,N"  ); // n_cycles:#nodes:#nodes:...
  }

  // Tmlp(Root)ANN
  if (Use["TMlpANN"]){
    factory->BookMethod(dataloader, TMVA::Types::kTMlpANN, "TMlpANN", "!H:!V:NCycles=200:HiddenLayers=N+1,N:LearningMethod=BFGS:ValidationFraction=0.3"  ); // n_cycles:#nodes:#nodes:...
  }

  // Support Vector Machine
  if (Use["SVM"]){
    factory->BookMethod(dataloader, TMVA::Types::kSVM, "SVM", "Gamma=0.25:Tol=0.001:VarTransform=Norm" );
  }
  // Boosted Decision Trees
  if (Use["BDTG"]){ // Gradient Boost
    factory->BookMethod(dataloader, TMVA::Types::kBDT, "BDTG",
			 "!H:!V:NTrees=1000:MinNodeSize=1.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedGrad:GradBaggingFraction=0.5:nCuts=20:MaxDepth=2" );
     }

  if (Use["BDT"]){
    cout << "Booking BDT" << endl;
    factory->BookMethod(dataloader, TMVA::Types::kBDT, "BDT","NTrees=1000:BoostType=Grad:MinNodeSize=5%:MaxDepth=3:Shrinkage=1.0:NegWeightTreatment=Pray");
  }


  if (Use["BDTB"]){ // Bagging
    factory->BookMethod(dataloader, TMVA::Types::kBDT, "BDTB",
			 "!H:!V:NTrees=400:BoostType=Bagging:SeparationType=GiniIndex:nCuts=20" );
     }
  if (Use["BDTD"]){ // Decorrelation + Adaptive Boost
    factory->BookMethod(dataloader, TMVA::Types::kBDT, "BDTD",
			 "!H:!V:NTrees=400:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=25:PruneMethod=CostComplexity:PruneStrength=25.0:VarTransform=Decorrelate");
       //"!H:!V:NTrees=400:MinNodeSize=5%:MaxDepth=3:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=20:VarTransform=Decorrelate" );
  }

  if (Use["BDTF"]){  // Allow Using Fisher discriminant in node splitting for (strong) linearly correlated variables
    factory->BookMethod(dataloader, TMVA::Types::kBDT, "BDTMitFisher",
			 "!H:!V:NTrees=50:MinNodeSize=2.5%:UseFisherCuts:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=20" );
     }

  // RuleFit -- TMVA implementation of Friedman's method
  if (Use["RuleFit"]){
    factory->BookMethod(dataloader, TMVA::Types::kRuleFit, "RuleFit",
			 "H:!V:RuleFitModule=RFTMVA:Model=ModRuleLinear:MinImp=0.001:RuleMinDist=0.001:NTrees=20:fEventsMin=0.01:fEventsMax=0.5:GDTau=-1.0:GDTauPrec=0.01:GDStep=0.01:GDNSteps=10000:GDErrScale=1.02" );
     }

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
