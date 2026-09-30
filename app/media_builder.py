from pathlib import Path
import subprocess, shutil
from app.config import Config

ROOT=Path(__file__).resolve().parent.parent
MUSIC=ROOT/'assets/music'

def music_for_theme(theme_id):
    return MUSIC / (f'{int(theme_id):02d}_' + {1:'sky_breeze',2:'mint_fresh',3:'peach_glow',4:'lavender_pop',5:'rose_petal',6:'lemon_sun',7:'aqua_glass',8:'coral_wave',9:'indigo_sky',10:'teal_garden',11:'blueberry',12:'apricot'}[int(theme_id)] + '.wav')

def make_video(image_path, video_path, theme_id, duration=18):
    image=Path(image_path); video=Path(video_path); music=music_for_theme(theme_id)
    if not image.exists(): raise FileNotFoundError(image)
    if not music.exists(): raise FileNotFoundError(music)
    video.parent.mkdir(parents=True,exist_ok=True)
    # Original, locally generated ambient track. Audio is intentionally mixed low.
    cmd=['ffmpeg','-y','-loop','1','-i',str(image),'-i',str(music),'-t',str(duration),'-vf','format=yuv420p','-c:v','libx264','-preset','veryfast','-tune','stillimage','-r','30','-c:a','aac','-b:a','96k','-af','volume=0.16','-shortest',str(video)]
    subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    return video
