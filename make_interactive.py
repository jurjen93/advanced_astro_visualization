from interactive_plot.scripts.interactive_plot import Interactive
import argparse
from astropy.utils.data import get_pkg_data_filename

parser = argparse.ArgumentParser("Make interactive plo from fits file.")
parser.add_argument('-d', '--downloading', type=int, help='download your own data')
parser.add_argument('-fi', '--fits', type=str, help='fits file to use')
args = parser.parse_args()

if __name__ == '__main__':
    if args.downloading == 1:
        download = input('Paste here your url where to find the fits file: ')
        fits_download=True
        Image = Interactive(fits_download=True)
    else:
        fits_download = False
        if args.fits:
            file = args.fits
        else:
            file = 'fits/mosaic-blanked.fits'
        Image = Interactive(fits_file=get_pkg_data_filename(file))

    image = Interactive(fits_file=file)
    image.imaging(image_name='main.png', save=True, dpi=750)
    image.html_from_png()