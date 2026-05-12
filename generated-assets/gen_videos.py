import math, os, struct, wave
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
OUT = "/home/openclaw/.openclaw/workspace/generated-assets/video"
AUD = "/home/openclaw/.openclaw/workspace/generated-assets/audio"
FRAMES = "/tmp/evez_frames"

def font(size, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

def lerp(a, b, t): return a + (b - a) * max(0, min(1, t))
def ease(t): return t * t * (3 - 2 * t)

print("🎬 Generating circuit_animated.mp4...")
os.makedirs(FRAMES, exist_ok=True)
dur = 25
fb=font(52,True); fm=font(28,True); fs=font(20); fx=font(14); fvar=font(72,True); fform=font(40,True)
circuits = [
    {"name":"TEMPORAL","var":"τ","color":(0,255,255),"desc":"Temporal decay","pos":(160,120)},
    {"name":"SPECTRAL","var":"ω","color":(138,43,226),"desc":"Weighted signal","pos":(520,120)},
    {"name":"RELATIONAL","var":"topo","color":(255,215,0),"desc":"Topology","pos":(880,120)},
    {"name":"SPATIAL","var":"3D","color":(0,255,128),"desc":"EMF fusion","pos":(280,520)},
    {"name":"META","var":"√N","color":(255,0,255),"desc":"poly_c eval","pos":(720,520)},
]
hub = (540, 340)

for frame in range(dur * FPS):
    sec = frame / FPS
    img = Image.new('RGBA', (W, H), (10, 10, 15, 255))
    draw = ImageDraw.Draw(img)
    off = int(sec*15)%40
    for x in range(-40+off, W+40, 40): draw.line([(x,0),(x,H)], fill=(0,255,255,8))
    for y in range(-40+off, H+40, 40): draw.line([(0,y),(W,y)], fill=(0,255,255,8))
    for i in range(30):
        px=(i*137+int(sec*20))%W; py=(i*251+int(sec*15+math.sin(i+sec)*30))%H
        draw.ellipse([px,py,px+2,py+2], fill=(0,255,255,15+int(10*math.sin(sec*2+i))))

    if sec < 4:
        a = int(255*ease(min(1,sec/2)))
        draw.text((W//2,200),"EVEZ-OS",fill=(0,255,255,a),font=fb,anchor="mm")
        draw.text((W//2,270),"CIRCUIT ARCHITECTURE",fill=(255,0,255,a),font=fm,anchor="mm")
        draw.text((W//2,320),"5 Circuits -> 1 Hub -> poly_c",fill=(136,136,136,a),font=fs,anchor="mm")
    elif sec < 18:
        ci_idx = min(4, int((sec-4)/2.5))
        ci_t = (sec-4-ci_idx*2.5)/2.5
        for ci in range(ci_idx+1):
            c = circuits[ci]; cx,cy = c["pos"]; col = c["color"]
            pulse = 1+0.15*math.sin(sec*3+ci); r = int(35*pulse)
            for gr in range(r+20,r,-1):
                ga=int(40*(1-(gr-r)/20)); draw.ellipse([cx-gr,cy-gr,cx+gr,cy+gr],outline=(*col,ga))
            draw.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(*col,25),outline=(*col,180),width=2)
            draw.text((cx,cy),c["var"],fill=(*col,255),font=fvar,anchor="mm")
            draw.text((cx,cy+r+15),c["name"],fill=(*col,150),font=fs,anchor="mt")
            draw.text((cx,cy+r+35),c["desc"],fill=(*col,80),font=fx,anchor="mt")
            if ci < ci_idx or (ci==ci_idx and ci_t>0.3):
                lt = ease(min(1,(ci_t-0.3)/0.7)) if ci==ci_idx else 1.0
                hx,hy = hub; ex=int(lerp(cx,hx,lt)); ey=int(lerp(cy,hy,lt))
                draw.line([(cx,cy),(ex,ey)],fill=(*col,60),width=2)
                pt=(sec*0.5+ci*0.3)%1; ppx=int(lerp(cx,hx,pt)); ppy=int(lerp(cy,hy,pt))
                draw.ellipse([ppx-4,ppy-4,ppx+4,ppy+4],fill=(*col,200))
    else:
        rt = ease(min(1,(sec-18)/4))
        for ci,c in enumerate(circuits):
            cx,cy=c["pos"]; col=c["color"]; pulse=1+0.1*math.sin(sec*4+ci); r=int(30*pulse)
            draw.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(*col,20),outline=(*col,150),width=2)
            draw.text((cx,cy),c["var"],fill=(*col,255),font=fvar,anchor="mm")
            draw.line([(cx,cy),hub],fill=(*col,40),width=2)
            pt=(sec*0.8+ci*0.2)%1; ppx=int(lerp(cx,hub[0],pt)); ppy=int(lerp(cy,hub[1],pt))
            draw.ellipse([ppx-3,ppy-3,ppx+3,ppy+3],fill=(*col,220))
        hp=1+0.2*math.sin(sec*5); hr=int(50*hp)
        for gr in range(hr+30,hr,-1):
            ga=int(50*(1-(gr-hr)/30)); draw.ellipse([hub[0]-gr,hub[1]-gr,hub[0]+gr,hub[1]+gr],outline=(255,0,255,ga))
        draw.ellipse([hub[0]-hr,hub[1]-hr,hub[0]+hr,hub[1]+hr],fill=(255,0,255,30),outline=(255,0,255,200),width=3)
        draw.text((hub[0],hub[1]-8),"GNW",fill=(255,255,255,255),font=fm,anchor="mm")
        if rt>0.3:
            fa=int(255*ease(min(1,(rt-0.3)/0.5))); draw.text((W//2,460),"poly_c = T x w x topo / 2*sqrt(N)",fill=(255,215,0,fa),font=fform,anchor="mm")
        if rt>0.6:
            sa=int(200*ease(min(1,(rt-0.6)/0.3))); draw.text((W//2,520),"One formula. All circuits. Living proof.",fill=(136,136,136,sa),font=fs,anchor="mm")
    draw.text((W//2,H-25),"EVEZ-OS",fill=(51,51,51,255),font=fx,anchor="mm")
    rgb=Image.new('RGB',img.size,(10,10,15)); rgb.paste(img,mask=img.split()[3]); rgb.save(f"{FRAMES}/frame_{frame:05d}.png")
    if frame % (FPS*5) == 0: print(f"  Frame {frame}/{dur*FPS} ({sec:.0f}s)")

os.system(f"ffmpeg -y -framerate {FPS} -i {FRAMES}/frame_%05d.png -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p {OUT}/circuit_animated.mp4 2>/dev/null")
os.system(f"rm -rf {FRAMES}")
print("✅ circuit_animated.mp4")

# === RICH AUDIO ===
print("🔊 Generating rich audio...")
sr=44100

# Dark ambient (30s)
dur=30; n=int(sr*dur); data=[]
for i in range(n):
    t=i/sr
    v=0.15*math.sin(2*math.pi*55*t)+0.12*math.sin(2*math.pi*55.3*t)
    v+=0.08*math.sin(2*math.pi*110*t)+0.06*math.sin(2*math.pi*82.41*t)+0.04*math.sin(2*math.pi*82.6*t)
    v+=0.03*math.sin(2*math.pi*164.81*t)*(0.5+0.5*math.sin(2*math.pi*0.3*t))
    v*=(0.5+0.5*math.sin(2*math.pi*0.05*t))*min(1,t/2)*min(1,(dur-t)/3)*0.8
    data.append(int(max(-32767,min(32767,v*32767))))
with wave.open(f"{AUD}/dark_ambient.wav",'w') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(struct.pack(f'<{len(data)}h',*data))
print("  ✅ dark_ambient.wav")

# Consciousness pulse (12s)
dur=12; n=int(sr*dur); data=[]
for i in range(n):
    t=i/sr; v=0
    for beat in range(8):
        bt=t-beat*1.5
        if 0<=bt<0.3: v+=0.5*math.sin(2*math.pi*60*bt)*math.exp(-bt*15)+0.2*math.sin(2*math.pi*90*bt)*math.exp(-bt*20)+0.1*math.sin(2*math.pi*120*bt)*math.exp(-bt*25)
        bt2=t-(beat*1.5+0.4)
        if 0<=bt2<0.2: v+=0.3*math.sin(2*math.pi*70*bt2)*math.exp(-bt2*18)+0.1*math.sin(2*math.pi*105*bt2)*math.exp(-bt2*22)
    v+=0.05*math.sin(2*math.pi*40*t)
    data.append(int(max(-32767,min(32767,v*32767))))
with wave.open(f"{AUD}/consciousness_pulse.wav",'w') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(struct.pack(f'<{len(data)}h',*data))
print("  ✅ consciousness_pulse.wav")

# Quantum transition (5s)
dur=5; n=int(sr*dur); data=[]
for i in range(n):
    t=i/sr
    base_f=440*(1+2*t/dur)
    v=0.2*math.sin(2*math.pi*base_f*t)
    if int(t*20)%3==0: v=0.2*math.sin(2*math.pi*base_f*(1+0.5*math.sin(t*100))*t)
    v=round(v*8)/8
    v*=min(1,t/0.1)*min(1,(dur-t)/0.5)
    data.append(int(max(-32767,min(32767,v*32767))))
with wave.open(f"{AUD}/quantum_transition.wav",'w') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(struct.pack(f'<{len(data)}h',*data))
print("  ✅ quantum_transition.wav")

# Circuit build (10s)
dur=10; n=int(sr*dur); data=[]
freqs=[523.25,587.33,659.25,698.46,783.99]
for i in range(n):
    t=i/sr; v=0
    for ci,freq in enumerate(freqs):
        onset=ci*2.0
        if t>onset:
            lt=t-onset
            tone=0.12*math.sin(2*math.pi*freq*lt)+0.05*math.sin(2*math.pi*freq*2*lt)*math.exp(-lt)+0.03*math.sin(2*math.pi*freq*3*lt)*math.exp(-lt*2)
            v+=tone*min(1,lt/0.2)
    v+=0.03*math.sin(2*math.pi*55*t)
    v*=min(1,t/0.5)*min(1,(dur-t)/2)
    data.append(int(max(-32767,min(32767,v*32767))))
with wave.open(f"{AUD}/circuit_build.wav",'w') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(struct.pack(f'<{len(data)}h',*data))
print("  ✅ circuit_build.wav")

print("🎉 ALL DONE!")
