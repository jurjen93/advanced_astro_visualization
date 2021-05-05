from poster.scripts.imaging import ImagingLofar
from astropy.utils.data import get_pkg_data_filename
import os
import pandas as pd
import argparse

parser = argparse.ArgumentParser("Make poster from fits file.")
parser.add_argument('-d', '--downloading', type=int, help='download your own data')
parser.add_argument('-csv', '--csvfile', help='csv file with outliers with RA and DEC in degrees', default='catalogue/catalogue_lockman.csv')
parser.add_argument('-fi', '--fits', type=str, help='fits file to use')
args = parser.parse_args()

if __name__ == '__main__':
    if args.csvfile:
        df = pd.read_csv(args.csvfile)[['RA', 'DEC', 'size_x', 'size_y']].to_numpy()[0:12]
    else:
        df = pd.read_csv(os.listdir('catalogue')[0])

    if args.downloading == 1:
        download = input('Paste here your url where to find the fits file: ')
        fits_download=True
        Image = ImagingLofar(fits_download=True)
    else:
        fits_download = False
        if args.fits:
            file = args.fits
        else:
            file = 'fits/lockman_hole.fits'
        Image = ImagingLofar(fits_file=get_pkg_data_filename(file))

    Image.imaging(image_name='main.png', save=True, dpi=3000)

    for n, position in enumerate(df):
        if position[3]==position[3]:
            Image.image_cutout(pos=tuple(position[0:2]), size=tuple(position[2:4]), image_name=f'cutout_{n}.png',
                               save=True, cmap='jet')
        else:
            Image.image_cutout(pos=tuple(position[0:2]), image_name=f'cutout_{n}.png', save=True, cmap='jet')

    try:
        os.system('python poster/scripts/make_pdf.py')
    except:
        print("You need Scribus version 1.5 or higher to convert the .sla file to .pdf \n"
              "see for example: "
              "https://sourceforge.net/projects/scribus/files/scribus-devel/1.5.5/scribus-1.5.5-windows-x64.exe/download")