# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = "Sergi Blanch-Torne"
__email__ = "srgblnchtrn@protonmail.ch"
__copyright__ = "Copyright 2016 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

from datetime import datetime
from gRijndael.Polynomials import *
from gRijndael import SBox
from gRijndael import KeyExpansion
from gRijndael import AddRoundKey
from gRijndael import SubBytes
from gRijndael import MixColumns
from gRijndael import gRijndael
from gRijndael.Logger import levelFromMeaning
from multiprocessing import Lock as _Lock
from numpy import array
from optparse import OptionParser
from random import randint
from time import sleep
try:
    from yamp import Pool
except:
    Pool = None


def extractParams(paramsStr):
    paramsSet = paramsStr.split(',')
    if len(paramsSet) not in [4, 5]:
        raise Exception("Cannot extract the test parameters using %r"
                        % paramsStr)
    nRounds = int(paramsSet[0])
    nRows = int(paramsSet[1])
    nColumns = int(paramsSet[2])
    wordSize = int(paramsSet[3])
    try:
        nKeyColumns = int(paramsSet[4])
    except:
        nKeyColumns = int(paramsSet[2])
    return (nRounds, nRows, nColumns, wordSize, nKeyColumns)


def BinaryPolynomialsXORCtr():
    for degree in range(2, 17):
        for field in [False, True]:
            if field:
                msg = "%2d degree binary extension field" % (degree)
                getModulo = getBinaryExtensionFieldModulo
            else:
                msg = "%2d degree binary extension ring " % (degree)
                getModulo = getBinaryExtensionRingModulo
            modulo = BinaryExtensionModulo(getModulo(degree))
            zero = modulo(0)
            one = modulo(1)
            biggest = modulo(2**degree-1)
            sample = modulo(randint(0, 2**degree))
            sample += zero
            sample += one
            sample += biggest
            sample *= zero
            sample *= one
            sample *= biggest
            print("%s: 3 additions and 3 products -> %4d xors"
                  % (msg, sample.xors))


def PolynomialRingXORCtr():
    for degree in range(2, 9):
        for coeffdegree in range(2, 17):
            c_x, ring, field = \
                getPolynomialRingWithBinaryCoefficients(degree, coeffdegree)
            c_x += c_x
            c_x += c_x
            c_x += c_x
            c_x *= c_x
            c_x *= c_x
            c_x *= c_x
            print("%2d ring degree with %2d coefficients degree: "
                  "3 additions and 3 products -> %4d xors"
                  % (degree, coeffdegree, c_x.xors))


def SBoxXORctr():
    for nRows in range(2, 9):
        for nColumns in range(2, 9):
            for wordSize in range(3, 17):
                doSBox(nRows, nColumns, wordSize)


def doSBox(nRows, nColumns, wordSize):
    sbox = SBox(wordSize)
    state = [[randint(0, 2**wordSize)
              for i in range(nColumns)]
             for j in range(nRows)]
    sbox.transform(state)
    print("%2d x %2d matrix with %2d bits cell: SBox transformation -> "
          "%5d xors" % (nRows, nColumns, wordSize, sbox.xors))


def keyExpansionXORctr():
    for nRows in range(2, 9):
        for nColumns in range(2, 17):
            for wordSize in range(3, 17):
                for nKolumns in range(2, 17):
                    nRounds = max(nKolumns, nColumns) + 6
                    doKeyExpansion(nRounds, nRows, nColumns, wordSize,
                                   nKolumns)


def doKeyExpansion(nRounds, nRows, nColumns, wordSize, nKeyWords):
    keyExp = KeyExpansion(0, nRounds, nRows, nColumns, wordSize, nKeyWords)
    keyExp.getKey()
    print("KeyExpansion(%2d, %2d, %2d, %2d, %2d)-> %6d xors"
          % (nRounds, nRows, nColumns, wordSize, nKeyWords, keyExp.xors))


def addRoundKeyXORctr():
    for nRows in range(2, 9):
        for nColumns in range(2, 9):
            for wordSize in range(3, 17):
                doAddRoundKey(nRows, nColumns, wordSize)


def doAddRoundKey(nRows, nColumns, wordSize):
    ark = AddRoundKey(nRows, nColumns, wordSize)
    state = [[randint(0, 2**wordSize)
              for i in range(nColumns)]
             for j in range(nRows)]
    subkey = [randint(0, 2**(wordSize*nRows))
              for j in range(nColumns)]
    ark.do(state, subkey)
    print("addRoundKey(%2d, %2d, %2d)-> %6d xors"
          % (nRows, nColumns, wordSize, ark.xors))


def subBytesXORctr():
    for nRows in range(2, 9):
        for nColumns in range(2, 9):
            for wordSize in range(3, 17):
                    doSubBytes(nRows, nColumns, wordSize)


def doSubBytes(nRows, nColumns, wordSize):
    subBytes = SubBytes(wordSize)
    state = [[randint(0, 2**wordSize)
              for i in range(nColumns)]
             for j in range(nRows)]
    subBytes.do(state)
    print("subBytes(%2d, %2d, %2d)-> %6d xors"
          % (nRows, nColumns, wordSize, subBytes.xors))


# ShiftRows doesn't do any xor operation


def mixColumnsXORctr():
    for nRows in range(2, 9):
        for nColumns in range(2, 9):
            for wordSize in range(3, 17):
                    doMixColumns(nRows, nColumns, wordSize)


def doMixColumns(nRows, nColumns, wordSize):
    mixColumns = MixColumns(nRows, nColumns, wordSize)
    state = [[randint(0, 2**wordSize)
              for i in range(nColumns)]
             for j in range(nRows)]
    mixColumns.do(state)
    print("MixColumns(%2d, %2d, %2d)-> %6d xors"
          % (nRows, nColumns, wordSize, mixColumns.xors))


def gRijndaelXORxtr(processors):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    fileName = "%s_gRijndaelXORxtr.csv" % (now)
    with open(fileName, 'a') as f:
        f.write("rounds\trow\tcolumns\twordsize\tkolumns\tblock\tkey"
                "\tsamples\tencrMean\tencrStd\tdecrMean\tdecrStd\n")
    lock = _Lock()
    errors = []
    arginLst = []
    for nRows in range(2, 9):
        for nColumns in range(2, 17):
            for wordSize in range(3, 17):
                for nKolumns in range(2, 17):
                    nRounds = max(nKolumns, nColumns) + 6
                    arginLst.append([nRounds, nRows, nColumns, wordSize,
                                     nKolumns])
    if processors is None or Pool is None:
        if Pool is None:
            print("\n\tyamp not available!"
                  "\n\tCalculation will NOT be parallel")
            sleep(5)
        for argin in arginLst:
            argout = doRijndael(argin)
            write2cvs(argin, argout, **{'lock': lock, 'fileName': fileName})
    else:
        pool = Pool(doRijndael, arginLst, processors,
                    postHook=write2cvs,
                    postExtraArgs={'lock': lock, 'fileName': fileName},
                    loggerName="XORctr", loggingFolder='.')
        pool.log2file = True
        pool.start()
        while pool.isAlive():
            sleep(10)
            computation, _ = pool.computation
            contributions = pool.contributions
            progress = pool.progress
            print("\n\tprogress: %.2f%%" % ((progress)*100))
            print("\tcontributions: %s" % (contributions))
            print("\tcomputation: %s\n" % (computation))


def doRijndael(argin):
    nRounds, nRows, nColumns, wordSize, nKolumns = argin
    encrXors = []
    decrXors = []
    for i in range(nRows*nColumns):
        data = randint(0, 2**(nRows*nColumns*wordSize))
        key = randint(0, 2**(nRows*nKolumns*wordSize))
        rijndael = gRijndael(key, nRounds, nRows, nColumns, wordSize, nKolumns)
        encData = rijndael.cipher(data)
        encrXors.append(rijndael.xors)
        rijndael.reset()
        if data != rijndael.decipher(encData):
            raise AssertionError("gRijndael(%2d, %2d, %2d, %2d, %2d)"
                                 % (nRounds, nRows, nColumns, wordSize,
                                    nKolumns))
        decrXors.append(rijndael.xors)
        rijndael.reset()
    encrXors = array(encrXors)
    decrXors = array(decrXors)
    return encrXors.mean(), encrXors.std(), decrXors.mean(), decrXors.std(),\
        nRows*nColumns

def write2cvs(argin, argout, **kwargs):
    nRounds, nRows, nColumns, wordSize, nKolumns = argin
    encrXors_mean, encrXors_std, decrXors_mean, decrXors_std, samples= argout
    blockSize = nRows*nColumns*wordSize
    keySize = nRows*nKolumns*wordSize
    fileName = kwargs['fileName']
    lock = kwargs['lock']
    with lock:
        print("gRijndael(%2d, %2d, %2d, %2d, %2d): (b%4d, k%4d)-> "
                  "%9d xors (%10g) & %9d xors (%10g) %d samples"
                  % (nRounds, nRows, nColumns, wordSize, nKolumns,
                     blockSize, keySize, encrXors_mean, encrXors_std,
                     decrXors_mean, decrXors_std, samples))
        with open(fileName, 'a') as f:
            f.write("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%e\t%d\t%e\n"
                    % (nRounds, nRows, nColumns, wordSize, nKolumns,
                       blockSize, keySize, samples, encrXors_mean,
                       encrXors_std, decrXors_mean, decrXors_std))


def main():
    parser = OptionParser()
    parser.add_option('', "--log-level", default="info",
                      help="Set log level: error, warning, info, debug, trace")
    parser.add_option('', "--rijndael", type='str',
                      help="Comma separated set of Rijndael's generalised"
                      "parameters. For example from the original Rijndael: "
                      "10,4,4,8 for 128, or 12,4,4,8,6 for 192 or "
                      "14,4,4,8,8 for 256 "
                      "(nRounds, nRows, nColumns, wordSize[, nKeyColumns])")
    parser.add_option('', "--processors", type="str",
                      help="Tell the application how many processors will be "
                      "used. A positive number will establish the number of "
                      "parallel workers and each will use one of the cores. "
                      "With the string'max' the application will use all the "
                      "available cores. Telling a negative number with be "
                      "understood as how many below the maximum will be used.")
    import sys
    (options, args) = parser.parse_args()
    loglevel = levelFromMeaning(options.log_level)
    if options.rijndael is not None:
        parameters = extractParams(options.rijndael)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        fileName = "%s_gRijndaelXORxtr.csv" % (now)
        doRijndael(fileName, *parameters)
    else:
        # BinaryPolynomialsXORCtr()
        # PolynomialRingXORCtr()
        # SBoxXORctr()
        # keyExpansionXORctr()
        # addRoundKeyXORctr()
        # subBytesXORctr()
        # mixColumnsXORctr()
        gRijndaelXORxtr(options.processors)


if __name__ == "__main__":
    main()
