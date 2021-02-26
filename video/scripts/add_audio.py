import moviepy.editor as mpe
import argparse

parser = argparse.ArgumentParser("Add audio to your video.")
parser.add_argument('-a', '--audio', type=str, help='audio file location')
parser.add_argument('-v', '--input video', type=str, help='input video file location')
parser.add_argument('-ov', '--output video', type=str, help='output video file', default='output.mp4')
args = parser.parse_args()

if __name__ == '__main__':
    my_clip = mpe.VideoFileClip(args.video)
    audio_background = mpe.AudioFileClip(args.audio)
    new_audioclip = mpe.CompositeAudioClip([audio_background])
    my_clip.audio = new_audioclip
    my_clip.write_videofile(args.output, codec= 'mpeg4', audio_codec='libvorbis')