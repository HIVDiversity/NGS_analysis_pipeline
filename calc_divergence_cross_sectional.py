#!/usr/bin/python
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import os
import sys
import collections
import argparse
from Bio import SeqIO
from glob import glob


__author__ = 'colin'


def fasta_to_dct(fn):
    '''
    :param fn: a fasta file
    :return: a dictionary
    '''
    dct = collections.OrderedDict()
    for seq_record in SeqIO.parse(open(fn), "fasta"):
        dct[seq_record.description.replace(" ", "_")] = str(seq_record.seq).replace("~", "-").upper()
    return dct


def gethxb2(dict):
    '''
    :param dict: a dictionary of your aligned input sequences. Must contain HXB2, with HXB2 in the header
    :return: the HXB2 sequence as a string
    '''
    found = False
    hxb2_seq = None
    hxb2_key = None
    for k in dict.keys():
        if "HXB2" in k.upper():
            found = True
            hxb2_key = k
            hxb2_seq = dict[k]
            print("Found hxb2 ref. seq. Its full name is: ", hxb2_key)
            break
    if not found:
        print("We could not find a sequence with 'HXB2' in its name. "
              "Please make sure you have an HXB2 ref. seq. included")

    return str(hxb2_key), str(hxb2_seq)


def customdist(s1, s2):

    if len(s1) != len(s2):
        print("sequences must be the same length")
        sys.exit()

    dist = 0
    for c1, c2 in zip(s1, s2):
        if c1 != c2:
            dist += 1
    diff = 0
    for i in range(len(s1)-1):
        if s1[i] != s2[i]:
            if (s1[i] == "-" and s1[i+1] == "-" and s2[i+1] != "-") \
                    or (s2[i] == "-" and s2[i+1] == "-" and s1[i+1] != "-"):
                diff += 1

    return (dist-diff)


def normcustomdist(s1, s2):

    if len(s1) != len(s2):
        print("sequences must be the same length")
        sys.exit()

    dist = 0
    for c1, c2 in zip(s1, s2):
        if c1 != c2:
            dist += 1
    diff = 0
    for i in range(len(s1)-1):
        if s1[i] != s2[i]:
            if (s1[i] == "-" and s1[i+1] == "-" and s2[i+1] != "-") \
                    or (s2[i] == "-" and s2[i+1] == "-" and s1[i+1] != "-"):
                diff += 1

    dist = dist-diff
    normdist = dist / len(s1)

    return normdist


def main(in_path, outpath, name):

    # set the outfile name
    name = name + "_divergence.csv"
    outfile = os.path.join(outpath, name)

    # write the headings to the outfile
    with open(outfile, "w") as handle:
        handle.write("participant,Normalised_hamming_distance_adjusted_(changes_per_100_bases),sequence_id\n")

    # get files
    in_files = os.path.join(in_path, "*sep.fasta")
    for file in glob(in_files):
        print(file)
        seqs_d = fasta_to_dct(file)
        ref_file = file.replace("sep.fasta", "hap.fasta")

        # get ref
        ref_record = next(SeqIO.parse(ref_file, "fasta"))
        ref_seq = str(ref_record.seq)
        ref_name = ref_record.name
        print(ref_name)

        # calculate the divergence from the reference for each sequnce
        for seq_name, seq in seqs_d.items():
            if len(seq) != len(ref_seq):
                print("input sequence and reference sequence were not the same length.")
                sys.exit()
            else:
                participant_id = seq_name.split("_")[0]

                # hamdist = distance.hamming(seq, refseq, normalized=True)
                normadjustdist_perc = round(normcustomdist(seq, ref_seq) * 100, 2)

                with open(outfile, "a") as handle:
                    handle.write(",".join([str(x) for x in [participant_id, normadjustdist_perc,  seq_name]]) + "\n")

    print("Divergence calculations are complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='calculate genetic distance from a reference sequence',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--inpath', type=str, required=True,
                        help='The path to the fasta file (ie: /path/to/5haplotype')
    parser.add_argument('-o', '--outpath', type=str, required=True,
                        help='The path to the where the outfile should be written')
    parser.add_argument('-n', '--name', type=str, required=True,
                        help='The name of the outfile (no extension')

    args = parser.parse_args()
    inpath = args.inpath
    outpath = args.outpath
    name = args.name

    main(inpath, outpath, name)
