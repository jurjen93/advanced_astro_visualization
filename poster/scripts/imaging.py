import matplotlib.pyplot as plt
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
from matplotlib.colors import LogNorm, SymLogNorm
import warnings
warnings.filterwarnings("ignore")

__all__ = ['ImagingLofar']

class ImagingLofar:
    def __init__(self, fits_file=None, fits_download: bool=False, vmin: float = None, vmax: float = None,
                 image_directory: str='poster/images', verbose: bool = True, zoom_effect: bool = True, interactive: bool = False):
        """
        Make LOFAR images (also applicable on other telescope surveys)
        ------------------------------------------------------------
        :param fits_file: Fits file name and path
        :param fits_download: Boolean for downloading or not
        :param vmin: cutoff minimal flux
        :param vmax: cutoff max flux
        :param image_directory: directory to output the images
        :param verbose: printing extra comments during making
        """
        self.fits_file = fits_file
        self.verbose = verbose
        self.zoom_effect = zoom_effect
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
        if vmin is None:
            self.vmin = np.nanstd(self.image_data)
        else:
            self.vmin = vmin
        if vmax is None:
            self.vmax = np.nanstd(self.image_data)*20
        else:
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

        #Transfer function
        if not interactive:
            if 'cutout' in self.fits_file:
                self.image_data = gaussian_filter(self.tonemap(image_data=self.image_data, b=0.25, threshold=self.vmin), sigma=3)
            elif 'ILTJ' in self.fits_file:
                self.image_data = gaussian_filter(self.tonemap(image_data=self.image_data, b=0.25, threshold=self.vmin/1.5), sigma=4)
            else:
                if self.zoom_effect:
                    self.image_data = gaussian_filter(self.tonemap(image_data=self.image_data, b=0.5, threshold=0), sigma=2)
                else:
                    self.image_data = gaussian_filter(self.tonemap(image_data=self.image_data, b=0.25, threshold=self.vmin/100), sigma=1)
        else:
            self.image_data = gaussian_filter(
                self.tonemap(image_data=self.image_data, b=0.25, threshold=self.vmin / 100), sigma=1)


    def tonemap(self, image_data=None, b: float = 0.25, threshold: float = None):
        """
        Tonemap the image based on dynamic range. This enables both diffuse and point structures to be clearly visible.
        Works best on unsigned data for now. Scaling both negative and positive is a bit experimental.
        This mapping is based on http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.219.7383&rep=rep1&type=pdf
        :param image_data: image data
        :param b: smoothing param
        :param threshold: threshold for positive and residual components
        :return transformed data
        """
        if threshold is None:
            threshold = 0
        data_pos = np.where(image_data > threshold, image_data, np.nan)
        data_res = np.where(image_data < threshold, image_data, np.nan)
        data_pos_tm = (np.nanmax(data_pos) * 0.01 / np.log10(np.nanmax(data_pos) + 1)) * (np.log10(data_pos + 1)) / (
            np.log10(2 + ((data_pos / np.nanmax(data_pos)) ** (np.log10(b) / np.log10(0.5))) * 8))
        data_res_tm = (np.nanmax(data_res) * 0.01/ np.log10(np.nanmax(data_res) + 1)) * (np.log10(data_res + 1)) / (
            np.log10(2 + ((data_res / np.nanmax(data_res)) ** (np.log10(b) / np.log10(0.5))) * 8))
        data_tm = np.where(image_data > threshold, np.sqrt(data_pos_tm), -1*np.sqrt(np.abs(data_res_tm)))
        return data_tm

    def imaging(self, image_data=None, wcs=None, image_name: str = 'Nameless', dpi: int = None, save: bool = True,
                cmap: str = 'CMRmap', text: str = None, imsize: float = None, ra=None, dec=None):
        """
        Imaging of your data.
        ------------------------------------------------------------
        :param image_data: the image data (in numpy array)
        :param wcs: coordinate system
        :param image_name: name of your output image
        :param dpi: dots per inch
        :param save: save image (True/False)
        :param cmap: cmap of your image
        :param text: text in the left down corner of your image
        :param imsize: image size in degrees
        :param ra: right ascension
        :param dec: declination
        """

        if image_data is None:
            image_data = self.image_data
        if wcs is None:
            wcs=self.wcs
        if dpi is None:
            w = 16
            h = image_data.shape[1]/image_data.shape[0]*9
            dpi = image_data.shape[0]/10
        else:
            h=9
            w=16
        plt.figure(figsize=(h, w))
        plt.subplot(projection=wcs)
        if imsize is None:
            imsize=1
        if 'cutout' in self.fits_file:
            plt.imshow(image_data, origin='lower', cmap=cmap, vmin=self.vmin*2)
        else:
            #HIGH RES VIDEO:
            if self.zoom_effect:
                vmax = self.vmax
                vmin = min((2/max(imsize,0.2))*(self.vmin/100), self.vmax/20)
                if imsize<1:
                    vmax/=max(imsize, 0.2)
                if imsize<0.1:
                    vmin+=imsize/100*(0.1/imsize)**1.35
                image_data=gaussian_filter(image_data, sigma=2)

                plt.imshow(image_data,
                           norm=SymLogNorm(linthresh=vmin*20, vmin=self.vmin/1.4, vmax=vmax), origin='lower', cmap=cmap)
            else:
                plt.imshow(np.clip(image_data, a_min=None, a_max=self.vmax),
                           norm=LogNorm(vmin=self.vmin / 1.4, vmax=self.vmax), origin='lower', cmap=cmap)
        if text:
            plt.annotate(
                s=text,
                xy=(0, 0),
                xytext=(0, 0),
                va='top',
                ha='left',
                fontsize=20,
                bbox=dict(facecolor='white', alpha=1),
            )
        elif ra and dec and imsize>0.1:
            plt.annotate(
                s=f'RA: {round(ra, 5)}\nDEC: {round(dec, 5)}',
                xy=(0, 0),
                xytext=(0, 0),
                va='top',
                ha='left',
                fontsize=10,
                bbox=dict(facecolor='white', alpha=0.7),
            )
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

        return self

    def make_cutout(self, pos: tuple = None, size: tuple = (1000, 1000)):
        """
        Make cutout from your image.
        ------------------------------------------------------------
        :param pos: position in degrees (RA, DEC)
        :param size: size of your image in pixel size
        :return: cutout data and cutout wcs (coordinate system)
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
        To pixel position from RA and DEC
        ------------------------------------------------------------
        :param ra: Right ascension (degrees)
        :param dec: Declination (degrees)
        :return: Pixel of position
        """
        position = coordinates.SkyCoord(ra, dec,
                                        frame=wcs.utils.wcs_to_celestial_frame(self.wcs).name,
                                        unit=(u.degree, u.degree))
        position = np.array(position.to_pixel(self.wcs))
        return position

    def image_cutout(self, pos: tuple = None, size: tuple = None, dpi: float = 1000, image_name: str = None,
                     save: bool = True, cmap: str = 'CMRmap', text: str = None, imsize: float = None):
        """
        Make image cutout and make image
        ------------------------------------------------------------
        :param pos: position in degrees (RA, DEC)
        :param size: size of your image in pixel size
        :param dpi: dots per inch
        :param image_name: name of output image
        :param save: save image (yes or no)
        :param cmap: cmap of your image
        :param text: text in the left down corner of your image
        :param imsize: image size in degrees
        """
        ra, dec = pos
        pix_x, pix_y = self.to_pixel(ra, dec)
        if size:
            if size[0]<2 and size[0]<2:
                size = (np.int(imsize/np.max(self.wcs.pixel_scale_matrix)), np.int(imsize/np.max(self.wcs.pixel_scale_matrix)))
        else:
            size = (np.int(imsize/np.max(self.wcs.pixel_scale_matrix)), np.int(imsize/np.max(self.wcs.pixel_scale_matrix)))
        image_data, wcs = self.make_cutout((pix_x, pix_y), size)
        if self.verbose:
            print(f"Let's now image '{image_name.replace('_',' ').replace('.png','').replace('.',' ').title()}'")
        if size[0]<dpi:
            dpi=size[0]
        self.imaging(image_data=image_data, wcs=wcs, image_name=image_name, dpi=dpi,
                     save=save, cmap=cmap, text=text, imsize=imsize, ra=ra, dec=dec)
        return self

    def make_fits(self, pos: tuple = None, size: tuple = (1000, 1000), filename: str = None, imsize: float = None):
        """
        Make image cutout and make fitsfile
        ------------------------------------------------------------
        :param pos: position in degrees (RA, DEC)
        :param size: size of your image in pixel size
        :param filename: name of output fits image
        :param imsize: image size in degrees
        """
        ra, dec = pos
        pix_x, pix_y = self.to_pixel(ra, dec)
        if size:
            if size[0]<2 and size[0]<2:
                size = (np.int(imsize/np.max(self.wcs.pixel_scale_matrix)), np.int(imsize/np.max(self.wcs.pixel_scale_matrix)))
        else:
            size = (np.int(imsize/np.max(self.wcs.pixel_scale_matrix)), np.int(imsize/np.max(self.wcs.pixel_scale_matrix)))
        image_data, wcs = self.make_cutout((pix_x, pix_y), size)
        self.hdu.data = image_data
        self.hdu.header.update(wcs.to_header())
        self.hdu.writeto(f'{self.image_directory}/{filename}', overwrite=True)
        return self

if __name__ == '__main__':
    print('Cannot call script directly.')
