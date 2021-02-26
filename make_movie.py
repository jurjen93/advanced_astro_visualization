import os
import warnings
from video.scripts.moviemaker import MovieMaker
from astropy.utils.data import get_pkg_data_filename
from timeit import default_timer as timer
import pandas as pd
import argparse
warnings.filterwarnings("ignore")

options = [1, 2]

parser = argparse.ArgumentParser("Make movie from fits file.")
parser.add_argument('-d', '--downloading', type=int, help='download your own data')
parser.add_argument('-csv', '--csvfile', help='csv file with outliers with RA and DEC in degrees')
parser.add_argument('-o', '--option', help=f'you can use the following standard video options: {" ".join([str(i) for i in options])}')
parser.add_argument('-fr', '--framerate', help='frame rate of your video')
parser.add_argument('-fi', '--fits', type=str, help='fits file to use')
args = parser.parse_args()

if __name__ == '__main__':
    start = timer()

    if args.csvfile: df = pd.read_csv(args.csvfile)[['RA', 'DEC', 'size_x', 'size_y']].to_numpy()
    else: df = pd.read_csv('catalogue/'+os.listdir('catalogue')[0])

    if args.option: OPTION = args.option
    else: OPTION = '1'

    if args.framerate: FRAMERATE = args.framerate
    else: FRAMERATE = 60

    if args.downloading == 1:
        download = input('Paste here your url where to find the fits file: ')
        fits_download = True
        Movie = MovieMaker(fits_download=True,
                           imsize=0.4,#defaul imsize
                            framerate=FRAMERATE)
    else:
        fits_download = False
        if args.fits:
            file = args.fits
        else:
            file = 'fits/lockman_hole.fits'
        Movie = MovieMaker(fits_file=get_pkg_data_filename(file),
                           imsize=0.4,#defaul imsize
                            framerate=FRAMERATE)
    if OPTION=='test':
        Movie.zoom_in(N_frames=5, first_time=True).\
            move_to(N_frames=5, ra=df['RA'].values[0], dec=df['DEC'].values[0]).\
            zoom_in(N_frames=5, imsize_out=0.2).\
            zoom_out(N_frames=5, imsize_out=0.7). \
            record()
    elif OPTION=='1':
        Movie.zoom_in(N_frames=750, first_time=True).\
            move_to(N_frames=2000, ra=df['RA'].values[0], dec=df['DEC'].values[0]).\
            zoom_in(N_frames=1000, imsize_out=0.2).\
            zoom_out(N_frames=500, imsize_out=0.7). \
            move_to(N_frames=2000, ra=df['RA'].values[2], dec=df['DEC'].values[2]).\
            zoom_in(N_frames=1000, imsize_out=0.2).\
            record()
    elif OPTION=='2':
        Movie.zoom_in(N_frames=1000, first_time=True).\
            move_to(N_frames=2000, ra=df['RA'].values[0], dec=df['DEC'].values[0]).\
            zoom_in(N_frames=1000, imsize_out=0.4).\
            move_to(N_frames=2000, ra=df['RA'].values[2], dec=df['DEC'].values[2]).\
            zoom_in(N_frames=1000, imsize_out=0.2). \
            move_to(N_frames=2000, ra=df['RA'].values[1], dec=df['DEC'].values[1]). \
            zoom_out(N_frames=1000, imsize_out=0.7). \
            record()

        """Add your own movie OPTIONS below!"""

    else:
        print(f'Choose from options: {" ".join([str(i) for i in options])} by using the -o or --option flag.\nYou can also create your own.')

    end = timer()
    print(f'MovieMaker took {int(end - start)} seconds')