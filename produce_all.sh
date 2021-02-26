#!/bin/bash

#make_poster flags
#-csv -> give catalogue csv-file.
#-d -> download fits file. Give 1 if yes.

#make_video flags
#-csv -> give catalogue csv-file.
#-d -> download fits file. Give 1 if yes.
#-o -> movie make option. Currently there are 2 two standard options. So, give 1 or 2.
#-f -> frame rate of the video. Advice is to use 60 to make video smooth.

python3 make_movie.py -csv catalogue/catalogue_lockman.csv -o 1 -f 60
python3 make_poster.py -csv catalogue/catalogue_lockman.csv