//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Thu Nov 23 17:50:42 2023 by ROOT version 6.24/08
// from TTree ttree/
// found on file: 02d8fae2-3a63-486e-8390-ed818d5e19cd_0.root
//////////////////////////////////////////////////////////

#ifndef ttree_h
#define ttree_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.

class ttree {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   UInt_t          Run;
   ULong64_t       Evt;
   UInt_t          LumiBlock;
   Float_t         rho;
   Int_t           npvs;
   Int_t           npvsGood;
   Float_t         fixedGridRhoFastjetCentralCalo;
   Float_t         fixedGridRhoFastjetCentralChargedPileUp;
   Int_t           nPU;
   Float_t         nPUtrue;
   Float_t         pthat;
   Long64_t        ttbar_trigWord;
   Long64_t        ttbar_chan;
   Double_t        ttbar_ptweight;
   Float_t         ttbar_w;
   Float_t         ttbar_met_pt;
   Float_t         ttbar_met_phi;
   Int_t           nJet;
   Float_t         Jet_pt[10];   //[nJet]
   Float_t         Jet_eta[10];   //[nJet]
   Float_t         Jet_phi[10];   //[nJet]
   Float_t         Jet_mass[10];   //[nJet]
   Float_t         Jet_uncorrpt[10];   //[nJet]
   Bool_t          Jet_looseID[10];   //[nJet]
   Bool_t          Jet_tightID[10];   //[nJet]
   Bool_t          Jet_tightlepvetoID[10];   //[nJet]
   Float_t         Jet_area[10];   //[nJet]
   Float_t         Jet_DeepFlavourBDisc[10];   //[nJet]
   Float_t         Jet_DeepFlavourCvsLDisc[10];   //[nJet]
   Float_t         Jet_DeepFlavourCvsBDisc[10];   //[nJet]
   Float_t         Jet_PNetBDisc[10];   //[nJet]
   Float_t         Jet_PNetCvsLDisc[10];   //[nJet]
   Float_t         Jet_PNetCvsBDisc[10];   //[nJet]
   Float_t         Jet_ParTBDisc[10];   //[nJet]
   Float_t         Jet_ParTCvsLDisc[10];   //[nJet]
   Float_t         Jet_ParTCvsBDisc[10];   //[nJet]
   Short_t         Jet_partonFlavour[10];   //[nJet]
   UChar_t         Jet_hadronFlavour[10];   //[nJet]
   Long64_t        Jet_flavour[10];   //[nJet]
   Double_t        Jet_genpt[10];   //[nJet]
   Long64_t        Jet_flavourCleaned[10];   //[nJet]
   Int_t           nttbar_lep;
   Float_t         ttbar_lep_pt[2];   //[nttbar_lep]
   Float_t         ttbar_lep_eta[2];   //[nttbar_lep]
   Float_t         ttbar_lep_phi[2];   //[nttbar_lep]
   Float_t         ttbar_lep_m[2];   //[nttbar_lep]
   Int_t           ttbar_lep_ch[2];   //[nttbar_lep]
   Int_t           ttbar_lep_id[2];   //[nttbar_lep]
   Long64_t        ttbar_lep_gid[2];   //[nttbar_lep]
   Int_t           nttbar_gen;
   Float_t         ttbar_gen_pt[13];   //[nttbar_gen]
   Float_t         ttbar_gen_eta[13];   //[nttbar_gen]
   Float_t         ttbar_gen_phi[13];   //[nttbar_gen]
   Float_t         ttbar_gen_m[13];   //[nttbar_gen]
   Int_t           ttbar_gen_id[13];   //[nttbar_gen]
   Int_t           nttbar_lhe_pdf_w;
   Float_t         ttbar_lhe_pdf_w[103];   //[nttbar_lhe_pdf_w]
   Int_t           nttbar_lhe_scale_w;
   Float_t         ttbar_lhe_scale_w[9];   //[nttbar_lhe_scale_w]
   Int_t           nttbar_ps_w;
   Float_t         ttbar_ps_w[4];   //[nttbar_ps_w]

   // List of branches
   TBranch        *b_Run;   //!
   TBranch        *b_Evt;   //!
   TBranch        *b_LumiBlock;   //!
   TBranch        *b_rho;   //!
   TBranch        *b_npvs;   //!
   TBranch        *b_npvsGood;   //!
   TBranch        *b_fixedGridRhoFastjetCentralCalo;   //!
   TBranch        *b_fixedGridRhoFastjetCentralChargedPileUp;   //!
   TBranch        *b_nPU;   //!
   TBranch        *b_nPUtrue;   //!
   TBranch        *b_pthat;   //!
   TBranch        *b_ttbar_trigWord;   //!
   TBranch        *b_ttbar_chan;   //!
   TBranch        *b_ttbar_ptweight;   //!
   TBranch        *b_ttbar_w;   //!
   TBranch        *b_ttbar_met_pt;   //!
   TBranch        *b_ttbar_met_phi;   //!
   TBranch        *b_nJet;   //!
   TBranch        *b_Jet_pt;   //!
   TBranch        *b_Jet_eta;   //!
   TBranch        *b_Jet_phi;   //!
   TBranch        *b_Jet_mass;   //!
   TBranch        *b_Jet_uncorrpt;   //!
   TBranch        *b_Jet_looseID;   //!
   TBranch        *b_Jet_tightID;   //!
   TBranch        *b_Jet_tightlepvetoID;   //!
   TBranch        *b_Jet_area;   //!
   TBranch        *b_Jet_DeepFlavourBDisc;   //!
   TBranch        *b_Jet_DeepFlavourCvsLDisc;   //!
   TBranch        *b_Jet_DeepFlavourCvsBDisc;   //!
   TBranch        *b_Jet_PNetBDisc;   //!
   TBranch        *b_Jet_PNetCvsLDisc;   //!
   TBranch        *b_Jet_PNetCvsBDisc;   //!
   TBranch        *b_Jet_ParTBDisc;   //!
   TBranch        *b_Jet_ParTCvsLDisc;   //!
   TBranch        *b_Jet_ParTCvsBDisc;   //!
   TBranch        *b_Jet_partonFlavour;   //!
   TBranch        *b_Jet_hadronFlavour;   //!
   TBranch        *b_Jet_flavour;   //!
   TBranch        *b_Jet_genpt;   //!
   TBranch        *b_Jet_flavourCleaned;   //!
   TBranch        *b_nttbar_lep;   //!
   TBranch        *b_ttbar_lep_pt;   //!
   TBranch        *b_ttbar_lep_eta;   //!
   TBranch        *b_ttbar_lep_phi;   //!
   TBranch        *b_ttbar_lep_m;   //!
   TBranch        *b_ttbar_lep_ch;   //!
   TBranch        *b_ttbar_lep_id;   //!
   TBranch        *b_ttbar_lep_gid;   //!
   TBranch        *b_nttbar_gen;   //!
   TBranch        *b_ttbar_gen_pt;   //!
   TBranch        *b_ttbar_gen_eta;   //!
   TBranch        *b_ttbar_gen_phi;   //!
   TBranch        *b_ttbar_gen_m;   //!
   TBranch        *b_ttbar_gen_id;   //!
   TBranch        *b_nttbar_lhe_pdf_w;   //!
   TBranch        *b_ttbar_lhe_pdf_w;   //!
   TBranch        *b_nttbar_lhe_scale_w;   //!
   TBranch        *b_ttbar_lhe_scale_w;   //!
   TBranch        *b_nttbar_ps_w;   //!
   TBranch        *b_ttbar_ps_w;   //!

   ttree(TTree *tree=0);
   virtual ~ttree();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif

#ifdef ttree_cxx
ttree::ttree(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("02d8fae2-3a63-486e-8390-ed818d5e19cd_0.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("02d8fae2-3a63-486e-8390-ed818d5e19cd_0.root");
      }
      TDirectory * dir = (TDirectory*)f->Get("02d8fae2-3a63-486e-8390-ed818d5e19cd_0.root:/btagana");
      dir->GetObject("ttree",tree);

   }
   Init(tree);
}

ttree::~ttree()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t ttree::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t ttree::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}

void ttree::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("Run", &Run, &b_Run);
   fChain->SetBranchAddress("Evt", &Evt, &b_Evt);
   fChain->SetBranchAddress("LumiBlock", &LumiBlock, &b_LumiBlock);
   fChain->SetBranchAddress("rho", &rho, &b_rho);
   fChain->SetBranchAddress("npvs", &npvs, &b_npvs);
   fChain->SetBranchAddress("npvsGood", &npvsGood, &b_npvsGood);
   fChain->SetBranchAddress("fixedGridRhoFastjetCentralCalo", &fixedGridRhoFastjetCentralCalo, &b_fixedGridRhoFastjetCentralCalo);
   fChain->SetBranchAddress("fixedGridRhoFastjetCentralChargedPileUp", &fixedGridRhoFastjetCentralChargedPileUp, &b_fixedGridRhoFastjetCentralChargedPileUp);
   fChain->SetBranchAddress("nPU", &nPU, &b_nPU);
   fChain->SetBranchAddress("nPUtrue", &nPUtrue, &b_nPUtrue);
   fChain->SetBranchAddress("pthat", &pthat, &b_pthat);
   fChain->SetBranchAddress("ttbar_trigWord", &ttbar_trigWord, &b_ttbar_trigWord);
   fChain->SetBranchAddress("ttbar_chan", &ttbar_chan, &b_ttbar_chan);
   fChain->SetBranchAddress("ttbar_ptweight", &ttbar_ptweight, &b_ttbar_ptweight);
   fChain->SetBranchAddress("ttbar_w", &ttbar_w, &b_ttbar_w);
   fChain->SetBranchAddress("ttbar_met_pt", &ttbar_met_pt, &b_ttbar_met_pt);
   fChain->SetBranchAddress("ttbar_met_phi", &ttbar_met_phi, &b_ttbar_met_phi);
   fChain->SetBranchAddress("nJet", &nJet, &b_nJet);
   fChain->SetBranchAddress("Jet_pt", Jet_pt, &b_Jet_pt);
   fChain->SetBranchAddress("Jet_eta", Jet_eta, &b_Jet_eta);
   fChain->SetBranchAddress("Jet_phi", Jet_phi, &b_Jet_phi);
   fChain->SetBranchAddress("Jet_mass", Jet_mass, &b_Jet_mass);
   fChain->SetBranchAddress("Jet_uncorrpt", Jet_uncorrpt, &b_Jet_uncorrpt);
   fChain->SetBranchAddress("Jet_looseID", Jet_looseID, &b_Jet_looseID);
   fChain->SetBranchAddress("Jet_tightID", Jet_tightID, &b_Jet_tightID);
   fChain->SetBranchAddress("Jet_tightlepvetoID", Jet_tightlepvetoID, &b_Jet_tightlepvetoID);
   fChain->SetBranchAddress("Jet_area", Jet_area, &b_Jet_area);
   fChain->SetBranchAddress("Jet_DeepFlavourBDisc", Jet_DeepFlavourBDisc, &b_Jet_DeepFlavourBDisc);
   fChain->SetBranchAddress("Jet_DeepFlavourCvsLDisc", Jet_DeepFlavourCvsLDisc, &b_Jet_DeepFlavourCvsLDisc);
   fChain->SetBranchAddress("Jet_DeepFlavourCvsBDisc", Jet_DeepFlavourCvsBDisc, &b_Jet_DeepFlavourCvsBDisc);
   fChain->SetBranchAddress("Jet_PNetBDisc", Jet_PNetBDisc, &b_Jet_PNetBDisc);
   fChain->SetBranchAddress("Jet_PNetCvsLDisc", Jet_PNetCvsLDisc, &b_Jet_PNetCvsLDisc);
   fChain->SetBranchAddress("Jet_PNetCvsBDisc", Jet_PNetCvsBDisc, &b_Jet_PNetCvsBDisc);
   fChain->SetBranchAddress("Jet_ParTBDisc", Jet_ParTBDisc, &b_Jet_ParTBDisc);
   fChain->SetBranchAddress("Jet_ParTCvsLDisc", Jet_ParTCvsLDisc, &b_Jet_ParTCvsLDisc);
   fChain->SetBranchAddress("Jet_ParTCvsBDisc", Jet_ParTCvsBDisc, &b_Jet_ParTCvsBDisc);
   fChain->SetBranchAddress("Jet_partonFlavour", Jet_partonFlavour, &b_Jet_partonFlavour);
   fChain->SetBranchAddress("Jet_hadronFlavour", Jet_hadronFlavour, &b_Jet_hadronFlavour);
   fChain->SetBranchAddress("Jet_flavour", Jet_flavour, &b_Jet_flavour);
   fChain->SetBranchAddress("Jet_genpt", Jet_genpt, &b_Jet_genpt);
   fChain->SetBranchAddress("Jet_flavourCleaned", Jet_flavourCleaned, &b_Jet_flavourCleaned);
   fChain->SetBranchAddress("nttbar_lep", &nttbar_lep, &b_nttbar_lep);
   fChain->SetBranchAddress("ttbar_lep_pt", ttbar_lep_pt, &b_ttbar_lep_pt);
   fChain->SetBranchAddress("ttbar_lep_eta", ttbar_lep_eta, &b_ttbar_lep_eta);
   fChain->SetBranchAddress("ttbar_lep_phi", ttbar_lep_phi, &b_ttbar_lep_phi);
   fChain->SetBranchAddress("ttbar_lep_m", ttbar_lep_m, &b_ttbar_lep_m);
   fChain->SetBranchAddress("ttbar_lep_ch", ttbar_lep_ch, &b_ttbar_lep_ch);
   fChain->SetBranchAddress("ttbar_lep_id", ttbar_lep_id, &b_ttbar_lep_id);
   fChain->SetBranchAddress("ttbar_lep_gid", ttbar_lep_gid, &b_ttbar_lep_gid);
   fChain->SetBranchAddress("nttbar_gen", &nttbar_gen, &b_nttbar_gen);
   fChain->SetBranchAddress("ttbar_gen_pt", ttbar_gen_pt, &b_ttbar_gen_pt);
   fChain->SetBranchAddress("ttbar_gen_eta", ttbar_gen_eta, &b_ttbar_gen_eta);
   fChain->SetBranchAddress("ttbar_gen_phi", ttbar_gen_phi, &b_ttbar_gen_phi);
   fChain->SetBranchAddress("ttbar_gen_m", ttbar_gen_m, &b_ttbar_gen_m);
   fChain->SetBranchAddress("ttbar_gen_id", ttbar_gen_id, &b_ttbar_gen_id);
   fChain->SetBranchAddress("nttbar_lhe_pdf_w", &nttbar_lhe_pdf_w, &b_nttbar_lhe_pdf_w);
   fChain->SetBranchAddress("ttbar_lhe_pdf_w", ttbar_lhe_pdf_w, &b_ttbar_lhe_pdf_w);
   fChain->SetBranchAddress("nttbar_lhe_scale_w", &nttbar_lhe_scale_w, &b_nttbar_lhe_scale_w);
   fChain->SetBranchAddress("ttbar_lhe_scale_w", ttbar_lhe_scale_w, &b_ttbar_lhe_scale_w);
   fChain->SetBranchAddress("nttbar_ps_w", &nttbar_ps_w, &b_nttbar_ps_w);
   fChain->SetBranchAddress("ttbar_ps_w", ttbar_ps_w, &b_ttbar_ps_w);
   Notify();
}

Bool_t ttree::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void ttree::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t ttree::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef ttree_cxx
