import optparse
import os,sys
import json
#import commands
import ROOT
import pickle
from plotter import Plot
from array import array

#VARSTOFIT  = [('kindisc',-1,1),('close_mlj',0,250)]
VARSTOFIT  = [('kindisc',-1,1)]
SLICEBINS  = {
    'jetpt': [(30,50),(50,70),(70,100),(100,140),(140,200),(200,300),(300,600)],
    #'jeteta': [(-2.4,-1.1),(-1.1,1.1),(1.1,2.4)],
    #'npv': [(0,7),(7,13),(13,16),(16,30)],
    }
SLICEVARTITLES={
    'jetpt':'Jet pT [GeV]',
    #'jeteta':'Pseudo-rapidity',
    #'npv':'Primary vertex multiplicity'
}
SLICEVAR   = 'jetpt'
#SYSTVARS   =  ['','jesup','jesdn','jerup','jerdn','trigdn','trigup','seldn','selup','qcdscaledn','qcdscaleup','puup','pudn','isrDefdn','isrDefup','fsrDefdn','fsrDefup']
# Updated:
# gkole try
SYSTVARS   = ['','jesup','jesdn','jerup','jerdn','pileupup','pileupdn','massup','massdn']
#SYSTVARS   =  ['','mistagup','mistagdn','jesup','jesdn','jerup','jerdn','trigdn','trigup','seldn','selup','qcdscaledn','qcdscaleup','pileupup','pileupdn','isrDefdn','isrDefup','fsrDefdn','fsrDefup']

"""
Project trees from files to build the templates
"""
def prepareTemplates(tagger,taggerDef,var,varRange,channelList,inDir,outDir,TT_syst):

    print ('Preparing template for %s tagger.'%(tagger))
    print ('Variable to fit is %s.'%(var))
    print ('Slice variable is %s.'%(SLICEVAR))

    nOPs=len(taggerDef)-2

    #prepare output file
    fOut=ROOT.TFile.Open('%s/%s_templates/%s.root'%(outDir,var,tagger),'RECREATE')

    #prepare tree with discriminator to unfold
    outT=ROOT.TTree( 'discdata', 'discdata')
    outT.SetDirectory(fOut)
    varVal = array( 'f', [ 0. ] )
    outT.Branch( 'var', varVal, 'var/F' )
    taggerVal = array( 'f', [ 0. ] )
    outT.Branch( 'tagger',taggerVal, 'taggerVal/F' )
    passSlice = array( 'i',len(SLICEBINS[SLICEVAR])*[ 0 ] )
    outT.Branch( 'slice', passSlice, 'slice[%d]/I'%len(SLICEBINS[SLICEVAR]) )

    #prepare templates
    histos={}
    baseHisto=ROOT.TH1F(var,';Discriminator;Jets',10*3,varRange[0],varRange[0]+3*(varRange[1]-varRange[0]))
    for flav in ['b','c','other','data']:
        for i in xrange(0,nOPs):
            for islice in xrange(0,len(SLICEBINS[SLICEVAR])):
                for systVar in SYSTVARS:
                    if flav=='data' and len(systVar)>0 : continue
                    #if TT_syst != 'nominal' and len(systVar)>0 : continue
                    if i==0:
                        hkey='%s_slice%d_%s'%(flav,islice,systVar)
                        histos[hkey]=ROOT.TH1F(hkey,';Discriminator;Jets',50,varRange[0],varRange[1])
                    for status in ['pass','fail']:
                        key='%s_%s%d_slice%d%s' % (flav, status, i, islice,systVar)
                        if i==0 and status=='fail': continue
                        histos[key]=baseHisto.Clone(key)
                        histos[key].SetDirectory(0)
                        histos[key].Sumw2(0)
    baseHisto.Delete()

    # Add files to the corresponding chains

    # If running on TT systematic variation we can simply ensure the TT samples are taken from the alternative directory
    files = []
    syst_TT_inDir=''
    print('inDir: ', inDir)
    if TT_syst != 'nominal':
        syst_TT_inDir = inDir
        #print("syst_TT_inDir: ", syst_TT_inDir)
        files = [ f for f in os.listdir(syst_TT_inDir) if '.root' in f ]
        files = files + [f_b for f_b in os.listdir(inDir) if '.root' in f_b and 'TTJets' not in f_b]
    else:
        files = [ f for f in os.listdir(inDir) if '.root' in f ]

    print('files: ', files)
    chains={'mc':ROOT.TChain('kin'), 'mcjesup':ROOT.TChain('kin'), 'mcjesdn':ROOT.TChain('kin'), 'mcjerup':ROOT.TChain('kin'), 'mcjerdn':ROOT.TChain('kin'), 'data':ROOT.TChain('kin'), 'mcmassup':ROOT.TChain('kin'), 'mcmassdn':ROOT.TChain('kin')}

    for f in files:
        if 'training' in f:
            continue
        # key = 'mc' if 'MC' in f else 'data' # this was Josh's setup
        # key = 'mc' if 'TTtoLNu2Q' in f else 'data' #gkole try (02Nov2023)
        # key = 'mc' if 'TTto2L2Nu' in f else 'data'
        if ('TTto2L2Nu' in f and 'jesup' in f):
            key = 'mcjesup'
        elif ('TTto2L2Nu' in f and 'jesdn' in f):
            key = 'mcjesdn'
        elif ('TTto2L2Nu' in f and 'jerup' in f):
            key = 'mcjerup'
        elif ('TTto2L2Nu' in f and 'jerdn' in f):
            key = 'mcjerdn'
        elif ('TTto2L2Nu' in f and 'massup' in f):
            key = 'mcmassup'
        elif ('TTto2L2Nu' in f and 'massdn' in f):
            key = 'mcmassdn'
        elif ('TTto2L2Nu' in f and not 'jesup' in f and not 'jesdn' in f and not 'jerup' in f and not 'jerdn' in f and not 'massup' in f and not 'massdn' in f):
            key = 'mc'
        else:
            key = 'data'

        if TT_syst != 'nominal' and 'MC13TeV_TTJets' in f:
            dir_file_name = syst_TT_inDir+'/'+f
            chains[key].Add(dir_file_name)
        else:
            dir_file_name=inDir+'/'+f
            print ("key", key, "and file", dir_file_name)
            chains[key].Add(dir_file_name)

    # Fill histos
    for key in chains:
        # print ("Loop over key: ", key)
        nentries=chains[key].GetEntries()
        print ('Starting with %s containing %d entries'%(key,nentries))

        for i in xrange(0,nentries):
            if i%1 == 0:
                sys.stdout.write("[%3d/100]\r" % (100*i/float(nentries)))
                sys.stdout.flush()

            # Get entry from TChain/TTree = kinTree_ = TTree w. entry per jet
            chains[key].GetEntry(i)

            #filter channel, if required
            if not chains[key].ttbar_chan in channelList : continue

            # Restrict jet multiplicity (one entry in kin tree)
            njets=chains[key].jetmult
            if 0:
                print ("gkole debug-> 0:")
                print ('Entry: %s , njets: %s ' % (i, njets))

            if njets<2 or njets>4 : continue
            # print ('SYSTVARS: ', SYSTVARS)
            for systVar in SYSTVARS:
                if key=='data' and len(systVar)>0 : continue
                #if key == 'mc' and systVar != '': continue
                if key == 'mcjesup' and systVar != 'jesup': continue
                if key == 'mcjesdn' and systVar != 'jesdn': continue
                if key == 'mcjerup' and systVar != 'jerup': continue
                if key == 'mcjerdn' and systVar != 'jerdn': continue
                if key == 'mcmassup' and systVar != 'massup': continue
                if key == 'mcmassdn' and systVar != 'massdn': continue
                # if systVar =='' and key != 'mc': continue
                # if systVar =='jesup' and key != 'mcjesup': continue
                # if systVar =='jesdn' and key != 'mcjesdn': continue
                # print ("key= ", key," & systVar= ", systVar)
                # Get alternative events weights for systemtics constructed from weight variations
                wgtIdx, systIdx = 0, 0
                # if systVar=='jesup'      : wgtIdx, systIdx = 1,  1
                # if systVar=='jesdn'      : wgtIdx, systIdx = 2,  2
                # if systVar=='jerup'      : wgtIdx, systIdx = 3,  3
                # if systVar=='jerdn'      : wgtIdx, systIdx = 4,  4
                #if systVar=='pudn'       : wgtIdx, systIdx = 5,  0
                if systVar=='pileupdn'       : wgtIdx, systIdx = 5,  0
                #if systVar=='puup'       : wgtIdx, systIdx = 6,  0
                if systVar=='pileupup'       : wgtIdx, systIdx = 6,  0
                #if systVar=='trigdn'     : wgtIdx, systIdx = 7,  0
                #if systVar=='trigup'     : wgtIdx, systIdx = 8,  0
                #if systVar=='seldn'      : wgtIdx, systIdx = 9,  0
                #if systVar=='selup'      : wgtIdx, systIdx = 10, 0
                #if systVar=='qcdscaledn' : wgtIdx, systIdx = 11, 0
                #if systVar=='qcdscaleup' : wgtIdx, systIdx = 12, 0
                ##if systVar=='hdampdn'    : wgtIdx, systIdx = 13, 0
                ##if systVar=='hdampup'    : wgtIdx, systIdx = 14, 0
                ##if systVar=='isrReddn'    : wgtIdx, systIdx = 15, 0
                ##if systVar=='isrRedup'    : wgtIdx, systIdx = 16, 0
                ##if systVar=='fsrReddn'    : wgtIdx, systIdx = 17, 0
                ##if systVar=='fsrRedup'    : wgtIdx, systIdx = 18, 0
                #if systVar=='isrDefdn'    : wgtIdx, systIdx = 19, 0
                #if systVar=='isrDefup'    : wgtIdx, systIdx = 20, 0
                #if systVar=='fsrDefdn'    : wgtIdx, systIdx = 21, 0
                #if systVar=='fsrDefup'    : wgtIdx, systIdx = 22, 0
                #if systVar=='isrCondn'    : wgtIdx, systIdx = 23, 0
                #if systVar=='isrConup'    : wgtIdx, systIdx = 24, 0
                #if systVar=='fsrCondn'    : wgtIdx, systIdx = 25, 0
                #if systVar=='fsrConup'    : wgtIdx, systIdx = 26, 0
                # print ("wgtIdx=  ", wgtIdx)
                #Event weight
                weight      = chains[key].weight[wgtIdx]

                # No need to proceed if event is not selected
                if weight==0: continue
                if 0:
                    print ("gkole debug-> 1:")
                    print ("weight", weight)
                # Variable to slice on
                sliceVarVal  = getattr(chains[key],SLICEVAR)
                # variable to be fit
                
                varVal[0]    = getattr(chains[key],var)      if var=='jpTagger'   else getattr(chains[key],var)[systIdx]
                # print ("varVal[0]", varVal[0])

                # print 'var: %s , tagger: %s' % (var,tagger)

                # Tagger to apply  
                # print "tagger: ", tagger
                # print "att of chains[key]", dir(chains[key])
                taggerVal[0] = getattr(chains[key],tagger)

                #determine categories
                #print "taggerVal[0] ",taggerVal[0] 
                # print 'sliceVarVal: ', sliceVarVal
                for islice in xrange(0,len(SLICEBINS[SLICEVAR])):
                    passSlice[islice]=0
                    if sliceVarVal<=SLICEBINS[SLICEVAR][islice][0] or sliceVarVal>SLICEBINS[SLICEVAR][islice][1] : continue
                    #print 'passed %s < jet pt < %s' % (SLICEBINS[SLICEVAR][islice][0], SLICEBINS[SLICEVAR][islice][1])
                    passSlice[islice]=1

                # print 'passSlice: ', passSlice
                #assign flavour
                flav='other'
                if abs(chains[key].flavour)==5: flav='b'
                if abs(chains[key].flavour)==4: flav='c'
                if key=='data' : flav='data'

                # Fill the histos
                normVarVal = ROOT.TMath.Min( varRange[1],ROOT.TMath.Max(varVal[0],varRange[0]) )
                normVarValJetBins = normVarVal+ (varRange[1]-varRange[0])*(njets-2)
                for islice in xrange(0,len(passSlice)):
                    if passSlice[islice]==0 : continue
                    #print 'njets = ', njets
                    if njets==2:
                        hkey='%s_slice%d_%s'%(flav,islice,systVar)
                        #print 'Filling njets==2 %s with normVarVal %s ' % (hkey,normVarVal)
                        histos[hkey].Fill(normVarVal,weight)

                    hkey='%s_pass0_slice%d%s'%(flav,islice,systVar)
                    # print 'Filling %s with normVarVal %s ' % (hkey,normVarVal) #gkole: 04/12/2023
                    histos[hkey].Fill(normVarVal,weight)

                    # Check to see if jet passed/failed the btag cut and fill appropriate histogram.
                    for iop in xrange(2,len(taggerDef)-1):
                        status='fail' if taggerVal[0] < taggerDef[iop] else 'pass'
                        hkey='%s_%s%d_slice%d%s'%(flav,status,iop-1,islice,systVar)
                        # print 'Check if jet passed/failed btag cut: taggerVal[0] = %s , taggerDef[iop] = %s' % (taggerVal[0], taggerDef[iop])
                        # print 'Filling %s with normVarValJetBins %s ' % (hkey,normVarValJetBins)
                        histos[hkey].Fill(normVarValJetBins,weight)

                #fill histo for data
                if key=='data' : outT.Fill()

    #save templates to file
    outT.Write()
    for key in histos :
        print ('Check histogram %s , integral %s ' % (key, histos[key].Integral()))
        histos[key].Write()
    fOut.Close()

"""
Wrapper to be used when run in parallel
"""
def runPrepareTemplatesPacked(args):
    print ('runPrepareTemplatesPacked . . . . ')
    tagger, taggerDef, var, varRange, channelList, inDir, outDir, TT_syst = args
    try:
        return prepareTemplates(tagger=tagger,
                                taggerDef=taggerDef,
                                var=var,
                                varRange=varRange,
                                channelList=channelList,
                                inDir=inDir,
                                outDir=outDir,
                                TT_syst=TT_syst)
    except :
        print ("Exception: %s " % sys.exc_info()[0])
        print ("Culprit: %s " % sys.exc_info()[1])
        print ("Full sys exc_info : %s " % sys.exc_info())
        return False

"""
Leave no bins with 0 counts
If negative values (negative weights in MC) set to minimum
"""
def checkTemplate(h,minVal=1e-5):
    for xbin in xrange(1,h.GetNbinsX()+1):
        y=h.GetBinContent(xbin)
        if y<=0: h.SetBinContent(xbin,minVal)

"""
run the fits
"""
def runSFFits(var,tagger,taggerDef,lumi,outDir):

    flavourGroups=[ ['b'], ['c','other'] ]
    if var=='jpTagger' : flavourGroups=[ ['b'], ['c'], ['other'] ]

    #customized fraction fitter tool
    ttFracFitter=ROOT.TTbarFracFitter()

    #input file
    input_file = '%s/%s_templates/%s.root' % (outDir, var, tagger)
    print ('input_file: ',input_file)
    fIn=ROOT.TFile.Open(input_file)

    effMeasurements,effExpected,sfMeasurements,systUncs,effUncs={},{},{},{},{}
    nOPs=len(taggerDef)-2
    for iop in xrange(1,nOPs):

        for islice in xrange(0,len(SLICEBINS[SLICEVAR])):

            totalExp=0
            baseNameNominal = '%d_slice%d' % (iop,islice)

            #get data
            data={}
            for status in ['pass','fail']:
                data[status]=fIn.Get('data_%s%s'%(status,baseNameNominal)).Clone()
                data[status].SetDirectory(0)
                data[status].SetTitle('data')

            #pseudo-data (to be constructed below from the nominal variation)
            pseudoData={}

            #iterate over the systematic variations
            for syst in SYSTVARS:

                #build flavour templates
                baseName = baseNameNominal+syst

                mc={'pass':ROOT.TObjArray(),
                    'fail':ROOT.TObjArray()}

                for flavGroup in flavourGroups:

                    title='+'.join(flavGroup)
                    name='%s_%s'%(title,baseName)

                    #build combined template
                    flavTemplates={}
                    for status in mc:

                        for flav in flavGroup:
                            hname='%s_%s%s'%(flav,status,baseName)
                            ihisto=fIn.Get(hname)
                            ihisto.Scale(lumi)

                            #only interested in shape variations
                            hnomname='%s_%s%s'%(flav,status,baseNameNominal)
                            inomhisto=fIn.Get(hnomname)
                            if inomhisto.Integral() == 0:
                                print ('Warning: Nominal template histogram ', hnomname, ' has integral = ', inomhisto.Integral())
                            if ihisto.Integral() == 0:
                                print ('Warning: Systematic template histogram ', hname, ' has integral = ', ihisto.Integral())
                            if inomhisto.Integral() != 0 and ihisto.Integral() != 0:
                                ihisto.Scale(inomhisto.Integral()/ihisto.Integral())

                            if not status in flavTemplates:
                                flavTemplates[status]=ihisto.Clone(name)
                                flavTemplates[status].SetDirectory(0)
                                flavTemplates[status].SetTitle(title)
                            else:
                                flavTemplates[status].Add( ihisto )

                    #check for empty bins and add to templates
                    for status in flavTemplates:
                        checkTemplate(flavTemplates[status])
                        mc[status].Add(flavTemplates[status])

                        #add also to pseudo-data
                        if syst=='':
                            if not status in pseudoData:
                                pseudoData[status]=flavTemplates[status].Clone( name.replace(title,'total exp.') )
                                pseudoData[status].SetDirectory(0)
                            else:
                                pseudoData[status].Add(flavTemplates[status])

                #fit
                if not iop in effMeasurements:
                    effMeasurements[iop]={}
                    sfMeasurements[iop]={}
                    effExpected[iop]={}
                    systUncs[iop]={}
                    effUncs[iop]={}

                if not islice in systUncs[iop]: systUncs[iop][islice]={}
                if not islice in effUncs[iop]: effUncs[iop][islice]={}

                Tagger = ROOT.TString('%s'%(tagger))
                saveResultIn = ROOT.TString('%s/%s_templates/%s_%s'%(outDir,var,tagger,baseName) if syst=='' else '')
                # Always fill nominal first and save results of fit in sfMeasurements(effMeasurements) etc.
                if len(syst)==0:
                    # Nominal variation
                    # print "GKOLE --> mc['pass']:   " , type(mc['pass'])
                    # print "GKOLE --> data['pass']: " , type(data['pass'])
                    res=ttFracFitter.fit(mc['pass'],data['pass'],mc['fail'],data['fail'],Tagger,0,iop,islice,0,saveResultIn,lumi/1000.)
                    sfMeasurements[iop][islice]=(res.sf,res.sfUnc)
                    effMeasurements[iop][islice]=(res.eff,res.effUnc)
                    effExpected[iop][islice]=(res.effExp,res.effExpUnc)
                    # Up variation
                    res=ttFracFitter.fit(mc['pass'],data['pass'],mc['fail'],data['fail'],Tagger,0,iop,islice,1)
                    systUncs[iop][islice]['closureup']=res.sf-sfMeasurements[iop][islice][0] #gkole it was commented out
                    effUncs[iop][islice]['closureup']=res.eff-effMeasurements[iop][islice][0] #gkole it was commented out
                    systUncs[iop][islice]['mistagup']=res.sf-sfMeasurements[iop][islice][0]
                    effUncs[iop][islice]['mistagup']=res.eff-effMeasurements[iop][islice][0]
                    # Down variation
                    res=ttFracFitter.fit(mc['pass'],data['pass'],mc['fail'],data['fail'],Tagger,0,iop,islice,2)
                    systUncs[iop][islice]['mistagdn']=res.sf-sfMeasurements[iop][islice][0] #gkole it was commented out
                    effUncs[iop][islice]['mistagdn']=res.eff-effMeasurements[iop][islice][0] #gkole it was commented out
                    systUncs[iop][islice]['closuredn']=res.sf-sfMeasurements[iop][islice][0]
                    effUncs[iop][islice]['closuredn']=res.eff-effMeasurements[iop][islice][0]
                else:# After nominal, compare with fits using systematic templates to obtain uncertainties.
                    #saveResultIn=ROOT.TString('%s/%s_templates/%s_%s_%s'%(outDir,var,tagger,baseName,syst))
                    #res=ttFracFitter.fit(mc['pass'],pseudoData['pass'],mc['fail'],pseudoData['fail'],0,saveResultIn,lumi/1000.)
                    #systUncs[iop][islice][syst]=res.sf-1.0
                    res=ttFracFitter.fit(mc['pass'],data['pass'],mc['fail'],data['fail'],Tagger,0,iop,islice,0)
                    systUncs[iop][islice][syst]=res.sf-sfMeasurements[iop][islice][0]
                    print ("syst", syst)
                    print ("res.sf", res.sf)
                    print ("sfMeasurements[iop][islice][0]", sfMeasurements[iop][islice][0])
                    effUncs[iop][islice][syst]=res.eff-effMeasurements[iop][islice][0]

    #all fits done
    fIn.Close()

    #dump to pickle
    cache = '%s/%s_templates/.%s_fits.pck' % (outDir,var,tagger)
    cachefile = open(cache,'w')
    fitInfo={'var':var,'tagger':tagger,'taggerDef':taggerDef,'slicevar':SLICEVAR,'slicebins':SLICEBINS[SLICEVAR]}
    print ('fitInfo: ')
    print (fitInfo)
    pickle.dump(fitInfo, cachefile,pickle.HIGHEST_PROTOCOL)
    pickle.dump(effExpected, cachefile, pickle.HIGHEST_PROTOCOL)
    pickle.dump(effMeasurements, cachefile, pickle.HIGHEST_PROTOCOL)
    pickle.dump(sfMeasurements, cachefile, pickle.HIGHEST_PROTOCOL)
    print ("systUncs: ", systUncs)
    pickle.dump(systUncs, cachefile, pickle.HIGHEST_PROTOCOL)
    print ("effUncs: ", effUncs)
    pickle.dump(effUncs, cachefile, pickle.HIGHEST_PROTOCOL)
    cachefile.close()
    print ('Fit results have been stored in %s'%cache)

"""
steer the script
"""
def main():

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gROOT.SetBatch(True)

    #configuration
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-t', '--taggers',            dest='taggers'  ,          help='json with list of taggers',    default=None,        type='string')
    parser.add_option('-i', '--inDir',              dest='inDir',              help='input directory with files',   default=None,        type='string')
    parser.add_option('-v', '--var',                dest='var',                help='templated variable',           default='kindisc',   type='string')
    parser.add_option('-s', '--sliceVar',           dest='sliceVar',           help='slicing variable',             default='jetpt',   type='string')
    parser.add_option(      '--recycleTemplates',   dest='recycleTemplates',   help='recycleTemplates',             default=False,       action='store_true')
    parser.add_option('-n', '--njobs',              dest='njobs',              help='# jobs to run in parallel',    default=0,           type='int')
    parser.add_option('-l', '--lumi',               dest='lumi',               help='integrated luminosity',        default=None,        type='float')##2017=41530.0, 2018=59740.0
    parser.add_option('-o', '--outDir',             dest='outDir',             help='output directory',             default='analysis',  type='string')
    parser.add_option(      '--channels',           dest='channels',           help='channels to use',              default='-143',  type='string')#-121=ee,-143=emu,-169=mumu
    parser.add_option(      '--TT_syst',           dest='TT_syst',           help='TT systematic variation',              default='nominal',  type='string')
    (opt, args) = parser.parse_args()

    #update slicing variable
    global SLICEVAR
    SLICEVAR=opt.sliceVar

    TT_syst=opt.TT_syst

    #read list of taggers
    taggersFile = open(opt.taggers,'r')
    taggersList=json.load(taggersFile,encoding='utf-8').items()
    taggersFile.close()

    #channels to filter
    channelList=[ int(k) for k in opt.channels.split(',') ]

    #re-create templates
    if not opt.recycleTemplates:
        task_list=[]
        for var,varMin,varMax in VARSTOFIT:
            os.system('mkdir -p %s/%s_templates'%(opt.outDir,var))
            for tagger,taggerDef in taggersList:
                if var==tagger : continue
                task_list.append((tagger,taggerDef,var,(varMin,varMax),channelList,opt.inDir,opt.outDir,opt.TT_syst))
        print ('%s jobs to run in %d parallel threads' % (len(task_list), opt.njobs))
        #Prepare templates
        if opt.njobs == 0:
            for tagger,taggerDef,var,varRange, channelList,inDir,outDir in task_list:
                prepareTemplates(tagger=tagger,
                                 taggerDef=taggerDef,
                                 var=var,
                                 varRange=varRange,
                                 channelList=channelList,
                                 inDir=inDir,
                                 outDir=outDir,
                                 TT_syst=TT_syst)
        else:
            from multiprocessing import Pool
            pool = Pool(opt.njobs)
            pool.map(runPrepareTemplatesPacked, task_list)

    #run the fits
    print ('Preparing to run fits:')
    ROOT.gSystem.CompileMacro("TTbarSFbFitTools.cc","fk","libTTbarSFbFitTools")
    ROOT.gSystem.Load("libTTbarSFbFitTools.so")
    for var,_,_ in VARSTOFIT:
        for tagger,taggerDef in taggersList:
            runSFFits(var,tagger,taggerDef,opt.lumi,opt.outDir)

    #all done here
    exit(0)


"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())
