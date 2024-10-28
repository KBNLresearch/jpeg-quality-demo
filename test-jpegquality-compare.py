#! /usr/bin/env python3

"""
Estimate JPEG quality using ImageMagick heuristic, modified ImageMagick heuristic and
table match method
"""
import math
import argparse
import csv
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


def computeJPEGQuality_im_orig(image, verboseFlag):
    """Returns JPEG quality of a JPEG image based on original ImageMagick
    algorithm"""

    _HASH_2 = [ 1020, 1015, 932,  848,  780,  735,  702,  679,  660,  645,
                632,  623,  613,  607,  600,  594,  589,  585,  581,  571,
                555,  542,  529,  514,  494,  474,  457,  439,  424,  410,
                397,  386,  373,  364,  351,  341,  334,  324,  317,  309,
                299,  294,  287,  279,  274,  267,  262,  257,  251,  247,
                243,  237,  232,  227,  222,  217,  213,  207,  202,  198,
                192,  188,  183,  177,  173,  168,  163,  157,  153,  148,
                143,  139,  132,  128,  125,  119,  115,  108,  104,  99,
                94,   90,   84,   79,   74,   70,   64,   59,   55,   49,
                45,   40,   34,   30,   25,   20,   15,   11,   6,    4,
                0 ]

    _SUMS_2 = [ 32640, 32635, 32266, 31495, 30665, 29804, 29146, 28599, 28104,
                27670, 27225, 26725, 26210, 25716, 25240, 24789, 24373, 23946,
                23572, 22846, 21801, 20842, 19949, 19121, 18386, 17651, 16998,
                16349, 15800, 15247, 14783, 14321, 13859, 13535, 13081, 12702,
                12423, 12056, 11779, 11513, 11135, 10955, 10676, 10392, 10208,
                9928,  9747,  9564,  9369,  9193,  9017,  8822,  8639,  8458,
                8270,  8084,  7896,  7710,  7527,  7347,  7156,  6977,  6788,
                6607,  6422,  6236,  6054,  5867,  5684,  5495,  5305,  5128,
                4945,  4751,  4638,  4442,  4248,  4065,  3888,  3698,  3509,
                3326,  3139,  2957,  2775,  2586,  2405,  2216,  2037,  1846,
                1666,  1483,  1297,  1109,  927,   735,   554,   375,   201,
                128,   0 ]

    _HASH_1 = [ 510,  505,  422,  380,  355,  338,  326,  318,  311,  305,
                300,  297,  293,  291,  288,  286,  284,  283,  281,  280,
                279,  278,  277,  273,  262,  251,  243,  233,  225,  218,
                211,  205,  198,  193,  186,  181,  177,  172,  168,  164,
                158,  156,  152,  148,  145,  142,  139,  136,  133,  131,
                129,  126,  123,  120,  118,  115,  113,  110,  107,  105,
                102,  100,  97,   94,   92,   89,   87,   83,   81,   79,
                76,   74,   70,   68,   66,   63,   61,   57,   55,   52,
                50,   48,   44,   42,   39,   37,   34,   31,   29,   26,
                24,   21,   18,   16,   13,   11,   8,    6,    3,    2,
                0 ]

    _SUMS_1 = [ 16320, 16315, 15946, 15277, 14655, 14073, 13623, 13230, 12859,
                12560, 12240, 11861, 11456, 11081, 10714, 10360, 10027, 9679,
                9368,  9056,  8680,  8331,  7995,  7668,  7376,  7084,  6823,
                6562,  6345,  6125,  5939,  5756,  5571,  5421,  5240,  5086,
                4976,  4829,  4719,  4616,  4463,  4393,  4280,  4166,  4092,
                3980,  3909,  3835,  3755,  3688,  3621,  3541,  3467,  3396,
                3323,  3247,  3170,  3096,  3021,  2952,  2874,  2804,  2727,
                2657,  2583,  2509,  2437,  2362,  2290,  2211,  2136,  2068,
                1996,  1915,  1858,  1773,  1692,  1620,  1552,  1477,  1398,
                1326,  1251,  1179,  1109,  1031,  961,   884,   814,   736,
                667,   592,   518,   441,   369,   292,   221,   151,   86,
                64,    0 ]

    qsum = 0
    qdict = image.quantization

    for i, qtable in qdict.items():
        qsum += sum(qtable)

    if len(qdict) >= 1:
        qvalue = qdict[0][2]+qdict[0][53]
        hashes, sums = _HASH_1, _SUMS_1
        if len(qdict) >= 2:
            qvalue += qdict[1][0]+qdict[1][-1]
            hashes, sums = _HASH_2, _SUMS_2
        for i in range(100):
            if verboseFlag:
                print("i: {}, qvalue: {}, hashes[i]:{}, qsum:{}, sums[i]{}".format(i,qvalue, hashes[i], qsum, sums[i]))
            if ((qvalue < hashes[i]) and (qsum < sums[i])):
                continue
            if (((qvalue <= hashes[i]) and (qsum <= sums[i])) or (i >= 50)):
                return i+1
            break
    return -1


def computeJPEGQuality_im_mod(image, verboseFlag):
    """Returns JPEG quality and exactness flag of a JPEG image based on modified ImageMagick
    algorithm that omits i >= 50 condition"""

    _HASH_2 = [ 1020, 1015, 932,  848,  780,  735,  702,  679,  660,  645,
                632,  623,  613,  607,  600,  594,  589,  585,  581,  571,
                555,  542,  529,  514,  494,  474,  457,  439,  424,  410,
                397,  386,  373,  364,  351,  341,  334,  324,  317,  309,
                299,  294,  287,  279,  274,  267,  262,  257,  251,  247,
                243,  237,  232,  227,  222,  217,  213,  207,  202,  198,
                192,  188,  183,  177,  173,  168,  163,  157,  153,  148,
                143,  139,  132,  128,  125,  119,  115,  108,  104,  99,
                94,   90,   84,   79,   74,   70,   64,   59,   55,   49,
                45,   40,   34,   30,   25,   20,   15,   11,   6,    4,
                0 ]

    _SUMS_2 = [ 32640, 32635, 32266, 31495, 30665, 29804, 29146, 28599, 28104,
                27670, 27225, 26725, 26210, 25716, 25240, 24789, 24373, 23946,
                23572, 22846, 21801, 20842, 19949, 19121, 18386, 17651, 16998,
                16349, 15800, 15247, 14783, 14321, 13859, 13535, 13081, 12702,
                12423, 12056, 11779, 11513, 11135, 10955, 10676, 10392, 10208,
                9928,  9747,  9564,  9369,  9193,  9017,  8822,  8639,  8458,
                8270,  8084,  7896,  7710,  7527,  7347,  7156,  6977,  6788,
                6607,  6422,  6236,  6054,  5867,  5684,  5495,  5305,  5128,
                4945,  4751,  4638,  4442,  4248,  4065,  3888,  3698,  3509,
                3326,  3139,  2957,  2775,  2586,  2405,  2216,  2037,  1846,
                1666,  1483,  1297,  1109,  927,   735,   554,   375,   201,
                128,   0 ]

    _HASH_1 = [ 510,  505,  422,  380,  355,  338,  326,  318,  311,  305,
                300,  297,  293,  291,  288,  286,  284,  283,  281,  280,
                279,  278,  277,  273,  262,  251,  243,  233,  225,  218,
                211,  205,  198,  193,  186,  181,  177,  172,  168,  164,
                158,  156,  152,  148,  145,  142,  139,  136,  133,  131,
                129,  126,  123,  120,  118,  115,  113,  110,  107,  105,
                102,  100,  97,   94,   92,   89,   87,   83,   81,   79,
                76,   74,   70,   68,   66,   63,   61,   57,   55,   52,
                50,   48,   44,   42,   39,   37,   34,   31,   29,   26,
                24,   21,   18,   16,   13,   11,   8,    6,    3,    2,
                0 ]

    _SUMS_1 = [ 16320, 16315, 15946, 15277, 14655, 14073, 13623, 13230, 12859,
                12560, 12240, 11861, 11456, 11081, 10714, 10360, 10027, 9679,
                9368,  9056,  8680,  8331,  7995,  7668,  7376,  7084,  6823,
                6562,  6345,  6125,  5939,  5756,  5571,  5421,  5240,  5086,
                4976,  4829,  4719,  4616,  4463,  4393,  4280,  4166,  4092,
                3980,  3909,  3835,  3755,  3688,  3621,  3541,  3467,  3396,
                3323,  3247,  3170,  3096,  3021,  2952,  2874,  2804,  2727,
                2657,  2583,  2509,  2437,  2362,  2290,  2211,  2136,  2068,
                1996,  1915,  1858,  1773,  1692,  1620,  1552,  1477,  1398,
                1326,  1251,  1179,  1109,  1031,  961,   884,   814,   736,
                667,   592,   518,   441,   369,   292,   221,   151,   86,
                64,    0 ]

    qsum = 0
    qdict = image.quantization

    for i, qtable in qdict.items():
        qsum += sum(qtable)

    if len(qdict) >= 1:
        qvalue = qdict[0][2]+qdict[0][53]
        hashes, sums = _HASH_1, _SUMS_1
        if len(qdict) >= 2:
            qvalue += qdict[1][0]+qdict[1][-1]
            hashes, sums = _HASH_2, _SUMS_2
        for i in range(100):
            if verboseFlag:
                print("i: {}, qvalue: {}, hashes[i]:{}, qsum:{}, sums[i]{}".format(i, qvalue, hashes[i], qsum, sums[i]))
            if ((qvalue < hashes[i]) and (qsum < sums[i])):
                continue
            else:
                quality= i+1
                exact = qsum <= sums[i]
                return quality, exact
            break
    return -1, False


def computeJPEGQuality_table(image):
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
    verboseFlag = args.verboseFlag
    fileOut = "jpeg-quality-comparison.csv"
    resultList = [["file", "q_im_orig", "q_im_mod",
                  "exact_im_mod", "q_im_tab", "rmse_tab", "nse_tab"]]

    for JPEG in myJPEGs:
        with open(JPEG, 'rb') as fIn:
            im = Image.open(fIn)
            im.load()
            q_im_orig = computeJPEGQuality_im_orig(im, verboseFlag)
            q_im_mod, exact_im_mod = computeJPEGQuality_im_mod(im, verboseFlag)
            q_tab, rmse_tab, nse_tab = computeJPEGQuality_table(im)
            resultList.append([JPEG, q_im_orig, q_im_mod, exact_im_mod,
                               q_tab, rmse_tab, nse_tab])

    with open(fileOut, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(resultList)

if __name__ == "__main__":
    main()