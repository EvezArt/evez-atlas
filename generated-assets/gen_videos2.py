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

# === CONSCIOUSNESS ENGINE ANIMATED ===
print("🎬 consciousness_animated.mp4...")
os.makedirs(FRAMES, exist_ok=True)
dur = 32
fb=font(44,True); fp=font(48,True); fm=font(22); fs=font(16); fx=font(12)
phases = [
    ("SENSE",(0,255,255),"Observe 11 services, knowledge graph, external signals"),
    ("DESIRE",(255,0,255),"Convert NEEDS to Goals: expand_knowledge (0.85), verify_claims (0.72)"),
    ("THINK",(138,43,226),"Inner monologue: 12 auditable thought chains. Novel reasoning."),
    ("PLAN",(255,215,0),"Create action sequences. Resource constraints + desire mapping."),
    ("ACT",(255,100,0),"Execute with safety checks. Risk gates + rollback mechanisms."),
    ("LEARN",(0,255,128),"Update beliefs. Evidence tracking. 3 beliefs monitored."),
    ("MODIFY",(255,0,255),"Falsifiable self-improvement. Changes tested before adoption."),
    ("REFLECT",(0,255,255),"Review cycle. Self-audit. Append-only spine record written."),
]

for frame in range(dur * FPS):
    sec = frame / FPS
    img = Image.new('RGBA', (W, H), (10, 10, 15, 255))
    draw = ImageDraw.Draw(img)
    # Background wave
    for x in range(0, W, 3):
        y = int(H//2 + math.sin(x*0.01+sec*2)*30 + math.sin(x*0.03+sec*3)*15)
        a = int(15+10*math.sin(sec+x*0.01))
        draw.ellipse([x-1,y-1,x+1,y+1], fill=(0,255,255,a))
    # Scan lines
    for y in range(0, H, 4):
        draw.line([(0,y),(W,y)], fill=(0,255,255,3))

    if sec < 4:
        a = int(255*ease(min(1,sec/2)))
        draw.text((W//2,H//2-40),"CONSCIOUSNESS ENGINE",fill=(255,0,255,a),font=fb,anchor="mm")
        draw.text((W//2,H//2+20),"8-Phase Mechanistic Dissection",fill=(136,136,136,a),font=fm,anchor="mm")
        pulse = int(80+40*math.sin(sec*4))
        draw.ellipse([W//2-60,100,W//2+60,220],outline=(255,0,255,pulse),width=1)
    else:
        phase_sec = sec - 4
        phase_idx = min(7, int(phase_sec / 3.5))
        phase_t = (phase_sec - phase_idx * 3.5) / 3.5
        name, color, desc = phases[phase_idx]
        # Cycle ring
        cx, cy = W//2, 350; ring_r = 200
        for i, (pname, pcol, _) in enumerate(phases):
            angle = -math.pi/2 + (2*math.pi*i/8)
            px = int(cx+ring_r*math.cos(angle)); py = int(cy+ring_r*math.sin(angle))
            is_current = (i == phase_idx)
            node_r = 35 if is_current else 20; node_a = 255 if is_current else 60
            if is_current:
                for gr in range(node_r+25,node_r,-1):
                    ga=int(50*(1-(gr-node_r)/25)); draw.ellipse([px-gr,py-gr,px+gr,py+gr],outline=(*pcol,ga))
                pulse=1+0.15*math.sin(sec*6); node_r=int(node_r*pulse)
            draw.ellipse([px-node_r,py-node_r,px+node_r,py+node_r],fill=(*pcol,node_a//4 if not is_current else node_a//2),outline=(*pcol,node_a),width=2 if not is_current else 3)
            draw.text((px,py),pname[:1],fill=(*pcol,node_a),font=fs,anchor="mm")
            lx=int(cx+(ring_r+50)*math.cos(angle)); ly=int(cy+(ring_r+50)*math.sin(angle))
            draw.text((lx,ly),pname,fill=(*pcol,node_a),font=fx,anchor="mm")
            # Connection arcs between adjacent nodes
            if i < 7:
                a2 = -math.pi/2+(2*math.pi*(i+1)/8)
                px2=int(cx+ring_r*math.cos(a2)); py2=int(cy+ring_r*math.sin(a2))
                arc_a = node_a//2 if (i==phase_idx or i==phase_idx-1) else 20
                draw.line([(px,py),(px2,py2)],fill=(*pcol,arc_a),width=1)
        # Active phase highlight
        reveal_a = int(255*ease(min(1,phase_t*3)))
        draw.text((W//2,50),name,fill=(*color,reveal_a),font=fp,anchor="mt")
        draw.text((W//2,110),f"Phase {phase_idx+1}/8",fill=(136,136,136,reveal_a),font=fm,anchor="mt")
        # Typing description
        if phase_t > 0.2:
            desc_t = ease(min(1,(phase_t-0.2)/0.6))
            visible = desc[:int(len(desc)*desc_t)]
            max_c = 60; lines = [visible[i:i+max_c] for i in range(0,len(visible),max_c)]
            for li,line in enumerate(lines):
                draw.text((W//2,160+li*24),line,fill=(200,200,200,reveal_a),font=fm,anchor="mt")
        # Progress bar
        if phase_t > 0.5:
            bar_w = int(300*ease(min(1,(phase_t-0.5)/0.5)))
            draw.rectangle([W//2-150,H-80,W//2+150,H-70],fill=(50,50,50,255))
            draw.rectangle([W//2-150,H-80,W//2-150+bar_w,H-70],fill=(*color,200))
    draw.text((W//2,H-20),"EVEZ-OS Consciousness Engine",fill=(51,51,51,255),font=fx,anchor="mm")
    rgb=Image.new('RGB',img.size,(10,10,15)); rgb.paste(img,mask=img.split()[3]); rgb.save(f"{FRAMES}/frame_{frame:05d}.png")
    if frame%(FPS*5)==0: print(f"  Frame {frame}/{dur*FPS} ({sec:.0f}s)")

os.system(f"ffmpeg -y -framerate {FPS} -i {FRAMES}/frame_%05d.png -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p {OUT}/consciousness_animated.mp4 2>/dev/null")
os.system(f"rm -rf {FRAMES}")
print("✅ consciousness_animated.mp4")

# === POLY_C FORMULA ANIMATED ===
print("🎬 polyc_animated.mp4...")
os.makedirs(FRAMES, exist_ok=True)
dur = 22
fh=font(64,True); fb=font(44,True); fm=font(26); fs=font(18); fv=font(80,True)
variables = [
    {"sym":"T","name":"TEMPORAL DECAY","color":(0,255,255),"range":"0.3-2.5",
     "mechanism":["signal(t) = S0 x e^(-lambda*t)","Recent obs weighted higher than stale","Measured from circuit scan intervals"]},
    {"sym":"w","name":"WEIGHTED SIGNAL","color":(138,43,226),"range":"0-1",
     "mechanism":["Anomaly = high w | Noise = low w","Spectral decomposition determines weight","Not all observations carry equal info"]},
    {"sym":"topo","name":"TOPOLOGY","color":(255,215,0),"range":"0-inf",
     "mechanism":["Betti numbers: b0 b1 b2","16 nodes, 145 edges = [1,3,0]","More loops = richer causal structure"]},
    {"sym":"sqrt(N)","name":"EVIDENCE","color":(255,0,255),"range":"1-10+",
     "mechanism":["Prevents overconfidence from volume","sqrt(N) grows slower than N","Quality > Quantity. Structure > Volume."]},
]

for frame in range(dur * FPS):
    sec = frame / FPS
    img = Image.new('RGBA', (W, H), (10, 10, 15, 255))
    draw = ImageDraw.Draw(img)
    # Matrix rain
    for i in range(20):
        x=(i*67)%W; y=(i*89+int(sec*40))%(H+200)-100
        for j,ch in enumerate("TwvNtopo01011"):
            ca=int(20+10*math.sin(sec+i+j)); draw.text((x,y+j*14),ch,fill=(0,255,255,ca),font=fs)

    if sec < 5:
        a=int(255*ease(min(1,sec/2)))
        draw.text((W//2,150),"poly_c",fill=(255,0,255,a),font=fh,anchor="mm")
        draw.text((W//2,250),"= T x w x topo / 2*sqrt(N)",fill=(255,215,0,a),font=fb,anchor="mm")
        draw.text((W//2,340),"The convergence metric that unifies everything",fill=(136,136,136,a),font=fm,anchor="mm")
        draw.line([(200,400),(W-200,400)],fill=(255,215,0,int(100*ease(min(1,(sec-2)/2)))),width=1)
    elif sec < 20:
        var_sec=sec-5; var_idx=min(3,int(var_sec/3.75)); var_t=(var_sec-var_idx*3.75)/3.75
        v=variables[var_idx]; col=v["color"]
        sym_a=int(255*ease(min(1,var_t*4)))
        sym_x=int(lerp(W+100,200,ease(min(1,var_t*2))))
        draw.text((sym_x,120),v["sym"],fill=(*col,sym_a),font=fv,anchor="mm")
        if var_t>0.15:
            na=int(255*ease(min(1,(var_t-0.15)/0.3)))
            nx=int(lerp(W+100,400,ease(min(1,(var_t-0.15)/0.5))))
            draw.text((nx,100),v["name"],fill=(*col,na),font=fb,anchor="lm")
            draw.text((400,150),f"Range: {v['range']}",fill=(*col,int(200*na/255)),font=fm,anchor="lm")
        if var_t>0.35:
            for li,line in enumerate(v["mechanism"]):
                lt=ease(min(1,(var_t-0.35-li*0.1)/0.3))
                if lt>0:
                    vis=int(len(line)*lt); la=int(200*lt)
                    draw.text((120,240+li*35),line[:vis],fill=(180,180,180,la),font=fm)
        # Value bar
        if var_t>0.5:
            bar_t=ease(min(1,(var_t-0.5)/0.3)); bar_w=int(400*bar_t)
            draw.rectangle([120,420,520,435],fill=(40,40,40,255))
            draw.rectangle([120,420,120+bar_w,435],fill=(*col,180))
            draw.text((530,427),f"{bar_t*0.75:.2f}",fill=(*col,200),font=fs,anchor="lm")
        # Other vars grayed
        for oi,ov in enumerate(variables):
            if oi!=var_idx:
                draw.text((950,80+oi*50),ov["sym"],fill=(*ov["color"],40),font=fm)
                draw.text((1000,80+oi*50),ov["name"][:12],fill=(*ov["color"],25),font=fx)
    else:
        conv_t=ease(min(1,(sec-20)/2))
        for i,v in enumerate(variables):
            col=v["color"]; angle=-math.pi/2+(2*math.pi*i/4)
            dist=150*(1-conv_t)
            px=int(W//2+dist*math.cos(angle)); py=int(300+dist*math.sin(angle))
            a=int(255*(0.3+0.7*conv_t))
            draw.text((px,py),v["sym"],fill=(*col,a),font=fb,anchor="mm")
        fa=int(255*ease(min(1,(conv_t-0.3)/0.5)))
        if fa>0:
            draw.text((W//2,450),"poly_c = T x w x topo / 2*sqrt(N)",fill=(255,215,0,fa),font=fb,anchor="mm")
            draw.text((W//2,520),"Previously a slogan. Now: implemented, scoring, alive.",fill=(136,136,136,fa),font=fm,anchor="mm")
    draw.text((W//2,H-20),"EVEZ-OS",fill=(40,40,40,255),font=fx,anchor="mm")
    rgb=Image.new('RGB',img.size,(10,10,15)); rgb.paste(img,mask=img.split()[3]); rgb.save(f"{FRAMES}/frame_{frame:05d}.png")
    if frame%(FPS*5)==0: print(f"  Frame {frame}/{dur*FPS} ({sec:.0f}s)")

os.system(f"ffmpeg -y -framerate {FPS} -i {FRAMES}/frame_%05d.png -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p {OUT}/polyc_animated.mp4 2>/dev/null")
os.system(f"rm -rf {FRAMES}")
print("✅ polyc_animated.mp4")

print("🎉 ALL ANIMATED VIDEOS DONE!")
