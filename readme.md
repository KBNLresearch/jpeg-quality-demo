## About

This repository contains all analysis scripts and data that were used for the following blog posts:

- [JPEG Quality estimation: experiments with a modified ImageMagick heuristic](https://www.bitsgalore.org/2024/10/23/jpeg-quality-estimation-experiments-with-a-modified-imagemagick-heuristic)
- [JPEG quality estimation using simple least squares matching of quantization tables](https://www.bitsgalore.org/2024/10/30/jpeg-quality-estimation-using-simple-least-squares-matching-of-quantization-tables)

## Scripts

Below scripts were tested with Python 3.8.10, with version 10.4.0 of [Pillow Imaging Library](https://python-pillow.org/). Pillow can be installed using:

```
pip install pillow
```

**Important note on Pillow version:** some of these scripts will either not work or give (very!) wrong results when used with older Pillow versions! This is because Pillow changed the order in which the values in the quantization tables are returned around the release of Pillow 8.3 (I think!), see [details here](https://github.com/python-pillow/Pillow/pull/4989). The below scripts are all based on the new/current behaviour!

Also the [plot-goodness-fit.py](./plot-goodness-fit.py) script needs Pandas. Installation:

```
pip install pandas
```

The scripts are:

- [jpegquality-im-original.py](./jpegquality-im-original.py): computes JPEG quality for one or more files using original ImageMagick heuristic. Option `--verbose` prints out values of all variables in main loop at each iteration.
- [jpegquality-im-modified.py](./jpegquality-im-modified.py): computes JPEG quality for one or more files using modified ImageMagick heuristic. Option `--verbose` prints out values of all variables in main loop at each iteration.
- [jpegquality-lsm.py](./jpegquality-lsm.py): computes JPEG quality for one or more files using least squares matching against standard JPEG quantization tables.
- [jpegquality-compare.py](./jpegquality-compare.py): computes JPEG quality for one or more files using all of the above methods, and write results in comma-delimited format. 
- [generate-testimages-pillow.py](./generate-testimages-pillow.py): generates a set of JPEG images at 6 quality levels from a user-defined source image.
- [generate-testimages-im.sh](./generate-testimages-im.sh): generates a set of JPEG images at 6 quality levels from a user-defined source image using [ImageMagick](https://imagemagick.org/).
- [test-quantization.py](./test-quantization.py): reads the quantization tables of one or more files and writes the values to 2 comma separated text files.
- [plot-goodness-fit.py](./plot-goodness-fit.py): creates scatterplots of image vs standard quantization tables and adds relevant measures (Q, RMSE, NSE).

Both ImageMagick based quality estimation scripts are derived and modified from [the Python port of ImageMagick's heuristic](https://gist.github.com/eddy-geek/c0f01dc5401dc50a49a0a821cdc9b3e8) by [Eddy O (AKA "eddygeek")](https://github.com/eddy-geek). In turn this port is based on [ImageMagick's original code](https://github.com/ImageMagick/ImageMagick6/blob/bf9bc7fee9f3cea9ab8557ad1573a57258eab95b/coders/jpeg.c#L925).

## Data

The directory [images](./images/) contains the following folders:

- [im_pil](./images/im_pil/): test images created with Python's Pillow library and and ImageMagick. Each image is compressed at level indicated in filename.
- [source](./images/source/): source images for all Pillow and ImageMagick test images.
- [dbnl](./images/dbnl/): examples of problematic access and master JPEGs from DBNL scans.
- [misc](./images/misc/): miscellaneous images, most of these give different quality estimates depending on which tool/method is used.

## Image attribution

- image-98.jpg, image-177.jpg: taken from [sample-images](https://github.com/yavuzceliker/sample-images)
- sample-birch-400x300.jpg: taken from [samplelib.com](https://samplelib.com/sample-jpeg.html)
- sample-jpg-files-sample-4.jpg: taken from [toolsfairy.com](https://toolsfairy.com/tools/image-test/sample-jpg-files)
- jpeg420exif.jpg, jpeg422jfif.jpg and jpeg444.jpg taken from [w3.org](https://www.w3.org/MarkUp/Test/xhtml-print/20050519/tests/A_2_1-BF-01.htm)
- hopper_16bit_qtables.jpg: taken from [Pillow test images](https://github.com/python-pillow/Pillow/tree/main/Tests/images).
