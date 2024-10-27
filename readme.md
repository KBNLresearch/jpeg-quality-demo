## About

This repository contains all analysis scripts and data that are covered by the blog post [JPEG Quality estimation: experiments with a modified ImageMagick heuristic](https://www.bitsgalore.org/2024/10/23/jpeg-quality-estimation-experiments-with-a-modified-imagemagick-heuristic).

## Scripts

Below scripts were tested with Python 3.8.10. They use the [Pillow Imaging Library](https://python-pillow.org/), which can be installed using:

```
pip install pillow
```

- [test-jpegquality-im-original.py](./test-jpegquality-im-original.py): computes JPEG quality for one or more files using original ImageMagick heuristic. Option `--verbose` prints out values of all variables in main loop at each iteration.
- [test-jpegquality-im-modified.py](./test-jpegquality-im-modified.py): computes JPEG quality for one or more files using modified ImageMagick heuristic. Option `--verbose` prints out values of all variables in main loop at each iteration.
- [test-jpegquality-tablematch.py](./test-jpegquality-tablematch.py): computes JPEG quality for one or more files using direct comparison against standard JPEG quantization tables.
- [test-jpegquality-compare.py](./test-jpegquality-compare.py): computes JPEG quality for one or more files using all of the above methods and write results in comma-delimited format. 
- [generate-testimages-pillow.py](./generate-testimages-pillow.py): generates a set of JPEG images at 6 quality levels from a user-defined source image.
- [generate-testimages-im.sh](./generate-testimages-im.sh): generates a set of JPEG images at 6 quality levels from a user-defined source image using [ImageMagick](https://imagemagick.org/).
- [test-quantization.py](./test-quantization.py): reads the quantization tables of one or more files and writes the values to 2 comma separated text files.

Both quality estimation scripts are derived and modified from [the Python port of ImageMagick's heuristic](https://gist.github.com/eddy-geek/c0f01dc5401dc50a49a0a821cdc9b3e8) by [Eddy O (AKA "eddygeek")](https://github.com/eddy-geek). In turn this port is based on [ImageMagick's original code](https://github.com/ImageMagick/ImageMagick6/blob/bf9bc7fee9f3cea9ab8557ad1573a57258eab95b/coders/jpeg.c#L925).

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
