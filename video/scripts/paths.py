from math import ceil

import numpy as np


def isNaN(a):
    return a != a


class ScanPaths:
    """
    ScanPaths is an accessible way to make scanning paths over an image.
    """

    def __init__(self, movie_obj=None, zoom_size: float = None, deg_per_sec: float = None):
        """
        :param movie_obj: instance of MovieMaker class
        :param zoom_size: size in deg to which the image is zoomed, default 1.4 deg
        """
        self.Movie = movie_obj
        self.zoom_size = zoom_size
        self.deg_per_sec = deg_per_sec
        self.fits_header = self.Movie.wcs.to_header()
        self.central_ra = self.fits_header["CRVAL1"]
        self.central_dec = self.fits_header["CRVAL2"]
        self.pix_x_size = int(self.fits_header["CRPIX1"] * 2)  # x axis size in pixels
        self.pix_y_size = int(self.fits_header["CRPIX2"] * 2)  # y axis size in pixels
        self.deg_x_size = np.abs(self.pix_x_size * self.fits_header["CDELT1"])  # x axis size in degrees
        self.deg_y_size = np.abs(self.pix_y_size * self.fits_header["CDELT2"])  # y axis size in degrees
        self.zoom_factor_x = self.deg_x_size / zoom_size  # For now assumed to be equal to zoom_factor_y

        # These pixel positions give a reference frame from which to build the paths:
        self.left_x = int(self.pix_x_size / (self.zoom_factor_x * 2))
        self.right_x = int(self.pix_x_size - self.left_x)
        self.upper_y = int(self.pix_y_size * ((self.zoom_factor_x * 2 - 1) / (self.zoom_factor_x * 2)))
        self.lower_y = int(self.pix_y_size - self.upper_y)

    def move_upper_left(self, positions):
        positions.append([self.left_x, self.upper_y])
        return positions

    def move_center(self, positions):
        positions.append([int(self.pix_x_size / 2), int(self.pix_y_size / 2)])
        return positions

    def move_full_left(self, positions):
        current_pos = positions[-1]
        positions.append([self.left_x, current_pos[1]])
        return positions

    def move_full_right(self, positions):
        current_pos = positions[-1]
        positions.append([self.right_x, current_pos[1]])
        return positions

    def move_full_down(self, positions):
        current_pos = positions[-1]
        positions.append([current_pos[0], self.lower_y])
        return positions

    def move_full_up(self, positions):
        current_pos = positions[-1]
        positions.append([current_pos[0], self.upper_y])
        return positions

    def vertical_shift(self, positions, shift_size):
        """Negative shift_size corresponds to a downward shift."""
        current_pos = positions[-1]
        positions.append([current_pos[0], current_pos[1] + shift_size])
        return positions

    def horizontal_shift(self, positions, shift_size):
        """Negative shift_size corresponds to a leftward shift."""
        current_pos = positions[-1]
        positions.append([current_pos[0] + shift_size, current_pos[1]])
        return positions

    def pix2deg(self, positions):
        try:
            positions = [
                (p.ra.degree, p.dec.degree)
                for p in [
                    self.Movie.wcs.pixel_to_world(position[0], position[1])
                    for position in positions
                    if not isNaN(self.Movie.image_data[position[0], position[1]])
                ]
            ]
        except BaseException:
            positions = [
                (p.ra.degree, p.dec.degree)
                for p in [self.Movie.wcs.pixel_to_world(position[0], position[1]) for position in positions]
            ]
        return positions

    def frames_per_move(self, deg_positions):
        # Include central starting position to calculate shift distance of first move
        start_pos = np.array([self.central_ra, self.central_dec])
        full_deg_positions = np.concatenate(([start_pos], deg_positions))

        # Calculate distance in degrees of each move
        ra_diff = np.abs(np.diff(full_deg_positions[:, 0]))
        ra_diff_min = np.where(ra_diff > 180, np.abs(ra_diff - 360), ra_diff)  # Corrects for crossing zero meridian
        dec_diff = np.abs(np.diff(full_deg_positions[:, 1]))
        dist = np.sqrt(ra_diff_min**2 + dec_diff**2)

        dist2frames = dist / self.deg_per_sec * self.Movie.framerate
        return np.maximum(dist2frames.astype(int), 2)

    def horizontal_scan(self):
        """Makes a horizontal scanning path over the image, starting from the upper left corner."""
        n_scans = int(ceil(self.deg_y_size / self.zoom_size))  # Amount of horizontally moving scans
        vertical_shift_size = int(self.pix_y_size / n_scans)

        positions = []
        self.move_upper_left(positions)  # Move to start position
        for i in range(n_scans):
            if i % 2 == 0:
                if i != n_scans - 1:  # The last move does not contain a shift downward
                    positions = self.move_full_right(positions)
                    positions = self.vertical_shift(positions, -vertical_shift_size)
                else:
                    positions = self.move_full_right(positions)
            else:
                if i != n_scans - 1:
                    positions = self.move_full_left(positions)
                    positions = self.vertical_shift(positions, -vertical_shift_size)
                else:
                    positions = self.move_full_left(positions)
        positions = self.move_center(positions)

        deg_positions = self.pix2deg(positions)
        n_frames = self.frames_per_move(deg_positions)
        return np.array(deg_positions), n_frames

    def spiral_scan(self):
        """Makes a spiralling scanning path over the image, starting from the upper left corner
        and going horizontally to the right."""
        n_scans = int(ceil(self.deg_y_size / self.zoom_size))  # Amount of horizontally moving scans
        shift_size = int(self.pix_y_size / n_scans)  # Again, assuming square image
        n_iterations = ceil(n_scans / 2 - 1)  # To account for performing multiple moves each iteration
        positions = []
        self.move_upper_left(positions)  # Move to start position
        for i in range(n_iterations + 1):
            if i == n_iterations:  # The last iteration is different for even and odd n_scans
                if i % 2 == 0:
                    positions = self.move_full_right(positions)
                    positions[-1][0] -= i * shift_size

                    positions = self.move_full_down(positions)
                    positions[-1][1] += i * shift_size

                    positions = self.move_full_left(positions)
                    positions[-1][0] += i * shift_size

                    positions = self.move_center(positions)
                else:
                    positions = self.move_full_right(positions)
                    positions[-1][0] -= i * shift_size
            else:
                positions = self.move_full_right(positions)
                positions[-1][0] -= i * shift_size

                positions = self.move_full_down(positions)
                positions[-1][1] += i * shift_size

                positions = self.move_full_left(positions)
                positions[-1][0] += i * shift_size

                positions = self.move_full_up(positions)
                positions[-1][1] -= (i + 1) * shift_size
        deg_positions = self.pix2deg(positions)
        n_frames = self.frames_per_move(deg_positions)
        return np.array(deg_positions), n_frames
