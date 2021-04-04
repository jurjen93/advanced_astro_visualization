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
    return sqrt((obj_1[0]-obj_2[0])**2+4*(obj_1[1]-obj_2[1])**2)

def isNaN(a):
    return a!=a

if __name__ == '__main__':
    start = timer()

    if args.framerate: FRAMERATE = args.framerate
    else: FRAMERATE = 60

    if args.sourcenum: N = args.sourcenum
    else: N = 2

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
                            framerate=FRAMERATE, zoom_effect=False)

    if args.csvfile:#go through all objects in csv file
        df = pd.read_csv(args.csvfile)[['RA', 'DEC']]

        start_coord = Movie.wcs.pixel_to_world(Movie.image_data.shape[0]/2, Movie.image_data.shape[0]/2)
        start_dec = start_coord.dec.degree
        start_ra = start_coord.ra.degree

        Movie.zoom_in(N_frames=800, first_time=True)
        for n in range(len(df)):#stack multiple sources
            if n > 0:
                dist = distance([last_RA, last_DEC], [df['RA'].values[n], df['DEC'].values[n]])
                move_to_frames = int(250*dist)
            else:
                dist = distance([start_ra, start_dec], [df['RA'].values[n], df['DEC'].values[n]])
                move_to_frames = int(250*dist)
            print(f'Number of frames {move_to_frames}')
            Movie.move_to(N_frames=move_to_frames, ra=df['RA'].values[n], dec=df['DEC'].values[n])
            Movie.zoom_in(N_frames=300, imsize_out=df['imsize'].values[n])
            if n<len(df)-1 and df['imsize'].values[n+1]>df['imsize'].values[n]:
                im_out = max(df['imsize'].values[n+1]+0.1, 0.3)
            else:
                im_out = max(df['imsize'].values[n] + 0.1, 0.3)
            Movie.zoom_out(N_frames=300, imsize_out=im_out)
            last_RA, last_DEC = df['RA'].values[n], df['DEC'].values[n]
        print(f"Number of frames {int(400*distance([start_ra, start_dec], [df['RA'].values[N-1], df['DEC'].values[N-1]]))}")
        Movie.move_to(N_frames=int(400*distance([start_ra, start_dec], [df['RA'].values[N-1], df['DEC'].values[N-1]])), ra=start_ra, dec=start_dec)
        Movie.zoom_out(N_frames=800, imsize_out=2)
        Movie.record()

        end = timer()
        print(f'MovieMaker took {int(end - start)} seconds')

    else:#go through whole field
        from numpy import sqrt, abs, isnan
        fits_header = Movie.wcs.to_header()

        number_of_steps = int(fits_header['CRPIX1']*2/3500)
        if number_of_steps%2==0:
            number_of_steps+=1 # make number of steps uneven to come back in the center

        # clean_image = Movie.image_data[~isnan(Movie.image_data).all(axis=1),:]
        # clean_image = clean_image[:,~isnan(clean_image).all(axis=0)]
        pix_x_size = fits_header['CRPIX1']*2 #pixel x axis size
        pix_y_size = fits_header['CRPIX2']*2 #pixel y axis size
        # x_cut = pix_x_size-clean_image.shape[0] #how much cut x
        # y_cut = pix_y_size-clean_image.shape[1] #how much cut y
        step_size_x = int(pix_x_size/number_of_steps)
        step_size_y = int(pix_y_size/number_of_steps)
        start_pix_x = int((pix_x_size)/(number_of_steps*2))
        start_pix_y = int(pix_y_size*((number_of_steps*2-1)/(number_of_steps*2)))

        pos_x = start_pix_x
        pos_y = start_pix_y
        positions = [[start_pix_x, start_pix_y]]
        for i in range(number_of_steps-1):
            pos_x+=step_size_x
            positions.append([pos_x, pos_y])

        for i in range(1,number_of_steps)[::-1]:
            for j in range(i):
                pos_y = pos_y + ((-1)**(i+number_of_steps))*step_size_y
                positions.append([pos_x, pos_y])
            for j in range(i):
                pos_x = pos_x + ((-1)**(i+number_of_steps))*step_size_x
                positions.append([pos_x, pos_y])

        positions = [(p.ra.degree, p.dec.degree) for p in [Movie.wcs.pixel_to_world(position[0], position[1])
                                                           for position in positions
                                                           if not isNaN(Movie.image_data[position[0], position[1]])]]

        Movie.imsize = 2*abs(fits_header['CDELT1']*fits_header['CRPIX1']/7)
        Movie.zoom_in(N_frames=600, first_time=True)
        start_coord = Movie.wcs.pixel_to_world(Movie.image_data.shape[0] / 2, Movie.image_data.shape[0] / 2)
        start_dec = start_coord.dec.degree
        start_ra = start_coord.ra.degree
        for n, position in enumerate(positions):
            if n==0:
                dist = distance([start_ra, start_dec], [position[0], position[1]])
            else:
                dist = distance([position[0], position[1]], [positions[n-1][0], positions[n-1][1]])
            move_to_frames = int(200 * dist)
            print(f'Number of frames {move_to_frames}')
            Movie.move_to(N_frames=move_to_frames, ra=position[0], dec=position[1])
        Movie.zoom_out(N_frames=600, imsize_out=3)
        Movie.record()