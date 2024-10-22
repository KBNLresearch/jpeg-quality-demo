#! /usr/bin/env python3

"""
Generate test images at different JPEG quality levels
"""
import os
import argparse
from PIL import Image

def parseCommandLine():
    """Parse command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument('imageIn',
                        action="store",
                        type=str,
                        help="input image")
    parser.add_argument('dirOut',
                        action="store",
                        type=str,
                        help="output directory")
    # Parse arguments
    args = parser.parse_args()
    return args

def main():
    args = parseCommandLine()
    imageIn =  args.imageIn
    dirOut = args.dirOut
    nameBase = os.path.splitext(os.path.basename(imageIn))[0]
    print(nameBase)
    with open(imageIn, 'rb') as fIn:
        im = Image.open(fIn)
        im.load()
        im = im.convert('RGB')

    for i in [5, 10, 25, 50, 75, 100]:
         nameOut = ("{}{}{}.jpeg".format(nameBase, '_pil_', f'{i:03}'))
         fileOut = os.path.join(dirOut, nameOut)
         im2 = im
         im2.save(fileOut, quality=i)

if __name__ == "__main__":
    main()