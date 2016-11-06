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


from gRijndael import gRijndael
from datetime import datetime


MINIMAL_KEY_SIZE = 0  # 80  # 128


class Parameters:
    def __init__(self, minRows=2, maxRows=8, minColumns=2, maxColumns=16,
                 minWord=3, maxWord=16, minKolumns=2, maxKolumns=16):
        self._minRows = minRows
        self._maxRows = maxRows
        self._minColumns = minColumns
        self._maxColumns = maxColumns
        self._minWord = minWord
        self._maxWord = maxWord
        self._minKolumns = minKolumns
        self._maxKolumns = maxKolumns

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        for rows in range(self._minRows, self._maxRows+1):
            for columns in range(self._minColumns, self._maxColumns+1):
                for word in range(self._minWord, self._maxWord+1):
                    for kolumns in range(self._minKolumns, self._maxKolumns+1):
                        yield rows, columns, word, kolumns


class Combinate(object):
    def __init__(self):
        super(Combinate, self).__init__()
        self._fileName = "%s_ParamCombinations"\
            % (datetime.now().strftime("%Y%m%d_%H%M%S"))
        self._blockCombinations = {}
        self._keyPossibilities = []
        self._nRounds = []
        self._n = 0

    def _log(self, text):
        with open(self._fileName+".log", 'a') as logfile:
            logfile.write(text+"\n")
        print(text)

    def _csv(self, text):
        with open(self._fileName+".csv", 'a') as logfile:
            logfile.write(text+"\n")
        self._log(text)

    def _store(self, blockSize, keySize, parameterCombination):
        msg = ""
        if blockSize not in self._blockCombinations.keys():
            msg += "new block size: %d,\t" % (blockSize)
            self._blockCombinations[blockSize] = {}
        else:
            msg += "    block size: %d,\t" % (blockSize)
        if keySize not in self._blockCombinations[blockSize].keys():
            self._blockCombinations[blockSize][keySize] = []
            self._n += 1
        if parameterCombination in self._blockCombinations[blockSize][keySize]:
            self._log("\tALERT: %s twice!" % (str(parameterCombination)))
        else:
            self._blockCombinations[blockSize][keySize].\
                append(parameterCombination)
        if keySize not in self._keyPossibilities:
            msg += "new key size: %d,\t" % (keySize)
            self._keyPossibilities.append(keySize)
        else:
            msg += "    key size: %d,\t" % (keySize)
        if parameterCombination[0] not in self._nRounds:
            msg += "new number of rounds: %d" % (parameterCombination[0])
            self._nRounds.append(parameterCombination[0])
        else:
            msg += "    number of rounds: %d" % (parameterCombination[0])
        self._log("\t* %s" % (msg))

    def iterate(self):
        n = 0
        t0 = datetime.now()
        generator = Parameters()
        prevBlockSize = None
        for rows, columns, word, kolumns in next(generator):
            if kolumns >= columns:
                obj = gRijndael(0, nRows=rows, nColumns=columns,
                                wordSize=word, nKeyColumns=kolumns)
                block = obj.blockSize
                if block != prevBlockSize:
                    self._log("Checking the block size: %d" % (block))
                    prevBlockSize = block
                key = obj.keySize
                if key >= MINIMAL_KEY_SIZE:
                    self._store(block, key,
                                (obj.nRounds, obj.nRows, obj.nColumns,
                                 obj.wordSize, obj.nKeyColumns))
        t_diff = datetime.now()-t0
        self._log("Combination search process has take %s, with %d pairs:"
                  % (t_diff, self._n))

    def analyse(self):
        self._nRounds.sort()
        self._log("Rounds varies in: %s" % self._nRounds)
        blockSizes = self._blockCombinations.keys()
        blockSizes.sort()
        self._log("Available block sizes: %s" % blockSizes)
        self._keyPossibilities.sort()
        self._log("Available key sizes: %s" % self._keyPossibilities)
        line = ["key/block"] + blockSizes
        self._csv("".join("\t%s" % each for each in line)[1:])
        for key in self._keyPossibilities:
            line = [key]
            for block in blockSizes:
                if key in self._blockCombinations[block].keys():
                    cell = "".join(", %s" % str(each) for each in\
                        self._blockCombinations[block][key])[2:]
                    line.append("%s" % cell)
                else:
                    line.append("")
            self._csv("".join("\t%s" % each for each in line)[1:])


def main():
    obj = Combinate()
    obj.iterate()
    obj.analyse()

if __name__ == "__main__":
    main()
