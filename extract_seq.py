#!/bin/env python
# encoding:utf-8
#
"""Sequence_Extractor 配列の特定領域を切り取って保存するプログラム

 LAST_UPDATE   : 2014-10-16
 推奨パッケージ: xlwt(必須ではありません)
 動作確認環境  :
    Mac OS X v10.9.4    (Python 2.7.6)
    Fedora 19           (Python 2.7.5)
    *Python3系で動作するかはわかりません。*

 コマンドラインオプションの詳細は*-h*または*--help*で確認して下さい。
 
 注意事項:
 各染色体配列のファイルは少なくとも*染色体番号.faで終わっている必要があります。
 入力先ディレクトリ(_INPUT_DIR)には基本的に他のファイルが含まれていても問題有りませんが、異なる*.faファイルが含まれている場合はエラーになります。
 
 出力されるファイルについて:
 実行する領域を抜き出したファイルの他にxlsファイル(xlwtパッケージ導入時のみ)と*_with_link.tsvファイルが作成されます。
 xlsファイル    : 最後のcolumnにファイルへのハイパーリンク(絶対パス, HYPERLINK関数使用)が貼られたエクセスファイル
 *_with_link.tsv: 最後のcolumnにファイルへの絶対パスを書き込んだtsvファイル
                  *_with_link.tsvからvimにより開くには vim `awk 'NR==(対象の行番号) {print $14}' Table10.1_with_link.tsv`
 この2つのファイルは_OUTPUT_DIRではなく実行したディレクトリ内に出力されます。

"""

__Author__  =  "Yoshihiro Tanaka"
__date__    =  "2014-10-10"
__version__ =  "0.1.1 (Stable)"

import os, sys, commands
from multiprocessing import Pool
from optparse import OptionParser

def waypoint(args, **kwargs):
    u"""multiprocessingパッケージを使用するための中継関数

    ref. http://www.rueckstiess.net/research/snippets/show/ca1d7d90
    """
    return FileProcessing.multiProcessing(*args, **kwargs)

def optSettings():
    u"""コマンドラインオプションの管理関数"""
    usage   = "%prog [-ioce] [options] [-s] [file]\nDetailed options -h or --help"
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
        '-e', '--ext',
        action  = 'store',
        type    = 'int',
        dest    = 'extension',
        default = '200',
        help    = 'Extend the specified area. (ex. 0) [default: %default]'
    )

    parser.add_option(
        '-c', '--cpucore',
        action  = 'store',
        type    = 'int',
        dest    = 'cpu_count',
        default = '-1',
        help    = 'Set number of worker processes (ex. 8) [default: %default (use all CPU cores)]'
    )

    parser.add_option(
        '-s', '--strand',
        action  = 'store_false',
        dest    = 'strand',
        default = True,
        help    = 'Do not carry out reverse complement when this option is specified.'
    )

    return parser.parse_args()


class FileProcessing:
    def __init__(self, options, args):
        u"""渡されたオプションと引数の正誤チェック"""
        try:
            self._TABLE_FILE = args[0]
        except:
            print "Table file is not specified."
            sys.exit()
        self._INPUT_DIR  = options.input_dir.rstrip("/")
        # ファイルが指定されていた場合は終了
        if os.path.isfile(self._INPUT_DIR):
            print "Please specify the directory name, not the file name."
            sys.exit()
        self._OUTPUT_DIR = options.output_dir.rstrip("/")
        if os.path.isfile(self._OUTPUT_DIR):
            print "Please specify the directory name, not the file name."
            sys.exit()
        else:
            # 出力先に指定されたディレクトリが存在しなければ作成する
            if not os.path.isdir(self._OUTPUT_DIR):
                os.system('mkdir -p ' + self._OUTPUT_DIR)
        self._EXTENSION  = int(options.extension)
        self._CPU_COUNT  = int(options.cpu_count)
        self._STRAND     = options.strand

    def createDict(self):
        u"""抽出対象の配列情報,及びファイルと染色体番号との紐付けを行う辞書の作成を行う関数"""
        u"""xargs -n 1 basenameでパスを削ってファイル名のみ取得する

        split("/")[-1]でも代用可
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
                # 格納先にリストが存在しない場合新たに作成する
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
                    # 染色体番号とfilenameを関連付け
                    fileDict[chrom] = filename
                    # exDictからfileListにある染色体番号のものだけ抜き出す
                    tmpDict[chrom]  = exDict[chrom]
        return tmpDict, fileDict

    def extractSeq(self, filename, start_pos, end_pos):
        u"""配列の特定領域を抜き出している関数"""
        infile = open(self._INPUT_DIR + "/" + filename, "r")

        start_pos = start_pos - self._EXTENSION
        end_pos   = end_pos   + self._EXTENSION

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
                # decodeしてバイト数から文字数のカウントに変換(アルファベットなのでバイト数でも問題はないが一応)
                length = len(line.decode('utf-8'))
                if start <= end_pos and end_pos < start+length:
                    seq += line[:end_pos - start + 1]
                    break
                if start <= start_pos and start_pos < start+length:
                    # startとendが同じlineにある時
                    if start <= end_pos and end_pos < start+length:
                        seq = line[start_pos - start:end_pos - start + 1]
                        break
                    seq = line[start_pos - start:]
                    flag = True
                else:
                    seq += line
                start += length
            line = infile.readline()
        infile.close()
        return seq

    def reverseComp(self, seq):
        u"""Reverse Complementを行う関数"""
        seq_OLD = seq
        seq = ""
        reDict = {"A": "T", "T": "A", "G": "C", "C": "G"}
        u"""文字列を反転させる

        ref. http://d.hatena.ne.jp/redcat_prog/20111104/1320395840
        """
        for s in seq_OLD[::-1]:
            if s in reDict:
                seq += reDict[s]
            else:
                seq += s
        return seq

    def multiProcessing(self, tuples):
        chrom    = tuples[0]
        items    = tuples[1]
        filename = tuples[2]
        print("Start the process of chromosome " + str(chrom) + ".")
        for item in items:
            outFile = open(self._OUTPUT_DIR + "/" + item[0] + "_" + chrom + "_" + item[1] + "_" + str(item[2]) + "_" + str(item[3]) + "_" + item[4] + ".txt", "w")
            seq = self.extractSeq(filename, item[2], item[3])
            if item[1] == "-" and self._STRAND:
                seq = self.reverseComp(seq)
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
                u"""KeyboardInterruptを正常に処理できないバグを回避するための記述
                
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
        u"""元ファイルにlinkを貼って出力し直すための関数"""
        xlsFlag = True
        try:
            import xlwt
        except ImportError as e:
            print e
            print "ex. sudo pip install xlwt"
            # xlwtパッケージがインストールされていない場合はエラーを出してtsvファイルのみ出力する
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
            u"""相対パス, もしくは'../'等が含まれているパスを絶対パスに変換する

            ref. http://stackoverflow.com/questions/11246189/how-to-convert-relative-path-to-absolute-path-in-unix
            """
            dirname  = os.system('cd ' + self._OUTPUT_DIR + ';pwd') + "/"
            filename = cells[1] + "_" + cells[8] + "_" + cells[9] + "_" + cells[10] + "_" + cells[11] + "_" + cells[12] + ".txt"
            outFile.write(line.rstrip("\r\n") + "\t" + dirname + filename + "\n")
            if xlsFlag:
                # HYPERLINK関数を使用してlinkを設定する
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
