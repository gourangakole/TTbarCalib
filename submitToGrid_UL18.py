import optparse
import os,sys
import json
import commands

"""
creates the crab cfg and submits the job
"""
def submitProduction(tag,lfnDirBase,dataset,isData,cfg,workDir,lumiMask,submit=False):

    os.system("rm -rvf %s/*%s* "%(workDir,tag))
    crabConfigFile=workDir+'/'+tag+'_cfg.py'
    config_file=open(crabConfigFile,'w')
    config_file.write('from WMCore.Configuration import Configuration\n')
    config_file.write('import os\n')
    config_file.write('config = Configuration()\n')
    config_file.write('\n')
    config_file.write('config.section_("General")\n')
    config_file.write('config.General.requestName = "%s"\n' % tag)
    config_file.write('config.General.workArea = "%s"\n' % workDir)
    config_file.write('config.General.transferOutputs=True\n')

    config_file.write('\n')
    config_file.write('config.section_("JobType")\n')
    config_file.write('config.JobType.pluginName = "Analysis"\n')
    config_file.write('config.JobType.psetName = "'+cfg+'"\n')
    config_file.write('config.JobType.disableAutomaticOutputCollection = False\n')
    if 'Run2018A' in dataset:
        defaults_label = '2018_UltraLegacy_DataRunA'
    elif 'Run2018B' in dataset:
        defaults_label = '2018_UltraLegacy_DataRunB'
    elif 'Run2018C' in dataset:
        defaults_label = '2018_UltraLegacy_DataRunC'
    elif 'Run2018D' in dataset:
        defaults_label = '2018_UltraLegacy_DataRunD'
    else:
        defaults_label = '2018_UltraLegacy'

    config_params = 'config.JobType.pyCfgParams = [\'defaults=%s\', \'useTTbarFilter=True\', \'miniAOD=True\', \'maxEvents=-1\', \'runOnData=%s\', \'groups=TTbar,JetDeepCSV,JetDeepFlavour,Josh,JetInfo,PV,EventInfo\']\n' % ( defaults_label, bool(isData) )
    print 'Used config parameters: '
    print config_params
    config_file.write(config_params)
    config_file.write('config.JobType.allowUndistributedCMSSW = True\n')

    config_file.write('\n')
    config_file.write('config.section_("Data")\n')
    config_file.write('config.Data.inputDataset = "%s"\n' % dataset)
    config_file.write('config.Data.inputDBS = "global"\n')
    config_file.write('config.Data.allowNonValidInputDataset=True\n')
    if isData :
        config_file.write('config.Data.splitting = "LumiBased"\n')
        config_file.write('config.Data.unitsPerJob = 100\n')
        config_file.write('config.Data.lumiMask = \'%s\'\n' %lumiMask)
    else :
        config_file.write('config.Data.splitting = "FileBased"\n')
        config_file.write('config.Data.unitsPerJob = 1\n')
    config_file.write('config.Data.publication = True\n')
    #config_file.write('config.Data.ignoreLocality = False\n')
    config_file.write('config.Data.ignoreLocality = True\n')
    config_file.write('config.Data.outLFNDirBase = \'%s\'\n' % lfnDirBase)
    config_file.write('\n')
    config_file.write('config.section_("Site")\n')
    config_file.write('config.Site.storageSite = "T2_CH_CERN"\n')
    config_file.write('config.Site.whitelist = ["T2_US*"]\n')

    config_file.close()

    if submit : os.system('crab submit -c %s' % crabConfigFile )

"""
steer the script
"""
def main():



    #configuration
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-c', '--cfg',         dest='cfg'   ,      help='cfg to be sent to grid',       default=None,    type='string')
    parser.add_option('-j', '--json',        dest='json'  ,      help='json with list of files',      default=None,    type='string')
    parser.add_option('-o', '--only',        dest='only'  ,      help='submit only these (csv)',      default=None,    type='string')
    parser.add_option('-l', '--lumi',        dest='lumiMask',    help='json with list of good lumis', default='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt')
    parser.add_option('-w', '--workDir',     dest='workDir',     help='working directory',            default='grid',  type='string')
    parser.add_option(      '--lfn',         dest='lfn',         help='base lfn to store outputs',    default='/store/group/phys_btag/Commissioning/TTbar', type='string')
    parser.add_option('-s', '--submit',      dest='submit',      help='submit jobs',                  default=False,   action='store_true')
    (opt, args) = parser.parse_args()

    #read list of samples
    jsonFile = open(opt.json,'r')
    samplesList=json.load(jsonFile,encoding='utf-8').items()
    jsonFile.close()

    githash = 'TTbar_UL18'
    lfnDirBase='%s/%s/' % (opt.lfn,githash)

    onlyList=[]
    try:
        onlyList=opt.only.split(',')
    except:
        pass

    #submit jobs
    os.system("mkdir -p %s" % opt.workDir)
    for tag,sample in samplesList:
        submit=False if len(onlyList)>0 else True
        for filtTag in onlyList:
            if filtTag in tag :
                submit=True
        if not submit : continue
        submitProduction(tag=tag,
                         lfnDirBase=lfnDirBase,
                         dataset=sample[2],
                         isData=sample[1],
                         lumiMask=opt.lumiMask,
                         cfg=opt.cfg,
                         workDir=opt.workDir,
                         submit=opt.submit)

    print 'crab cfg files have been created under %s' % opt.workDir
    if opt.submit:
        print 'Jobs have been submitted'
        print 'Monitor jobs with http://dashb-cms-job.cern.ch/dashboard/templates/task-analysis/ or locally with crab'
        print 'Output will be found in %s' % lfnDirBase

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())
