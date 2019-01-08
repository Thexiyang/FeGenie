#!/usr/bin/env python3
# !/bin/sh
from collections import defaultdict
import re
import os
import textwrap
import argparse
import urllib.request
import ssl


# TODO: ADD CYTOCHROME 579 HMM (next release)
# TODO: FIX HMM CROSS VALIDATION
# UPDATE: removed constraints on MtrC identification as an Fe reductase
# UPDATE: raised minimum siderophore cluster size to three


def derep(ls):
    outLS = []
    for i in ls:
        if i not in outLS:
            outLS.append(i)
    return outLS


def cluster(data, maxgap):
    '''Arrange data into groups where successive elements
       differ by no more than *maxgap*

        #->>> cluster([1, 6, 9, 100, 102, 105, 109, 134, 139], maxgap=10)
        [[1, 6, 9], [100, 102, 105, 109], [134, 139]]

        #->>> cluster([1, 6, 9, 99, 100, 102, 105, 134, 139, 141], maxgap=10)
        [[1, 6, 9], [99, 100, 102, 105], [134, 139, 141]]

    '''
    # data = sorted(data)
    data.sort(key=int)
    groups = [[data[0]]]
    for x in data[1:]:
        if abs(x - groups[-1][-1]) <= maxgap:
            groups[-1].append(x)
        else:
            groups.append([x])
    return groups


def lastItem(ls):
    x = ''
    for i in ls:
        x = i
    return x


def RemoveDuplicates(ls):
    empLS = []
    counter = 0
    for i in ls:
        if i not in empLS:
            empLS.append(i)
        else:
            pass
    return empLS


def allButTheLast(iterable, delim):
    x = ''
    length = len(iterable.split(delim))
    for i in range(0, length-1):
        x += iterable.split(delim)[i]
        x += delim
    return x[0:len(x)-1]


def secondToLastItem(ls):
    x = ''
    for i in ls[0:len(ls)-1]:
        x = i
    return x


def pull(item, one, two):
    ls = []
    counter = 0
    for i in item:
        if counter == 0:
            if i != one:
                pass
            else:
                counter += 1
                ls.append(i)
        else:
            if i != two:
                ls.append(i)
            else:
                ls.append(i)
                counter = 0
    outstr = "".join(ls)
    return outstr


def stabilityCounter(int):
    if len(str(int)) == 1:
        string = (str(0) + str(0) + str(0) + str(0) + str(int))
        return (string)
    if len(str(int)) == 2:
        string = (str(0) + str(0) + str(0) + str(int))
        return (string)
    if len(str(int)) == 3:
        string = (str(0) + str(0) + str(int))
        return (string)
    if len(str(int)) == 4:
        string = (str(0) + str(int))
        return (string)


def replace(stringOrlist, list, item):
    emptyList = []
    for i in stringOrlist:
        if i not in list:
            emptyList.append(i)
        else:
            emptyList.append(item)
    outString = "".join(emptyList)
    return outString


def remove(stringOrlist, list):
    emptyList = []
    for i in stringOrlist:
        if i not in list:
            emptyList.append(i)
        else:
            pass
    outString = "".join(emptyList)
    return outString


def remove2(stringOrlist, list):
    emptyList = []
    for i in stringOrlist:
        if i not in list:
            emptyList.append(i)
        else:
            pass
    # outString = "".join(emptyList)
    return emptyList


def removeLS(stringOrlist, list):
    emptyList = []
    for i in stringOrlist:
        if i not in list:
            emptyList.append(i)
        else:
            pass
    return emptyList


def fasta(fasta_file):
    seq = ''
    header = ''
    Dict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
    for i in fasta_file:
        i = i.rstrip()
        if re.match(r'^>', i):
            if len(seq) > 0:
                Dict[header] = seq
                header = i[1:]
                seq = ''
            else:
                header = i[1:]
                seq = ''
        else:
            seq += i
    Dict[header] = seq
    # print(count)
    return Dict


def filter(list, items):
    outLS = []
    for i in list:
        if i not in items:
            outLS.append(i)
    return outLS


def delim(line):
    ls = []
    string = ''
    for i in line:
        if i != " ":
            string += i
        else:
            ls.append(string)
            string = ''
    ls = filter(ls, [""])
    return ls


parser = argparse.ArgumentParser(
    prog="FeGenie.py",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''
    *******************************************************

    Developed by Arkadiy Garber and Nancy Merino;
    University of Southern California, Earth Sciences
    Please send comments and inquiries to arkadiyg@usc.edu

    *******************************************************
    '''))

parser.add_argument('-hmm_lib', type=str, help='HMM database; directory titled \'HMM-lib\', can be found in the FeGenie folder')

parser.add_argument('-bin_dir', type=str, help="directory of bins")

parser.add_argument('-bin_ext', type=str, help="extension for bins (do not include the period)")

parser.add_argument('-contigs_source', type=str, help="are the provided contigs from a single organism (single)"
                                                     "or metagenomic/metatranscriptomic assemblies (meta)? "
                                                     "(default=single)", default="single")

parser.add_argument('-bit', type=str, help="tsv file with bitscore cut-offs for all HMMs")

parser.add_argument('-d', type=int, help="maximum distance between genes to be considered in a genomic \'cluster\'."
                                         "This number should be an integer and should reflect the maximum number of "
                                         "genes in between putative iron-related genes identified by the HMM database "
                                         "(default=10)", default=10)

parser.add_argument('-pfam', type=str, help="location of Pfam HMM (optional, if you want the identified candidate"
                                            "iron genes to be compared against Pfam)", default="NA")

parser.add_argument('-nr', type=str, help="path to NCBI's nr database (optional, if you want the identified candidate "
                                          "iron genes compared against NCBI)", default="NA")

parser.add_argument('-R', type=str, help="location of R scripts directory (optional, only if you would like to obtain"
                                         "dotplot, dendrogram, and heatmap summaries of your data)", default="NA")

parser.add_argument('-out', type=str, help="name of output file; please provide full path (default=fegenie_out)", default="fegenie_out")

parser.add_argument('-inflation', type=int, help="inflation factor for final gene category counts (default=1000)",
                    default=1000)

parser.add_argument('-t', type=int, help="number of threads to use for DIAMOND BLAST and HMMSEARCH "
                                         "(default=1, max=16)", default=1)

args = parser.parse_args()


# **************************************************************************************************************
# ********************************************* PART 1 *********************************************************
# **************************************************************************************************************

# *************** SET DIRECTORY LOCATION VARIABLES ************************** #
print("starting pipeline...")
cwd = os.getcwd()
os.system("mkdir %s" % args.out)
outDirectory = "%s" % args.out
outDirectoryLS = os.listdir("%s" % args.out)

if args.pfam != "NA":
    PFAM = args.pfam
    PFAMnameDict = defaultdict(lambda: defaultdict(lambda: "EMPTY"))
    pfam = open(args.pfam, "r")
    for entry in pfam:
        if re.match(r'NAME', entry):
            name = entry.rstrip().split("  ")[1]
        if re.match(r'DESC', entry):
            desc = entry.rstrip().split("  ")[1]
            PFAMnameDict[name] = desc
else:
    pass

binDir = args.bin_dir + "/"
binDirLS = os.listdir(args.bin_dir)


# *************** MAKE NR A DIAMOND DB AND READ THE FILE INTO HASH MEMORY ************************ #
if args.nr != "NA":
    try:
        testFile = open(args.nr + ".dmnd")
        print("Found Diamond database file: " + args.nr + ".dmnd")
        print("Skipping the building")

    except FileNotFoundError:
        print("Diamond database not found. Mkaing the database now")
        os.system("diamond makedb --in %s -d %s" % (args.nr, args.nr))


    nr = open(args.nr, "r")
    nrDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
    print("Reading nr into Dict memory")
    for i in nr:
        if re.match('>', i):
            accession = i.rstrip().split(" ")[0][1:]
            header = replace(i.rstrip(), [","], ";")
            header = header[1:]
            nrDict[accession] = header
else:
    pass


# *************** CALL ORFS FROM BINS AND READ THE ORFS INTO HASH MEMORY ************************ #
BinDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
for i in binDirLS:
    if lastItem(i.split(".")) == args.bin_ext:
        cell = i
        try:
            testFile = open("%s%s-proteins.faa" % (binDir, i), "r")
            print("ORFS for %s found. Skipping Prodigal." % i)

        except FileNotFoundError:
            if args.contigs_source == "single":
                os.system("prodigal -i %s%s -a %s%s-proteins.faa -o %s%s-prodigal.out" % (binDir, i, binDir, i, binDir, i))
            else:
                os.system("prodigal -i %s%s -a %s%s-proteins.faa -o %s%s-prodigal.out -p meta" % (binDir, i, binDir, i, binDir, i))

        file = open(binDir + i + "-proteins.faa", "r")
        file = fasta(file)
        for j in file.keys():
            orf = j.split(" # ")[0]
            BinDict[cell][orf] = file[j]


# ******************** READ BITSCORE CUT-OFFS INTO HASH MEMORY ****************************** #
meta = open(args.bit, "r")
metaDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
for i in meta:
    ls = i.rstrip().split("\t")
    metaDict[ls[0]] = ls[1]


# ******************* BEGINNING MAIN ALGORITHM **********************************))))


FerrJinnDir = os.listdir(args.hmm_lib)
for FeCategory in FerrJinnDir:
    if FeCategory != ".DS_Store":
        print("")
        print("Looking for following iron-related functional category: " + FeCategory)
        hmmDir = args.hmm_lib + "/%s/" % FeCategory
        hmmDirLS = os.listdir(args.hmm_lib + "/%s" % FeCategory)

        HMMdict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: "EMPTY")))
        for i in binDirLS:  # ITERATION THROUGH EACH BIN IN A GIVEN DIRECTORY OF BINS
            if lastItem(i.split(".")) == args.bin_ext:  # FILTERING OUT ANY NON-BIN-RELATED FILES
                print("analyzing: " + i)
                FASTA = open(binDir + i + "-proteins.faa", "r")
                FASTA = fasta(FASTA)
                os.system(
                    "mkdir " + binDir + "/" + i + "-HMM")  # CREATING DIRECTORY, FOR EACH BIN, TO WHICH HMMSEARCH RESULTS
                # WILL BE WRITTEN
                for hmm in hmmDirLS:  # ITERATING THROUGH ALL THE HMM FILES IN THE HMM DIRECTORY
                    if len(metaDict[hmm.split(".")[0]]) == 0:
                        bit = 0
                    else:
                        bit = metaDict[hmm.split(".")[0]]

                    if re.findall(r'\.hmm', hmm):  # AVOIDING THE ALIGNMENT FOLDER
                        # print("performing HMMSEARCH")
                        os.system(
                            "hmmsearch --cpu %d -T %d --tblout %s/%s-HMM/%s.tblout -o %s/%s-HMM/%s.txt %s/%s %s/%s-proteins.faa"
                            % (int(args.t), float(bit), binDir, i, hmm, binDir, i, hmm, hmmDir, hmm, binDir, i))

                        # REMOVING THE STANDARD OUTPUT FILE
                        os.system("rm " + binDir + "/" + i + "-HMM/" + hmm + ".txt")

                        # READING IN THE HMMSEARCH RESULTS (TBLOUT) OUT FILE
                        hmmout = open(binDir + i + "-HMM/" + hmm + ".tblout", "r")

                        # COLLECTING SIGNIFICANT HMM HITS IN THE FILE
                        for line in hmmout:
                            if not re.match(r'#', line):
                                # print(line)
                                ls = delim(line)
                                evalue = float(ls[4])
                                bit = float(ls[5])
                                orf = ls[0]
                                if evalue < float(1E-1):  # FILTERING OUT BACKGROUND NOISE
                                    # LOADING HMM HIT INTO DICTIONARY, BUT ONLY IF THE ORF DID NOT HAVE ANY OTHER HMM HITS

                                    if orf not in HMMdict[i]:
                                        HMMdict[i][orf]["hmm"] = hmm
                                        HMMdict[i][orf]["evalue"] = evalue
                                        HMMdict[i][orf]["bit"] = bit
                                    else:
                                        # COMPARING HITS FROM DIFFERENT HMM FILES TO THE SAME ORF
                                        if bit > HMMdict[i][orf]["bit"]:
                                            HMMdict[i][orf]["hmm"] = hmm
                                            HMMdict[i][orf]["evalue"] = evalue
                                            HMMdict[i][orf]["bit"] = bit
                                        else:
                                            pass

                                else:
                                    pass

                            else:
                                pass
                os.system("rm -r " + binDir + "/" + i + "-HMM")

        out = open(outDirectory + "/%s-summary.csv" % (FeCategory), "w")
        out.write("cell" + "," + "ORF" + "," + "HMM" + "," + "evalue" + "," + "bitscore" + "\n")
        for key in HMMdict.keys():
            # print(key)
            for j in HMMdict[key]:
                # print("cell: " + key + " - ORF: " + j)
                out.write(key + "," + j + "," + HMMdict[key][j]["hmm"] + "," +
                          str(HMMdict[key][j]["evalue"]) + "," + str(HMMdict[key][j]["bit"]) + "\n")

        out.close()

        # CREATING A FASTA FILE BASED ON HMM SEARCH RESULTS
        print("writing FASTA files")
        summary = open(outDirectory + "/%s-summary.csv" % (FeCategory), "r")
        outFASTA = open(outDirectory + "/%s-summary.fa" % (FeCategory), "w")

        for j in summary:
            ls = j.rstrip().split(",")
            if ls[0] != "cell":
                orf = ls[1]
                cell = ls[0]
                seq = BinDict[cell][orf]
                outFASTA.write(">" + cell + "|" + orf + "\n")
                outFASTA.write(seq + "\n")

        outFASTA.close()
        summary.close()

        # HMMSEARCH OF FASTA FILE AGAINST PFAM

        summaryFASTA = open("%s/%s-summary.fa" % (outDirectory, FeCategory))
        numSeqs = 0
        for SEQ in summaryFASTA:
            if re.findall(r'>', SEQ):
                numSeqs += 1

        if numSeqs > 0:
            if args.nr != "NA":
                print("Performing Diamond BLASTx search of putative iron genes against NCBI's nr database")
                if args.t <= 16:
                    os.system(
                        "diamond blastp --db %s.dmnd --out %s/%s.dmndout --max-target-seqs 1 --outfmt 6 --threads %d "
                        "--query %s/%s-summary.fa"
                        % (args.nr, outDirectory, FeCategory, args.t, outDirectory, FeCategory))
                else:
                    os.system(
                        "diamond blastp --db %s.dmnd --out %s/%s.dmndout --max-target-seqs 1 --outfmt 6 --threads 16 "
                        "--query %s/%s-summary.fa"
                        % (args.nr, outDirectory, FeCategory, outDirectory, FeCategory))

                print("reading BLASTx results")
                dmndblastDict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 'EMPTY')))
                dmndblast = open("%s/%s.dmndout" % (outDirectory, FeCategory), "r")
                for hit in dmndblast:
                    lst = hit.rstrip().split("\t")
                    evalue = lst[10]
                    cell = lst[0].split("|")[0]
                    orf = lst[0].split("|")[1]
                    target = nrDict[lst[1]]
                    dmndblastDict[cell][orf]["e"] = evalue
                    dmndblastDict[cell][orf]["target"] = target
            else:
                print("Skipping NCBI cross-validation")

print("Preparing final summary file")
OUT = open(outDirectory + "/FinalSummary.csv", "w")

if args.nr != "NA":
    OUT.write(
        "category" + "," + "cell" + "," + "orf" + "," + "related_hmm" + "," + "HMM-bitscore" + "," + "NCBI_closest_match"
        + "," + "NCBI_aln_eval" + "\n")

if args.nr == "NA":
    OUT.write("category" + "," + "cell" + "," + "orf" + "," + "related_hmm" + "," + "HMM-bitscore" + "\n")

resultsDir = os.listdir(outDirectory)

MasterDict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 'EMPTY')))
for i in resultsDir:
    if lastItem(i.split("-")) == "summary.csv":
        result = open(outDirectory + "/" + i, "r")
        for j in result:
            ls = j.rstrip().split(",")
            cell = ls[0]
            orf = ls[1]
            hmm = ls[2]
            bit = ls[4]

            if cell != "cell":

                OUT.write(i.split("-summary")[0] + "," + cell + "," + orf + "," + hmm + "," + str(bit) + ",")
                if args.nr != "NA":
                    if cell in dmndblastDict.keys() and orf in dmndblastDict[cell]:
                        OUT.write(
                            dmndblastDict[cell][orf]["target"] + "," + str(dmndblastDict[cell][orf]["e"]) + ",")
                    else:
                        OUT.write("NA" + "," + "NA" + ",")
                else:
                    pass

                OUT.write("\n")
OUT.close()
# ****************************************** DEREPLICATION *********************************************************
summary = open(outDirectory + "/FinalSummary.csv", "r")
SummaryDict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 'EMPTY')))
for i in summary:
    ls = i.rstrip().split(",")
    if ls[0] != "category" and ls[0] != "FeGenie":
        if len(ls) > 0:
            category = ls[0]
            cell = ls[1]
            orf = ls[2]
            hmm = ls[3]
            hmmBit = ls[4]

            if args.nr != "NA":
                NCBImatch = ls[5]
                NCBIeval = ls[6]
            if args.nr == "NA":
                pass

            if cell not in SummaryDict.keys():
                SummaryDict[cell][orf]["hmm"] = hmm
                SummaryDict[cell][orf]["hmmBit"] = hmmBit
                SummaryDict[cell][orf]["category"] = category

                if args.nr != "NA":
                    SummaryDict[cell][orf]["NCBImatch"] = NCBImatch
                    SummaryDict[cell][orf]["NCBIeval"] = NCBIeval
            else:
                if orf not in SummaryDict[cell]:
                    SummaryDict[cell][orf]["hmm"] = hmm
                    SummaryDict[cell][orf]["hmmBit"] = hmmBit
                    SummaryDict[cell][orf]["category"] = category
                    if args.nr != "NA":
                        SummaryDict[cell][orf]["NCBImatch"] = NCBImatch
                        SummaryDict[cell][orf]["NCBIeval"] = NCBIeval
                else:
                    if float(hmmBit) > float(SummaryDict[cell][orf]["hmmBit"]):
                        SummaryDict[cell][orf]["hmm"] = hmm
                        SummaryDict[cell][orf]["hmmBit"] = hmmBit
                        SummaryDict[cell][orf]["category"] = category
                        if args.nr != "NA":
                            SummaryDict[cell][orf]["NCBImatch"] = NCBImatch
                            SummaryDict[cell][orf]["NCBIeval"] = NCBIeval
                    else:
                        pass

# ****************************** CLUSTERING OF ORFS BASED ON GENOMIC PROXIMITY *************************************
CoordDict = defaultdict(lambda: defaultdict(list))
print("Building Coordinates dictionary")
try:
    for i in SummaryDict.keys():
        if i != "category":
            for j in SummaryDict[i]:
                contig = allButTheLast(j, "_")
                numOrf = lastItem(j.split("_"))
                CoordDict[i][contig].append(int(numOrf))

    print("Clustering ORFs...")
    OUT2 = open(outDirectory + "/FinalSummary-dereplicated-clustered.csv", "w")
    for i in CoordDict.keys():
        for j in CoordDict[i]:
            LS = (CoordDict[i][j])
            clusters = (cluster(LS, args.d))
            for k in clusters:
                if len(RemoveDuplicates(k)) == 1:
                    orf = j + "_" + str(k[0])

                    if args.nr != "NA":
                        ncbiHomolog = SummaryDict[i][orf]["NCBImatch"]
                        if ncbiHomolog != "NA":
                            ncbiHomolog = ncbiHomolog.split("]")[0] + "]"
                        else:
                            ncbiHomolog = "NA"

                        OUT2.write(SummaryDict[i][orf]["category"] + "," + i + "," + orf + "," +
                                   SummaryDict[i][orf]["hmm"] + "," + str(SummaryDict[i][orf]["hmmBit"]) + "," +
                                   ncbiHomolog + "," + str(SummaryDict[i][orf]["NCBIeval"]) + "," +
                                   str(SummaryDict[i][orf]["PfamBit"]) + "\n")
                        OUT2.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
                    else:
                        OUT2.write(SummaryDict[i][orf]["category"] + "," + i + "," + orf + "," +
                                   SummaryDict[i][orf]["hmm"] + "," + str(SummaryDict[i][orf]["hmmBit"]) + "\n")
                        OUT2.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")

                else:
                    if args.nr != "NA":
                        for l in RemoveDuplicates(k):
                            orf = j + "_" + str(l)
                            ncbiHomolog = SummaryDict[i][orf]["NCBImatch"]
                            if ncbiHomolog != "NA":
                                ncbiHomolog = ncbiHomolog.split("]")[0] + "]"
                            else:
                                ncbiHomolog = "NA"

                            OUT2.write(
                                SummaryDict[i][orf]["category"] + "," + i + "," + orf + "," + SummaryDict[i][orf]["hmm"]
                                + "," + str(SummaryDict[i][orf]["hmmBit"]) + "," + ncbiHomolog
                                + "," + str(SummaryDict[i][orf]["NCBIeval"]) + "\n")
                        OUT2.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
                    else:
                        for l in k:
                            orf = j + "_" + str(l)

                            OUT2.write(
                                SummaryDict[i][orf]["category"] + "," + i + "," + orf + "," + SummaryDict[i][orf]["hmm"]
                                + "," + str(SummaryDict[i][orf]["hmmBit"]) + "\n")
                        OUT2.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
    OUT2.close()
except ValueError:
    print("")
    print("Fegenie was attempting to cluster your identified iron genes based on genomic proximity, but it looks like"
          "the FASTA files with ORFs does not have the expected header format that is "
          "created with Prodigal. No biggie. FeGenie will still give you your candidate iron genes; however, "
          "clusters will not be identified.\n")
    OUT2 = open(outDirectory + "/FinalSummary-dereplicated-clustered.csv", "w")
    for i in SummaryDict.keys():
        for j in SummaryDict[i]:
            if args.nr != "NA":
                ncbiHomolog = SummaryDict[i][j]["NCBImatch"]
                if ncbiHomolog != "NA":
                    ncbiHomolog = ncbiHomolog.split("]")[0] + "]"
                else:
                    ncbiHomolog = "NA"

                OUT2.write(SummaryDict[i][j]["category"] + "," + i + "," + j + "," +
                           SummaryDict[i][j]["hmm"] + "," + str(SummaryDict[i][j]["hmmBit"]) + "," +
                           ncbiHomolog + "," + str(SummaryDict[i][j]["NCBIeval"]) + "," +
                           str(SummaryDict[i][j]["PfamBit"]) + "\n")
                OUT2.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
            else:
                OUT2.write(SummaryDict[i][j]["category"] + "," + i + "," + j + "," +
                           SummaryDict[i][j]["hmm"] + "," + str(SummaryDict[i][j]["hmmBit"]) + "\n")
                OUT2.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
    OUT2.close()


# ****************************** REMOVING REDUNDANT HITS TO THE SAME ORFS ************************************
counter = 0
OUT23 = open(outDirectory + "/FinalSummary-clustered-dereplicated.csv", "w")
clustDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
final = open(outDirectory + "/FinalSummary-dereplicated-clustered.csv", "r")
for i in final:
    ls = i.rstrip().split(",")
    if ls[0] == "" and counter == 0:
        for j in clustDict.keys():
            OUT23.write(clustDict[j])
        OUT23.write("\n")
        clustDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
        counter += 1
    elif ls[0] == "" and counter != 0:
        counter = 0
    else:
        if ls[2] not in clustDict.keys():
            clustDict[ls[2]] = i
            counter = 0
OUT23.close()

# ****************************** FILTERING IRON OXIDATION/REDUCTION HITS *************************************
Cyc2 = ["Cyc2_repCluster1.hmm", "Cyc2_repCluster2.hmm", "Cyc2_repCluster3.hmm"]

FilterDict = defaultdict(lambda: defaultdict(list))
summary = open(outDirectory + "/FinalSummary-clustered-dereplicated.csv", "r")
for i in summary:
    ls = (i.rstrip().split(","))
    if ls[0] != "":
        FilterDict[ls[1]][ls[3]].append(ls[2])
    else:
        pass

Cyc2dict = defaultdict(lambda: defaultdict(list))
Mtx2dict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
FoxEYZdict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
FoxABCdict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
mamDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
flavinDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
for i in FilterDict.keys():
    if len(FilterDict[i]["FmnA.hmm"]) > 0:
        if len(FilterDict[i]["FmnA.hmm"]) + len(FilterDict[i]["DmkA.hmm"]) + len(FilterDict[i]["FmnB.hmm"]) + \
                len(FilterDict[i]["PplA.hmm"]) + len(FilterDict[i]["Ndh2.hmm"]) + len(FilterDict[i]["EetA.hmm"]) + \
            len(FilterDict[i]["EetB.hmm"]) + len(FilterDict[i]["DmkB.hmm"]) > 6:
            flavinDict[i]["FmnA.hmm"] = "iron_reduction"
    if len(FilterDict[i]["DmkA.hmm"]) > 0:
        if len(FilterDict[i]["FmnA.hmm"]) + len(FilterDict[i]["DmkA.hmm"]) + len(FilterDict[i]["FmnB.hmm"]) + \
                len(FilterDict[i]["PplA.hmm"]) + len(FilterDict[i]["Ndh2.hmm"]) + len(FilterDict[i]["EetA.hmm"]) + \
            len(FilterDict[i]["EetB.hmm"]) + len(FilterDict[i]["DmkB.hmm"]) > 6:
            flavinDict[i]["DmkA.hmm"] = "iron_reduction"
    if len(FilterDict[i]["FmnB.hmm"]) > 0:
        if len(FilterDict[i]["FmnA.hmm"]) + len(FilterDict[i]["DmkA.hmm"]) + len(FilterDict[i]["FmnB.hmm"]) + \
                len(FilterDict[i]["PplA.hmm"]) + len(FilterDict[i]["Ndh2.hmm"]) + len(FilterDict[i]["EetA.hmm"]) + \
            len(FilterDict[i]["EetB.hmm"]) + len(FilterDict[i]["DmkB.hmm"]) > 6:
            flavinDict[i]["FmnB.hmm"] = "iron_reduction"
    if len(FilterDict[i]["PplA.hmm"]) > 0:
        if len(FilterDict[i]["FmnA.hmm"]) + len(FilterDict[i]["DmkA.hmm"]) + len(FilterDict[i]["FmnB.hmm"]) + \
                len(FilterDict[i]["PplA.hmm"]) + len(FilterDict[i]["Ndh2.hmm"]) + len(FilterDict[i]["EetA.hmm"]) + \
            len(FilterDict[i]["EetB.hmm"]) + len(FilterDict[i]["DmkB.hmm"]) > 6:
            flavinDict[i]["PplA.hmm"] = "iron_reduction"
    if len(FilterDict[i]["Ndh2.hmm"]) > 0:
        if len(FilterDict[i]["FmnA.hmm"]) + len(FilterDict[i]["DmkA.hmm"]) + len(FilterDict[i]["FmnB.hmm"]) + \
                len(FilterDict[i]["PplA.hmm"]) + len(FilterDict[i]["Ndh2.hmm"]) + len(FilterDict[i]["EetA.hmm"]) + \
            len(FilterDict[i]["EetB.hmm"]) + len(FilterDict[i]["DmkB.hmm"]) > 6:
            flavinDict[i]["Ndh2.hmm"] = "iron_reduction"
    if len(FilterDict[i]["EetA.hmm"]) > 0:
        if len(FilterDict[i]["FmnA.hmm"]) + len(FilterDict[i]["DmkA.hmm"]) + len(FilterDict[i]["FmnB.hmm"]) + \
                len(FilterDict[i]["PplA.hmm"]) + len(FilterDict[i]["Ndh2.hmm"]) + len(FilterDict[i]["EetA.hmm"]) + \
            len(FilterDict[i]["EetB.hmm"]) + len(FilterDict[i]["DmkB.hmm"]) > 6:
            flavinDict[i]["EetA.hmm"] = "iron_reduction"
    if len(FilterDict[i]["EetB.hmm"]) > 0:
        if len(FilterDict[i]["FmnA.hmm"]) + len(FilterDict[i]["DmkA.hmm"]) + len(FilterDict[i]["FmnB.hmm"]) + \
                len(FilterDict[i]["PplA.hmm"]) + len(FilterDict[i]["Ndh2.hmm"]) + len(FilterDict[i]["EetA.hmm"]) + \
            len(FilterDict[i]["EetB.hmm"]) + len(FilterDict[i]["DmkB.hmm"]) > 6:
            flavinDict[i]["EetB.hmm"] = "iron_reduction"
    if len(FilterDict[i]["DmkB.hmm"]) > 0:
        if len(FilterDict[i]["FmnA.hmm"]) + len(FilterDict[i]["DmkA.hmm"]) + len(FilterDict[i]["FmnB.hmm"]) + \
                len(FilterDict[i]["PplA.hmm"]) + len(FilterDict[i]["Ndh2.hmm"]) + len(FilterDict[i]["EetA.hmm"]) + \
            len(FilterDict[i]["EetB.hmm"]) + len(FilterDict[i]["DmkB.hmm"]) > 6:
            flavinDict[i]["DmkB.hmm"] = "iron_reduction"

    if len(FilterDict[i]["Cyc1.hmm"]) > 0:
        if len(FilterDict[i]["Cyc2_repCluster1.hmm"] + FilterDict[i]["Cyc2_repCluster2.hmm"] +
                       FilterDict[i]["Cyc2_repCluster3.hmm"]) > 0:
            Cyc2dict[i]["Cyc1.hmm"].append(i)

    if len(FilterDict[i]["MtrB_TIGR03509.hmm"]) > 0:

        if len(FilterDict[i]["MtoA.hmm"]) > 0:
            if len(FilterDict[i]["MtrC_TIGR03507.hmm"]) == 0:
                Mtx2dict[i]["MtrB_TIGR03509.hmm"] = "iron_oxidation"
            else:
                Mtx2dict[i]["MtrB_TIGR03509.hmm"] = "iron_reduction"

        elif len(FilterDict[i]["MtrA.hmm"]) > 0:
            if len(FilterDict[i]["MtrC_TIGR03507.hmm"]) == 0:
                Mtx2dict[i]["MtrB_TIGR03509.hmm"] = "iron_oxidation"
            else:
                Mtx2dict[i]["MtrB_TIGR03509.hmm"] = "iron_reduction"

    if len(FilterDict[i]["MtoA.hmm"]) > 0:
        if len(FilterDict[i]["MtrB_TIGR03509.hmm"]) > 0 and len(FilterDict[i]["MtrC_TIGR03507.hmm"]) == 0:
            Mtx2dict[i]["MtoA.hmm"] = "iron_oxidation"

        if len(FilterDict[i]["MtrB_TIGR03509.hmm"]) > 0 and len(FilterDict[i]["MtrC_TIGR03507.hmm"]) > 0:
            Mtx2dict[i]["MtoA.hmm"] = "iron_reduction"

    if len(FilterDict[i]["MtrA.hmm"]) > 0:
        if len(FilterDict[i]["MtrB_TIGR03509.hmm"]) > 0 and len(FilterDict[i]["MtrC_TIGR03507.hmm"]) == 0:
            Mtx2dict[i]["MtrA.hmm"] = "iron_oxidation"

        if len(FilterDict[i]["MtrB_TIGR03509.hmm"]) > 0 and len(FilterDict[i]["MtrC_TIGR03507.hmm"]) > 0:
            Mtx2dict[i]["MtrA.hmm"] = "iron_reduction"

    if len(FilterDict[i]["MtrC_TIGR03507.hmm"]) > 0:
        # if len(FilterDict[i]["MtrB_TIGR03509.hmm"]) > 0 and len(FilterDict[i]["MtrA.hmm"]) == 0 and \
        #                 len(FilterDict[i]["MtoA.hmm"]) == 0:
        #     Mtx2dict[i]["MtrC_TIGR03507.hmm"] = "iron_oxidation"
        #
        # if len(FilterDict[i]["MtrB_TIGR03509.hmm"]) > 0 and \
        #         (len(FilterDict[i]["MtoA.hmm"]) > 0 or len(FilterDict[i]["MtrA.hmm"]) > 0):
        #     Mtx2dict[i]["MtrB_TIGR03507.hmm"] = "iron_reduction"
        Mtx2dict[i]["MtrC_TIGR03507.hmm"] = "iron_reduction"

    if len(FilterDict[i]["FoxY.hmm"]) > 0:
        if len(FilterDict[i]["FoxZ.hmm"]) > 0 or len(FilterDict[i]["FoxE.hmm"]) > 0:
            FoxEYZdict[i]["FoxY.hmm"] = "iron_oxidation"
    if len(FilterDict[i]["FoxZ.hmm"]) > 0:
        if len(FilterDict[i]["FoxY.hmm"]) > 0 or len(FilterDict[i]["FoxE.hmm"]) > 0:
            FoxEYZdict[i]["FoxZ.hmm"] = "iron_oxidation"
    if len(FilterDict[i]["FoxE.hmm"]) > 0:
        if len(FilterDict[i]["FoxZ.hmm"]) > 0 or len(FilterDict[i]["FoxY.hmm"]) > 0:
            FoxEYZdict[i]["FoxE.hmm"] = "iron_oxidation"

    if len(FilterDict[i]["FoxA.hmm"]) > 0:
        if len(FilterDict[i]["FoxB.hmm"]) > 0 or len(FilterDict[i]["FoxC.hmm"]) > 0:
            FoxABCdict[i]["FoxA.hmm"] = "iron_oxidation"
    if len(FilterDict[i]["FoxB.hmm"]) > 0:
        if len(FilterDict[i]["FoxC.hmm"]) > 0 or len(FilterDict[i]["FoxA.hmm"]) > 0:
            FoxABCdict[i]["FoxB.hmm"] = "iron_oxidation"
    if len(FilterDict[i]["FoxC.hmm"]) > 0:
        if len(FilterDict[i]["FoxB.hmm"]) > 0 or len(FilterDict[i]["FoxA.hmm"]) > 0:
            FoxABCdict[i]["FoxC.hmm"] = "iron_oxidation"

    # MAGNETOSOME FORMATION
    # if len(FilterDict[i]["MamA.hmm"]) > 0:
    #     if len(FilterDict[i]["MamB.hmm"]) + len(FilterDict[i]["MamC.hmm"]) + len(FilterDict[i]["MamD.hmm"])\
    #             + len(FilterDict[i]["MamF.hmm"]) + len(FilterDict[i]["MamG.hmm"]) + len(FilterDict[i]["MamJ.hmm"]) \
    #             + len(FilterDict[i]["MamK.hmm"]) + len(FilterDict[i]["MamM.hmm"]) + len(FilterDict[i]["MamP.hmm"]) \
    #             + len(FilterDict[i]["MamW.hmm"]) + len(FilterDict[i]["MamX.hmm"]) + len(FilterDict[i]["MamY.hmm"]) > 0:
    #         mamDict[i]["MamA.hmm"] = "magnetosome_formation"
    #
    # elif len(FilterDict[i]["MamE.hmm"]) > 0:
    #     if len(FilterDict[i]["MamB.hmm"]) + len(FilterDict[i]["MamC.hmm"]) + len(FilterDict[i]["MamD.hmm"])\
    #             + len(FilterDict[i]["MamF.hmm"]) + len(FilterDict[i]["MamG.hmm"]) + len(FilterDict[i]["MamJ.hmm"]) \
    #             + len(FilterDict[i]["MamK.hmm"]) + len(FilterDict[i]["MamM.hmm"]) + len(FilterDict[i]["MamP.hmm"]) \
    #             + len(FilterDict[i]["MamW.hmm"]) + len(FilterDict[i]["MamX.hmm"]) + len(FilterDict[i]["MamY.hmm"]) > 0:
    #         mamDict[i]["MamE.hmm"] = "magnetosome_formation"

    elif len(FilterDict[i]["MamM.hmm"]) > 0:
        if len(FilterDict[i]["MamC.hmm"]) + len(FilterDict[i]["MamD.hmm"])\
                + len(FilterDict[i]["MamF.hmm"]) + len(FilterDict[i]["MamG.hmm"]) + len(FilterDict[i]["MamJ.hmm"]) \
                + len(FilterDict[i]["MamK.hmm"]) + len(FilterDict[i]["MamP.hmm"]) \
                + len(FilterDict[i]["MamW.hmm"]) + len(FilterDict[i]["MamX.hmm"]) + len(FilterDict[i]["MamY.hmm"]) > 0:
            mamDict[i]["MamM.hmm"] = "magnetosome_formation"
        else:
            mamDict[i]["MamM.hmm"] = "iron_aquisition-iron_uptake"

    elif len(FilterDict[i]["MamB.hmm"]) > 0:
        if len(FilterDict[i]["MamC.hmm"]) + len(FilterDict[i]["MamD.hmm"])\
                + len(FilterDict[i]["MamF.hmm"]) + len(FilterDict[i]["MamG.hmm"]) + len(FilterDict[i]["MamJ.hmm"]) \
                + len(FilterDict[i]["MamK.hmm"]) + len(FilterDict[i]["MamP.hmm"]) \
                + len(FilterDict[i]["MamW.hmm"]) + len(FilterDict[i]["MamX.hmm"]) + len(FilterDict[i]["MamY.hmm"]) > 0:
            mamDict[i]["MamB.hmm"] = "magnetosome_formation"
        else:
            mamDict[i]["MamB.hmm"] = "iron_aquisition-iron_uptake"

    elif len(FilterDict[i]["MamC.hmm"]) > 0:
        mamDict[i]["MamC.hmm"] = "magnetosome_formation"
    elif len(FilterDict[i]["MamD.hmm"]) > 0:
        mamDict[i]["MamD.hmm"] = "magnetosome_formation"
    elif len(FilterDict[i]["MamF.hmm"]) > 0:
        mamDict[i]["MamF.hmm"] = "magnetosome_formation"
    elif len(FilterDict[i]["MamG.hmm"]) > 0:
        mamDict[i]["MamG.hmm"] = "magnetosome_formation"
    elif len(FilterDict[i]["MamJ.hmm"]) > 0:
        mamDict[i]["MamJ.hmm"] = "magnetosome_formation"
    elif len(FilterDict[i]["MamK.hmm"]) > 0:
        mamDict[i]["MamK.hmm"] = "magnetosome_formation"
    elif len(FilterDict[i]["MamP.hmm"]) > 0:
        mamDict[i]["MamP.hmm"] = "magnetosome_formation"
    elif len(FilterDict[i]["MamW.hmm"]) > 0:
        mamDict[i]["MamW.hmm"] = "magnetosome_formation"
    elif len(FilterDict[i]["MamX.hmm"]) > 0:
        mamDict[i]["MamX.hmm"] = "magnetosome_formation"
    elif len(FilterDict[i]["MamY.hmm"]) > 0:
        mamDict[i]["MamY.hmm"] = "magnetosome_formation"


summary = open(outDirectory + "/FinalSummary-clustered-dereplicated.csv", "r")
OUT3 = open(outDirectory + "/FinalSummary-clustered-dereplicated-filtered.csv", "w")
for i in summary:
    ls = (i.rstrip().split(","))
    if ls[0] != "":
        category = ls[0]
        genome = ls[1]
        orf = ls[2]
        hmm = ls[3]
        bitscore = ls[4]
        if args.nr != "NA":
            ncbiMatch = ls[5]
            ncbiEval = ls[6]

            if category == "iron_oxidation" or category == "iron_reduction":
                if genome in Mtx2dict.keys() and hmm in Mtx2dict[genome]:
                    OUT3.write(
                        Mtx2dict[genome][hmm] + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "," +
                        ncbiMatch + "," + str(ncbiEval) + "\n")
                if genome in Cyc2dict.keys():
                    OUT3.write("iron_oxidation" + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "," +
                               ncbiMatch + "," + str(ncbiEval) + "\n")

                if hmm in Cyc2:
                    OUT3.write(category + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "," +
                               ncbiMatch + "," + str(ncbiEval) + "\n")

                if genome in FoxEYZdict.keys() and hmm in FoxEYZdict[genome]:
                    OUT3.write(
                        FoxEYZdict[genome][hmm] + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "," +
                        ncbiMatch + "," + str(ncbiEval) + "\n")

                if genome in FoxABCdict.keys() and hmm in FoxABCdict[genome]:
                    OUT3.write(
                        FoxABCdict[genome][hmm] + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "," +
                        ncbiMatch + "," + str(ncbiEval) + "\n")

                if genome in flavinDict.keys() and hmm in flavinDict[genome]:
                    OUT3.write(
                        flavinDict[genome][hmm] + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "," +
                        ncbiMatch + "," + str(ncbiEval) + "\n")

            elif category == "magnetosome_formation":
                if genome in mamDict.keys() and hmm in mamDict.keys():
                    OUT3.write(
                        mamDict[genome][hmm] + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "," +
                        ncbiMatch + "," + str(ncbiEval) + "\n")

            else:
                OUT3.write(category + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "," +
                           ncbiMatch + "," + str(ncbiEval) + "\n")
        else:
            if category == "iron_oxidation" or category == "iron_reduction":
                if genome in Mtx2dict.keys() and hmm in Mtx2dict[genome]:
                    OUT3.write(
                        Mtx2dict[genome][hmm] + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) +  "\n")
                if genome in Cyc2dict.keys():
                    OUT3.write("iron_oxidation" + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "\n")

                if hmm in Cyc2:
                    OUT3.write(category + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "\n")

                if genome in FoxEYZdict.keys() and hmm in FoxEYZdict[genome]:
                    OUT3.write(
                        FoxEYZdict[genome][hmm] + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "\n")

                if genome in FoxABCdict.keys() and hmm in FoxABCdict[genome]:
                    OUT3.write(
                        FoxABCdict[genome][hmm] + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "\n")

                if genome in flavinDict.keys() and hmm in flavinDict[genome]:
                    OUT3.write(
                        flavinDict[genome][hmm] + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "\n")

            elif category == "magnetosome_formation":
                if genome in mamDict.keys() and hmm in mamDict[genome]:
                    OUT3.write(
                        mamDict[genome][hmm] + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "\n")

            else:
                OUT3.write(
                    category + "," + genome + "," + orf + "," + hmm + "," + str(bitscore) + "," + "\n")

    else:
        OUT3.write(
            "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")

OUT3.close()

# ************************** BLAST-BASED METHODS/LOOKING FOR UNMODELED MARKERS ********************************

thermincola = args.hmm_lib + "/iron_reduction/non-aligned/TherJR_SLCs.faa"
geobacter = args.hmm_lib + "/iron_reduction/non-aligned/geobacter_PCCs.faa"

for i in binDirLS:
    if lastItem(i.split(".")) == args.bin_ext:

        os.system(
            "makeblastdb -dbtype prot -in %s/%s-proteins.faa -out %s/%s-proteins.faa" % (binDir, i, binDir, i))
        os.system(
            "blastp -query %s -db %s/%s-proteins.faa -num_threads 8 -outfmt 6 -out %s/%s-thermincola.blast -evalue 1E-4"
            % (thermincola, binDir, i, outDirectory, i))

        os.system(
            "blastp -query %s -db %s/%s-proteins.faa -num_threads 8 -outfmt 6 -out %s/%s-geobacter.blast -evalue 1E-4"
            % (geobacter, binDir, i, outDirectory, i))


geoDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
geo = open(args.hmm_lib + "/iron_reduction/non-aligned/geobacter_PCCs.faa")
geo = fasta(geo)
for i in geo.keys():
    id = i.split(" ")[0]
    type = (i.split(" ")[2])
    type = type[1:len(type) - 1]
    geoDict[id]["type"] = type
    geoDict[id]["header"] = i

thermDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
therm = open(args.hmm_lib + "/iron_reduction/non-aligned/TherJR_SLCs.faa")
therm = fasta(therm)
for i in therm.keys():
    id = i.split(" ")[0]
    thermDict[id]["header"] = i

out = open(outDirectory + "/GeoThermin.csv", "w")
for blastresult in os.listdir(args.out):
    blastDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
    if re.findall(r'geobacter\.blast', blastresult):
        blast = open(outDirectory + "/" + blastresult, "r")

        for i in blast:
            ls = i.rstrip().split("\t")
            if ls[1] not in blastDict.keys():
                blastDict[ls[1]]["query"] = ls[0]
                blastDict[ls[1]]["e"] = ls[10]
            else:
                if float(ls[10]) < float(blastDict[ls[1]]["e"]):
                    blastDict[ls[1]]["query"] = ls[0]
                    blastDict[ls[1]]["e"] = ls[10]
                else:
                    pass

        operonDict = defaultdict(list)
        for i in blastDict.keys():
            orf = (i)
            contig = allButTheLast(i, "_")
            orfCall = lastItem(orf.split("_"))
            id = (blastDict[i]["query"])
            type = geoDict[id]["type"]
            operonDict[contig].append(int(orfCall))

        count = 0
        operonDict2 = defaultdict(lambda: defaultdict(list))
        for i in operonDict.keys():
            contig = (i)
            clu = cluster(operonDict[i], 2)
            for j in clu:
                if len(j) > 1:
                    operon = (j)
                    count += 1
                    for k in operon:
                        orf = str(contig) + "_" + str(k)
                        id = blastDict[orf]["query"]
                        header = geoDict[id]["header"]
                        type = geoDict[id]["type"]
                        operonDict2["operon" + str(count)]["types"].append(type)
                        operonDict2["operon" + str(count)]["orfs"].append(orf)
                        operonDict2["operon" + str(count)]["headers"].append(header)

        for i in operonDict2.keys():
            if "porin" in operonDict2[i]["types"] and (
                    "pc" in operonDict2[i]["types"] or "omc" in operonDict2[i]["types"]):
                genome = blastresult.split("-geobacter.blas")[0]
                category = "iron_reduction"
                for j in range(0, len(operonDict2[i]["types"])):
                    orf = (operonDict2[i]["orfs"][j])
                    evalue = blastDict[orf]["e"]
                    header = (operonDict2[i]["headers"][j])
                    out.write(category + "," + genome + "," + orf + "," + replace(header, [","],
                                                                                  ";") + "," + "evalue: " + str(
                        evalue) + "\n")
                out.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
                # print("\n\n")

    if re.findall(r'thermincola\.blast', blastresult):
        blast = open(outDirectory + "/" + blastresult, "r")

        for i in blast:
            ls = i.rstrip().split("\t")
            if ls[1] not in blastDict.keys():
                blastDict[ls[1]]["query"] = ls[0]
                blastDict[ls[1]]["e"] = ls[10]
            else:
                if float(ls[10]) < float(blastDict[ls[1]]["e"]):
                    blastDict[ls[1]]["query"] = ls[0]
                    blastDict[ls[1]]["e"] = ls[10]
                else:
                    pass

        operonDict = defaultdict(lambda: defaultdict(list))
        for i in blastDict.keys():
            orf = (i)
            contig = allButTheLast(i, "_")
            id = (blastDict[i]["query"])
            header = thermDict[id]["header"]
            operonDict[blastresult]["headers"].append(header)
            operonDict[blastresult]["orfs"].append(orf)

        count = 0
        operonDict2 = defaultdict(lambda: defaultdict(list))
        for i in operonDict.keys():
            gene1 = "646797728 YP_003639887 TherJR_1122 cytochrome C family protein [Thermincola sp. JR: NC_014152]"
            gene2 = "646799199 YP_003641333 TherJR_2595 hypothetical protein [Thermincola sp. JR: NC_014152]"
            gene3 = "646796949 YP_003639120 TherJR_0333 hypothetical protein [Thermincola sp. JR: NC_014152]"
            if gene1 in operonDict[i]["headers"] and gene2 in operonDict[i]["headers"] and gene3 in operonDict[i][
                "headers"]:
                genome = blastresult.split("-thermincola.blas")[0]
                category = "iron_reduction"
                for j in range(0, len(operonDict[i]["orfs"])):
                    orf = (operonDict[i]["orfs"][j])
                    header = (operonDict[i]["headers"][j])
                    evalue = blastDict[orf]["e"]
                    out.write(category + "," + genome + "," + orf + "," + replace(header, [","],
                                                                                  ";") + "," + "evalue: " + str(
                        evalue) + "\n")
                out.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
out.close()

outfinal = open(outDirectory + "/FinalSummary-clustered-dereplicated-filtered-combined.csv", "w")
summary = open(outDirectory + "/FinalSummary-clustered-dereplicated-filtered.csv", "r")
GeoThermin = open(outDirectory + "/GeoThermin.csv", "r")
if args.nr == "NA":
    if args.contigs_source == "single":
        outfinal.write("category" + "," + "genome" + "," + "ORF" + "," + "related_HMM" + "," + "bitscore" + "\n")
    else:
        outfinal.write("category" + "," + "assembly" + "," + "ORF" + "," + "related_HMM" + "," + "bitscore" + "\n")
else:
    if args.contigs_source == "single":
        outfinal.write("category" + "," + "genome" + "," + "ORF" + "," + "related_HMM" + "," + "bitscore" + "," +
                       "NCBI_closest_match" + "," + "NCBI_aln_eval" + "\n")
    else:
        outfinal.write("category" + "," + "assembly" + "," + "ORF" + "," + "related_HMM" + "," + "bitscore" + "," +
                       "NCBI_closest_match" + "," + "NCBI_aln_eval" + "\n")

orfList = []
for i in summary:
    ls = i.rstrip().split(",")
    if ls[0] == "":
        outfinal.write(i)
    else:
        orf = ls[2]
        if orf not in orfList:
            outfinal.write(i)
            orfList.append(orf)
        else:
            pass

for i in GeoThermin:
    outfinal.write(i)
outfinal.close()


# ******************************* SIDEROPHORE CLEANUP *******************************************
summary = open(outDirectory + "/FinalSummary-clustered-dereplicated-filtered-combined.csv", "r")
out = open(outDirectory + "/FeGenie-presummary.csv", "w")
clusterDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
clustListDict = defaultdict(list)
counter = 0
for i in summary:
    ls = i.rstrip().split(",")
    if ls[0] != "":
        if re.findall(r'siderophore', ls[0]):
            counter += 1
            clusterDict[ls[2]] = i
            if ls[3] not in clustListDict["sid"]:
                clustListDict["sid"].append(ls[3])
        else:
            out.write(i)
            out.write("\n")

    else:
        if counter == 0:
            out.write(i)
            out.write("\n")

        else:
            if len(clustListDict["sid"]) > 2:
                for j in clusterDict.keys():
                    out.write(clusterDict[j])

            out.write("\n")
            out.write("\n")

        clusterDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
        clustListDict = defaultdict(list)
        counter = 0
out.close()
os.system("rm %s/FinalSummary-clustered-dereplicated-filtered-combined.csv" % outDirectory)


# ****************************** ADDING SEQUENCES AND COUNTING HEME-BINDING MOTIFS *************************************
seqDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
for i in binDirLS:
    if lastItem(i.split(".")) == args.bin_ext:
        file = open("%s/%s-proteins.faa" % (binDir, i), "r")
        file = fasta(file)
        for k in file.keys():
            seqDict[i][k.split(" # ")[0]] = file[k]

count = 0
blankList = []
final = open(outDirectory + "/FeGenie-presummary.csv", "r")
out = open(outDirectory + "/FeGenie-summary.csv", "w")
for i in final:
    ls = (i.rstrip().split(","))
    if count == 0:

        if args.nr == "NA":
            if args.contigs_source == "single":
                out.write(
                    "category" + "," + "genome" + "," + "ORF" + "," + "related_HMM" + "," + "bitscore" + ","
                    + "numberOfHemes" + "," + "sequence" + "\n")
            else:
                out.write(
                    "category" + "," + "assembly" + "," + "ORF" + "," + "related_HMM" + "," + "bitscore" + ","
                    + "numberOfHemes" + "," + "sequence" + "\n")
        else:
            if args.contigs_source == "single":
                out.write(
                    "category" + "," + "genome" + "," + "ORF" + "," + "related_HMM" + "," + "bitscore" + "," +
                    "NCBI_closest_match" + "," + "NCBI_aln_eval" + "," + "numberOfHemes" + "," + "sequence" + "\n")
            else:
                out.write(
                    "category" + "," + "assembly" + "," + "ORF" + "," + "related_HMM" + "," + "bitscore" + "," +
                    "NCBI_closest_match" + "," + "NCBI_aln_eval" + "," + "numberOfHemes" + "," + "sequence" + "\n")

        count += 1
    else:
        if ls[0] == "":
            if len(blankList) == 0:

                blankList.append(ls[0])
            elif len(blankList) == 1:
                blankList.append(ls[0])
                out.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
            else:
                pass

        else:
            blankList = []
            line = i.rstrip()[0:len(i.rstrip()) - 1]
            out.write(line + ",")
            process = ls[0]
            cell = ls[1]
            orf = ls[2]
            gene = ls[3]
            seq = seqDict[cell][orf]
            hemes = len(re.findall(r'C(..)CH', seq)) + len(re.findall(r'C(...)CH', seq)) \
                    + len(re.findall(r'C(....)CH', seq)) + len(re.findall(r'C(..............)CH', seq)) \
                    + len(re.findall(r'C(...............)CH', seq))

            out.write(str(hemes) + "," + seq + "\n")

out.close()


# **************************************************************************************************************
# ********************************************* PART 2 *********************************************************
# **************************************************************************************************************

os.system("grep -v ^$ %s/FeGenie-summary.csv > %s/FeGenie-summary-fixed.csv" % (args.out, args.out))
summary = open("%s/FeGenie-summary-fixed.csv" % args.out, newline='')
blastDict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 'EMPTY')))
for i in summary:
    ls = i.rstrip().split(",")
    if re.findall(r'evalue', ls[4]):
        cat = ls[0]
        cell = ls[1]
        orf = ls[2]
        hit = ls[3]
        e = ls[4]
        blastDict[cell][orf]["cat"] = cat
        blastDict[cell][orf]["hit"] = hit
        blastDict[cell][orf]["e"] = e
        if "NA" != "NA":
            blastDict[cell][orf]["NCBImatch"] = ls[5]
            blastDict[cell][orf]["NCBIeval"] = ls[6]
            blastDict[cell][orf]["hemes"] = ls[7]
            blastDict[cell][orf]["seq"] = ls[8]
        else:
            blastDict[cell][orf]["hemes"] = ls[5]
            blastDict[cell][orf]["seq"] = ls[6]


CoordDict = defaultdict(lambda: defaultdict(list))
print("Building Coordinates dictionary")
try:
    for i in blastDict.keys():
        if i != "category":
            for j in blastDict[i]:
                contig = allButTheLast(j, "_")
                numOrf = lastItem(j.split("_"))
                CoordDict[i][contig].append(int(numOrf))

    print("Clustering ORFs...")
    OUT2 = open("%s/FeGenie-summary-fixed-blastclustered.csv" % args.out, "w")
    for i in CoordDict.keys():
        for j in CoordDict[i]:
            LS = (CoordDict[i][j])
            clusters = (cluster(LS, 10))
            for k in clusters:
                if len(RemoveDuplicates(k)) == 1:
                    orf = j + "_" + str(k[0])

                    if args.nr != "NA":
                        ncbiHomolog = blastDict[i][orf]["NCBImatch"]
                        if ncbiHomolog != "NA":
                            ncbiHomolog = ncbiHomolog.split("]")[0] + "]"
                        else:
                            ncbiHomolog = "NA"

                        OUT2.write(blastDict[i][orf]["cat"] + "," + i + "," + orf + "," +
                                   blastDict[i][orf]["hit"] + "," + str(blastDict[i][orf]["e"]) + "," +
                                   ncbiHomolog + "," + str(blastDict[i][orf]["NCBIeval"]) + "," +
                                   str(blastDict[i][orf]["e"]) + "," + str(blastDict[i][orf]["hemes"]) + "," +
                                   blastDict[i][orf]["seq"] + "\n")
                        OUT2.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
                    else:
                        OUT2.write(blastDict[i][orf]["cat"] + "," + i + "," + orf + "," +
                                   blastDict[i][orf]["hit"] + "," + str(blastDict[i][orf]["e"]) + "," +
                                   str(blastDict[i][orf]["hemes"]) + "," + blastDict[i][orf]["seq"] + "\n")
                        OUT2.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")

                else:
                    if args.nr != "NA":
                        for l in RemoveDuplicates(k):
                            orf = j + "_" + str(l)
                            ncbiHomolog = blastDict[i][orf]["NCBImatch"]
                            if ncbiHomolog != "NA":
                                ncbiHomolog = ncbiHomolog.split("]")[0] + "]"
                            else:
                                ncbiHomolog = "NA"

                            OUT2.write(
                                blastDict[i][orf]["cat"] + "," + i + "," + orf + "," + blastDict[i][orf]["hit"]
                                + "," + str(blastDict[i][orf]["e"]) + "," + ncbiHomolog
                                + "," + str(blastDict[i][orf]["NCBIeval"]) + "\n")
                            OUT2.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
                    else:
                        for l in k:
                            orf = j + "_" + str(l)

                            OUT2.write(
                                blastDict[i][orf]["cat"] + "," + i + "," + orf + "," + blastDict[i][orf]["hit"]
                                + "," + str(blastDict[i][orf]["e"]) + "\n")
                            OUT2.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")
    OUT2.close()

except ValueError:
    pass

out = open("%s/FeGenie-finalsummary.csv" % args.out, "w")
clustListDict = defaultdict(lambda: defaultdict(list))
summary = open("%s/FeGenie-summary-fixed.csv" % args.out, newline='')
result = open("%s/FeGenie-summary-fixed-blastclustered.csv" % args.out, "r")
counter = 0
contigList = []
for i in summary:
    ls = i.rstrip().split(",")
    if not re.findall(r'evalue', ls[4]):
        # print(ls[2])
        contig = (allButTheLast(ls[2], "_"))
        if ls[0] != "":
            if len(clustListDict[counter]["contigs"]) == 0:
                clustListDict[counter]["line"].append(i)
                clustListDict[counter]["contigs"].append(contig)
                clustListDict[counter]["hmm"].append(i.rstrip().split(",")[3])
            else:
                if contig in clustListDict[counter]["contigs"]:
                    clustListDict[counter]["line"].append(i)
                    clustListDict[counter]["contigs"].append(contig)
                    clustListDict[counter]["hmm"].append(i.rstrip().split(",")[3])
                else:
                    counter += 1
                    clustListDict[counter]["line"].append(i)
                    clustListDict[counter]["contigs"].append(contig)
                    clustListDict[counter]["hmm"].append(i.rstrip().split(",")[3])

        else:
            contigList = []
            counter += 1


for i in clustListDict.keys():
    ls = (clustListDict[i]["hmm"])
    if len(ls) > 0:
        lsStripped = remove2(ls, ["PF01618-MotA_TolQ_ExbB_proton_channel_family.hmm", "PF02472-ExbD.hmm",
                                  "PF07715_sub-TonB_dependent_siderophore_receptor-plug.hmm",
                                  "HasB-TonB_paralog_heme_uptake-rep.hmm", "PF00593-TonB_dependent_receptor.hmm"])

        if len(lsStripped) > 0:
            if ls[0] == "Cyc1.hmm":
                # print(ls)
                lsStripped = ls
                lsStripped = remove2(ls, ["Cyc1.hmm"])
                # print(lsStripped)
                # print(len(lsStripped))
                # print("")

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MtoA.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["CymA.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["FoxZ.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["FoxY.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["FoxX.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["FoxA.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["FoxB.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["FoxC.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamY.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamX.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamB.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamC.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamD.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamF.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamG.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamJ.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamK.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamM.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamP.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["MamW.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["FmnA.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["DmkA.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["FmnB.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["PplA.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["Ndh2.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["EetA.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["EetB.hmm"])

        if len(lsStripped) > 0:
            lsStripped = ls
            lsStripped = remove2(ls, ["DmkB.hmm"])

        if len(lsStripped) > 0:
            for j in clustListDict[i]["line"]:
                out.write(j)
            out.write("" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "," + "" + "\n")

for i in result:
    out.write(i)
out.close()


# ****************************** CREATING A HEATMAP-COMPATIBLE CSV FILE *************************************
cats = ["iron_aquisition-iron_uptake", "iron_aquisition-heme_uptake", "iron_aquisition-heme_lyase", "iron_aquisition-siderophore_synthesis",
        "iron_aquisition-siderophore_uptake", "iron_gene_regulation", "iron_oxidation", "iron_reduction",
        "iron_storage", "magnetosome_formation"]

Dict = defaultdict(lambda: defaultdict(list))
final = open("%s/FeGenie-finalsummary.csv" % args.out, "r")
for i in final:
    ls = (i.rstrip().split(","))
    if ls[0] != "" and ls[1] != "assembly" and ls[1] != "genome":
        process = ls[0]
        cell = ls[1]
        orf = ls[2]
        gene = ls[3]
        Dict[cell][process].append(gene)
#         print(cell)
# print("\n\n")

normDict = defaultdict(lambda: defaultdict(lambda: 'EMPTY'))
for i in os.listdir(args.bin_dir):
    if lastItem(i.split(".")) == args.bin_ext:
        file = open("%s/%s-proteins.faa" % (args.bin_dir, i), "r")
        # file = open("%s/%s" % (orfs, i), "r")
        file = fasta(file)
        normDict[i] = len(file.keys())
# print("\n\n")

outHeat = open("%s/FeGenie-heatmap-data.csv" % args.out, "w")
outHeat.write("X" + ',')
for i in sorted(Dict.keys()):
    outHeat.write(i + ",")
outHeat.write("\n")

for i in cats:
    outHeat.write(i + ",")
    for j in sorted(Dict.keys()):
        # filename = j + "-proteins.faa"
        outHeat.write(str((len(Dict[j][i]) / int(normDict[j])) * float(args.inflation)) + ",")
    outHeat.write("\n")

outHeat.close()

os.system("mkdir %s/ORF-calls" % args.out)
for i in os.listdir(args.bin_dir):
    if lastItem(i.split(".")) == args.bin_ext:
        os.system("mv %s/%s-proteins.faa %s/ORF-calls" % (args.bin_dir, i, args.out))
        os.system("rm %s/%s-proteins.faa.psq" % (args.bin_dir, i))
        os.system("rm %s/%s-proteins.faa.pin" % (args.bin_dir, i))
        os.system("rm %s/%s-proteins.faa.phr" % (args.bin_dir, i))
        os.system("rm %s/%s-prodigal.out" % (args.bin_dir, i))
        os.system("rm %s/%s-thermincola.blast" % (args.out, i))
        os.system("rm %s/%s-geobacter.blast" % (args.out, i))


for i in os.listdir(args.hmm_lib):
    if i != ".DS_Store":
        os.system("rm %s/%s-summary.csv" % (args.out, i))
        os.system("rm %s/%s-summary.fa" % (args.out, i))
        if args.nr != "NA":
            os.system("rm %s/%s.dmndout" % (args.out, i))

os.system("rm %s/GeoThermin.csv" % args.out)
os.system("rm %s/FinalSummary-clustered-dereplicated-filtered.csv" % args.out)
os.system("rm %s/FinalSummary-dereplicated-clustered.csv" % args.out)
os.system("rm %s/FinalSummary-clustered-dereplicated.csv" % args.out)
os.system("rm %s/FinalSummary.csv" % args.out)
os.system("rm %s/FeGenie-summary-fixed.csv" % args.out)
os.system("rm %s/FeGenie-summary.csv" % args.out)
os.system("rm %s/FeGenie-summary-fixed-blastclustered.csv" % args.out)
os.system("rm %s/FeGenie-presummary.csv" % args.out)

'''
if args.R != "NA":
    os.system("Rscript --vanilla %s/dendro-heatmap.R %s/FeGenie-heatmap-data.csv %s" % (args.R, args.out, args.out))
    os.system("Rscript --vanilla %s/DotPlot.R %s/FeGenie-heatmap-data.csv %s" % (args.R, args.out, args.out))
'''

print("Pipeline finished without crashing!!! Hopefully the output is all there. If not, let me know. Thanks for using :)")