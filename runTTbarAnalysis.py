import optparse
import os,sys
import json
import commands
import ROOT
import pickle
import math
from array import array
from storeTools import *

CHANNELS={-11*11:'ee', -13*13:'mumu', -11*13:'emu'}

"""
Perform the analysis on a single file
"""
def runTTbarAnalysis(inFile, outFile, wgt, tmvaWgts=None, isData=False):

    from ROOT import TTbarEventAnalysis
    evAnalysis=TTbarEventAnalysis()
    print 'inFile: ' , inFile

    #MC specifics
    if 'TTJets' in inFile: evAnalysis.setReadTTJetsGenWeights(True)

    # Be careful to insure the triggers used here match those used in TTbarSelectionProducer_cfi
    # Also ensure overlap between datastreams is avoided if necessary
    # Trigger bit entry comes in pairs: (index , channel it's valid for)
    if isData:
        if 'MuonEG'   in inFile :
            evAnalysis.addTriggerBit(0,-11*13)
            evAnalysis.addTriggerBit(1,-11*13)
            evAnalysis.addTriggerBit(2,-11*13)
            evAnalysis.addTriggerBit(3,-11*13)
            evAnalysis.addTriggerBit(4,-11*13)
            evAnalysis.addTriggerBit(5,-11*13)
            evAnalysis.addTriggerBit(6,-11*13)
    else:
            evAnalysis.addTriggerBit(0,-11*13)
            evAnalysis.addTriggerBit(1,-11*13)
            evAnalysis.addTriggerBit(2,-11*13)
            evAnalysis.addTriggerBit(3,-11*13)
            evAnalysis.addTriggerBit(4,-11*13)
            evAnalysis.addTriggerBit(5,-11*13)
            evAnalysis.addTriggerBit(6,-11*13)

    for v in ['close_mlj[0]', 'close_dphi', 'close_deta', 'close_lj2ll_dphi', 'close_lj2ll_deta',
              'far_mlj',      'far_dphi',   'far_deta',   'far_lj2ll_dphi',   'far_lj2ll_deta',
              'j2ll_dphi',    'j2ll_deta']:
        evAnalysis.addVarForTMVA(ROOT.TString(v))
    if not (tmvaWgts is None) : evAnalysis.setTMVAWeightsBaseDir(tmvaWgts)

    file_good = evAnalysis.checkFile(ROOT.TString(inFile))
    if file_good == 1:
        evAnalysis.prepareOutput(ROOT.TString(outFile))
        evAnalysis.processFile(ROOT.TString(inFile),wgt,isData)
        evAnalysis.finalizeOutput(wgt)
    else:
        process_name = inFile.split('/')[-2]
        file_name = (inFile.split('/')[-1]).split('.')[0]
        production_monitoring ='%s/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/production_info/failed_files_%s_%s.txt'%(os.environ['CMSSW_BASE'] , process_name,file_name)
        file_warning = 'WARNING! %s file_good == 0 (file can be read but no entries to run on!) \n' % inFile
        print(file_warning)

"""
Wrapper to be used when run in parallel
"""
def runTTbarAnalysisPacked(args):

    inFile, outFile, wgt, tmvaWgts, isData = args
    try:
        return runTTbarAnalysis(inFile=inFile, outFile=outFile, wgt=wgt, tmvaWgts=tmvaWgts, isData=isData)
    except :
        print 50*'<'
        print "Problem (%s) with %s continuing without"%(sys.exc_info()[1],inFile)
        print 50*'<'
        return False

"""
steer the script
"""
def main():

    #configuration
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-j', '--json',        dest='json'  ,      help='json with list of files',      default=None,        type='string')
    parser.add_option('-i', '--inDir',       dest='inDir',       help='input directory with files',   default=None,        type='string')
    parser.add_option('-o', '--outDir',      dest='outDir',      help='output directory',             default='analysis',  type='string')
    parser.add_option(      '--only',        dest='only',        help='process only matching (csv)',  default='',          type='string')
    parser.add_option(      '--tmvaWgts',    dest='tmvaWgts',    help='tmva weights',                 default=None,        type='string')
    parser.add_option(      '--dyScale',     dest='dyScale',     help='DY scale factor',              default=None,        type='string')
    parser.add_option('-n', '--njobs',       dest='njobs',       help='# jobs to run in parallel',    default=0,           type='int')
    (opt, args) = parser.parse_args()

    #compile c++ wrapper to run over trees
    ROOT.gSystem.Load("libJetMETCorrectionsObjects.so")
    ROOT.gSystem.CompileMacro("TTbarEventAnalysis.cc","fkgd","libTTbarEventAnalysis");
    ROOT.gSystem.Load("libTTbarEventAnalysis.so")

    #read list of samples
    jsonFile = open(opt.json,'r')
    samplesList=json.load(jsonFile,encoding='utf-8').items()
    jsonFile.close()

    #prepare output
    if len(opt.outDir) : os.system('mkdir -p %s' % opt.outDir)

    #only list
    onlyList=opt.only.split(',')

    #read normalization
    xsecWgts, integLumi = {}, {}
    cache='%s/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/data/.xsecweights.pck'%os.environ['CMSSW_BASE']
    try:
        cachefile = open(cache, 'r')
        xsecWgts  = pickle.load(cachefile)
        integLumi = pickle.load(cachefile)
        cachefile.close()
        print 'Normalization read from cache (%s)' % cache

        for tag,sample in samplesList:
            if not tag in xsecWgts:
                raise KeyError

    except:
        print '(Re-)Computing original number of events and storing in cache, this may take a while if it\'s the first time'
        print 'Current cache contains %d processes'%len(xsecWgts)
        xsecWgts, integLumi = produceNormalizationCache(samplesList=samplesList,inDir=opt.inDir,cache=cache, normWgts=xsecWgts, integLumi=integLumi)

    #DY scale factor
    if opt.dyScale:
        cachefile=open(opt.dyScale,'r')
        dySF=pickle.load(cachefile)
        cachefile.close()
        for tag in xsecWgts:
            if not 'DY' in tag: continue
            print 'DY SF: '
            print tag,xsecWgts[tag].GetBinContent(1),' -> ',
            xsecWgts[tag].Scale(dySF[0])
            print xsecWgts[tag].GetBinContent(1)

    #create the analysis jobs
    runTags = []
    task_list = []
    sample_count = 0;
    for tag,sample in samplesList:
        #print '[runTTbarAnalysis] tag: %s , sample: %s, xSecWeights: %s' % (tag,sample,xsecWgts[tag].GetBinContent(1))
        #check if in list
        if len(onlyList)>0:
            veto=True
            for selTag in onlyList:
                if selTag in tag: veto=False
            if veto : continue

        runTags.append(tag)
        input_list=getEOSlslist(directory=opt.inDir+'/'+tag)
        # Weight histograms passed here are passed from storeTools
        wgt = xsecWgts[tag]

        for nf in xrange(0,len(input_list)) :
            #if nf > 0: # Use to run only one file for tests
            #    continue
            outF='%s/%s_%d.root'%(opt.outDir,tag,nf)
            task_list.append( (input_list[nf], outF, wgt, opt.tmvaWgts, sample[1]) )

    task_list=list(set(task_list))
    print '%s jobs to run in %d parallel threads' % (len(task_list), opt.njobs)

    # Run the analysis jobs
    if opt.njobs == 0:
        for inFile, outFile, wgt, tmvaWgts, isData in task_list:
            runTTbarAnalysis(inFile=inFile, outFile=outFile, wgt=wgt, tmvaWgts=tmvaWgts, isData=isData)
    else:
        from multiprocessing import Pool
        pool = Pool(opt.njobs)
        pool.map(runTTbarAnalysisPacked, task_list)

    print 'Analysis results are available in %s' % opt.outDir
    exit(0)

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())
