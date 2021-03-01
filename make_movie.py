import os
import warnings
from video.scripts.moviemaker import MovieMaker
from astropy.utils.data import get_pkg_data_filename
from timeit import default_timer as timer
import pandas as pd
import argparse
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser("Make movie from fits file.")
parser.add_argument('-d', '--downloading', type=int, help='Download your own data')
parser.add_argument('-csv', '--csvfile', help='Csv file with outliers with RA and DEC in degrees')
parser.add_argument('-fr', '--framerate', help='Frame rate of your video')
parser.add_argument('-fi', '--fits', type=str, help='Fits file to use')
parser.add_argument('-N', '--sourcenum', type=int, help='Number of sources from catalogue')
args = parser.parse_args()

if __name__ == '__main__':
    start = timer()

    if args.csvfile: df = pd.read_csv(args.csvfile)[['RA', 'DEC', 'size_x', 'size_y']].to_numpy()
    else: df = pd.read_csv('catalogue/'+os.listdir('catalogue')[0])

    if args.framerate: FRAMERATE = args.framerate
    else: FRAMERATE = 60

    if args.sourcenum: N = args.sourcenum
    else: N = 1

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

    Movie.zoom_in(N_frames=500, first_time=True)
    Movie.move_to(N_frames=1500, ra=df['RA'].values[0], dec=df['DEC'].values[0]).\
        zoom_in(N_frames=500, imsize_out=0.35).\
        zoom_out(N_frames=500, imsize_out=0.7)
    for n in range(1, N):#stack multiple sources
        Movie.move_to(N_frames=1500, ra=df['RA'].values[n], dec=df['DEC'].values[n]).\
            zoom_in(N_frames=500, imsize_out=0.3). \
            zoom_out(N_frames=500, imsize_out=0.7)
    Movie.record()


    end = timer()
    print(f'MovieMaker took {int(end - start)} seconds')