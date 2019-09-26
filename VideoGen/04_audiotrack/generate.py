import os, random, pathlib, time
from moviepy.editor import *
from math import *
import time

start_time = time.time()
cwd =  pathlib.Path.cwd()
pathlib.Path( cwd / 'input' ).mkdir( parents=True, exist_ok=True )
src_path = cwd / 'input'
output_file_duration = 10 # specified length of the video
duration_left = output_file_duration # time left in video
allowed = [ ".mov", ".mp4", ".m4v" ] # allowed file extensions in input folder
max_seg_length = 3 # max segment length
output_size = ( 1920, 1080 )

audios = []

def generate():
    global audios
    print( "Creating movie of %s seconds. Max segment length: %s." % ( output_file_duration, max_seg_length ) )

    files = getVideoFiles( src_path ) # load all the clips in the /input directory
    final = mainComp( files ) # make random selection add filters and concat them

    # als de videos random gekozen worden in mainComp worden de audio tracks
    # ebwaard in de lijst 'audios'
    random.shuffle( audios ) # die randomizen we
    # om de tijden aan elkaar te plakken moeten we de begin tijd elke track
    # aan passen aan het einde van de vorige
    t = 0 # begin tijd van eerste audio track
    new_audios = [] #nieuwe lijst

    for track in audios:
        track = track.set_start( t ) # t = begin tijd
        t = t + track.duration # duration van deze track erbij op tellen
        new_audios.append( track ) # opslaan in de lijst
    audio = CompositeAudioClip( new_audios )# van de nieuwe lijst maken we audio track
    final.audio = audio # en die gebruiken we voor de uiteindelijke video

    # final = effectsGenerator( final, 2 ) # add effects to the whole shebang

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
    global duration_left, audios
    edits = []
    while duration_left > 0:
        seg = randomEdit( files, duration_left )
        audios.append( aud ) # kopie van de audio van dit segment bewaren we in de lijst audios
        seg = effectsGenerator( seg )
        duration_left -= seg.duration
        print( "duration left: %s" % duration_left )
        edits.append( seg )
    return concatenate_videoclips( edits )

def randomEdit( files, max_duration ):
    # global duration_left
    clip = VideoFileClip( str( random.choice ( files ) ) )
    len = random.uniform( 0.1, min( min( max_seg_length, max_duration ), clip.duration ) ) # random length, shorter than duration of the clip, time left in the video and max_seg_length
    start = random.uniform( 0, int( clip.duration ) - len )
    if start + len > clip.duration: # length cant be longer then the time left in the clip
        len = int( clip.duration - start )
    print( "Segment \"%s\", start: %ss, length: %ss, clip duration: %ss" % ( os.path.basename(clip.filename), start, len, clip.duration ) )
    seg = clip.subclip( start, start + len )
    print( "seg ", seg.duration, seg.audio.duration )
    seg = seg.on_color( size=output_size, color=randomColor() )
    return seg

def randomColor():
    return ( random.randint( 0, 255 ), random.randint( 0, 255 ), random.randint( 0, 255 ) )

def effectsGenerator( clip, chance = 6 ):
    luckyNumber = random.randint( 0, chance ) # pick a random number
    # luckyNumber = 2
    effects = {
        0: effect_flicker,
        1: effect_saturate,
        2: effect_saturate2,
        3: effect_invert,
        4: effect_speed,
        # 4: effect_blink,
    }
    if( luckyNumber in effects ): # if the lucky number has an effect, apply it.
        print( "Apply effect %s" % effects[ luckyNumber ] )
        clip = effects[ luckyNumber ]( clip )
    return clip

def effect_flicker( clip ):
    # clip = ( clip.fx( vfx.colorx, 0.5 ) ) # darken
    return clip.fl_image( fuck_channels )

def effect_saturate( clip ):
    return clip.fx( vfx.colorx, factor=3 )

def effect_saturate2( clip ):
    return clip.fx( vfx.colorx, factor=2 )

def effect_speed( clip ):
    return clip.fx( vfx.time_symmetrize ).fx( vfx.speedx, factor = 2 )

def effect_invert( clip ):
    return clip.fx( vfx.invert_colors   )

def invert_green_blue( image ):
    return image[:,:,[0,2,1]]

def fuck_channels( image ):
    r = random.randint( 0, 2 ) # change channel order for each frame
    if r == 0:
        return image[:,:,[2,0,1]]
    elif r == 1:
        return image[:,:,[1,2,0]]
    else:
        return image[:,:,[0,2,1]]

def main(argv):
    generate()

if __name__ == "__main__":
   main( sys.argv[ 1: ] )
