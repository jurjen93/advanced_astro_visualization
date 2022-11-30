import argparse
import warnings
from timeit import default_timer as timer

import numpy as np
import pandas as pd
from astropy.utils.data import get_pkg_data_filename

from paths import ScanPaths
from video.scripts.moviemaker import MovieMaker

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser("Make movie from fits file.")
parser.add_argument("-d", "--downloading", type=int, help="Download your own data")
parser.add_argument("-csv", "--csvfile", help="Csv file with outliers with RA and DEC in degrees")
parser.add_argument("-fr", "--framerate", type=int, help="Frame rate of your video")
parser.add_argument("-zs", "--zoomsize", type=float, help="Size in deg of the zoomed image")
parser.add_argument("-dr", "--degrate", type=float, help="Amount of degrees traversed each second")
parser.add_argument("-fi", "--fits", type=str, help="Fits file to use")
parser.add_argument("-sc", "--scan", type=str, help="Scanning path type")
args = parser.parse_args()


def distance(obj_1, obj_2):
    return np.sqrt((obj_1[0] - obj_2[0]) ** 2 + 4 * (obj_1[1] - obj_2[1]) ** 2)


if __name__ == "__main__":
    start = timer()

    if args.framerate:
        FRAMERATE = args.framerate
    else:
        FRAMERATE = 20

    if args.zoomsize:
        ZOOMSIZE = args.zoomsize
    else:
        ZOOMSIZE = 1.4

    if args.degrate:
        DEGRATE = args.degrate
    else:
        DEGRATE = 1.0

    if args.downloading == 1:
        download = input("Paste here your url where to find the fits file: ")
        fits_download = True
        Movie = MovieMaker(fits_download=True, imsize=0.4, framerate=FRAMERATE)  # default imsize
    else:
        fits_download = False
        if args.fits:
            file = args.fits
        else:
            file = "fits/elias.fits"
        try:
            fitsfile = get_pkg_data_filename(file)
        except BaseException:
            fitsfile = file
        Movie = MovieMaker(fits_file=fitsfile, imsize=0.4, framerate=FRAMERATE, zoom_effect=False)  # default imsize

    if args.csvfile:  # go through all objects in csv file
        df = pd.read_csv(args.csvfile)[["RA", "DEC", "imsize"]]

        start_coord = Movie.wcs.pixel_to_world(Movie.image_data.shape[1] / 2, Movie.image_data.shape[0] / 2)
        start_dec = start_coord.dec.degree
        start_ra = start_coord.ra.degree

        Movie.zoom(N_frames=int(5 * Movie.framerate), first_time=True)
        for n in range(len(df) - 1):  # stack multiple sources
            if n > 0:
                dist = distance([last_RA, last_DEC], [df["RA"].values[n], df["DEC"].values[n]])
                move_to_frames = np.max(int(4 * dist * Movie.framerate), 2)
            else:
                dist = distance([start_ra, start_dec], [df["RA"].values[n], df["DEC"].values[n]])
                move_to_frames = np.max(int(4 * dist * Movie.framerate), 2)
            Movie.move_to(N_frames=move_to_frames, ra=df["RA"].values[n], dec=df["DEC"].values[n])
            zoom_frames = np.max(int(0.1 * Movie.framerate * Movie.imsize / df["imsize"].values[n]), 2)
            Movie.zoom(N_frames=zoom_frames, imsize_out=df["imsize"].values[n])
            if n < len(df) - 1 and df["imsize"].values[n + 1] > df["imsize"].values[n]:
                im_out = np.max(df["imsize"].values[n + 1] + 0.3, 0.3)
            else:
                im_out = np.max(df["imsize"].values[n] + 0.3, 0.3)
            Movie.zoom(N_frames=np.max(zoom_frames // 5, 1), imsize_out=im_out)
            last_RA, last_DEC = df["RA"].values[n], df["DEC"].values[n]
        move_to_frames = np.max(int(4 * Movie.framerate * distance([start_ra, start_dec], [last_RA, last_DEC])), 2)
        Movie.move_to(N_frames=move_to_frames, ra=start_ra, dec=start_dec)
        Movie.zoom(N_frames=int(5 * Movie.framerate), imsize_out=2)
        Movie.record()

        end = timer()
        print(f"MovieMaker took {int(end - start)} seconds")

    else:  # Go through whole field
        full_size = Movie.image_data.shape[0] * np.max(Movie.wcs.pixel_scale_matrix)

        Path = ScanPaths(movie_obj=Movie, zoom_size=ZOOMSIZE, deg_per_sec=DEGRATE)

        if args.scan == "horizontal":
            positions, n_frames = Path.horizontal_scan()
        elif args.scan == "spiral":
            positions, n_frames = Path.spiral_scan()
        else:
            print("No preferred scanning path chosen. Defaulting to horizontal scan.")
            positions, n_frames = Path.horizontal_scan()

        print(f"Moving to positions {positions} in {n_frames} frames.")

        Movie.imsize = ZOOMSIZE
        Movie.zoom(N_frames=FRAMERATE, first_time=True, full_im=True)  # Start with zoom in
        for n, pos in enumerate(positions):  # Move through path
            Movie.move_to(N_frames=n_frames[n], ra=pos[0], dec=pos[1])
        Movie.zoom(N_frames=FRAMERATE, imsize_out=full_size)  # End with zoom out
        Movie.record()

        """
        Could be added later as well: a video starting with a zoom in and ending in a zoom out could
        reuse the zoom in frames for the zoom out which should save computation time.
        """
