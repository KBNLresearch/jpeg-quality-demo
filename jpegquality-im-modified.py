#! /usr/bin/env python3

"""
Implement JPEG quality computation following (an adapted version of)
ImageMagick's heuristic algorithm.

Adapted from Edward O's Python port:

https://gist.github.com/eddy-geek/c0f01dc5401dc50a49a0a821cdc9b3e8#file-jpg_quality_pil_magick-py

Which is in turn based on the original ImageMagick code:

https://github.com/ImageMagick/ImageMagick/blob/7.1.0-57/coders/jpeg.c#L782

See also https://stackoverflow.com/questions/4354543/

Usage:

```
image = Img.open(...)
quality = computeJPEGQuality1(image)
```
"""

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


def computeJPEGQuality(image, verboseFlag):
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
                quality, exactFlag = computeJPEGQuality(im, verboseFlag)
                print("quality: {}, exactFlag: {}".format(quality, exactFlag))

if __name__ == "__main__":
    main()