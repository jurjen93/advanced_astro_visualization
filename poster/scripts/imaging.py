import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
from astropy.wcs import WCS
from astropy.io import fits
from astropy.utils.data import download_file
from astropy.nddata import Cutout2D
import astropy.units as u
from astropy import wcs
from astropy import coordinates
import numpy as np
import os
from scipy.ndimage import gaussian_filter

__all__ = ['ImagingLofar']

class ImagingLofar:
    def __init__(self,fits_file=None, fits_download: bool=False, vmin: float = -2.5e-05, vmax: float = 6.520e-03,
                 image_directory: str='poster/images', verbose=True):
        self.verbose = verbose
        if self.verbose:
            print(f"Started imaging {fits_file.split('/')[-1].replace('.fits','').replace('_',' ').replace('.',' ').title()}...")
        if fits_download:
            link = input('Past here your fits link: \n')
            self.hdu = download_file(link, cache=True)
        else:
            self.hdu = fits.open(fits_file)[0]
        self.image_data=self.hdu.data
        while len(self.image_data.shape)!=2:
            self.image_data=self.image_data[0]
        self.wcs = WCS(self.hdu.header, naxis=2)
        self.vmin = vmin
        self.vmax = vmax
        self.image_directory = image_directory
        try:
            os.mkdir(self.image_directory)
        except OSError:
            if verbose:
                print(f"The directory '{self.image_directory}' already exists.")
            else:
                pass
        else:
            print(f"Successfully created the directory: '{self.image_directory}'")

    def imaging(self, image_data=None, wcs=None, image_name: str = 'Nameless', dpi: int = None, save: bool = True,
                cmap: str = 'CMRmap', gaussian : bool = False):
        """
        Image your data with this method.
        image_data -> you can insert other image_data manually
        image_name -> pick a name for your image
        dpi -> pixel density, default=1000
        save -> boolean True/False, default=True (because we like to save stuff)
        cmap -> choose your cmap
        """
        if image_data is None:
            image_data = self.image_data
        if wcs is None:
            wcs=self.wcs
        if dpi is None:
            w = 10
            h = image_data.shape[1]/image_data.shape[0]*10
            dpi = image_data.shape[0]/10
        else:
            h=10
            w=10
        if gaussian:
            image_data = gaussian_filter(image_data, sigma=3)
        plt.figure(figsize=(h, w))
        plt.subplot(projection=wcs)
        plt.imshow(image_data, norm=SymLogNorm(linthresh=1e-5,vmin=7e-5, vmax=np.nanstd(image_data)*25), origin='lower', cmap=cmap)
        plt.xlabel('Galactic Longitude')
        plt.ylabel('Galactic Latitude')
        plt.grid(False)
        plt.axis('off')
        plt.tight_layout()
        plt.subplots_adjust(left=0.0, bottom=0.0, top=1.0, right=1.0)
        if save:
            plt.savefig(f'{self.image_directory}/{image_name}', bbox_inches='tight', dpi=dpi, facecolor='black',
                        edgecolor='black')
            plt.close()
        else:
            plt.show()
        if self.verbose:
            print(f"You can now find your image in '{self.image_directory}/{image_name}'")

    def make_cutout(self, pos: tuple = None, size: tuple = (1000, 1000)):
        """
        Make cutout from your image with this method.
        pos (tuple) -> position in pixels, no default
        size (tuple) -> size of your image in pixel size, default=(1000,1000)
        """
        if self.verbose:
            print(f"We are now making a cutout from your image.")
        cutout = Cutout2D(
            data=self.image_data,
            position=pos,
            size=size,
            wcs=self.wcs,
            mode='partial'
        )
        if self.verbose:
            print(f"Cutout finished")
        return cutout.data, cutout.wcs

    def to_pixel(self, ra: float = None, dec: float = None):
        """
        ra -> right ascension in degrees, default=None
        dec -> declination in degrees, default=None,
        """
        position = coordinates.SkyCoord(ra, dec,
                                        frame=wcs.utils.wcs_to_celestial_frame(self.wcs).name,
                                        unit=(u.degree, u.degree))
        position = np.array(position.to_pixel(self.wcs))
        return position

    def image_cutout(self, pos: tuple = None, size: tuple = (1000, 1000), dpi: float = 1000, image_name: str = 'Nameless',
                     save: bool = True, cmap: str = 'jet', gaussian : bool = False):
        """
        pos (tuple) -> position in degrees, no default
        size (tuple) -> size of your image in pixel size, default=(1000,1000)
        image_name (str) -> give your image a name, default='No name'
        save (bool) -> save your image
        cmap (str) -> choose cmap
        """
        ra, dec = pos
        pix_x, pix_y = self.to_pixel(ra, dec)
        if size[0]<2 and size[0]<2:
            size = self.to_pixel(size[0], size[1])
        image_data, wcs = self.make_cutout((pix_x, pix_y), size)
        if self.verbose:
            print(f"Let's now image '{image_name.replace('_',' ').replace('.png','').replace('.',' ').title()}'")
        if size[0]<dpi:
            dpi=size[0]
        self.imaging(image_data=image_data, wcs=wcs, image_name=image_name, dpi=dpi,
                     save=save, cmap=cmap, gaussian=gaussian)

if __name__ == '__main__':
    print('Cannot call script directly.')