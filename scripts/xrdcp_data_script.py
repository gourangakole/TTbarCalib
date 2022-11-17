###########################################
#          make_xrdcp_script.py
###########################################
#          Joshuha Thomas-Wilsker
#           CERN, IHEP Beijing
###########################################
# Short script to copy files from an old
# directory structure on EOS to a new
# directory struture also on EOS which is
# much simpler in the context of the BTV
# TTbar analysis measurements.
###########################################
# Ensure you ahve a valid grid proxy:
# $>voms-proxy-init --voms cms
# and have set up the cmssw environment of
# your choice before running this script.
###########################################

import os
import os.path

redirector_name = "root://xrootd-cms.infn.it//"

#Force use of IPv4 (temporary issues with IPv6 on lxplus)
os.popen('export XRD_NETWORKSTACK=IPv4')

# Original directory name on EOS and subsequent directories for individual samples.
original_directory = '/store/group/phys_btag/Commissioning/TTbar/TTbar_UL16_v3/'
original_subdir_list = [
'MuonEG'
]

# EOS directory with new structure to store output (easier for runTTbarAnalysis packages to use).
new_directory = '/eos/cms/store/group/phys_btag/Commissioning/TTbar/TTbar_UL16_StructuredDir_v3/'
# Make the new EOS directory.
eos_mkdir_cmd = 'eos mkdir '
temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory
os.system(temp_eos_mkdir_cmd)

# Sample counter to ensure correct new directory name is used.
sample_counter = 0

# Loop over list of old sample directories
full_pathname = ''
full_pathname = os.path.join(original_directory,original_subdir_list[0])

# Construct eos path by iterating down through old directory structure.
# Needed for copy command.
eos_ls_cmd = 'eos ls '
eos_dir = '/eos/cms/'+full_pathname
temp_eos_ls_cmd = eos_ls_cmd + eos_dir
temp_os_output = os.popen(temp_eos_ls_cmd).read()
data_dir = temp_os_output.splitlines()
# Can add or remove data directories from this list.

data_dir = [
'crab_crab_Data13TeV_MuonEG_Run2016B_v2_HIPM_vUL2016',
'crab_crab_Data13TeV_MuonEG_Run2016C_HIPM_vUL2016',
'crab_crab_Data13TeV_MuonEG_Run2016D_HIPM_vUL2016',
'crab_crab_Data13TeV_MuonEG_Run2016E_HIPM_vUL2016',
'crab_crab_Data13TeV_MuonEG_Run2016F_HIPM_vUL2016'
]

# Loop over crab job output directories for data inside MuonEG directory.
for subdir_2 in data_dir:
    # Create new directroy.
    temp_eos_mkdir_cmd = eos_mkdir_cmd + new_directory + subdir_2
    os.system(temp_eos_mkdir_cmd)
    temp_full_pathname = ''
    temp_full_pathname = os.path.join(full_pathname,subdir_2)
    temp_eos_ls_cmd = eos_ls_cmd + temp_full_pathname
    temp_os_output = os.popen(temp_eos_ls_cmd).read()

    temp_os_output = os.popen(temp_eos_ls_cmd).read()
    subdir_4 = temp_os_output.splitlines()

    for temp_dir in subdir_4:
        temp_full_pathname_2 = os.path.join(temp_full_pathname,temp_dir)
        temp_eos_ls_cmd = eos_ls_cmd + temp_full_pathname_2
        temp_os_output = os.popen(temp_eos_ls_cmd).read()
        file_list = temp_os_output.splitlines()

        # Construct and initiate xrdcp command.
        for temp_subdir in file_list:
            temp_full_path_to_file = os.path.join(temp_full_pathname_2,temp_subdir)
            temp_eos_ls_cmd = eos_ls_cmd + temp_full_path_to_file
            temp_os_output = os.popen(temp_eos_ls_cmd).read()
            subdir_5 = temp_os_output.splitlines()
            for temp_file in subdir_5:
                command_line_arg1 = redirector_name + temp_full_path_to_file + '/' + temp_file
                command_line_arg2 = new_directory + subdir_2 + "/" + temp_file
                command_line = 'xrdcp ' + command_line_arg1 +  ' ' + command_line_arg2
                print command_line
                if os.path.isfile(command_line_arg2):
                    print('Already copied, skipping!')
                    continue
                os.popen(command_line)
# Increment counter so new directory name matches old directory name.
sample_counter = sample_counter + 1
