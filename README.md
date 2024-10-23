# TTBarCalib Instructions
## Gouranga Kole (NTU)

The following instructions will explain practically how to perform the KIN method analysis. The instructions should provide you with all the information needed to go from collecting a list of samples required for this analysis and running the BTVNanoCommissioning to extracting the KIN method scale factors and uncertainties and creating the .csv files that are used in the different CMS analysis. Firstly we need to create a CMSSW working directory and env. Check which CMSSW to use for new campaigns and follow the setup instructions in the relevant github README:

```
https://github.com/cms-btv-pog/BTVNanoCommissioning
```
We first run the ``BTVNanoCommissioning`` to create ntuples for a TTbar analysis. It's not in the scope of this README to give detailed information on the ``BTVNanoCommissioning`` but one can find the relevant information following the github above or reading through the relevant code in that Git repository. These are what are then used as input to the TTbarCalib code used to create the flat ntuples. We then describe the two separate procedures that perform Kinematic fit method. However, firstly you will need to know where to find the centrally produced datasets for the campaign on which you are about to embark.
## Using DAS
CMS DAS service will help you to find the MC and data files for your scale factor campaign. Example command for Fall17 Production:
```
das_client.py --query="dataset dataset=/*/RunIII*/NANOAODSIM status=* " --limit=300
```

### Measuring X-Sections of Samples on McM / DAS client
See here for more detail:
```
https://twiki.cern.ch/twiki/bin/viewauth/CMS/HowToGenXSecAnalyzer#Automated_scripts_to_compute_the
```

For McM prepID input:
```
./calculateXSectionAndFilterEfficiency.sh -f datasets_mcm.txt  -m -n 1000000
```
Once the file has finished running you will see the following output:

Before matching = cross-section the output before any matching or filter.
After matching = cross-section after matching but before filter.
Filter efficiency = efficiency of any filter.
After filter = final cross-section.
### Filter Efficiencies
You can use the script from the twiki:
```
https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideSubgroupMC#Measure_filter_efficiencies_and
```
or just find your sample on McM e.g.
```
https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_test/B2G-RunIIFall17DRPremix-00045
```
To find the associated wmLHEGS in the chain (you basically need the LHE fragments):
```
https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_test/B2G-RunIIFall17wmLHEGS-00071
```
Click on the circle with the tick on it to get the test command. Copy and paste into a shell script and this should run. In the output look for the string "GenXsecAnalyzer".

## Creation of Ntuples Using the BTVNanoCommissioning
###Installation


MC and data ttbar_BTA are here below( Produced by Ming-Yan and Uttiya)
```
/eos/cms/store/group/phys_btag/milee/BTA_ttbar/Summer22/
/eos/cms/store/group/phys_btag/milee/BTA_ttbar/Summer22EE/
/eos/cms/store/group/phys_btag/milee/BTA_ttbar/Summer23/
/eos/cms/store/group/phys_btag/milee/BTA_ttbar/Summer23BPix/
```

###Downloading files to run on locally
If the files you wish to run on localy do not exits in the eos space, one can download them using xrootd tools. First, choose the file you want from the disk resident CMS data on a grid site. One can search for a dataset on DAS and find the '/stroe' tree path in the 'site' information. Now check the file is accessible:
```
xrdfs cms-xrd-global.cern.ch locate </store/pathtofile>
```
Now try to download it locally:
```
xrdcp -d 1 -f root://xrootd-cms.infn.it//<filepath> <local_file_path>
```

## Pileup estimation

This is done my Ming-Yan but I get weight file and used it.


## Creation of flat ntuples using TTbarCalib package
The creation of flat ntuples using the BTagAnalyzer outputs is done using the the runTTbarAnalysis.py script in the TTBarCalib package:
```
python runTTbarAnalysis.py -i /store/group/phys_btag/milee/BTA_ttbar/Summer23/ -o XXX/ -j data/XXX.json -n 50
```
IMPORTANT: ttbar samples is splitted to ensure the classifier can be evaluated on a statistically independent sample.
Currently splits sample 25/75

### Introduction to TTbarCalib package (update needed)
- Runs local analysis to produce the root files used in the efficiency measurement. MC will be weighted by cross section here.
- Option -n indicates how many threads should be used.
- 'condor_run_dir' contains scripts to launch jobs on condor (singular or multi-threaded)
- The first time the script will produce a pickle file with the weights to be used according to the number of files found, xsec specified in the json file. It is advised to run all samples on a single thread the first time you run (suggest running just one event) to create the aforementioned pickle files otherwise the code crashes (this part is not thread safe). Once the pickle files have been created, you can run on multiple threads.
- The inputs you need (from the BTagAnalyzer step) are usually stored somewhere in the common BTV eos space '/store/group/phys_btag/Commissioning/TTbar/'. If you didn't run the BtagAnalyzer, ask whoever did for the path to the ttbar datasets.
- runTTbarAnalysis.py creates a TTbarEventAnalysis object.
- Output stored in directory named after '-o' command line option.
- Input directory defined by '-i' option.
- Samples used as input can be found in .json file defined by -j option.
- Make sure that the number of root files equals the num of ntuple files. This is needed because sometimes the ntuples->rootfiles step fails.
- If you update the ttrees at any point, to ensure the xsec or lumi you have is correct, it's advised to remove by hand the pickle file, otherwise the necessary normalisations will not be recalculated accordingly and will be wrong.:
```
```
- Check corrections are up-to-date in TTbarEventAnalysis code


### Triggers and scale factors (NOT used but old (UL) information)
First thing to ensure is that inside the runTTbarAnalysis.py script, all the triggers in the TTbarSelectionProducer_cfi.py config are present and applied in the same way in MC as in data. In data, these have already been applied in the BTagAnalyzer step.

Inside TTbarEventAnalysis.cc one can find where the trigger requirement 'hasTrigger' is applied. The code will loop over the triggers in 'triggerBits' which is a list of pairs containing the index of the trigger in the aforementioned config and the channel it is relevant for (ttbar_chan = assigned channel from ID of selected leptons). This list is created in runTTbarAnalysis.py and affects the trigger selection so its very important to check the indices and channels assigned match the config.

ttbar_trigWord is a number that when converted to binary, has '1's in positions at the left push value of the index of the trigger in the config. This is done in the BTagAnalyzer step and the code is found in TTbarSelectionProducer. If we right push the same amount of times as the index of the trigger, the resulting binary number should have a 1 in the right most place (if that trigger fired) and the result of the & with 1 should be 1. We should be able to repeat this successfully for all the triggers that fired.

Each trigger we want to use is listed in the TriggerResults object that stores pass or fail result for each HLT path. Only triggers relevant for the ttbar decay channel (ttbar_chan = assigned channel from ID of selected leptons) assigned to the event are checked. If for the event, a trigger was accepted, we push a '1' back through the binary number N places, where N is the index of the trigger in the config, hence the importance of this index in later stages of the code.

Functionality exists to use single lepton triggers but would require the derivation of new scale factors. Currently just using eµ cross-triggers.

Find beneath an explanation of the operators used on trigger binary numbers.
```
x>>y
```
This right-shifts the bits x (in our case 'ttbar_trigWord') by y places (in our case y = triggerBits_[ibit].first). This is the equivalent of dividing x by 2^y.

One must also check the trigger SFs in TTbarEventAnalysis.cc function getTriggerScaleFactor() are up-to-date. The information on the cross-triggers can be found at https://twiki.cern.ch/twiki/bin/view/CMS/TopTrigger.

The script 'calculate_DilepTrig_SFs.py' can be used to extract the numbers from the files provided on the twiki and print out the code you need to add to the scripts.

### Lepton Selection Efficiencies and Scale factors
As objects we currently use:
- Medium 'cutBasedElectronID' for electron selection
- 'isTightMuon' = CutBasedIdTight muon selection

You may have to use the slightly outdated versions of the scale factors for preliminary results. Check here:

Electrons:
  https://twiki.cern.ch/twiki/bin/view/CMS/EgammaRunIIRecommendations
  https://twiki.cern.ch/twiki/bin/view/CMS/EgammaUL2016To2018
Muons:
  https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2Legacy

If you need to update these values there is a script already written 'egamma-SFs' that will produce a .txt with the SF's in. Similar script for muons.
Find the .root file for your lepton selection method (cut-based or MVA based) and your working point in the git repo.
Use the  python script to print out values of the pt and eta bins along with the errors that you should add to the appropriate function in TTbarEventAnalysis.cc.
  ```
  python calculate_EG_SFs.py > EG_mediumWP_eff_SFs.txt
  ```

### Jet resolution and energy corrections (new method is applied as new ntuples created by BTVNanoCommissioning)

Instances of the jet corrections and uncertainties can be found in TTbarEventAnalysis.h

JER recommendations and the <version for your data> can be found at:
  https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetResolution
  https://github.com/cms-jet/JRDatabase/tree/master/textFiles

JEC recommendations and the <version for your data> can be found at:
  https://twiki.cern.ch/twiki/bin/view/CMS/JECAnalysesRecommendations
  https://twiki.cern.ch/twiki/bin/view/CMS/JECUncertaintySources
  https://github.com/cms-jet/JECDatabase/tree/master/textFiles

Ensure latest and greatest corrections are present in code for both

### Pileup Corrections
Check you using the correct pileup re-weighting file: look for 'SetPUWeightTarget' variable
Very important to ensure otherwise weights can be quite small/large.
https://twiki.cern.ch/twiki/bin/view/CMS/PileupJSONFileforData#Recommended_cross_section

## Data Luminosity
To ensure you aren't missing any data and to find out the integrated luminosity to which you should be scaling MC. One can use the brilcalc tool as demonstrated beneath on the golden json for the 2017 dataset. If it's not 2016 you are looking for one can check here: /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/CollisionsXX/13TeV/ and look for the relevant .json.
```
export PATH=$HOME/.local/bin:/afs/cern.ch/cms/lumi/brilconda-1.1.7/bin:$PATH
brilcalc lumi -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt -u /pb
```
Output for 2017 data:
Total recorded luminosity: 41860.080

This number is the number to use as the 'lumi' argument when using the plotter.py script.

### Running local analysis for 2TagCount
After b-tag analyzer trees are produced, the first two steps of the 2TagCount analysis are the same.  The first is to run the analysis and make histograms (and trees):
```
python runTTbarAnalysis.py -i /store/group/phys_btag/Commissioning/TTbar/Moriond19_2018_StructuredDir/ --json data/samples_Run2018.json -o /tmp/MYUSERNAME/Moriond19_Run2018 -n 70 --doTwoTag 1
```

Re-organize plots and make data, mc comparison canvases (inclusive 2TagCount plots are in):
```
python plotter.py -i /tmp/MYUSERNAME/Moriond19_Run2018 --json data/samples_Run2018.json --lumi 58000
```

Take the 2TagCount histograms and compute efficiency scale factor comparing the following: 1)  b-tagging effiency for each working point for events with two b-jets at truth level (MC eff) and 2) data minus non-double b-jet MC divided by the number of MC events with two matched particle level b-jets:
```
python twoTag.py /tmp/MYUSERNAME/Moriond19_Run2018/plots/plotter.root
```
### Control plots
```
Update this part
```
 - Makes control plots and stores all in a ROOT file. Different options may be passed to filter plots, and show differently the plots.
- When merging rootples, be careful because if different sample names are called similarly (eg tW and atW)  you can risk doing double-merging.
- When scaling to a given luminosity (--lumi) ensure that you enter the luminosity in inverse picobarns i.e. 1000 pb-1 not 1 fb-1.
- The plotting macro also scale to cross-section. This is where the cross-section reported in the json file is used. The values used are those from the relevant XSDB entry.

### Train KinDiscriminator
```
 sh KIN_runClassifier.sh 
```
- After running the local analysis use the kin tree stored in the ttbar sample to train a kinematics discriminator of ttbar-system b-jets vs. non-b jets mostly from the ISR/FSR in the same events. The script compiles and runs KIN_trainClassifier.C which should be modified in case different trainings are required. 
- Rearrange new folders created by KIN_runClassifier.sh.
- Don't forget to split your ttbar sample to ensure you don't overtrain your classifier.
- The number of events used in the training has been optimised to get the best separation between signal and background while maintaining a flat background.
- One must be aware that changing this number can change the shape of the kinematic discriminant.
- In order to be able to store the input variable ranking, one needs to ensure to write the output log of the training to a log file so that it can be parsed later. The ranking information is not saved and cannot be accessed via the weights file because it iss deleted at the end of the training along with the BDT.

### Re-running flat ntuples to add mva training to TTrees
```
 python runTTbarAnalysis.py -i /store/group/phys_btag/Commissioning/TTbar/<ntuples_directory> -o <output_directory> -j data/<samples_list>.json --tmvaWgts data/KIN/ -n 4 
```
- Re-run the analysis to store the KIN discriminator value per jet and merge appropriately.
- Make sure that the number of root files equals the num of ntuples.
- Need to be careful about the number of nodes you run jobs on. If you use too many it can cause a errors and result in corrupt files.
- The condor scripts come in very useful here. Seeing as multithreading these jobs means they would all compete for the same resources i.e. trying to access the TMVA weights file.
- Using condor one can submit several jobs on different nodes on subsets of the input files. This will still take a while so its important we can use condor and set the job running in the appropriate queue. In this case I've used the 'tomorrow' queue as the jobs most likely finish within one day.

### Taggers
- The tagger json e.g. taggers_Run2017.json, can be found in the data directory.
- This file contains all the information on the taggers and working points you want to derive scale factors for.
- The current naming convention matches the code, if you want to change this you must ensure this is changed in all other relevant files.
- The working points are updated most campaigns so ensure you are synchronised with the other BTV calibration methods.
### Prepare and Perform Fit
```
python Templated_btagEffFitter.py --taggers data/<taggers_WP>.json --inDir <output of previous steps> --outDir fit_dir -n 500
```
- If you already have your templates, use the option '--recycleTemplates'
- Results of the fits will be stored in the pickle output file (efficiencies and the uncertainties).

- Also has option to run channel: ```--channels <121,-143,-169>```
- 121=ee,-143=emu,-169=mumu
- Make sure that all the ntuples are correctly merged: check their size to confirm that.
- Check that the names of the root file are properly saved, with the prefix MC13TeV_ and Data13TeV_.
- The fit is done in two parts:
  1.) Templated_btagEffFitter.py where the templates are prepared and the functions from TTbarSFbFitTools() are run to perform the fit.
  2.) TTbarSFbFitTools.cc where the Roofit implementation of fit actually is.
- As the method dictactes, these templates are filled with one entry per jet.
- Check in the 'lumi' value set correctly in TTbarSFbFitTools.h.
- Check labels on plots are correct in TTbarSFbFitTools.cc.
- Check the value of mistag rates defined in TTbarSFbFitTools.cc (tagger, WP, and jetpt dependent).
- There is also a script in condor_run_dir to submit jobs for this.
- Can be time consuming to keep running fits for each systematic. Simply need to ensure you seperate directories for the alternative TT samples, along with the data and nominal non-TT and one can add these directories to the list in the condor submission script.

### Post Fit Plots
- PostFit plots are made using ' PostFitter.sh '.
- Again check "LUMI=" line is correct.
- This is just a shell script that runs 'createSFbSummaryReport.py' which creates post-fit plots of efficiency measurements and sf values printed in a tex file Note along with a summary of the fit results.
- It may be the script stops because of some latex reason. If so hold return until the script finishes. Varying latex libraries on different machines means this can happen if a method is missing in the library you're using. The output should still be fine, this is an old script that needs updating.
- Among the other results, a csv.root files is produced at some points.
- The histos made are normalised to 1/pb
- In particular "b/c/other_pass0_slice0" contains the inclusive distributions, before any cuts on b tag discriminator WPs.
- So from (b/c/other)_ pass0_slice0->Integral() you can get the relative contribution of b, c, other cases.
- And from (b/c/other)_ pass0_slice0->DrawNormalized() you can compare the templates for the b, c, other cases.
- In general we expect the b and c templates to be comparable.

### SFb reports
- The sfb_report tables will only include the systematics that are in the pickle file (which it uses for input). This means they only include the systematics that can be evaluated via variations of the event weights. If you want to include the systematics that are evaluated using alternative samples, you need to add them by hand yourself at this point. For this you will need to rerun the nominal fits in alternative fit directories using the alternative samples.
- The alternative fitted SFb value is then used as the systematic variation i.e. the systematics are externalised.
- For this you can use SommaQuadratura.cc.
- Take the <Tagger_name>.csv file that contains your results.
- Remove the quotation marks from the values inside the file like before with the kin_calib.csv.
- Now run the grep command like before to get the values of the systematic variation e.g.
```
cat <Tagger_name>.csv | grep central | awk '{printf "%.12f\n", $11}'
```
- Copy these numbers into an appropriate array in SommaQuadratura.cc like before.
- At the end of the script you will also see some commented lines of the type:
```
cout << "~~~{\\small \\it total } & ${\\small" << toterr_up << "/ " << toterr_down << "}$ \\\\ " << endl;
```
- Uncomment/write your own version of this line to get the print out you require.
- Now simply add this to the sfb_report.tex document inside the appropriate table (paying attention to the working points / pt bins etc.).

## Additional Information Systematics
### ttbar weight systematics
Some useful reading:
1) Evaluating Theoretical Uncertainties with EDM event weights and which weights are stored in MC:
https://twiki.cern.ch/twiki/bin/view/CMS/ScaleAndPDFUncertaintiesFromEventWeights

2) Accessing the event weights from an EDM file with CMSSW:
https://twiki.cern.ch/twiki/bin/viewauth/CMS/LHEReaderCMSSW

3) Top systematics:
https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopSystematics#Factorization_and_renormalizatio

4) PSWeights:
https://github.com/cms-sw/cmssw/pull/21477

Ensure you have read these and are up-to-date with the run-of-the-mill systematics and think if there is anything new you should add.

In this code, generator weights are stored in the output from the crab jobs (jobs run by the BTagAnalyzer).
The weights are stored in a ttree branch called 'ttbar_w' which is filled @ around line 1460:
```
CMSSW_X_Y_Z/src/RecoBTag/PerformanceMeasurements/plugins/BTagAnalyzer.cc
```
### PDF weights in my sample

To know which integer or string corresponds to which weight use the package here:
```
git clone https://github.com/kdlong/TheoreticalUncertainties
```

It needs to be used inside a CMSSW environment but otherwise runs pretty well out of the box:
```
python getWeightInfoFromEDMFile.py -f /store/mc/RunIIFall17MiniAOD/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/94X_mc2017_realistic_v10-v1/60000/002E7FEA-16E0-E711-922D-0242AC130002.root
```

The printout will take the form:
```
<weightgroup combine="envelope" name="scale_variation">
<weight id="1001"> muR=1 muF=1 </weight>
<weight id="1002"> muR=1 muF=2 </weight>
<weight id="1003"> muR=1 muF=0.5 </weight>
<weight id="1004"> muR=2 muF=1 </weight>

<weightgroup combine="hessian" name="PDF_variation">
<weight id="2001"> PDF set = 260001 </weight>
<weight id="2002"> PDF set = 260002 </weight>
```

So for example, the command above gave me:

```
<weightgroup combine="envelope" name="scale_variation">
<weight id="1001"> lhapdf=306000 renscfact=1d0 facscfact=1d0 </weight>
<weight id="1002"> lhapdf=306000 renscfact=1d0 facscfact=2d0 </weight>
<weight id="1003"> lhapdf=306000 renscfact=1d0 facscfact=0.5d0 </weight>

<weightgroup combine="hessian" name="PDF_variation1">
<weight id="2000"> lhapdf=306000 </weight>
<weight id="2001"> lhapdf=306001 </weight>
<weight id="2002"> lhapdf=306002 </weight>
<weight id="2003"> lhapdf=306003 </weight>
<weight id="2004"> lhapdf=306004 </weight>
```
e.g. Systematic sample: https://cms-pdmv.cern.ch/mcm/requests?range=TOP-RunIIFall17wmLHEGS-00042,TOP-RunIIFall17wmLHEGS-00065&page=0&shown=127

### nonttXsec Systematic
30% cross-section normalisation uncertainty on non-tt background estimation.
30% was a carefully evaluated choice with Pedro Silva during the Moriond 17 version of the method. The major background is tW and 30% is conservative but on the pratical side unless a measurement of tW is made or we have a complete set of MCs with QCD scale variations at ME and PS levels for tW (which we don't), it's probably the value to use as it was used in other TOP analyses.
30% was a conservative variation of the non-ttbar backgrounds in the 2TagCount method based on the data-driven estimations: https://indico.cern.ch/event/548571/contributions/2231888/attachments/1304815/1950801/btag_ttbar_sf_06-07-2016.pdf (slide #4)

To run the non-tt normalisation xsection uncertainty, increase/decrease the x-sec for non-tt backgrounds by 30% in 'storeTools.py'. You can find the code to do so commented out at present. Simply uncomment the code and run TTbar analyser on non-tt MC directing the output to a new directory. hadd the samples as usual and collect in directory ready for fit. Copy the nominal data and ttbar outputs from the nominal output directory to this directory and run fit machinery.

## Tips 'n' tricks
### Debugging the BTagAnalyzer
Ensure all the versions of the various packages you are using are correct. You can do this by running the b-tag analyzer interactively from the 'ttbar/test' directory:
```
python -i runBTagAnalyzer_cfg.py defaults=Moriond18 useTTbarFilter=True runFatJets=True miniAOD=True
```
You can then run various process' e.g.
```
process.btagana
```
which will print to screen the EDAnalyzer that is run by that part of the process. The following commands will show you the version of DeepFlavour you are using:
```
process.selectedUpdatedPatJetsPFlow
process.updatedPatJetsTransientCorrectedPFlow
process.updatedPatJetsTransientCorrectedPFlow.discriminatorSources
process.pfDeepFlavourJetTagsPFlow
```
If you want to check the difference between the various defaults you can check the python scripts:
```
diff test/python/defaults/Moriond18.py test/python/defaults/Summer18.py
```
## Useful commands:
Print all files in directory, excluding those with "HIPM", in single list delimited by spaces:
```
find /eos/cms/store/group/phys_btag/Commissioning/TTbar//TTbar_UL16_StructuredDir/ -type d -name "*" -printf "%f\n" | grep -v "HIPM" | tr '\n' ' '
```
## CRAB
'allowNonValidInputDataset' - Add to config and you can run on non-valid datasets e.g.:
```
config_file.write('config.Data.allowNonValidInputDataset=True\n')
```
##  FIN
