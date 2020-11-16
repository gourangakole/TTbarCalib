#!/usr/bin/python
#################################################################
#                       crab_manager.py
#                    Joshuha Thomas-Wilsker
#                         IHEP, CERN
#################################################################
#        Python script with functionality to kill, get status,
#        and resubmit all jobs in a given directory that conatains
#        crab run directories.
#################################################################
# Usage: python crab_manager.py -d crab_projects-GEN-SIM-v1 -o (resubmit,kill,status)
#################################################################

from httplib import HTTPException
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from optparse import OptionParser
import sys, os, getopt

def get_all_status(dir_name,file_name):
    st = {}
    '''parser=OptionParser()
    parser.add_option('--long', '--crabCmdOpts',
                      dest = 'crabCmdOpts',
                      default = '--verboseErrors',
                      help = "options for crab command CMD",
                      metavar = 'OPTS')
    (options, arguments) = parser.parse_args()

    print options.crabCmdOpts.split()'''

    try:
        #st = crabCommand("status", dir = os.path.join(dir_name,file_name), *options.crabCmdOpts.split())
        st = crabCommand('status', dir = os.path.join(dir_name,file_name))
    except HTTPException as ex:
        print 'Problem getting jobs status: %s' % ex

    if st.get("jobList"):
        print(st.get("jobList"))

def kill_all_jobs(dir_name,file_name):
    try:
        crabCommand("kill", dir = os.path.join(dir_name,file_name))
    except HTTPException as ex:
        print 'Problem killing job: %s ' % ex

def resubmit_all_jobs(dir_name,file_name):
    try:
        crabCommand('resubmit', dir = os.path.join(dir_name,file_name))
    except HTTPException as ex:
        print 'Problem resubmitting job: %s' % ex
    except ClientException as cle:
        print "Failed resubmitting task: %s" % (cle)

def main(argv):
    directory_name = ''
    crab_mode = ''

    #Errors required to catch exceptions where command line wasnt given any options
    try:
        directory_name = argv[0]
    except IndexError:
        print('Please pass valid directory name as first command line argument.')
        sys.exit(2)
    try:
        crab_mode = argv[1]
    except:
        print('Please pass valid crab mode as second command line argument (\'kill\',\'resubmit\',\'status\')')
        sys.exit(2)

    # Raise exception when unrecognised option or when option requiring argument was given but no argument was found.
    try:
        opts, args = getopt.getopt(argv,"hd:o:",["dir=","opt="])
    except getopt.GetoptError:
        print 'crab_manager.py -d <crab_dir> -o <crab_command>'
        sys.exit(0)

    for opt,arg in opts:
        if opt == '-h':
            print 'Usage: crab_manager.py -d <crab_dir> -o <crab_command>'
            sys.exit(0)
        elif opt in ("-d", "--dir"):
            directory_name = arg
            print 'Directory name: ', directory_name
        elif opt in ("-o", "--opt"):
            crab_mode = arg
            print 'Crab mode: ', crab_mode

    for files in os.listdir(directory_name):
        print 'Job dir: ', directory_name
        if 'crab_' in files:
            print 'crab working dir = ', files
            if crab_mode == 'status':
                print 'Checking status of crab jobs in directory.'
                get_all_status(directory_name,files)
            elif crab_mode == 'kill':
                print 'Killing all crab jobs in directory.'
                kill_all_jobs(directory_name,files)
            elif crab_mode == 'resubmit':
                print 'Resubmitting crab job: ' , files
                resubmit_all_jobs(directory_name,files)

    return

if __name__ == '__main__':
    main(sys.argv[1:])
