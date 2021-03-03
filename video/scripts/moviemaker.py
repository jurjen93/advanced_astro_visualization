import os
import numpy as np
from multiprocessing import cpu_count, Pool
from multiprocessing.dummy import Pool as ThreadPool
import warnings
from poster.scripts.imaging import ImagingLofar
from tqdm import tqdm
warnings.filterwarnings("ignore")

__all__ = ['MovieMaker']

class MovieMaker(ImagingLofar):
    """
    MovieMaker makes it possible to make individual frames and turn them into a video.
    """
    def __init__(self, fits_file: str = None, imsize: float = None, framerate: float = None, process: str = None,
                 fits_download: bool=False, new: bool = True, highres: bool = False, text: str = None):
        """
        :param fits_file: fits file name
        :param imsize: initial image size
        :param framerate: frame rate
        :param process: process [multiprocess, multithread, None]
        :param fits_download: download fits file
        """
        super().__init__(fits_file = fits_file, image_directory='video/frames', verbose=False, fits_download = fits_download)
        self.process = process
        self.imsize = imsize
        self.framerate = framerate
        self.ra = None
        self.dec = None
        self.highres = highres
        self.text = text
        if new:
            os.system('rm -rf video/frames; mkdir video/frames')

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
        if self.process == 'multiprocess':
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
        self.image_cutout(pos=(ra, dec),
                          size=(imsize/np.max(self.wcs.pixel_scale_matrix), imsize/np.max(self.wcs.pixel_scale_matrix)),
                          dpi=dpi,
                          image_name=f'image_{str(N).rjust(5, "0")}.png',
                          gaussian=False,
                          tonemap=self.highres,
                          cmap='CMRmap',
                          text=self.text)
        return self

    def make_frames(self):
        """
        Record individual frames and save in video/frames/
        ------------------------------------------------------------
        """
        N_max = len(os.listdir('video/frames'))+len(self.ragrid) #max number of videos
        N_min = len(os.listdir('video/frames')) #min number of videos
        inputs = zip(range(N_min, N_max), self.ragrid, self.decgrid, self.imsizes,
                     np.clip(200/np.array(self.imsizes), a_min=100, a_max=350).astype(int))
        if self.process == "multithread":
            print(f"Multithreading")
            print(f"Might get error or bad result because multithreading is difficult with imaging.")
            with ThreadPool(8) as p:
                p.starmap(self.make_frame, inputs)
        elif self.process == 'multiprocess':
            print(f"You are using {cpu_count()} cpu's for multiprocessing")
            with Pool(cpu_count()) as p:
                p.starmap(self.make_frame, inputs)
        else:
            for inp in tqdm(inputs):
                self.make_frame(inp[0], inp[1], inp[2], inp[3], inp[4])
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

    def zoom_in(self, N_frames: int = None, first_time: bool=False, imsize_out: float = None, full_im: bool = False):
        """
        Zoom in.
        ------------------------------------------------------------
        :param N_frames: Number of frames.
        :param first_time: Is this the first move? If so, give True.
        :param imsize_out: Output image size.
        :param full_im: start with full image. Otherwise with 1/4th (can be manually changed if needed)
        """
        if first_time:
            begin_size = self.image_data.shape[0] * np.max(self.wcs.pixel_scale_matrix)
            if not full_im:
                begin_size/=4
            end_size = self.imsize
            coordinates = self.wcs.pixel_to_world(self.image_data.shape[0]/2, self.image_data.shape[0]/2)
            self.dec = coordinates.dec.degree
            self.ra = coordinates.ra.degree
        else:
            begin_size = self.imsize
            end_size = max(imsize_out, 0.03)
        self.imsizes = np.linspace(end_size, begin_size, N_frames)[::-1]
        self.imsize = self.imsizes[-1]
        self.ragrid = np.array([self.ra]*len(self.imsizes))
        self.decgrid = np.array([self.dec]*len(self.imsizes))
        self.make_frames()
        return self

    def zoom_out(self, N_frames: int = None, imsize_out: float = None):
        """
        Zoom out.
        ------------------------------------------------------------
        :param N_frames: Number of frames.
        :param imsize_out: Output image size.
        """
        self.imsizes = np.linspace(self.imsize, imsize_out, N_frames)
        self.imsize = self.imsizes[-1]
        self.ragrid = np.array([self.ra]*len(self.imsizes))
        self.decgrid = np.array([self.dec]*len(self.imsizes))
        self.make_frames()
        return self

    def record(self, audio: str = None):
        """
        Frames to video, which will be saved as movie.mp4.
        ------------------------------------------------------------
        :param audio: add audio (True or False).
        """
        os.system(f'rm movie.mp4; ffmpeg -f image2 -r {self.framerate} -start_number 0 -i video/frames/image_%05d.png movie.mp4')
        if audio:
            try:
                audio_file = input(audio)
                os.system(f'ffmpeg -i movie.mp4 -i {audio_file} -t 65 audiomovie.mp4')
            except:
                print('Audio file does not exist')
        return self

if __name__ == '__main__':
    print('Cannot call script directly.')