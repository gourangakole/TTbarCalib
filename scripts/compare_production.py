#############################
#   compare_production.py
#############################
#  Joshuha Thomas-Wilsker
#   CERN, IHEP Beijing
#############################
# Short python script that
# compares production files
# sizes stored on eos and
# gives warnings if it finds
# any differences.
#############################
import sys
import os
import re

def make_file_list_dic(temp_eos_ls_cmd=""):
    file_list_dic={}
    temp_os_output = os.popen(temp_eos_ls_cmd).read()
    file_list = temp_os_output.splitlines()
    print('Adding %i files from directory to dictionary' % len(file_list))
    for x in xrange(len(file_list)):
        file_info = file_list[x]
        file_list_labels = re.search('JetTree(.*?).root', file_info).group(1)
        start_of_target_string = file_info[39:]
        file_info_size = start_of_target_string[:7]
        file_list_dic[file_list_labels] = file_info_size.strip()
    return file_list_dic

def check_total_of_split_sample(dirkey, dirval):
    combined_dic = {}
    dirval_training = dirval + '_training'
    dirval_testing = dirval + '_testing'
    temp_eos_ls_cmd_training = 'eos ls -lh /store/group/phys_btag/Commissioning/TTbar/TTbar_UL18_StructuredDir/'+dirval_training+'/'
    temp_eos_ls_cmd_testing = 'eos ls -lh /store/group/phys_btag/Commissioning/TTbar/TTbar_UL18_StructuredDir/'+dirval_testing+'/'
    #print('Training directory: ', temp_eos_ls_cmd_training)
    #print('Testing directory: ', temp_eos_ls_cmd_testing)
    file_dic_training = make_file_list_dic(temp_eos_ls_cmd_training)
    print('%s files from %s added to training dictionary' % (len(file_dic_training), temp_eos_ls_cmd_training) )
    file_dic_testing = make_file_list_dic(temp_eos_ls_cmd_testing)
    print('%s files from %s added to testing dictionary' % (len(file_dic_testing), temp_eos_ls_cmd_testing) )
    combined_dic = file_dic_training.copy()
    combined_dic.update(file_dic_testing)
    print('%i combined (training + testing) dictionary entries ' % len(combined_dic))
    return combined_dic

def main():
    # Need to check nominal ttbar samples independently. Samples have been split into training and testing directories.
    dir_translator = {
    #"TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_DL",
    #"TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_SL",
    #"TTToHadronic_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_AH",
    #"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8" : "MC13TeV_DYJetsToLL-M-50",
    #"ST_tW_antitop_5f_DS_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_atW",
    #"ST_tW_top_5f_DS_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_tW",
    #"TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_DL_hdampDOWN",
    #"TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_DL_hdampUP",
    #"TTTo2L2Nu_mtop171p5_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_DL_mtop171p5",
    #"TTTo2L2Nu_mtop173p5_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_DL_mtop173p5",
    #"TTTo2L2Nu_TuneCP5down_13TeV-powheg-pythia8" : "MC13TeV_TTJets_DL_TuneCP5down",
    #"TTTo2L2Nu_TuneCP5up_13TeV-powheg-pythia8" : "MC13TeV_TTJets_DL_TuneCP5up",
    #"TTToHadronic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_AH_hdampDOWN",
    #"TTToHadronic_hdampUP_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_AH_hdampUP",
    #"TTToHadronic_mtop171p5_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_AH_mtop171p5",
    #"TTToHadronic_mtop173p5_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_AH_mtop173p5",
    #"TTToHadronic_TuneCP5up_13TeV-powheg-pythia8" : "MC13TeV_TTJets_AH_TuneCP5up",
    #"TTToHadronic_TuneCP5down_13TeV-powheg-pythia8" : "MC13TeV_TTJets_AH_TuneCP5down",
    #"TTToSemiLeptonic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_SL_hdampDOWN",
    #"TTToSemiLeptonic_hdampUP_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_SL_hdampUP",
    #"TTToSemiLeptonic_mtop171p5_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_SL_mtop171p5",
    #"TTToSemiLeptonic_mtop173p5_TuneCP5_13TeV-powheg-pythia8" : "MC13TeV_TTJets_SL_mtop173p5",
    #"TTToSemiLeptonic_TuneCP5down_13TeV-powheg-pythia8" : "MC13TeV_TTJets_SL_TuneCP5down",
    #"TTToSemiLeptonic_TuneCP5up_13TeV-powheg-pythia8" : "MC13TeV_TTJets_SL_TuneCP5up",
    #"WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8" : "MC13TeV_WJetsToLNu",
    #"WW_TuneCP5_13TeV-pythia8" : "MC13TeV_WW",
    #"WZ_TuneCP5_13TeV-pythia8" : "MC13TeV_WZ",
    #"ZZ_TuneCP5_13TeV-pythia8" : "MC13TeV_ZZ",
    "MuonEG_RunA" : "crab_Data13TeV_MuonEG_UL18A",
    "MuonEG_RunB" : "crab_Data13TeV_MuonEG_UL18B",
    "MuonEG_RunC" : "crab_Data13TeV_MuonEG_UL18C",
    "MuonEG_RunD" : "crab_Data13TeV_MuonEG_UL18D"
    }

    for dir_key, dir_val in dir_translator.items():
        print("****** Comparing files copied from: %s ******" % (dir_key))
        # Create file dictionary using structured/copy directory
        file_list_1_dic = {}
        temp_eos_ls_cmd_1 = ''
        if "MuonEG" in dir_key:
            temp_eos_ls_cmd_1 = 'eos ls -lh /store/group/phys_btag/Commissioning/TTbar/TTbar_UL18_StructuredDir/crab_'+dir_val+'/'
            file_list_1_dic = make_file_list_dic(temp_eos_ls_cmd_1)
            print('%s files from %s added to dictionary 1' % (len(file_list_1_dic),temp_eos_ls_cmd_1))
        elif "MC13TeV_TTJets" in dir_val:
            # If ttbar sample, combine the divided training and testing sample into one dictionary.
            file_list_1_dic = check_total_of_split_sample(dir_key,dir_val)
        else:
            temp_eos_ls_cmd_1 = 'eos ls -lh /store/group/phys_btag/Commissioning/TTbar/TTbar_UL18_StructuredDir/'+dir_val+'/'
            file_list_1_dic = make_file_list_dic(temp_eos_ls_cmd_1)
            print('%s files from %s added to dictionary 1' % (len(file_list_1_dic),temp_eos_ls_cmd_1))

        # Now create dictionary for original crab output directory
        if "MuonEG" in dir_key:
            temp_eos_ls_cmd_subdir = 'eos ls /store/group/phys_btag/Commissioning/TTbar/TTbar_UL18/'+dir_key[:6]+'/crab_'+dir_val
        #elif "_TuneCP5_13TeV-powheg-pythia8" in dir_key:
        #    temp_eos_ls_cmd_subdir = 'eos ls /store/group/phys_btag/Commissioning/TTbar/TTbar_UL18/'+dir_key[:-8]+'/crab_'+dir_val
        else:
            temp_eos_ls_cmd_subdir = 'eos ls /store/group/phys_btag/Commissioning/TTbar/TTbar_UL18/'+dir_key+'/crab_'+dir_val

        subdir_1 = os.popen(temp_eos_ls_cmd_subdir).read()
        subdir_1 = subdir_1.strip()
        temp_eos_ls_cmd_subdir = os.path.join(temp_eos_ls_cmd_subdir,subdir_1)
        print("Checking for sudirectories in: ", temp_eos_ls_cmd_subdir)
        temp_os_output = os.popen(temp_eos_ls_cmd_subdir).read()
        file_list_subdirs = temp_os_output.splitlines()
        file_list_2_combined_dic = {}
        for subdir_2 in file_list_subdirs:
            subdir_2 = subdir_2.strip()
            if "MuonEG" in dir_key:
                temp_eos_ls_cmd_2 = os.path.join('/store/group/phys_btag/Commissioning/TTbar/TTbar_UL18/',dir_key[:6],'crab_'+dir_val,subdir_1,subdir_2)
            else:
                temp_eos_ls_cmd_2 = os.path.join('/store/group/phys_btag/Commissioning/TTbar/TTbar_UL18/',dir_key,'crab_'+dir_val,subdir_1,subdir_2)
            temp_eos_ls_cmd_2 = "eos ls -lh "+temp_eos_ls_cmd_2
            #temp_os_output_2 = os.popen(temp_eos_ls_cmd_2).read()
            file_list_2_combined_dic.update(make_file_list_dic(temp_eos_ls_cmd_2))
            print('%s files from %s added to dictionary 2' % (len(file_list_2_combined_dic),temp_eos_ls_cmd_2))
            #make_file_list_dic(file_list_2_dic, temp_eos_ls_cmd_2)
            #print('%s files from %s added to dictionary 2' % (len(file_list_2_dic),temp_eos_ls_cmd_2))

        logfile1_filesizes = []
        logfile2_filesizes = []
        if len(file_list_1_dic) != len(file_list_2_combined_dic):
            print('WARNING! %i files in dictionary 1, %i in dictionary 2' % (len(file_list_1_dic),len(file_list_2_combined_dic)))
        else:
            print('Ok, good start: dictionary 1 = %i , dictionary 2 = %i' % (len(file_list_1_dic), len(file_list_2_combined_dic)))

        size_errors = False
        for key, value in file_list_1_dic.items():
            value_in_file2 = file_list_2_combined_dic.get(key)
            if value_in_file2 == None:
                print('Key: ', key, ' not found in directory 2')
                size_errors = True
                continue
            elif value != value_in_file2:
                print('File size in directory 1: ', value, ', file size in directory 2: ', value_in_file2)
                exit(-1)
                size_errors = True
        if size_errors == False:
            print('Seems files in directories match. Copy succeeded!')
    exit(0)


"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())
