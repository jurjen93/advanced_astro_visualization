from bokeh.plotting import figure, show, output_file
from poster.scripts.imaging import ImagingLofar

class Interactive(ImagingLofar):
    def __init__(self, fits_file: str=None, fits_download: bool=False):
        super().__init__(fits_file=fits_file, image_directory='interactive_plot/images',
                         verbose=False, fits_download=fits_download, interactive=True)

    def html_from_png(self):

        output_file('interactive.html')
        x_low, y_low = list(float(i) for i in self.wcs.array_index_to_world_values(0, 0))
        x_high, y_high = list(float(i) for i in self.wcs.array_index_to_world_values(self.image_data.shape[0], self.image_data.shape[1]))
        print(x_low, y_low)
        print(x_high, y_high)
        p = figure(x_range=(x_low, x_high), y_range=(y_low, y_high), tools='hover,pan,wheel_zoom',
                   active_scroll='wheel_zoom', active_drag='pan')
        p.image_url(['interactive_plot/images/main.png'], x=x_low, y=y_high, h=y_high-y_low, w=x_low-x_high)
        p.xgrid.visible = False
        p.ygrid.visible = False

        p.xaxis.axis_label = 'RA (deg)'
        p.yaxis.axis_label = 'DEC (deg)'
        p.xaxis.axis_label_text_font_style = "bold"
        p.yaxis.axis_label_text_font_style = "bold"

        p.xaxis.major_tick_line_color = "firebrick"
        p.xaxis.major_tick_line_width = 3
        p.xaxis.minor_tick_line_color = "orange"

        p.yaxis.major_tick_line_color = "firebrick"
        p.yaxis.major_tick_line_width = 3
        p.yaxis.minor_tick_line_color = "orange"

        p.axis.major_tick_out = 10
        p.axis.minor_tick_in = -3
        p.axis.minor_tick_out = 8

        show(p)

if __name__ == '__main__':
    print('Cannot call script directly.')