#! /usr/bin/env python3
"""
Write CSV file with luminance, chrominance values from quantization tables,
as well as corresponding values from closest "standard" tables.
"""

import os
import math
import argparse
import csv
from PIL import Image
import pandas as pd
from matplotlib import pylab
from matplotlib import pyplot as plt

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
    """Estimates JPEG quality based on best correspondence between image
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

    # Default quantization table bit depth
    qBitDepth = 8

    if max(qdict[0]) > 255:
        # Any values greater than 255 indicate bir depth 16 
        qBitDepth = 16
    if noTables >= 2:
        if max(qdict[1]) > 255:
            qBitDepth = 16

    # Calculate mean of all value in quantization tables
    Tsum = sum(qdict[0])
    if noTables >= 2:
        Tsum += sum(qdict[1])
    Tmean = Tsum / (noTables*64)

    # List for storing squared error values
    errors = []

    ## TEST
    qTablesStandard = []
    ## TEST

    # List for storing Nash–Sutcliffe Efficiency values
    nseVals = []

    # Iterate over all quality levels
    for i in range(100):
        # Quality level
        Q = i+1
        # Scaling factor (Eq 1 in Kornblum, 2008)
        if Q < 50:
            S = 5000/Q
        else:
            S = 200 - 2*Q

        ## TEST
        lumStandard = []
        chromStandard = []
        ## TEST

        # Initialize sum of squared differences between image quantization values
        # and corresponding values from standard q tables for this quality level
        sumSqErrors = 0

        # Initialize sum of squared differences between image quantization values
        # and mean image quantization value (needed to calculate Nash Efficiency)
        sumSqMean = 0

        # Iterate over all values in quantization tables for this quality
        for j in range(64):
            # Compute standard luminance table value from scaling factor
            # (Eq 2 in Kornblum, 2008)
            Tslum = max(math.floor((S*lum_base[j] + 50) / 100), 1)
            # Cap Tslum at 255 if bit depth is 8
            if qBitDepth == 8:
                Tslum = min(Tslum, 255)
            ## TEST
            lumStandard.append(Tslum)
            ## TEST
            # Update sum of squared errors relative to corresponding
            # image table value
            sumSqErrors += (qdict[0][j] - Tslum)**2

            # Sum of luminance and chrominance values          
            Tcombi = qdict[0][j]

            if noTables >= 2:
                # Compute standard chrominance table value from scaling factor
                # (Eq 2 in Kornblum, 2008)
                Tschrom = max(math.floor((S*chrom_base[j] + 50) / 100), 1)
                # Cap Tschrom at 255 if bit depth is 8
                if qBitDepth == 8:
                    Tschrom = min(Tschrom, 255)
                ## TEST
                chromStandard.append(Tschrom)
                ## TEST
                # Update sum of squared errors relative to corresponding
                # image table value
                sumSqErrors  += (qdict[1][j] - Tschrom)**2

                # Update sum of luminance and chrominance values
                Tcombi += qdict[1][j]
   
            # Update sumSqMMean
            sumSqMean += (Tcombi - Tmean)**2

            j += 1

        # Calculate Nash-Sutcliffe Effiency
        nse = 1 - sumSqErrors/sumSqMean

        # Add calculated statistics to lists
        errors.append(sumSqErrors)
        nseVals.append(nse)
        ## TEST
        qTablesStandard.append([lumStandard, chromStandard])
        ## TEST

    # Quality is estimated as level with smallest sum of squared errors
    # Note that this will return the smallest quality level in case
    # the smallest SSE occurs for more than one level!
    # TODO: perhaps add a check for this and report as output?
    qualityEst = errors.index(min(errors)) + 1
    # Corresponding SSE. Value 0 indicates exact match with standard JPEG
    # quantization tables. Any other value means non-standard tables were
    # used, and quality estimate is an approximation
    sumSqErrors = min(errors)
    # Compute corresponding root mean squared error
    rmsError = round(math.sqrt(sumSqErrors / (noTables * 64)), 3)
    nse = round(max(nseVals), 3)
    return qualityEst, rmsError, nse, qTablesStandard[errors.index(min(errors))]


def main():
    args = parseCommandLine()
    myJPEG =  args.JPEGIn

    fileName = os.path.basename(myJPEG)
    baseName = os.path.splitext(fileName)[0]

    listOut = []

    with open(myJPEG, 'rb') as fIn:
        im = Image.open(fIn)
        im.load()
        quality, rmse, nse, qTablesStandard = computeJPEGQuality(im)
        qtables = im.quantization
        noTables = len(qtables)
        for i in range(len(qtables[0])):
            lum = qtables[0][i]
            lum_s = qTablesStandard[0][i]
            listOut.append([lum, lum_s])
            if noTables >= 2:
                chrom = qtables[1][i]
                chrom_s = qTablesStandard[1][i]
                listOut.append([chrom, chrom_s])

    # Convert list to Pandas dataframe
    df = pd.DataFrame(listOut, columns=["T", "Ts"])

    # Maximum Ts value (used for plot)
    TsMax = df.max(axis=0)['Ts']

    # Create scatter plot of actual vs standard quantization values
    myPlot = df.plot.scatter(x = 'T', y = 'Ts', s = 20, color = 'b')
    # Add 1:1 line
    myPlot.axline([0, 0], [1, 1], linewidth=1, linestyle='dashed', color = 'r')
    # Add text
    myPlot.text(0, 0.8*TsMax, f'{fileName}\nQuality = {quality}%\nRMSE = {rmse}\nNSE = {nse}')
    fig = myPlot.get_figure()
    fig.savefig(f'{baseName}-scatter.png', dpi=150)

    """
    with open(f'{baseName}-qvalues.csv', "w", encoding="UTF-8") as fp:
        writer = csv.writer(fp, delimiter=",")
        for row in listOut:
            writer.writerow(row)
    """

if __name__ == "__main__":
    main()