## About

This repository contains all analysis scripts and data that are covered by the blog post [JPEG Quality estimation: experiments with a modified ImageMagick heuristic](https://www.bitsgalore.org/2024/10/23/jpeg-quality-estimation-experiments-with-a-modified-imagemagick-heuristic).

## Scripts

Below scripts were tested with Python 3.8.10. They use the [Pillow Imaging Library](https://python-pillow.org/), which can be installed using:

```
pip install pillow
```

- [test-jpegquality-original.py](./test-jpegquality-original.py): computes JPEG quality for one or more files using original ImageMagick heuristic. Option `--verbose` prints out values of all variables in main loop at each iteration.
- [test-jpegquality-modified.py](./test-jpegquality-modified.py): computes JPEG quality for one or more files using modified ImageMagick heuristic. Option `--verbose` prints out values of all variables in main loop at each iteration.
- [test-jpegquality-sse.py](./test-jpegquality-sse.py): computes JPEG quality for one or more files using direct comparison against standard JPEG quantization tables.
- [generate-testimages-pillow.py](./generate-testimages-pillow.py): generates a set of JPEG images at 6 quality levels from a user-defined source image.
- [generate-testimages-im.sh](./generate-testimages-im.sh): generates a set of JPEG images at 6 quality levels from a user-defined source image using [ImageMagick](https://imagemagick.org/).
- [test-quantization.py](./test-quantization.py): reads the quantization tables of one or more files and writes the values to 2 comma separated text files.

Both quality estimation scripts are derived and modified from [the Python port of ImageMagick's heuristic](https://gist.github.com/eddy-geek/c0f01dc5401dc50a49a0a821cdc9b3e8) by [Eddy O (AKA "eddygeek")](https://github.com/eddy-geek). In turn this port is based on [ImageMagick's original code](https://github.com/ImageMagick/ImageMagick6/blob/bf9bc7fee9f3cea9ab8557ad1573a57258eab95b/coders/jpeg.c#L925).

## Data

The directory [images](./images/) contains the following test images:

- [260761857-bdf17e14-c697-4f4a-b6d5-e3067e0afc08.jpg](./images/260761857-bdf17e14-c697-4f4a-b6d5-e3067e0afc08.jpg): example of problematic JPEG extracted from scanned PDF for which ImageMagick's heuristic fails. 
- test_pil_0??.jpg: test images compressed at ??% quality using Python's Pillow library.
- test_im_0??.jpg: test images compressed at ??% quality using ImageMagick.
- test.tif: source image for all Pillow and ImageMagick tesy images.
