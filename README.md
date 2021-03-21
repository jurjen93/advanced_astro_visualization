### Details

With this repo you can make a **poster**, a **video**, or **interactive plot** of a full .fits image.

Note that this script is written for **astronomy applications**. However, by rewriting some parts in the script, 
you can also use it for other types of applications. In the example we used the lockman_hole.fits made with LOFAR.\
Other .fits files from LOFAR can be found here:
https://lofar-surveys.org/ \

### Clone repo
You need to clone this repo with:
```git clone https://github.com/jurjen93/advanced_astro_visualiziation.git```

### Catalogue csv file
You need to have a catalogue with sources. We have an example given in the folder 'catalogue'.\
Use the following fields:
* ```source_id```   -> id of the source
* ```RA```          -> right ascension of the object
* ```DEC```         -> declination of the object
* ```size_x```      -> size on the x-axis of the object (in pixel or degree size)
* ```size_y```      -> size on the y-axis of the object (in pixel or degree size)
* ```imsize```      -> image size in degrees

### How to make the poster

First, download **Scribus**:
https://sourceforge.net/projects/scribus/files/scribus-devel/1.5.5/scribus-1.5.5-windows-x64.exe/download

Run now:\
```python make_poster.py```\
where you can use the following flags
* ```-d``` -> Choose to download a specific fits file from the internet. Use ```1``` if you want to, leave empty otherwise.
* ```-csv``` -> Give a specific csv file with sources to include as cutouts in the poster.
* ```-fi``` -> Fits file to use. (If you don't download your fits file)

Example:\
```python make_poster.py -csv catalogue/catalogue_lockman.csv -fi fits/lockman_hole.fits```
  
### How to make the video
Run:\
```python make_video.py```\
where you can use the following flags
* ```-d``` -> Choose to download a specific fits file from the internet. Use ```1``` if you want to, leave empty otherwise.
* ```-csv``` -> Give a specific csv file with sources to include as cutouts in the poster.
* ```-N``` -> Number of sources to use
* ```-fr``` -> Frame rate of the video. Advice is to use ```60``` to make the video smooth.
* ```-fi``` -> Fits file to use. (If you don't download your fits file)

Example:\
```python make_video.py -csv catalogue/catalogue_lockman.csv -d 1 -N 2 -f 60```
Example videos: \
https://www.youtube.com/watch?v=r5oo5qSEYbc \
https://www.youtube.com/watch?v=dwDbPiB35eI

### How to make the interactive plot
Run:\
```python make_interactive.py```\
where you can use the following flags
* ```-d``` -> Choose to download a specific fits file from the internet. Use ```1``` if you want to, leave empty otherwise.
* ```-fi``` -> Fits file to use. (If you don't download your fits file)

Example:\
```python make_interactive.py -fi fits/lockman_hole.fits```

### Output
**Poster**: *poster.pdf*\
**Video**: *movie.mp4*\
**Interactive plot**: *interactive.html*

### Future development

The project is not finished because the following things are still on the todo-list:
* Make sure that higher resolution images can be transformed into a pdf as well. (video/poster)
* Place the cutouts near the source location with a line attached. (poster)
* Automatically classify sources as interesting for the cutouts. (video/poster)
* Automatically assign an image size to the object for the cutouts. (poster)
* Other fancy updates are welcome as well!

### Contact/Collaboration

Feel free to send me a message if you want to help me out with improvements or if you have any suggestions.\
Contact: jurjendejong(AT)strw.leidenuniv.nl
