#! /usr/bin/env python3

"""
Implement JPEG quality computation based on minimum sum of squared errors
between quantization tables and standard JPEG quantization tables

Usage:

```
image = Img.open(...)
quality = computeJPEGQuality1(image)
```
"""
import math
import array
import argparse
from PIL import Image

def parseCommandLine():
    """Parse command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument('JPEGsIn',
                        action="store",
                        type=str,
                        nargs='+',
                        help="input JPEG(s) (wildcards allowed)")
    parser.add_argument('--verbose',
                        action="store_true",
                        help="print variable values at each iteration",
                        dest="verboseFlag",
                        default=False)

    # Parse arguments
    args = parser.parse_args()

    return args


def computeJPEGQuality(image):
    """Returns JPEG quality and exactness flag of a JPEG image based on
    minimum sum of squared errors between quantization tables and standard
    JPEG quantization tables"""

    # Standard JPEG luminance and chrominance quantization tables
    # for 50% quality (ISO/IEC 10918-1 : 1993(E)), Annex K
    lum_base = [16,  11,  12,  14,  12,  10,  16,  14,
                13,  14,  18,  17,  16,  19,  24,  40,
                26,  24,  22,  22,  24,  49,  35,  37,
                29,  40,  58,  51,  61,  60,  57,  51,
                56,  55,  64,  72,  92,  78,  64,  68,
                87,  69,  55,  56,  80, 109,  81,  87,
                95,  98, 103, 104, 103,  62,  77, 113,
                121,112, 100, 120,  92, 101, 103, 99]


    chrom_base = [17,  18,  18,  24,  21,  24,  47,  26,
                  26,  47,  99,  66,  56,  66,  99,  99,
                  99,  99,  99,  99,  99,  99,  99,  99,
                  99,  99,  99,  99,  99,  99,  99,  99,
                  99,  99,  99,  99,  99,  99,  99,  99,
                  99,  99,  99,  99,  99,  99,  99,  99,
                  99,  99,  99,  99,  99,  99,  99,  99,
                  99,  99,  99,  99,  99,  99,  99,  99]

    # Generate standard quantization tables for all possible quality levels
    # See https://stackoverflow.com/a/29216609/1209004, which is based on
    # Kornblum (2008)

    lum_all = {}
    chrom_all = {}

    for i in range(100):
        lum = array.array('I')
        chrom = array.array('I')
        # Quality level
        Q = i+1
        # Scaling factor
        if Q < 50:
            S = 5000/Q
        else:
            S = 200 - 2*Q

        # Compute all table values from scaling factor
        for Tbl in lum_base:
            Tsl = max(math.floor((S*Tbl + 50) / 100), 1)
            lum.append(Tsl)

        for Tbc in chrom_base:
            Tsc = max(math.floor((S*Tbc + 50) / 100), 1)
            chrom.append(Tsc)

        # Add arrays to dictionary
        lum_all[i] = lum
        chrom_all[i] = chrom

    # Quantization tables of image
    qdict = image.quantization
    noTables = len(qdict)

    # Array for storing squared errors
    errors = array.array('I')

    # Iterate over all quality levels
    for i in range(100):
        # Iterate over all values in standard quantization tables for this
        # quality level, and compute sum of squared differences relative to
        # actual values in image quantization tables
        sumSqErrors = 0
        for j in range(len(qdict[0])):
            #print(j, qdict[0][j], lum_all[i][j], qdict[1][j], chrom_all[i][j])
            # Luminance quantization table
            sumSqErrors += (qdict[0][j] - lum_all[i][j])**2
            if noTables >= 2:
                # Chrominance quantization table
                sumSqErrors  += (qdict[1][j] - chrom_all[i][j])**2

        errors.append(sumSqErrors)

    qualityEst = errors.index(min(errors)) + 1
    sumSqErrors = min(errors)
    return qualityEst, sumSqErrors

def main():
    args = parseCommandLine()
    myJPEGs =  args.JPEGsIn
    myJPEGs.sort()
    verboseFlag = args.verboseFlag

    for JPEG in myJPEGs:
        with open(JPEG, 'rb') as fIn:
            im = Image.open(fIn)
            im.load()
            print("*** Image {}:".format(JPEG))
            quality, sumSqErrors = computeJPEGQuality(im, verboseFlag)
            print("quality: {}, sumSqErrors: {}".format(quality, sumSqErrors))


if __name__ == "__main__":
    main()