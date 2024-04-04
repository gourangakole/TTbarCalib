#include <TFile.h>
#include <TH1.h>

void cloneHistograms(const char* inputFile, const char* outputFile) {
    // Open the input ROOT file
    TFile* inFile = new TFile(inputFile, "READ");
    if (!inFile || inFile->IsZombie()) {
        std::cerr << "Error: Could not open input file " << inputFile << std::endl;
        return;
    }

    // Open the output ROOT file
    TFile* outFile = new TFile(outputFile, "RECREATE");
    if (!outFile || outFile->IsZombie()) {
        std::cerr << "Error: Could not create output file " << outputFile << std::endl;
        inFile->Close();
        delete inFile;
        return;
    }

    // Iterate over the keys in the input file
    TIter nextKey(inFile->GetListOfKeys());
    TKey* key;
    while ((key = dynamic_cast<TKey*>(nextKey()))) {
        // Get the object associated with the key
        TObject* obj = key->ReadObj();
        // Check if the object is a histogram
        if (obj && obj->InheritsFrom(TH1::Class())) {
            // Clone the histogram
            TH1* hist = static_cast<TH1*>(obj->Clone());
            // Write the cloned histogram to the output file
            hist->Write();
            // Delete the cloned histogram (optional)
            delete hist;
        }
    }

    // Close the input and output files
    inFile->Close();
    outFile->Close();

    // Clean up
    delete inFile;
    delete outFile;
}

int main() {
    const char* inputFile = "puwei_2022_postEE.histo.root";
    const char* outputFile = "output.root";

    cloneHistograms(inputFile, outputFile);

    return 0;
}
