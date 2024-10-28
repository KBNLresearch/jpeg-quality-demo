#! /usr/bin/env python3
"""
Write CSV file with luminance, chrominance values from quantization tables,
as well as corresponding values from closest "standard" tables.
"""

import math
import os
import argparse
import csv
from PIL import Image

def parseCommandLine():
    """Parse command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument('JPEGIn',
                        action="store",
                        type=str,
                        help="input JPEG")

    # Parse arguments
    args = parser.parse_args()

    return args


def computeJPEGQuality(image):
    """Returns JPEG quality based on best correspondence between image
    quantization tables and standard tables from the JPEG ISO standard.
    
    The image quantization tables are compared against standard quantization
    tables for *all* possible quality levels, which are generated using
    Equations 1 and 2 in Kornblum (2008):

    https://www.sciencedirect.com/science/article/pii/S1742287608000285

    (Also explained in: https://stackoverflow.com/a/29216609/1209004)
    """

    # Standard JPEG luminance and chrominance quantization tables
    # for 50% quality (ISO/IEC 10918-1 : 1993(E)), Annex K)
    lum_base = [16, 11, 10, 16, 24, 40, 51, 61,
                12, 12, 14, 19, 26, 58, 60, 55,
                14, 13, 16, 24, 40, 57, 69, 56,
                14, 17, 22, 29, 51, 87, 80, 62,
                18, 22, 37, 56, 68, 109, 103, 77,
                24, 35, 55, 64, 81, 104, 113, 92,
                49, 64, 78, 87, 103, 121, 120, 101,
                72, 92, 95, 98, 112, 100, 103, 99]

    chrom_base = [17, 18, 24, 47, 99, 99, 99, 99,
                  18, 21, 26, 66, 99, 99, 99, 99,
                  24, 26, 56, 99, 99, 99, 99, 99,
                  47, 66, 99, 99, 99, 99, 99, 99,
                  99, 99, 99, 99, 99, 99, 99, 99,
                  99, 99, 99, 99, 99, 99, 99, 99,
                  99, 99, 99, 99, 99, 99, 99, 99,
                  99, 99, 99, 99, 99, 99, 99, 99]

    # Image quantization tables
    qdict = image.quantization
    noTables = len(qdict)

    # Get bit depth of quantization tables by checking for any values
    # greater than 255
    qBitDepth = 8
    if max(qdict[0]) > 255:
        qBitDepth = 16
    if noTables >= 2:
        if max(qdict[1]) > 255:
            qBitDepth = 16

    # List for storing squared error values
    errors = []

    qTablesStandard = []

    # Iterate over all quality levels
    for i in range(100):
        # Quality level
        Q = i+1
        # Scaling factor (Eq 1 in Kornblum, 2008)
        if Q < 50:
            S = 5000/Q
        else:
            S = 200 - 2*Q

        lumStandard = []
        chromStandard = []

        # Initialize sum of squared errors, which is used to characterize
        # agreement between image q tables and standard q tables for each
        # quality level
        sumSqErrors = 0

        # Iterate over all values in quantization tables for this quality
        for j in range(64):
            # Compute standard luminance table value from scaling factor
            # (Eq 2 in Kornblum, 2008)
            Tslum = max(math.floor((S*lum_base[j] + 50) / 100), 1)
            # Cap Tslum at 255 if bit depth is 8
            if qBitDepth == 8:
                Tslum = min(Tslum, 255)
            lumStandard.append(Tslum)
            # Update sum of squared errors relative to corresponding
            # image table value
            sumSqErrors += (qdict[0][j] - Tslum)**2

            if noTables >= 2:
                # Compute standard chrominance table value from scaling factor
                # (Eq 2 in Kornblum, 2008)
                Tschrom = max(math.floor((S*chrom_base[j] + 50) / 100), 1)
                # Cap Tschrom at 255 if bit depth is 8
                if qBitDepth == 8:
                    Tschrom = min(Tschrom, 255)
                chromStandard.append(Tschrom)
                # Update sum of squared errors relative to corresponding
                # image table value
                sumSqErrors  += (qdict[1][j] - Tschrom)**2

            j += 1

        errors.append(sumSqErrors)
        qTablesStandard.append([lumStandard, chromStandard])

    # Quality is estimated as level with smallest sum of squared errors
    # Note that this will return the smallest quality level in case
    # the smallest SSE occurs for more than one level!
    # TODO: perhaps add a check for this and report as output?
    qualityEst = errors.index(min(errors)) + 1
    # Corresponding SSE. Value 0 indicates exact match with standard JPEG
    # quantization tables. Any other value means non-standard tables were
    # used, and quality estimate is an approximation
    sumSqErrors = min(errors)
    # Compute corresponding root mean squared error (easier to interpret)
    rmsError = round(math.sqrt(sumSqErrors / (noTables * 64)), 3)

    return qualityEst, rmsError, qTablesStandard[errors.index(min(errors))]

def main():
    args = parseCommandLine()
    myJPEG =  args.JPEGIn

    listOut = [["lum", "lum_s", "chrom", "chrom_s"]]

    with open(myJPEG, 'rb') as fIn:
        im = Image.open(fIn)
        im.load()
        quality, rmse, qTablesStandard = computeJPEGQuality(im)
        qtables = im.quantization
        noTables = len(qtables)
        for i in range(len(qtables[0])):
            lum = qtables[0][i]
            lum_s = qTablesStandard[0][i]
            if noTables >= 2:
                chrom = qtables[1][i]
                chrom_s = qTablesStandard[1][i]
            else:
                chrom = -1
                chrom_s = -1
            listOut.append([lum, lum_s, chrom, chrom_s])

    with open("qtables.csv", "w", encoding="UTF-8") as fp:
        writer = csv.writer(fp, delimiter=",")
        for row in listOut:
            writer.writerow(row)

if __name__ == "__main__":
    main()