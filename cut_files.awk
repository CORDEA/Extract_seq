#!/bin/awk -f
#encoding:utf-8
#
# Author : Yoshihiro Tanaka
# Date   : 2014-11-04
# Version: 0.1.3

function output(chrom, header, seq) {
    filename = "db/Canis_familiaris.CanFam3.1.dna.chromosome." chrom ".fa";
    printf header >  filename;
    print  seq    >> filename;
    close(filename);
    print "Successful output: " filename;
}
BEGIN {
    c  = 0
}
{
    if (">" == substr($1, 1, 1)) {
        if (c != 0) {
            if (chrom ~ /^([0-9][0-9]?|MT|X)/) {
                output(chrom, header, seq)
            }
        }
        chrom  = substr($1, 2);
        header = $0;
        seq = "";
    } else {
        seq = seq "\n" $0
    }
    c++;
    printf("progress: %d\r\b", c)
}
END {
    output(chrom, header, seq)
}
