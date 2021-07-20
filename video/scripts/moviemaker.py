import os
import numpy as np
from multiprocessing import cpu_count, Pool
from multiprocessing.dummy import Pool as ThreadPool
import warnings
from poster.scripts.imaging import ImagingLofar
import cv2 as cv
from glob import glob
from termcolor import colored
warnings.filterwarnings("ignore")

__all__ = ['MovieMaker']

class MovieMaker(ImagingLofar):
    """
    MovieMaker makes it possible to make individual frames and turn them into a video.
    """
    def __init__(self, fits_file: str = None, imsize: float = None, framerate: float = None, process: str = None,
                 fits_download: bool=False, new: bool = True, text: str = None, vmin: float = None, vmax: float = None, zoom_effect: bool = False,
                 output_file: str = 'frames', cmap: str = None):
        """
        :param fits_file: fits file name
        :param imsize: initial image size
        :param framerate: frame rate
        :param process: process [multiprocess, multithread, None]
        :param fits_download: download fits file
        :param cmap: choose your favorite cmap
        """
        self.output_file = output_file
        super().__init__(fits_file = fits_file, image_directory=self.output_file, verbose=False, fits_download=fits_download, vmin=vmin, vmax=vmax, zoom_effect=zoom_effect)
        self.process = process
        self.imsize = imsize
        self.framerate = framerate
        self.ra = None
        self.dec = None
        self.text = text
        self.zoom_effect = zoom_effect
        self.total_count = 0
        if cmap:
            self.cmap = cmap
        else:
            self.cmap = 'CMRmap'
        if new:
            os.system(f'rm -rf {output_file}; mkdir {output_file}')


    def __call__(self, imsize: float = None, process: str = None):
        """
        __call__ method enables the option to change the instances.
        You don't have to type '__call__'. So, you can change the instance in the following way:
        Movie = MovieMaker(fits_file, imsize, process,...)
        Movie(imsize=0.9, process='multiprocess')
        ------------------------------------------------------------
        :param imsize: current new image size
        :param process: process [multiprocess, multithread, None]
        """
        if imsize:
            self.imsize=imsize
            print(f'Current image size: {self.imsize}')
        if process:
            self.process=process
            print(f'Process: {self.process}')
        pass

    def __getstate__(self):
        """ This is called before pickling"""
        if self.process=='multiprocess':
            state = self.__dict__.copy()
            del state['hdu']
            return state

    def __setstate__(self, state):
        """ This is called while unpickling. """
        self.__dict__.update(state)

    def make_frame(self, N, ra = None, dec = None, imsize: float = None, dpi: float = 300):
        """
        Make seperate frame (image)
        ------------------------------------------------------------
        :param N: image number
        :param ra: right ascension (degrees)
        :param dec: declination (degrees)
        :param imsize: image size (pixel or degree size)
        :param dpi: dots per inch (pixel density)
        """
        print(colored(f"Frame number: {N-self.N_min}/{self.N_max-self.N_min}", 'red'), end='\r')

        ## reduce jitter by always having a central pixel (force odd size)
        size1 = np.int(imsize/np.max(self.wcs.pixel_scale_matrix))
        size2 = np.int(imsize/np.max(self.wcs.pixel_scale_matrix)*1.77)
        if size1%2 == 0:
            size1 = size1 + 1
        if size2%2 == 0:
            size2 = size2 + 1
        self.image_cutout(pos=(ra, dec),
                          size=(size1,size2),
                          dpi=dpi,
                          image_name=f'image_{str(N).rjust(5, "0")}.png',
                          cmap=self.cmap,
                          text=self.text,
                          imsize=imsize)
        return self

    def make_frames(self):
        """
        Record individual frames and save in frames/
        ------------------------------------------------------------
        """
        self.N_max = len(os.listdir(self.output_file))+len(self.ragrid) #max number of videos
        self.N_min = len(os.listdir(self.output_file)) #min number of videos
        inputs = zip(range(self.N_min, self.N_max), self.ragrid, self.decgrid, self.imsizes,
                     np.clip(200/np.array(self.imsizes), a_min=450, a_max=700).astype(int))

        print('-------------------------------------------------')
        print(colored(f'Imaging {len(self.ragrid)} frames for current move.', 'green'))

        if self.process == "multithread":
            print(f"Multithreading")
            print(f"Might get error or bad result because multithreading is difficult with imaging.")
            with ThreadPool(8) as p:
                p.starmap(self.make_frame, inputs)
        elif self.process == 'multiprocess':
            cpus=2
            print(f"You are using {cpus} cpu's for multiprocessing")
            def chunked_input(input, chunksize):
                input = list(input)
                input_out=[]
                for r in range(chunksize):
                    input_out +=input[r::chunksize]
                del input
                return input_out
            try:
                with Pool(cpus) as p:
                    p.starmap(self.make_frame, chunked_input(inputs,cpus), chunksize=cpus)
            except:
                pass
        else:
            for inp in inputs:
                self.make_frame(inp[0], inp[1], inp[2], inp[3], inp[4])
        print('-------------------------------------------------')
        return self

    def move_to(self, first_time: bool = False, ra: float = None, dec: float = None, N_frames: int = None):
        """
        Move to specific location.
        ------------------------------------------------------------
        :param first_time: Is this the first move? If so, give True.
        :param ra: Right Ascension of end point.
        :param dec: Declination of end point.
        :param N_frames: Number of frames.
        """
        if first_time:
            start_ra, start_dec = max(ra, 0), max(dec, 0)
        else:
            start_ra, start_dec = self.ra, self.dec
        self.ra, self.dec = ra, dec
        if ra>start_ra:
            self.ragrid = np.linspace(start_ra, ra, N_frames)  # deg
        else:
            self.ragrid = np.linspace(ra, start_ra, N_frames)[::-1]
        if dec>start_dec:
            self.decgrid = np.linspace(start_dec, dec, N_frames)  # deg
        else:
            self.decgrid = np.linspace(dec, start_dec, N_frames)[::-1]
        self.imsizes = [self.imsize]*N_frames
        self.make_frames()
        return self

    def zoom(self, N_frames: int = None, first_time: bool=False, imsize_out: float = None, full_im: bool = False):
        """
        Zoom in.
        ------------------------------------------------------------
        :param N_frames: Number of frames.
        :param first_time: Is this the first move? If so, give True.
        :param imsize_out: Output image size.
        :param full_im: start with full image (when first_time==True)
        """
        if first_time:
            begin_size = self.image_data.shape[0] * np.max(self.wcs.pixel_scale_matrix)
            if not full_im:
                begin_size/=2
            end_size = self.imsize
            coordinates = self.wcs.pixel_to_world(int(self.image_data.shape[1]/2), int(self.image_data.shape[0]/2))
            self.dec = coordinates.dec.degree
            self.ra = coordinates.ra.degree
        else:
            begin_size = self.imsize
            end_size = imsize_out
        self.imsizes = np.linspace(begin_size, end_size, N_frames)
        self.imsize = self.imsizes[-1]
        self.ragrid = np.array([self.ra]*len(self.imsizes))
        self.decgrid = np.array([self.dec]*len(self.imsizes))
        self.make_frames()
        return self

    # def zoom_out(self, N_frames: int = None, imsize_out: float = None):
    #     """
    #     Zoom out.
    #     ------------------------------------------------------------
    #     :param N_frames: Number of frames.
    #     :param imsize_out: Output image size.
    #     """
    #     self.imsizes = np.linspace(self.imsize, imsize_out, N_frames)
    #     self.imsize = imsize_out
    #     self.ragrid = np.array([self.ra]*len(self.imsizes))
    #     self.decgrid = np.array([self.dec]*len(self.imsizes))
    #     self.make_frames()
    #     return self

    def record(self, audio: str = None):
        """
        Frames to video, which will be saved as movie.mp4.
        ------------------------------------------------------------
        :param audio: add audio (True or False).
        """
        os.system(f'rm movie.mp4; ffmpeg -f image2 -r {self.framerate} -start_number 0 -i {self.output_file}/image_%05d.png movie.mp4')
        if audio:
            try:
                audio_file = input(audio)
                os.system(f'ffmpeg -i movie.mp4 -i {audio_file} -t 65 audiomovie.mp4')
            except:
                print('Audio file does not exist')
        return self

def crop_center(img,cropx,cropy):
    y,x,_ = img.shape
    startx = x//2-(cropx//2)
    starty = y//2-(cropy//2)
    return img[starty:starty+cropy,startx:startx+cropx,:]

def fading_effect(source, frames):
    images = glob('/home/jurjen/Documents/Python/advanced_astro_visualization/frames_high/*')
    img1 = cv.imread(sorted(images)[-1])
    img1 = cv.GaussianBlur(img1, (5,5), 0)
    img2 = cv.imread(glob(f'/home/jurjen/Documents/Python/advanced_astro_visualization/fits/highres_P205/{source}*MFS-image.png')[0])

    #add extra empty rows to reshape img2
    add_rows = int((img1.shape[1]/img1.shape[0]*img2.shape[1]-img2.shape[1])/2)
    new = np.zeros((img2.shape[0], img2.shape[1]+add_rows*2, 3), dtype=np.float32)
    new[:, add_rows:new.shape[1]-add_rows, :] = img2
    img2 = new
    #resize now img2
    img1 = cv.resize(img1, (img2.shape[1], img2.shape[0]), interpolation=cv.INTER_AREA) # reshape image
    for i in np.append(np.linspace(0, 1, frames//2), np.linspace(0, 1, frames//2)[::-1]):
        alpha = i
        beta = 1 - alpha
        output = cv.addWeighted(img2, alpha, img1, beta, 0, dtype=cv.CV_32F)
        output = crop_center(output, int((1 - i/4) * output.shape[1]), int((1 - i/4) * output.shape[0]))
        n=1
        if alpha==1:
            n=frames//6
        for r in range(n):
            images = glob('/home/jurjen/Documents/Python/advanced_astro_visualization/frames_high/*')
            new_im_name = f'/home/jurjen/Documents/Python/advanced_astro_visualization/frames_high/image_{str(len(images)).rjust(5, "0")}.png'
            cv.imwrite(new_im_name, output)

if __name__ == '__main__':
    print('Cannot call script directly.')
