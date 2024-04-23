#ifndef _TTbarEventAnalysis_h_
#define _TTbarEventAnalysis_h_

#include "TFile.h"
#include "TH1F.h"
#include "TString.h"
#include "TTree.h"
#include "TSystem.h"
#include "Math/VectorUtil.h"
#include "TGraph.h"
#include "TMVA/Reader.h"
#include "string"
#include "sstream"
#include "algorithm"
#include "iterator"
#include <map>
#include <vector>
#include <iostream>

#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "JetMETCorrections/Modules/interface/JetResolution.h"

struct LJKinematics_t
{
  Float_t dr,dphi,deta,ptrel,mlj,kindisc;
  Float_t lj2ll_deta,lj2ll_dphi;
};

bool sortLJKinematicsByDR (LJKinematics_t i,LJKinematics_t j) { return (i.dr<j.dr); }

class TTbarEventAnalysis
{
 public:
 TTbarEventAnalysis() :
    tmvaReader_(0),
    readTTJetsGenWeights_(false)
      //puWgtGr_(0),puWgtDownGr_(0),puWgtUpGr_(0)
      {
	// Jet resolution/energy correction uncertainty parameterizations
	//TString jecUncUrl("${CMSSW_BASE}/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/data/Summer19UL16_V7_MC_Uncertainty_AK4PFchs.txt");
	//TString jecUncUrl("${CMSSW_BASE}/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/data/Summer19UL16APV_V7_MC_Uncertainty_AK4PFchs.txt");
	TString jecUncUrl("${CMSSW_BASE}/src/TTbarCalib/data/Summer22_22Sep2023_V1_MC_Uncertainty_AK4PFPuppi.txt");
	gSystem->ExpandPathName(jecUncUrl);
	jecUnc_ = new JetCorrectionUncertainty(jecUncUrl.Data());
	//TString jer_file("${CMSSW_BASE}/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/data/Summer20UL16_JRV3_MC_PtResolution_AK4PFchs.txt");
	TString jer_file("${CMSSW_BASE}/src/TTbarCalib/data/Summer20UL16APV_JRV3_MC_PtResolution_AK4PFchs.txt");

	gSystem->ExpandPathName(jer_file);
	resolution = new JME::JetResolution(jer_file.Data());
	//TString jer_SF_file("${CMSSW_BASE}/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/data/Summer20UL16_JRV3_MC_SF_AK4PFchs.txt");
	//TString jer_SF_file("${CMSSW_BASE}/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/data/Summer20UL16APV_JRV3_MC_SF_AK4PFchs.txt");
	// gkole:
	TString jer_SF_file("${CMSSW_BASE}/src/TTbarCalib/data/Summer20UL16APV_JRV3_MC_SF_AK4PFchs.txt");
	gSystem->ExpandPathName(jer_SF_file);
	resolution_sf = new JME::JetResolutionScaleFactor(jer_SF_file.Data());
      }
  ~TTbarEventAnalysis(){}
  void setReadTTJetsGenWeights(bool readTTJetsGenWeights)     { readTTJetsGenWeights_=readTTJetsGenWeights; }
  void setTMVAWeightsBaseDir(TString url)                     { weightsDir_=url; gSystem->ExpandPathName(weightsDir_); }
  void addTriggerBit(Int_t bit,Int_t ch)                      { triggerBits_.push_back(std::pair<Int_t,Int_t>(bit,ch)); }
  void addVarForTMVA(TString varName)                         { tmvaVarNames_.push_back(varName); }
  void prepareOutput(TString outFile);
  Int_t checkFile(TString inFile);
  TH1F* readHistogram(const char* fileName, const char* histogramName);
  Int_t processFile(TString inFile,Float_t xsecWgt,Bool_t isData);
  void finalizeOutput(Float_t xsecWgt);
  
 private:
  JetCorrectionUncertainty *jecUnc_;
  JME::JetResolution *resolution;
  JME::JetResolutionScaleFactor *resolution_sf;
  std::pair<float,float> getTriggerEfficiency(int id1,float pt1,float eta1,int id2,float pt2,float eta2,int ch);
  std::pair<float,float> getTriggerScaleFactor(float pt1, float pt2, int ch, int trigger_index);
  std::pair<float,float> getLeptonIDScaleFactor(int id,float pt,float eta);
  std::pair<float,float> getElectronRECOScaleFactor(int id,float pt,float eta);
  std::pair<float,float> getMuonISOScaleFactor(int id,float pt,float eta);
  std::vector<float> getJetEnergyScales(float pt,float eta,float rawsf,float area,float rho);
  //std::vector<float> getJetResolutionScales(float pt, float eta, float genjpt);
  std::vector<float> getJERVariations(float pt, float eta, float genjpt, float JER_sf, float JER_sf_up, float JER_sf_down, float JER_mc);
  TH1F *puWgtGr_, *puWgtDownGr_, *puWgtUpGr_;
  bool readTTJetsGenWeights_;
  TString weightsDir_;
  std::vector<TString> tmvaVarNames_;
  TMVA::Reader *tmvaReader_;
  TFile *outF_;
  ULong64_t npv_;
  Int_t eventInfo_[3],ttbar_chan_, nSV,nTrack,Jet_nseltracks[100],Jet_CombIVF_N[100],Jet_SV_multi[100],Jet_nFirstSV[100],Jet_nLastSV[100],Jet_nFirstTrack[10000],Jet_nLastTrack[10000];
  Float_t SV_mass[100], SV_flight[100],Jet_Svx[10], SV_vtx_pt[10], Track_pt[10];
  Int_t SV_nTrk[100];
  Float_t Jet_SoftMuN[1000];
  Float_t Jet_SoftMu[1000];

  Float_t largest_SV_, largestSV_flightdistance_;
  Float_t nSVtracks_nocut_, nSVtracks_pass_DeepJet_WPL_, nSVtracks_pass_DeepJet_WPM_, nSVtracks_pass_DeepJet_WPT_, nSVtracks_pass_DeepCSV_WPL_, nSVtracks_pass_DeepCSV_WPM_, nSVtracks_pass_DeepCSV_WPT_;
  Float_t SV_mass_pass_nSVtracks2_, SV_mass_pass_nSVtracks3_, SV_mass_pass_nSVtracks4_, SV_mass_pass_nSVtracks5_, SV_mass_pass_nSVtracks6to10_;
  Float_t SV_mass_pass_DeepJetWPL_, SV_mass_pass_DeepJetWPM_, SV_mass_pass_DeepJetWPT_, SV_mass_pass_DeepCSVWPL_, SV_mass_pass_DeepCSVWPM_, SV_mass_pass_DeepCSVWPT_;
  Float_t SV_mass_pass_DeepJetWPM_nSVtracks2_, SV_mass_pass_DeepJetWPM_nSVtracks3_, SV_mass_pass_DeepJetWPM_nSVtracks4_, SV_mass_pass_DeepJetWPM_nSVtracks5_, SV_mass_pass_DeepJetWPM_nSVtracks6to10_;
  Float_t SV_mass_pass_DeepCSVWPM_nSVtracks2_, SV_mass_pass_DeepCSVWPM_nSVtracks3_, SV_mass_pass_DeepCSVWPM_nSVtracks4_, SV_mass_pass_DeepCSVWPM_nSVtracks5_, SV_mass_pass_DeepCSVWPM_nSVtracks6to10_;

  Float_t weight_[31];
  Int_t jetFlavour_[2],jetmult_,jetrank_;
  Float_t jetPt_[2],jetEta_[2];
  Float_t close_mlj_[5],close_deta_,close_dphi_,close_ptrel_,close_lj2ll_deta_, close_lj2ll_dphi_;
  Float_t far_mlj_, far_deta_, far_dphi_, far_ptrel_,far_lj2ll_deta_, far_lj2ll_dphi_;
  Float_t  j2ll_deta_,j2ll_dphi_;
  Float_t kinDisc_[5];
  Float_t jp_[2],svhe_[2],csv_[2];
  Float_t DeepCSVb_[2], DeepCSVc_[2], DeepCSVl_[2], DeepCSVbb_[2], DeepCSVcc_[2], DeepCSVbN_[2], DeepCSVcN_[2], DeepCSVlN_[2], DeepCSVbbN_[2], DeepCSVccN_[2], DeepCSVbP_[2], DeepCSVcP_[2], DeepCSVlP_[2], DeepCSVbbP_[2], DeepCSVccP_[2];
  Float_t DeepCSVBDisc_[2], DeepCSVBDiscN_[2], DeepCSVBDiscP_[2], DeepCSVCvsLDisc_[2], DeepCSVCvsLDiscN_[2], DeepCSVCvsLDiscP_[2], DeepCSVCvsBDisc_[2], DeepCSVCvsBDiscN_[2], DeepCSVCvsBDiscP_[2];
  Float_t DeepFlavourBDisc_[2], PNetBDisc_[2], ParTBDisc_[2], DeepFlavourCvsLDisc_[2], DeepFlavourCvsBDisc_[2];
  Float_t DeepFlavourB_[2], DeepFlavourBB_[2], DeepFlavourLEPB_[2];
  std::vector<std::pair<Int_t,Int_t> > triggerBits_;
  TTree *kinTree_,*ftmTree_,*evVarTree_;
  std::map<TString,TH1F *> histos_;

};

#endif
