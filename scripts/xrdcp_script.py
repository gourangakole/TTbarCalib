###########################################
#          xrdcp_script.py
###########################################
#          Joshuha Thomas-Wilsker
#           CERN, IHEP Beijing
###########################################
# Short script to copy files from an old
# directory structure on EOS to a new
# directory struture also on EOS which is
# much simpler in the context of the BTV
# ZJets analysis measurements.
###########################################
# Ensure you ahve a valid grid proxy:
# $>voms-proxy-init --voms cms
# and have set up the cmssw environment of
# your choice before running this script.
###########################################

import os, subprocess
import os.path

redirector_name = "root://xrootd-cms.infn.it//"

#Force use of IPv4 (temporary issues with IPv6 on lxplus)
os.popen('export XRD_NETWORKSTACK=IPv4')

# Original directory name on EOS and subsequent directories
# for individual samples.
original_directory = '/store/group/phys_btag/Commissioning/TTbar/TTbar_UL17/'
original_subdir_list = [
#'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
#'TTToHadronic_TuneCP5_13TeV-powheg-pythia8',
#'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8',
#'ST_tW_top_5f_DS_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8',
#'ST_tW_antitop_5f_DS_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8',
#'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
#'WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8',
#'WW_TuneCP5_13TeV-pythia8',
#'WZ_TuneCP5_13TeV-pythia8',
#'ZZ_TuneCP5_13TeV-pythia8'
'TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8',
'TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8',
'TTTo2L2Nu_mtop171p5_TuneCP5_13TeV-powheg-pythia8',
'TTTo2L2Nu_mtop173p5_TuneCP5_13TeV-powheg-pythia8',
'TTTo2L2Nu_TuneCP5down_13TeV-powheg-pythia8',
'TTTo2L2Nu_TuneCP5_erdON_13TeV-powheg-pythia8',
'TTTo2L2Nu_TuneCP5up_13TeV-powheg-pythia8',
'TTToHadronic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8',
'TTToHadronic_hdampUP_TuneCP5_13TeV-powheg-pythia8',
'TTToHadronic_mtop171p5_TuneCP5_13TeV-powheg-pythia8',
'TTToHadronic_mtop173p5_TuneCP5_13TeV-powheg-pythia8',
'TTToHadronic_TuneCP5down_13TeV-powheg-pythia8',
'TTToHadronic_TuneCP5_erdON_13TeV-powheg-pythia8',
'TTToHadronic_TuneCP5up_13TeV-powheg-pythia8',
'TTToSemiLeptonic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8',
'TTToSemiLeptonic_hdampUP_TuneCP5_13TeV-powheg-pythia8',
'TTToSemiLeptonic_mtop171p5_TuneCP5_13TeV-powheg-pythia8',
'TTToSemiLeptonic_mtop173p5_TuneCP5_13TeV-powheg-pythia8',
'TTToSemiLeptonic_TuneCP5down_13TeV-powheg-pythia8',
'TTToSemiLeptonic_TuneCP5_erdON_13TeV-powheg-pythia8',
'TTToSemiLeptonic_TuneCP5up_13TeV-powheg-pythia8'
]

# EOS directory with new structure to store output (easier for runTTbarAnalysis packages to use).
new_directory = '/eos/cms/store/group/phys_btag/Commissioning/TTbar/TTbar_UL17_StructuredDir/'
new_subdir_list = [
#'MC13TeV_TTJets_DL',
#'MC13TeV_TTJets_AH',
#'MC13TeV_TTJets_SL',
#'MC13TeV_atW',
#'MC13TeV_tW',
#'MC13TeV_DYJetsToLL-M-50',
#'MC13TeV_WJetsToLNu',
#'MC13TeV_WW',
#'MC13TeV_WZ',
#'MC13TeV_ZZ',
'MC13TeV_TTJets_DL_hdampDOWN',
'MC13TeV_TTJets_DL_hdampUP',
'MC13TeV_TTJets_DL_mtop171p5',
'MC13TeV_TTJets_DL_mtop173p5',
'MC13TeV_TTJets_DL_TuneCP5down',
'MC13TeV_TTJets_DL_TuneCP5_erdON',
'MC13TeV_TTJets_DL_TuneCP5up',
'MC13TeV_TTJets_AH_hdampDOWN',
'MC13TeV_TTJets_AH_hdampUP',
'MC13TeV_TTJets_AH_mtop171p5',
'MC13TeV_TTJets_AH_mtop173p5',
'MC13TeV_TTJets_AH_TuneCP5down',
'MC13TeV_TTJets_AH_TuneCP5_erdON',
'MC13TeV_TTJets_AH_TuneCP5up',
'MC13TeV_TTJets_SL_hdampDOWN',
'MC13TeV_TTJets_SL_hdampUP',
'MC13TeV_TTJets_SL_mtop171p5',
'MC13TeV_TTJets_SL_mtop173p5',
'MC13TeV_TTJets_SL_TuneCP5down',
'MC13TeV_TTJets_SL_TuneCP5_erdON',
'MC13TeV_TTJets_SL_TuneCP5up'
]

# Ensure the above lists of samples in old and new directory match.
if len(original_subdir_list) != len(new_subdir_list):
    print 'Warning!!!! Old samples list and new samples list do not match in size!'
    print '# original list = ', len(original_subdir_list)
    print '# new list = ', len(new_subdir_list)

# Make the new EOS directory.
eos_mkdir_cmd = 'eos mkdir '
temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory
os.system(temp_eos_mkdir_cmd)

# Sample counter to ensure correct new directory name is used.
sample_counter = 0

# Loop over list of old sample directories
for subdir in original_subdir_list:
    full_pathname = ''
    full_pathname = os.path.join(original_directory,subdir)

    ttbar_sysflag = False
    ttbar_systematics_list = ['hdampUP','hdampDOWN','TuneCP5up','TuneCP5down','mtop171p5','mtop173p5','TuneCP5_erdON']
    for ttsyst in ttbar_systematics_list:
        if ttsyst in full_pathname:
            ttbar_sysflag=True

    # Create new directroy struture.
    # If: TTbar samples, need to split simulation. Half used to train BDT half for testing/results.
    # Else: Proceed as normal.
    if 'TTTo' in subdir and ttbar_sysflag == False:
        temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory + new_subdir_list[sample_counter] + '_training'
        print temp_eos_mkdir_cmd
        os.system(temp_eos_mkdir_cmd)
        temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory + new_subdir_list[sample_counter] + '_testing'
        print temp_eos_mkdir_cmd
        os.system(temp_eos_mkdir_cmd)
    else:
        temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory + new_subdir_list[sample_counter]
        print temp_eos_mkdir_cmd
        os.system(temp_eos_mkdir_cmd)

    # Construct eos path by iterating down through old directory structure.
    # Needed for copy command.
    eos_ls_cmd = 'eos ls '
    eos_dir = '/eos/cms/'+full_pathname
    temp_eos_ls_cmd = eos_ls_cmd + eos_dir

    temp_os_output = os.popen(temp_eos_ls_cmd).read()
    #subdir_2 = "".join(temp_os_output.split())
    subdir_2 = temp_os_output.splitlines()

    for temp_dir_2 in subdir_2:
        #full_pathname = os.path.join(full_pathname,subdir_2)
        full_pathname = os.path.join(original_directory,subdir)
        full_pathname = os.path.join(full_pathname,temp_dir_2)
        temp_eos_ls_cmd = eos_ls_cmd + full_pathname
        print 'temp_eos_ls_cmd ', temp_eos_ls_cmd
        temp_os_output = os.popen(temp_eos_ls_cmd).read()
        subdir_3 = temp_os_output.split()
        for temp_dir_3 in subdir_3:
            print 'temp_dir_3: ' , temp_dir_3
            temp3_full_pathname = os.path.join(full_pathname,temp_dir_3)
            temp_eos_ls_cmd = eos_ls_cmd + temp3_full_pathname

            # WARNING: OK, in this subdirectory we have two further directories.
            #          Can split returned string using new line delimiter, into
            #          an array of strings of directory names.
            temp_os_output = os.popen(temp_eos_ls_cmd).read()
            subdir_4 = temp_os_output.splitlines()

            print 'subdir_4; ', subdir_4

            for temp_dir in subdir_4:
                temp4_full_pathname = os.path.join(temp3_full_pathname,temp_dir)
                temp_eos_ls_cmd = eos_ls_cmd + temp4_full_pathname
                temp_os_output = os.popen(temp_eos_ls_cmd).read()
                file_list = temp_os_output.splitlines()

                # Construct and initiate xrdcp command.
                # If: TTbar sample, copy half the files into training and half into testing directory.
                # Else: all files go into single new directory.
                if 'TTTo' in subdir and ttbar_sysflag == False:
                    ttbar_half_index = (len(file_list)/2)
                    training_ttbar_files_list = file_list[ 0:ttbar_half_index ]
                    testing_ttbar_files_list = file_list[ ttbar_half_index:len(file_list) ]
                    print 'train files list'
                    print training_ttbar_files_list
                    print 'test files list:'
                    print testing_ttbar_files_list
                    for temp_file in training_ttbar_files_list:
                        #temp_file = training_ttbar_files_list[x]
                        if '.root' not in temp_file:
                            continue
                        temp_full_path_to_file = os.path.join(temp4_full_pathname,temp_file)
                        new_subdirectory_name = new_subdir_list[sample_counter] + "_training/"
                        #command_line = 'xrdcp ' + redirector_name + temp_full_path_to_file + ' ' + new_directory + new_subdirectory_name + temp_file
                        command_line = 'xrdcp'
                        command_line_arg1 = redirector_name + temp_full_path_to_file
                        command_line_arg2 = new_directory + new_subdirectory_name + temp_file
                        full_command_line = command_line + ' ' + command_line_arg1 + ' ' + command_line_arg2
                        print full_command_line
                        # If file already exists, go to next file.
                        if os.path.isfile(command_line_arg2):
                            continue
                        ##os.popen(command_line)
                        p = subprocess.Popen([command_line, command_line_arg1, command_line_arg2], stdout=subprocess.PIPE)
                        print p.communicate()
                    for temp_file in testing_ttbar_files_list:
                        #temp_file = file_list[x]
                        if '.root' not in temp_file:
                            continue
                        temp_full_path_to_file = os.path.join(temp4_full_pathname,temp_file)
                        new_subdirectory_name = new_subdir_list[sample_counter] + "_testing/"
                        #command_line = 'xrdcp ' + redirector_name + temp_full_path_to_file + ' ' + new_directory + new_subdirectory_name+ temp_file
                        command_line = 'xrdcp'
                        command_line_arg1 = redirector_name + temp_full_path_to_file
                        command_line_arg2 = new_directory + new_subdirectory_name+ temp_file
                        full_command_line = command_line + command_line_arg1 + command_line_arg2
                        print full_command_line
                        # If file already exists, go to next file.
                        if os.path.isfile(command_line_arg2):
                            continue
                        print full_command_line
                        ##os.popen(command_line)
                        p = subprocess.Popen([command_line, command_line_arg1, command_line_arg2], stdout=subprocess.PIPE)
                        print p.communicate()
                else:
                    for temp_file in file_list:
                        if '.root' not in temp_file:
                            continue
                        temp_full_path_to_file = os.path.join(temp4_full_pathname,temp_file)
                        if '_ext1' in temp_full_path_to_file:
                            temp_file = temp_file[:-5] + '_ext1.root'
                        command_line_arg1 = redirector_name + temp_full_path_to_file
                        command_line_arg2 = new_directory + new_subdir_list[sample_counter] + "/" + temp_file
                        #command_line = 'xrdcp ' + redirector_name + temp_full_path_to_file + ' ' + new_directory + new_subdir_list[sample_counter] + "/" + temp_file
                        command_line = 'xrdcp ' + command_line_arg1 + ' ' + command_line_arg2
                        # If file already exists, go to next file.
                        if os.path.isfile(command_line_arg2):
                            continue
                        print 'command_line: '
                        print command_line
                        os.popen(command_line)
        # Increment counter so new directory name matches old directory name.
    sample_counter = sample_counter + 1
