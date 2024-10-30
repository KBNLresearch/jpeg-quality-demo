#! /usr/bin/env python3

"""
JPEG quality least squares matching demo.

Johan van der Knijff, KB National Library of the Netherlands, 2024.

See also:

https://www.bitsgalore.org/2024/10/30/jpeg-quality-estimation-using-simple-least-squares-matching-of-quantization-tables

"""
import math
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

    # Parse arguments
    args = parser.parse_args()

    return args


def computeJPEGQuality(image):
    """Estimates JPEG quality using least squares matching between image
    quantization tables and standard tables from the JPEG ISO standard.
    
    This compares the image quantization tables against the standard quantization
    tables for *all* possible quality levels, which are generated using
    Equations 1 and 2 in Kornblum (2008):

    https://www.sciencedirect.com/science/article/pii/S1742287608000285

    Returns quality estimate, root mean squared error of residuals between
    image quantization coefficients and corresponding standard coefficients,
    and Nash-Sutcliffe Efficiency measure.
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
    return qualityEst, rmsError, nse


def main():
    args = parseCommandLine()
    myJPEGs =  args.JPEGsIn
    myJPEGs.sort()

    for JPEG in myJPEGs:
        with open(JPEG, 'rb') as fIn:
            im = Image.open(fIn)
            im.load()
            print("*** Image: {}".format(JPEG))
            quality, rmsError, nse = computeJPEGQuality(im)
            print("quality: {}, RMS Error: {}, NSE: {}".format(quality, rmsError, nse))


if __name__ == "__main__":
    main()