import os
import warnings
from video.scripts.moviemaker import MovieMaker
from astropy.utils.data import get_pkg_data_filename
from timeit import default_timer as timer
import pandas as pd
import argparse
from numpy import sqrt
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser("Make movie from fits file.")
parser.add_argument('-d', '--downloading', type=int, help='Download your own data')
parser.add_argument('-csv', '--csvfile', help='Csv file with outliers with RA and DEC in degrees')
parser.add_argument('-fr', '--framerate', help='Frame rate of your video')
parser.add_argument('-fi', '--fits', type=str, help='Fits file to use')
parser.add_argument('-N', '--sourcenum', type=int, help='Number of sources from catalogue')
args = parser.parse_args()

def distance(obj_1, obj_2):
    return sqrt((obj_1[0]-obj_2[0])**2+(obj_1[1]-obj_2[1])**2)

if __name__ == '__main__':
    start = timer()

    if args.framerate: FRAMERATE = args.framerate
    else: FRAMERATE = 64

    if args.sourcenum: N = args.sourcenum
    else: N = 2

    if args.csvfile: df = pd.read_csv(args.csvfile)[['RA', 'DEC']]
    else: df = pd.read_csv('catalogue/'+os.listdir('catalogue')[0])[0:N]

    if args.downloading == 1:
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

    start_coord = Movie.wcs.pixel_to_world(Movie.image_data.shape[0]/2, Movie.image_data.shape[0]/2)
    start_dec = start_coord.dec.degree
    start_ra = start_coord.ra.degree
    Movie.zoom_in(N_frames=1000, first_time=True)
    for n in range(len(df)):#stack multiple sources
        if n > 0:
            dist = distance([last_RA, last_DEC], [df['RA'].values[n], df['DEC'].values[n]])
            move_to_frames = int(300*dist)
        else:
            dist = distance([start_ra, start_dec], [df['RA'].values[n], df['DEC'].values[n]])
            move_to_frames = int(300*dist)
        print(f'Number of frames {move_to_frames}')
        Movie.move_to(N_frames=move_to_frames, ra=df['RA'].values[n], dec=df['DEC'].values[n])
        Movie.zoom_in(N_frames=300, imsize_out=df['imsize'].values[n])
        if n<len(df)-1 and df['imsize'].values[n+1]>df['imsize'].values[n]:
            im_out = max(df['imsize'].values[n+1]+0.1, 0.3)
        else:
            im_out = max(df['imsize'].values[n] + 0.1, 0.3)
        Movie.zoom_out(N_frames=300, imsize_out=im_out)
        last_RA, last_DEC = df['RA'].values[n], df['DEC'].values[n]
    Movie.move_to(N_frames=int(600*distance([start_ra, start_dec], [df['RA'].values[N-1], df['DEC'].values[N-1]])), ra=start_ra, dec=start_dec)
    Movie.zoom_out(N_frames=1000, imsize_out=2)
    Movie.record()

    end = timer()
    print(f'MovieMaker took {int(end - start)} seconds')

