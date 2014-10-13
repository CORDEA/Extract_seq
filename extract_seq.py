#!/bin/env python
# encoding:utf-8
#
"""Sequence_Extractor $BG[Ns$NFCDjNN0h$r@Z$j<h$C$FJ]B8$9$k%W%m%0%i%`(B

 LAST_UPDATE   : 2014-10-11
 $B?d>)%Q%C%1!<%8(B: xlwt($BI,?\$G$O$"$j$^$;$s(B)
 $BF0:n3NG'4D6-(B  :
    Mac OS X v10.9.4    (Python 2.7.6)
    Fedora 19           (Python 2.7.5)
    *Python3$B7O$GF0:n$9$k$+$O$o$+$j$^$;$s!#(B*

 $B%3%^%s%I%i%$%s%*%W%7%g%s$N>\:Y$O(B*-h*$B$^$?$O(B*--help*$B$G3NG'$7$F2<$5$$!#(B
 
 $BCm0U;v9`(B:
 $B3F@w?'BNG[Ns$N%U%!%$%k$O>/$J$/$H$b(B*$B@w?'BNHV9f(B.fa$B$G=*$o$C$F$$$kI,MW$,$"$j$^$9!#(B
 $BF~NO@h%G%#%l%/%H%j(B(_INPUT_DIR)$B$K$O4pK\E*$KB>$N%U%!%$%k$,4^$^$l$F$$$F$bLdBjM-$j$^$;$s$,!"0[$J$k(B*.fa$B%U%!%$%k$,4^$^$l$F$$$k>l9g$O%(%i!<$K$J$j$^$9!#(B
 
 $B=PNO$5$l$k%U%!%$%k$K$D$$$F(B:
 $B<B9T$9$kNN0h$rH4$-=P$7$?%U%!%$%k$NB>$K(Bxls$B%U%!%$%k(B(xlwt$B%Q%C%1!<%8F3F~;~$N$_(B)$B$H(B*_with_link.tsv$B%U%!%$%k$,:n@.$5$l$^$9!#(B
 xls$B%U%!%$%k(B    : $B:G8e$N(Bcolumn$B$K%U%!%$%k$X$N%O%$%Q!<%j%s%/(B($B@dBP%Q%9(B, HYPERLINK$B4X?t;HMQ(B)$B$,E=$i$l$?%(%/%;%9%U%!%$%k(B
 *_with_link.tsv: $B:G8e$N(Bcolumn$B$K%U%!%$%k$X$N@dBP%Q%9$r=q$-9~$s$@(Btsv$B%U%!%$%k(B
                  *_with_link.tsv$B$+$i(Bvim$B$K$h$j3+$/$K$O(B vim `awk 'NR==($BBP>]$N9THV9f(B) {print $14}' Table10.1_with_link.tsv`
 $B$3$N(B2$B$D$N%U%!%$%k$O(B_OUTPUT_DIR$B$G$O$J$/<B9T$7$?%G%#%l%/%H%jFb$K=PNO$5$l$^$9!#(B

"""

__Author__  =  "Yoshihiro Tanaka"
__date__    =  "2014-10-10"
__version__ =  "0.1.0"


import os, sys, commands
from multiprocessing import Pool
from optparse import OptionParser

def waypoint(args, **kwargs):
    u"""multiprocessing$B%Q%C%1!<%8$r;HMQ$9$k$?$a$NCf7Q4X?t(B

    ref. http://www.rueckstiess.net/research/snippets/show/ca1d7d90
    """
    return FileProcessing.multiProcessing(*args, **kwargs)

def optSettings():
    u"""$B%3%^%s%I%i%$%s%*%W%7%g%s$N4IM}4X?t(B"""
    usage   = "%prog [-ioc] [options] [file]\nDetailed options -h or --help"
    version = __version__
    parser  = OptionParser(usage=usage, version=version)

    parser.add_option(
        '-i', '--input',
        action  = 'store',
        type    = 'str',
        dest    = 'input_dir',
        default = 'db/',
        help    = 'Set directory that contains the input file. (ex. db/) [default: %default]'
    )

    parser.add_option(
        '-o', '--output',
        action  = 'store',
        type    = 'str',
        dest    = 'output_dir',
        default = 'result/',
        help    = 'Set output directory (ex. result/) [default: %default]'
    )

    parser.add_option(
        '-c', '--cpucore',
        action  = 'store',
        type    = 'int',
        dest    = 'cpu_count',
        default = '-1',
        help    = 'Set number of worker processes (ex. 8) [default: %default (use all CPU cores)]'
    )

    return parser.parse_args()


class FileProcessing:
    def __init__(self, options, args):
        u"""$BEO$5$l$?%*%W%7%g%s$H0z?t$N@58m%A%'%C%/(B"""
        try:
            self._TABLE_FILE = args[0]
        except:
            print "Table file is not specified."
            sys.exit()
        self._INPUT_DIR  = options.input_dir.rstrip("/")
        # $B%U%!%$%k$,;XDj$5$l$F$$$?>l9g$O=*N;(B
        if os.path.isfile(self._INPUT_DIR):
            print "Please specify the directory name, not the file name."
            sys.exit()
        self._OUTPUT_DIR = options.output_dir.rstrip("/")
        if os.path.isfile(self._OUTPUT_DIR):
            print "Please specify the directory name, not the file name."
            sys.exit()
        else:
            # $B=PNO@h$K;XDj$5$l$?%G%#%l%/%H%j$,B8:_$7$J$1$l$P:n@.$9$k(B
            if not os.path.isdir(self._OUTPUT_DIR):
                os.system('mkdir -p ' + self._OUTPUT_DIR)
        self._CPU_COUNT  = int(options.cpu_count)

    def createDict(self):
        u"""$BCj=PBP>]$NG[Ns>pJs(B,$B5Z$S%U%!%$%k$H@w?'BNHV9f$H$NI3IU$1$r9T$&<-=q$N:n@.$r9T$&4X?t(B"""
        u"""xargs -n 1 basename$B$G%Q%9$r:o$C$F%U%!%$%kL>$N$_<hF@$9$k(B

        split("/")[-1]$B$G$bBeMQ2D(B
        """
        fileList = [r for r in commands.getoutput('ls ' + self._INPUT_DIR + "/*.fa | xargs -n 1 basename").split("\n")]
        infile = open(self._TABLE_FILE, "r")
        lines = infile.readlines()
        infile.close()
        
        exDict = {}
        for line in lines:
            cells = [r.rstrip("\r\n") for r in line.split("\t")]
            EnsemblID   = cells[1]
            chrom       = str(cells[8])
            strand      = cells[9]
            start_pos   = int(cells[10])
            end_pos     = int(cells[11])
            block_count = cells[12]
            try:
                exDict[chrom].append([EnsemblID, strand, start_pos, end_pos, block_count])
            except:
                # $B3JG<@h$K%j%9%H$,B8:_$7$J$$>l9g?7$?$K:n@.$9$k(B
                exDict[chrom] = []
                exDict[chrom].append([EnsemblID, strand, start_pos, end_pos, block_count])
        return self.check(exDict, fileList)

    def check(self, exDict, fileList):
        fileDict = {}
        first = True
        tmpDict = {}
        for chrom in exDict.keys():
            for filename in fileList:
                if "." + chrom + ".fa" in filename:
                    # $B@w?'BNHV9f$H(Bfilename$B$r4XO"IU$1(B
                    fileDict[chrom] = filename
                    # exDict$B$+$i(BfileList$B$K$"$k@w?'BNHV9f$N$b$N$@$1H4$-=P$9(B
                    tmpDict[chrom]  = exDict[chrom]
        return tmpDict, fileDict

    def extractSeq(self, filename, start_pos, end_pos):
        u"""$BG[Ns$NFCDjNN0h$rH4$-=P$7$F$$$k4X?t(B"""
        infile = open(self._INPUT_DIR + "/" + filename, "r")

        start = 1
        line = infile.readline()
        flag = False
        header = True
        seq = ""
        while line:
            if header:
                header = False
            else:
                line = line.rstrip("\r\n")
                # decode$B$7$F%P%$%H?t$+$iJ8;z?t$N%+%&%s%H$KJQ49(B($B%"%k%U%!%Y%C%H$J$N$G%P%$%H?t$G$bLdBj$O$J$$$,0l1~(B)
                length = len(line.decode('utf-8'))
                if start <= end_pos and end_pos < start+length:
                    seq += line[:end_pos - start + 1]
                    break
                if start <= start_pos and start_pos < start+length:
                    seq = line[start_pos - start:]
                    flag = True
                else:
                    seq += line
                start += length
            line = infile.readline()
        infile.close()
        return seq

    def multiProcessing(self, tuples):
        chrom    = tuples[0]
        items    = tuples[1]
        filename = tuples[2]
        print("Start the process of chromosome " + str(chrom) + ".")
        for item in items:
            outFile = open(self._OUTPUT_DIR + "/" + item[0] + "_" + chrom + "_" + item[1] + "_" + str(item[2]) + "_" + str(item[3]) + "_" + item[4] + ".txt", "w")
            seq = self.extractSeq(filename, item[2], item[3])
            outFile.write(seq)
            outFile.close()
        print("Finished the process of chromosome " + str(chrom) + ".")
        return

    def output(self, exDict, fileDict):
        print "Start output"
        single = False
        if self._CPU_COUNT == -1:
            pool = Pool()
        elif self._CPU_COUNT == 1:
            single = True
        else:
            pool = Pool(self._CPU_COUNT)

        items = []
        for chrom in exDict.keys():
            if single:
                items = (chrom, exDict[chrom], fileDict[chrom])
                self.multiProcessing(items)
            else:
                items.append((chrom, exDict[chrom], fileDict[chrom]))

        if not single:
            try:
                u"""KeyboardInterrupt$B$r@5>o$K=hM}$G$-$J$$%P%0$r2sHr$9$k$?$a$N5-=R(B
                
                ref. http://stackoverflow.com/questions/1408356/keyboard-interrupts-with-pythons-multiprocessing-pool
                """
                pool.map_async(waypoint, zip([self]*len(items), items)).get(9999999)
                pool.close()
            except KeyboardInterrupt:
                pool.terminate()
            except Exception as e:
                print e
                pool.terminate()
            finally:
                pool.join()

    def linkFileCreate(self):
        u"""$B85%U%!%$%k$K(Blink$B$rE=$C$F=PNO$7D>$9$?$a$N4X?t(B"""
        xlsFlag = True
        try:
            import xlwt
        except ImportError as e:
            print e
            print "ex. sudo pip install xlwt"
            # xlwt$B%Q%C%1!<%8$,%$%s%9%H!<%k$5$l$F$$$J$$>l9g$O%(%i!<$r=P$7$F(Btsv$B%U%!%$%k$N$_=PNO$9$k(B
            xlsFlag = False
        if xlsFlag:
            book = xlwt.Workbook()
            sheet = book.add_sheet(self._TABLE_FILE)

        infile = open(self._TABLE_FILE, "r")
        lines = infile.readlines()
        infile.close()

        outFile = open(self._TABLE_FILE + "_with_link.tsv", "w")

        row = 0
        for line in lines:
            cells = [r.rstrip("\r\n") for r in line.split("\t")]
            column = 0
            if xlsFlag:
                for cell in cells:
                    sheet.write(row, column, cell)
                    column += 1
                sheet.col(1).width = 8000
                sheet.col(8).width = 5000
            u"""$BAjBP%Q%9(B, $B$b$7$/$O(B'../'$BEy$,4^$^$l$F$$$k%Q%9$r@dBP%Q%9$KJQ49$9$k(B

            ref. http://stackoverflow.com/questions/11246189/how-to-convert-relative-path-to-absolute-path-in-unix
            """
            dirname  = os.system('cd ' + self._OUTPUT_DIR + ';pwd') + "/"
            filename = cells[1] + "_" + cells[8] + "_" + cells[9] + "_" + cells[10] + "_" + cells[11] + "_" + cells[12] + ".txt"
            outFile.write(line.rstrip("\r\n") + "\t" + dirname + filename + "\n")
            if xlsFlag:
                # HYPERLINK$B4X?t$r;HMQ$7$F(Blink$B$r@_Dj$9$k(B
                sheet.write(row, column, xlwt.Formula('HYPERLINK("' +  dirname + filename + '","' + 'link' + '")'))
            row += 1
        outFile.close()
        if xlsFlag:
            book.save(self._TABLE_FILE + '.xls')

if __name__=='__main__':
    options, args = optSettings()
    fp = FileProcessing(options, args)
    exDict, fileDict = fp.createDict()
    fp.output(exDict, fileDict)
    fp.linkFileCreate()
    print "All processing has finished."
