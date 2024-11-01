#!/bin/bash
# Generate test images using separate quality levels for
# luminance and chrominance
if [ "$#" -ne 2 ] ; then
  echo "Usage: generate-testimages-cjpeg.sh imageIn dirOut" >&2
  exit 1
fi

if ! [ -f "$1" ] ; then
  echo "imageIn must be a file" >&2
  exit 1
fi

if ! [ -d "$2" ] ; then
  echo "output directory must be a directory" >&2
  exit 1
fi

imageIn="$1"
dirOut="$2"

fName=$(basename "$imageIn")
bName=${fName%%.*}

for qlum in {1..100}
  do
    for qchrom in {1..100}
      do
        i=$(printf %03d $qlum)
        j=$(printf %03d $qchrom)
        nameOut="$bName"_l"$i"_c"$j".jpg""
        imageOut="$dirOut""/""$nameOut" 
        cjpeg "-q" "$qlum","$qchrom" "$imageIn" > "$imageOut"
      done
  done