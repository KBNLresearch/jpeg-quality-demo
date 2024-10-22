#!/bin/bash

if [ "$#" -ne 2 ] ; then
  echo "Usage: generate-testimages-im.sh imageIn dirOut" >&2
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

declare -a qualities=("5" "10" "25" "50" "75" "100")

for i in "${qualities[@]}"
  do
    j=$(printf %03d $i)
    nameOut="$bName""_im_""$j"".jpg"
    imageOut="$dirOut""/""$nameOut" 
    echo "$imageOut"
    convert "-quality" "$i" "$imageIn"  "$imageOut"
  done
 

