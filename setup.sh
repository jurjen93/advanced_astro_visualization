#!/bin/bash

#install requirements
pip install -r requirements.txt

#make alias to run script easier
alias makevideo="python3 $PWD/make_movie.py"
alias makeimage="python3 $PWD/make_image.py"
alias makeposter="python3 $PWD/make_poster.py"
alias makeinteractive="python3 $PWD/make_interactive.py"

#chmod everything
chmod u+x $PWD/make_movie.py
chmod u+x $PWD/make_image.py
chmod u+x $PWD/make_poster.py
chmod u+x $PWD/make_interactive.py