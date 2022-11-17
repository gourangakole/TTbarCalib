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
import commands
os.environ['EOS_MGM_URL'] = 'root://eoscms.cern.ch/'

redirector_name = "root://xrootd-cms.infn.it//"
#redirector_name = "root://cms-xrd-global.cern.ch//"

#Force use of IPv4 (temporary issues with IPv6 on lxplus)
os.popen('export XRD_NETWORKSTACK=IPv4')

# Original directory name on EOS and subsequent directories
# for individual samples.
original_directory = '/store/group/phys_btag/Commissioning/TTbar/TTbar_UL16_v3/'
original_subdir_list = [
#'DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8',
#'DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8',
#'ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8',
#'ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8',
#'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
#'TTTo2L2Nu_TuneCP5_erdON_13TeV-powheg-pythia8',
#'TTTo2L2Nu_TuneCP5down_13TeV-powheg-pythia8',
#'TTTo2L2Nu_TuneCP5up_13TeV-powheg-pythia8',
#'TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8',
#'TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8',
#'TTTo2L2Nu_mtop171p5_TuneCP5_13TeV-powheg-pythia8',
#'TTTo2L2Nu_mtop173p5_TuneCP5_13TeV-powheg-pythia8',
#'TTToHadronic_TuneCP5_13TeV-powheg-pythia8',
#'TTToHadronic_TuneCP5_erdON_13TeV-powheg-pythia8',
#'TTToHadronic_TuneCP5down_13TeV-powheg-pythia8',
#'TTToHadronic_TuneCP5up_13TeV-powheg-pythia8',
#'TTToHadronic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8',
#'TTToHadronic_hdampUP_TuneCP5_13TeV-powheg-pythia8',
#'TTToHadronic_mtop171p5_TuneCP5_13TeV-powheg-pythia8',
#'TTToHadronic_mtop173p5_TuneCP5_13TeV-powheg-pythia8',
#'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8',
#'TTToSemiLeptonic_TuneCP5_erdON_13TeV-powheg-pythia8',
#'TTToSemiLeptonic_TuneCP5down_13TeV-powheg-pythia8',
'TTToSemiLeptonic_TuneCP5up_13TeV-powheg-pythia8',
#'TTToSemiLeptonic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8',
#'TTToSemiLeptonic_hdampUP_TuneCP5_13TeV-powheg-pythia8',
#'TTToSemiLeptonic_mtop171p5_TuneCP5_13TeV-powheg-pythia8',
#'TTToSemiLeptonic_mtop173p5_TuneCP5_13TeV-powheg-pythia8'
#'WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8',
#'WW_TuneCP5_13TeV-pythia8',
#'WZ_TuneCP5_13TeV-pythia8',
#'ZZ_TuneCP5_13TeV-pythia8'
]

# EOS directory with new structure to store output (easier for runTTbarAnalysis packages to use).
new_directory = '/eos/cms/store/group/phys_btag/Commissioning/TTbar/TTbar_UL16_StructuredDir_v3/'
new_subdir_list = [
#'MC13TeV_DYJetsToLL-M-10to50_HIPM',
#'MC13TeV_DYJetsToLL-M-50_HIPM',
#'MC13TeV_atW_HIPM',
#'MC13TeV_tW_HIPM',
#'MC13TeV_TTJets_DL_HIPM',
#'MC13TeV_TTJets_DL_erdON_HIPM',
#'MC13TeV_TTJets_DL_TuneCP5down_HIPM',
#'MC13TeV_TTJets_DL_TuneCP5up_HIPM',
#'MC13TeV_TTJets_DL_hdampDOWN_HIPM',
#'MC13TeV_TTJets_DL_hdampUP_HIPM',
#'MC13TeV_TTJets_DL_mtop171p5_HIPM',
#'MC13TeV_TTJets_DL_mtop173p5_HIPM',
#'MC13TeV_TTJets_AH_HIPM',
#'MC13TeV_TTJets_AH_erdON_HIPM',
#'MC13TeV_TTJets_AH_TuneCP5down_HIPM',
#'MC13TeV_TTJets_AH_TuneCP5up_HIPM',
#'MC13TeV_TTJets_AH_hdampDOWN_HIPM',
#'MC13TeV_TTJets_AH_hdampUP_HIPM',
#'MC13TeV_TTJets_AH_mtop171p5_HIPM',
#'MC13TeV_TTJets_AH_mtop173p5_HIPM',
#'MC13TeV_TTJets_SL_HIPM',
#'MC13TeV_TTJets_SL_erdON_HIPM',
#'MC13TeV_TTJets_SL_TuneCP5down_HIPM',
'MC13TeV_TTJets_SL_TuneCP5up_HIPM',
#'MC13TeV_TTJets_SL_hdampDOWN_HIPM',
#'MC13TeV_TTJets_SL_hdampUP_HIPM',
#'MC13TeV_TTJets_SL_mtop171p5_HIPM',
#'MC13TeV_TTJets_SL_mtop173p5_HIPM'
#'MC13TeV_WJetsToLNu_HIPM',
#'MC13TeV_WW_HIPM',
#'MC13TeV_WZ_HIPM',
#'MC13TeV_ZZ_HIPM'
]

# Ensure the above lists of samples in old and new directory match.
if len(original_subdir_list) != len(new_subdir_list):
    print 'Warning!!!! Old samples list and new samples list do not match in size!'
    print '# original list = ', len(original_subdir_list)
    print '# new list = ', len(new_subdir_list)

# Make the new EOS directory.
eos_mkdir_cmd = 'eos mkdir '
temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory

if os.path.isfile(temp_eos_mkdir_cmd):
    print('Campaign directory %s already exists' % temp_eos_mkdir_cmd)
else:
    print('Making campaign directory: ', temp_eos_mkdir_cmd)
    os.system(temp_eos_mkdir_cmd)

# Sample counter to ensure correct new directory name is used.
sample_counter = 0

# Loop over list of old sample directories
for subdir in original_subdir_list:
    full_pathname = ''
    full_pathname = os.path.join(original_directory,subdir)

    ttbar_sysflag = False
    ttbar_systematics_list = ['erdON','hdampUP','hdampDOWN','TuneCP5up','TuneCP5down','mtop171p5','mtop173p5']
    for ttsyst in ttbar_systematics_list:
        if ttsyst in full_pathname:
            ttbar_sysflag=True

    # Construct eos path by iterating down through old directory structure.
    # Needed for copy command.
    prepend='root://eoscms.cern.ch'
    eos_dir = '/eos/cms/%s ' % (full_pathname)
    eos_cmd = 'eos ' + prepend + ' ls ' + eos_dir
    subdir_2 = commands.getoutput(eos_cmd).splitlines()
    print("subdir_2: ", subdir_2)
    for temp_dir_2 in subdir_2:
        if 'HIPM' not in temp_dir_2:# run on pre-VFP (HIPM) or post-VFP (non-HIPM)?
            continue
        new_sub_dir=temp_dir_2[5:]
        # Create new directories
        # If: TTbar samples, need to split simulation. Half used to train BDT half for testing/results.
        # Else: Proceed as normal.
        '''if 'TTTo' in subdir and ttbar_sysflag == False:
            #temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory + new_subdir_list[sample_counter] + '_training'
            temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory + new_sub_dir + '_training'
            if os.path.isfile(temp_eos_mkdir_cmd):
                print('Directory %s already exists' % temp_eos_mkdir_cmd)
            else:
                print('Making directory: ', temp_eos_mkdir_cmd)
                os.system(temp_eos_mkdir_cmd)

            #temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory + new_subdir_list[sample_counter] + '_testing'
            temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory + new_sub_dir + '_testing'
            if os.path.isfile(temp_eos_mkdir_cmd):
                print('Directory %s already exists' % temp_eos_mkdir_cmd)
            else:
                print('Making directory: ', temp_eos_mkdir_cmd)
                os.system(temp_eos_mkdir_cmd)
        else:'''
        temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory + new_sub_dir# new_subdir_list[sample_counter]
        print('temp_eos_mkdir_cmd: ', temp_eos_mkdir_cmd)
        print 'Make directory: ', temp_eos_mkdir_cmd
        os.system(temp_eos_mkdir_cmd)

        full_pathname = os.path.join(original_directory,subdir)
        full_pathname = os.path.join(full_pathname,temp_dir_2)
        print('full_pathname: ',full_pathname)
        eos_dir = '/eos/cms/%s ' % (full_pathname)
        eos_cmd = 'eos ' + prepend + ' ls ' + eos_dir

        subdir_3 = commands.getoutput(eos_cmd).splitlines()

        print('subdir_3: ',subdir_3)

        for temp_dir_3 in subdir_3:
            print('temp_dir_3: ', temp_dir_3)
            temp3_full_pathname = os.path.join(full_pathname,temp_dir_3)
            eos_dir = '/eos/cms/%s ' % (temp3_full_pathname)
            eos_cmd = 'eos ' + prepend + ' ls ' + eos_dir
            # WARNING: OK, in this subdirectory we have two further directories.
            #          Can split returned string using new line delimiter, into
            #          an array of strings of directory names.
            subdir_4 = commands.getoutput(eos_cmd).splitlines()

            for temp_dir in subdir_4:
                print('temp_dir: ', temp_dir)
                temp4_full_pathname = os.path.join(temp3_full_pathname,temp_dir)
                eos_dir = '/eos/cms/%s ' % (temp4_full_pathname)
                eos_cmd = 'eos ' + prepend + ' ls ' + eos_dir
                temp_os_output = commands.getoutput(eos_cmd)
                test_dir_temp = redirector_name+'/eos/cms/'+temp4_full_pathname
                file_list = temp_os_output.splitlines()

                for temp_file in file_list:
                    if '.root' not in temp_file:
                        print('Skipping file. Not root format.')
                        continue
                    temp_full_path_to_file = os.path.join(temp4_full_pathname,temp_file)
                    if '_ext1' in temp_full_path_to_file:
                        temp_file = temp_file[:-5] + '_ext1.root'
                    command_line = 'xrdcp'
                    command_line_arg1 = redirector_name + temp_full_path_to_file
                    command_line_arg2 = new_directory + new_sub_dir + "/" + temp_file
                    full_command_line = command_line + ' ' + command_line_arg1 + ' ' + command_line_arg2
                    print('Performing: ', full_command_line)
                    # If file already exists, go to next file.
                    if os.path.isfile(command_line_arg2):
                        print('Already performed %s . Skipping.' % command_line_arg2)
                        continue
                    else:
                        print('Copying files . . . ')
                    p = subprocess.Popen([command_line, command_line_arg1, command_line_arg2], stdout=subprocess.PIPE)
                    print p.communicate()
        # Increment counter so new directory name matches old directory name.
    sample_counter = sample_counter + 1
