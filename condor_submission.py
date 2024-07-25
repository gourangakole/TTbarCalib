import os
import optparse
import sys
import json

usage = 'python condor_submission.py -d dataset_name -f destination_folder'
parser = optparse.OptionParser(usage)
parser.add_option('-e', '--era', dest='era', type=str, default = '2017', help='Please enter an era')
parser.add_option('-f', '--folder', dest='folder', type=str, default = 'v5', help='Please enter a destination folder')
parser.add_option('-s', '--sample', dest='sample', type=str, default = 'TTto2L2Nu', help='Please put sample name')
(opt, args) = parser.parse_args()
uid = 0
username = str(os.environ.get('USER'))
inituser = str(os.environ.get('USER')[0])

def sub_writer(sample):
    f = open("condor.sub", "w")
    f.write("universe                = vanilla\n")
    f.write("Notification            = Error\n")
    f.write("should_transfer_files   = YES\n")
    f.write("when_to_transfer_output = ON_EXIT\n")
    f.write("transfer_input_files    = runner_"+sample+".sh \n")
    f.write("+JobFlavour             = \"tomorrow\"\n") # options are espresso = 20 minutes, microcentury = 1 hour, longlunch = 2 hours, workday = 8 hours, tomorrow = 1 day, testmatch = 3 days, nextweek     = 1 week
    f.write("executable              = runner_"+sample+".sh \n")
    f.write("output                  = condor/output/"+ sample + "_part.out\n")
    f.write("error                   = condor/error/"+ sample + "_part.err\n")
    f.write("log                     = condor/log/"+ sample + "_part.log\n")
    f.write("queue\n")

def runner_writer(sample, era, folder):
    f = open("runner_"+sample+".sh", "w")
    f.write("#!/bin/bash -e\n")
    f.write("echo 'TEST FIRST'\n")
    f.write("PWD=`pwd`\n")
    f.write("HOME=$PWD\n")
    f.write("echo $HOME\n")
    f.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
    f.write("cd " + str(os.getcwd()) + "\n")
    f.write("pwd \n")
    f.write("eval `scramv1 runtime -sh`\n")

    #main excutable
    f.write("python3 runTTbarAnalysis.py -i /store/group/phys_btag/milee/BTA_ttbar/" + str(era) + "/" + " -o /eos/cms/store/user/gkole/BTV_SF/" + str(folder) + "/ -j data/samples_"+str(era)+"_"+str(sample)+".json --tmvaWgts data/KIN_MVA_"+ str(era)+"_BDT -n 4 --nfiles 10000\n" )

if not os.path.exists("condor/output"):
    os.makedirs("condor/output")
if not os.path.exists("condor/error"):
    os.makedirs("condor/error")
if not os.path.exists("condor/log"):
    os.makedirs("condor/log")

# main to run

# this runs good
# runner_writer("TTto2L2Nu","Summer23BPix","24Jul2024")
# sub_writer("TTto2L2Nu")

# this runs good
# runner_writer("TTto2L2Nu_JES","Summer23BPix","24Jul2024")
# sub_writer("TTto2L2Nu_JES")

# this runs good
# runner_writer("TTto2L2Nu_JER","Summer23BPix","24Jul2024")
# sub_writer("TTto2L2Nu_JER")

# this runs good
# runner_writer("TTto2L2Nu_JER","Summer23BPix","24Jul2024")
# sub_writer("TTto2L2Nu_JER")

# this runs good
# runner_writer("TTto2L2Nu_CP5Tune","Summer23BPix","24Jul2024")
# sub_writer("TTto2L2Nu_CP5Tune")

# this runs good
# runner_writer("TTto2L2Nu_Hdamp","Summer23BPix","24Jul2024")
# sub_writer("TTto2L2Nu_Hdamp")

# this runs good
# runner_writer("TTto2L2Nu_TopMass","Summer23BPix","24Jul2024")
# sub_writer("TTto2L2Nu_TopMass")

# this runs good
runner_writer("MuonEG","Summer23BPix","24Jul2024")
sub_writer("MuonEG")


# os.system('condor_submit condor.sub')