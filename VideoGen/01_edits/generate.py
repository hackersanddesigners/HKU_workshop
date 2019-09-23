import os, random, pathlib, time
from moviepy.editor import *
from math import *
import time

start_time = time.time()
cwd =  pathlib.Path.cwd()
pathlib.Path( cwd / 'input' ).mkdir( parents=True, exist_ok=True )
src_path = cwd / 'input'
output_file_duration = 15 # specified length of the video
duration_left = output_file_duration # time left in video
allowed = [ ".mov", ".mp4", ".m4v" ] # allowed file extensions in input folder
max_seg_length = 5 # max segment length
output_size = ( 1920, 1080 )

def generate():
    print( "Creating movie of %s seconds. Max segment length: %s." % ( output_file_duration, max_seg_length ) )

    files = getVideoFiles( src_path ) # load all the clips in the /input directory
    final = mainComp( files ) # make random selection add filters and concat them

    timestr = time.strftime( "%Y-%m%d-%H%M%S" )
    filename = "output/hdsa%s.mp4" % timestr
    final.write_videofile( filename, threads = 16 ) # write the video to file
    #final.save_frame( "frame.png", t = 0.5 ) # saves the frame a t=2s

    print ( "\a" )
    print("--- %s seconds ---" % (time.time() - start_time))

# Load all clips and store them in an array
def getVideoFiles( path ):
    files = []
    for i, file in enumerate( sorted( path.glob( '*' ) ) ):
        filename, ext = os.path.splitext( file.name )
        if( ext in allowed ):
            print( "Input file: %s" % file )
            files.append( file )
    return files

# The main edit sequence. Pick a bunch of random clips, pick a random segment of those clips,
# stick them together until we reach the desired duration. Apply effects to some of them.
def mainComp( files ):
    global duration_left
    edits = []
    while duration_left > 0:
        seg = randomEdit( files, duration_left )
        duration_left -= seg.duration
        print( "duration left: %s" % duration_left )
        edits.append( seg )
    return concatenate_videoclips( edits )

def randomEdit( files, max_duration ):
    # global duration_left
    clip = VideoFileClip( str( random.choice ( files ) ) )
    len = random.uniform( 1, min( min( max_seg_length, max_duration ), clip.duration ) ) # random length, shorter than duration of the clip, time left in the video and max_seg_length
    start = random.uniform( 0, int( clip.duration ) - len )
    if start + len > clip.duration: # length cant be longer then the time left in the clip
        len = int( clip.duration - start )
    print( "Segment \"%s\", start: %ss, length: %ss, clip duration: %ss" % ( os.path.basename(clip.filename), start, len, clip.duration ) )
    seg = clip.subclip( start, start + len )
    seg = seg.on_color( size=output_size, color=randomColor() )
    return seg

def randomColor():
    return ( random.randint( 0, 255 ), random.randint( 0, 255 ), random.randint( 0, 255 ) )

def main(argv):
    generate()

if __name__ == "__main__":
   main( sys.argv[ 1: ] )