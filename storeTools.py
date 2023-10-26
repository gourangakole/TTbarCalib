#################
# storeTools.py
#################
# This code calculates the normalisation for the processes
# Takes the sum(generator weights) histogram (each bin = sum of nominal or systematically varied weights)
# Resets each bin to XS/sum(generator weights)
# This will then be multiplied into each events event weight in TTbarEventAnalysis.cc
# Thus, the resulting distributions only need to be scaled to the desired luminosity, which can be done in the plotting stage

import ROOT, pickle, commands, os

"""
Takes a directory on eos (starting from /store/...) and returns a list of all files with 'prepend' prepended
"""
def getEOSlslist(directory, mask='', prepend='root://eoscms.cern.ch'):
    from subprocess import Popen, PIPE
    print 'looking into: '+directory+'...'

    eos_dir = '/eos/cms/%s' % directory
    eos_cmd = 'eos ' + prepend + ' ls ' + eos_dir
    out = commands.getoutput(eos_cmd)
    full_list = []
    ## if input file was single root file:
    if directory.endswith('.root'):
        if len(out.split('\n')[0]) > 0:
            return [os.path.join(prepend,eos_dir).replace(" ","")]
    ## instead of only the file name append the string to open the file in ROOT
    for line in out.split('\n'):
        if len(line.split()) == 0: continue
        full_list.append(os.path.join(prepend,eos_dir,line).replace(" ",""))
    ## strip the list of files if required
    if mask != '':
        stripped_list = [x for x in full_list if mask in x]
        return stripped_list

    return full_list

"""
Loops over a list of samples and produces a cache file to normalize MC
"""
def produceNormalizationCache(samplesList,inDir,cache,normWgts,integLumi):

    #loop over samples
    for tag,sample in samplesList:
        print('Tag: %s, sample: %s' % (tag,sample))
        if sample[1]==1 :
            print '[storeTools] sample = %i (=data)' % sample[1]
            print 'skipping normWeights in pickle file'
            normWgts[tag]=None
            continue

        if tag in normWgts:
            print '[Warning] won\'t override current definition for',tag,'. Use --resetCache option to override'
            continue

        input_list=getEOSlslist(directory=inDir+'/'+tag)

        print ("gkole 0 input_list:  ", input_list)
        print ("gkole 0 tag:  ", tag )
        fIn=ROOT.TFile.Open(input_list[0])
        tree=fIn.Get("btagana/ttree")
        nentries=tree.GetEntries()
        if nentries > 0:
            tree.GetEntry(0)
            print("Process: %s, File: %s, Generator XS: %s" % (tag, input_list[0], getattr(tree, 'ttbar_w')))
        fIn.Close()

        norigEvents=None
        temp_mcweight = 1.
        # To run the non-tt normalisation xsection uncertainty, multiply the mcweight for non-tt backgrounds by 30%.
        temp_mcweight=temp_mcweight*0.7
        # temp_mcweight=temp_mcweight*1.3

        # Combine all sub-samples for process and sum the weights
        for f in input_list:
            fIn=ROOT.TFile.Open(f)
            tree=fIn.Get("btagana/ttree")
            nentries=tree.GetEntries()
            print('nentries: ', nentries)
            if nentries > 0 and 'MC13TeV' in tag:
                for entry in xrange(0,nentries):
                    tree.GetEntry(entry)
                    temp_mcweight = getattr(tree, 'ttbar_w')
            '''
            if norigEvents is None:
                # Clone and reset just the histogram integral, contents and error (ICE)
                norigEvents=fIn.Get('ttbarselectionproducer/wgtcounter').Clone('normwgts')
                norigEvents.SetDirectory(0)
                norigEvents.Reset('ICE')
            # Add wgtcounter histogram from this file to combined histogram
            # wgtcounter histogram bin 1 is filled with nominal generator weight value
            wgtcounter_hist = fIn.Get('ttbarselectionproducer/wgtcounter')
            norigEvents.Add(wgtcounter_hist)
            fIn.Close()
        try:
            # Each bin in norigEvents gives the sum of weights for the nominal or systematic variation
            # This is for all events BEFORE any selection i.e all events generated
            # Loop over all entries and replace each bin content with the 1/sum(gen weights)
            print "sum(weights) = %s" % (norigEvents.GetBinContent(1))
            for xbin in xrange(1,norigEvents.GetNbinsX()+1):
                #print "Nominal weight entry: TAG = %s , sum(weights) = %s" % (tag, norigEvents.GetBinContent(xbin))
                #print "Fill wgtcounter with ", 1./norigEvents.GetBinContent(xbin)
                norigEvents.SetBinContent(xbin,1./norigEvents.GetBinContent(xbin))
                norigEvents.SetBinError(xbin,0.)
        except:
            print 'No normalization histogram for ',tag
            '''
        # normWgts[tag]  = norigEvents
        # integLumi[tag] = 1./norigEvents.GetBinContent(1) if norigEvents else 0.
        normWgts[tag]  = temp_mcweight
        integLumi[tag] = 1./temp_mcweight if temp_mcweight else 0.
        if temp_mcweight:
            print('%s: 1/sum(LHEWeight) = %.10f' % (tag, normWgts[tag]))

    #dump to file
    cachefile=open(cache,'w')
    pickle.dump(normWgts, cachefile, pickle.HIGHEST_PROTOCOL)
    pickle.dump(integLumi, cachefile, pickle.HIGHEST_PROTOCOL)
    cachefile.close()
    print 'Produced normalization cache and pileup weights @ %s'%cache

    return normWgts,integLumi
