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

    # Iterate over all quality levels
    for i in range(100):
        # Quality level
        Q = i+1
        # Scaling factor (Eq 1 in Kornblum, 2008)
        if Q < 50:
            S = 5000/Q
        else:
            S = 200 - 2*Q

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
                # Update sum of squared errors relative to corresponding
                # image table value
                sumSqErrors  += (qdict[1][j] - Tschrom)**2

            j += 1

        errors.append(sumSqErrors)

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

    return qualityEst, rmsError


def main():
    args = parseCommandLine()
    myJPEGs =  args.JPEGsIn
    myJPEGs.sort()

    for JPEG in myJPEGs:
        with open(JPEG, 'rb') as fIn:
            im = Image.open(fIn)
            im.load()
            print("*** Image {}:".format(JPEG))
            quality, rmsError = computeJPEGQuality(im)
            print("quality: {}, RMS Error: {}".format(quality, rmsError))


if __name__ == "__main__":
    main()