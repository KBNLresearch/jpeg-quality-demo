#! /usr/bin/env python3

import os
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

    # Parse arguments
    args = parser.parse_args()

    return args


def main():
    args = parseCommandLine()
    myJPEGs =  args.JPEGsIn
    myJPEGs.sort()

    luminance = []
    chrominance = []

    for JPEG in myJPEGs:
        with open(JPEG, 'rb') as fIn:
                im = Image.open(fIn)
                im.load()
                qtables = im.quantization
                luminanceVals = [os.path.basename(JPEG)]
                chrominanceVals = [os.path.basename(JPEG)]
                for i in range(len(qtables[0])):
                    luminanceVals.append(str(qtables[0][i]))
                for i in range(len(qtables[1])):
                    chrominanceVals.append(str(qtables[1][i]))
                luminance.append(luminanceVals)
                chrominance.append(chrominanceVals)

    with open("luminance.csv", "w", encoding="UTF-8") as fp:
        writer = csv.writer(fp, delimiter=",")
        for row in luminance:
            writer.writerow(row)
    with open("chrominance.csv", "w", encoding="UTF-8") as fp:
        writer = csv.writer(fp, delimiter=",")
        for row in chrominance:
            writer.writerow(row)


if __name__ == "__main__":
    main()