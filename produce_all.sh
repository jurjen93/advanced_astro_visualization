#!/bin/bash

#make_poster.py flags
#-csv -> give catalogue csv-file.
#-d -> download fits file. Give 1 if yes.
#-fi -> fits file to use. (If you don't download your fits file)

#make_video.py flags
#-csv -> give catalogue csv-file.
#-d -> download fits file. Give 1 if yes.
#-o -> movie make option. Currently there are 2 two standard options. So, give 1 or 2.
#-f -> frame rate of the video. Advice is to use 60 to make video smooth.
#-fi -> fits file to use. (If you don't download your fits file)

#make_interactive.py flags
#-d -> download fits file. Give 1 if yes.
#-fi -> fits file to use. (If you don't download your fits file)

python3 make_movie.py -csv catalogue/catalogue_lockman.csv -o 1 -fr 60
python3 make_poster.py -csv catalogue/catalogue_lockman.csv
python3 make_interactive.py