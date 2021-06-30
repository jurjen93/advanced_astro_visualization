from poster.scripts.imaging import ImagingLofar
import argparse
import os

parser = argparse.ArgumentParser("Make cutout image from fits file.")
parser.add_argument('-fi', '--fits', type=str, help='Fits file to use')
parser.add_argument('-ra', '--right_ascension', type=float, help='RA in degrees')
parser.add_argument('-dec', '--declination', type=float, help='DEC in degrees')
parser.add_argument('-si', '--image_size', type=float, help='Image size in degrees (for squared region)')
parser.add_argument('-ia', '--interactive', type=bool, default=True, help='Display image in interactive mode')
args = parser.parse_args()

if args.image_size:
    imsize = args.image_size
else:
    imsize = 0.4

filename = '_'.join(args.fits.split('/')[-1].split('.')[0:-1]+[str(args.right_ascension), str(args.declination)])

Image = ImagingLofar(fits_file=args.fits, image_directory='cutouts', verbose=False)
Image.image_cutout(image_name=filename+'.png',
              dpi=100, pos=(args.right_ascension, args.declination), imsize=imsize)
print(f'Made {filename}.png')
Image.make_fits(pos=(args.right_ascension, args.declination), imsize=0.4,
                filename=filename+'.fits')
print(f'Made {filename}.fits')

if args.interactive:
    os.system(f'python make_interactive.py -fi cutouts/{filename}.fits')