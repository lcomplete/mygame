#!/usr/bin/env python3
"""Original, editable vector artwork + synthesized audio for 斩令.
All geometry, animation poses and waveforms are authored here. No stock art.
Run from any directory; deterministic output (seed 1709).
"""
from pathlib import Path
import math, random, wave, struct
ROOT = Path(__file__).resolve().parents[1] / 'game/assets'
rng = random.Random(1709)
def svg(path, w, h, body):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True)
    scale=4 if path.parts[0]=="characters" else 1
    p.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w*scale}" height="{h*scale}" viewBox="0 0 {w} {h}">{body}</svg>\n')
def rect(x,y,w,h,c,extra=''): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" {extra}/>'
def path(d,c,stroke='',sw=1): return f'<path d="{d}" fill="{c}"'+(f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else '')+'/>'
def line(x,y,a,b,c,sw=1): return f'<path d="M{x} {y}L{a} {b}" fill="none" stroke="{c}" stroke-width="{sw}"/>'
# Layered sky, deliberately lit behind the silhouettes.
svg(Path('environment/sky.svg'),1280,720,'''<defs><linearGradient id="s" x2="0" y2="1"><stop stop-color="#070e1a"/><stop offset=".48" stop-color="#173744"/><stop offset="1" stop-color="#234449"/></linearGradient><radialGradient id="m"><stop stop-color="#9bb7a0" stop-opacity=".19"/><stop offset="1" stop-color="#9bb7a0" stop-opacity="0"/></radialGradient></defs><rect width="1280" height="720" fill="url(#s)"/><ellipse cx="930" cy="220" rx="330" ry="250" fill="url(#m)"/>''')
# Mountain silhouette and faint cloud ribbons.
b=''
for n,c in [(0,'#17313d'),(1,'#1d3d48'),(2,'#23464e')]:
    pts=[(0,520+n*30)]
    for x in range(0,2660,100): pts.append((x, rng.randrange(190+n*70,410+n*60)))
    d='M'+' L'.join(f'{x} {y}' for x,y in pts)+' L2560 720 L0 720Z'
    b+=path(d,c)
for i in range(30):
    x=rng.randrange(2560); y=rng.randrange(160,520)
    b+=path(f'M{x} {y} q100 -20 250 0 q-100 8 -230 5Z','#7da3a0') .replace('fill="#7da3a0"','fill="#7da3a0" opacity=".045"')
svg(Path('environment/mountains.svg'),2560,720,b)
def building(x,base,w,h,c,detail=False):
    b=rect(x,base-h,w,h,c)
    tiers=max(1,int(h/85))
    for t in range(tiers):
        yy=base-h+t*78
        b+=path(f'M{x-24} {yy+10} Q{x-6} {yy+5} {x+9} {yy-10} L{x+w*.48} {yy-32} L{x+w-9} {yy-10} Q{x+w+6} {yy+5} {x+w+24} {yy+10} L{x+w+18} {yy+17} L{x-18} {yy+17}Z',c)
        b+=line(x-18,yy+15,x+w+18,yy+15,'#42616a' if detail else '#27434b',2)
        if detail:
            for j in range(0,int(w),12): b+=line(x+j,yy+3,x+j+3,yy+12,'#304b55',1)
        for j in range(3):
            if rng.random()<.55:
                xx=x+12+j*(w-20)/3
                b+=rect(xx,yy+32,8,15,'#aa7250' if detail else '#466062')
                b+=line(xx+4,yy+32,xx+4,yy+47,c,1)
    return b
b=''
for x in range(-40,2600,100): b+=building(x,680,rng.randrange(65,110),rng.randrange(120,300),'#102934')
svg(Path('environment/city_far.svg'),2560,720,b)
b=''
for x in range(-80,2600,195): b+=building(x,740,rng.randrange(110,190),rng.randrange(180,390),'#0b202a',True)
svg(Path('environment/city_near.svg'),2560,720,b)
# Distinct bell tower landmark, scenery only.
b=rect(166,180,108,390,'#101d29')
for y,w in [(125,120),(240,176),(365,220),(505,276)]:
    x=220-w/2
    b+=rect(x+18,y+20,w-36,105,'#142c36')
    b+=path(f'M{x-25} {y+27} Q{x+2} {y+18} {x+10} {y-1} L220 {y-43} L{x+w-10} {y-1} Q{x+w-2} {y+18} {x+w+25} {y+27} L{x+w+18} {y+36} L{x-18} {y+36}Z','#091923','#46616b',2)
    for xx in range(int(x+30),int(x+w-20),26): b+=rect(xx,y+48,9,39,'#af6a43')
b+=path('M218 25 L223 25 L222 75 L238 86 L204 86 L220 70Z','#9a7860')
svg(Path('environment/tower.svg'),440,640,b)
# Repeating roof / walkable platform face with tile rows and a vermilion trim.
b=rect(0,0,256,96,'#111d27')+rect(0,0,256,7,'#5e7a7e')+rect(0,7,256,3,'#203e49')+rect(0,30,256,4,'#4e3033')
for y in (11,20):
    for x in range(-12,270,24): b+=path(f'M{x} {y+7} Q{x+12} {y-7} {x+24} {y+7}', 'none','#304c56',2)
for x in range(12,256,42): b+=rect(x,39,8,55,'#1e333d')+rect(x+2,40,2,55,'#2a4148')
b+=rect(0,88,256,8,'#09141d')
svg(Path('environment/platform.svg'),256,96,b)
# Hanging lantern, banner, gnarled branches, floor props.
b=line(32,0,32,22,'#1a2731',3)+path('M20 22 L44 22 L52 34 L50 70 L42 80 L22 80 L14 70 L12 34Z','#9c403d','#d98d67',2)+rect(18,34,28,34,'#c06149')
for x in (20,28,36,44): b+=line(x,32,x,72,'#e19d70',1)
b+=line(14,36,50,36,'#edb986',2)+line(14,66,50,66,'#edb986',2)+rect(27,80,10,4,'#cf956a')+line(32,83,32,99,'#b65246',3)
svg(Path('environment/lantern.svg'),64,104,b)
svg(Path('environment/banner.svg'),96,220,line(48,0,48,20,'#283c43',2)+rect(17,19,62,151,'#762f37')+path('M17 169 L17 206 L48 190 L79 213 L79 169Z','#762f37')+rect(24,27,48,130,'none','stroke="#b87864" stroke-width="2"')+path('M35 48 L59 48 L59 55 L35 55Z M31 71 L65 71 L65 78 L51 78 L51 132 L42 132 L42 78 L31 78Z M34 95 L61 95 L61 102 L34 102Z','#d6ad86'))
svg(Path('environment/branches.svg'),540,340,path('M0 40 Q130 64 230 162 Q330 191 509 159 L531 164 Q387 202 249 182 Q287 249 390 302 L385 312 Q271 275 220 194 Q116 103 0 103Z','#071720')+path('M134 114 Q165 90 231 75 L270 34 L276 36 L241 84 L175 113 L220 162Z','#071720')+path('M304 179 L368 97 L416 72 L420 78 L380 105 L329 183Z','#071720'))
svg(Path('environment/crate.svg'),64,64,rect(2,2,60,60,'#3c3432','stroke="#776052" stroke-width="3"')+path('M6 6 L58 58 M6 58 L58 6','none','#6e5147',5)+rect(5,5,54,54,'none','stroke="#9e7960" stroke-width="2"'))
# Hand-posed articulated characters. Feet anchor at (64,112).
def character(kind,pose,frame):
    boss=kind=='magistrate'; archer=kind=='archer'; hero=kind=='ninja'; old=kind=='scribe'
    cloth='#123540' if hero else '#5d303d' if boss else '#394956' if archer else '#30343f'
    light='#386774' if hero else '#bd7164' if boss else '#8c8d8c'
    bob=math.sin(frame*math.pi/3)*2 if pose=='run' else math.sin(frame*math.pi)*1
    lean=9 if pose=='run' else 15 if pose=='dash' else 0
    step=math.sin(frame*math.pi/3)*15 if pose=='run' else 7
    if pose=='jump': step=19
    if pose=='dash': step=23
    cx=62+lean; y=54+bob
    body=''
    # Scarf has its own successive poses.
    if hero:
        tail=math.sin(frame*1.7)*7
        body+=path(f'M{cx-4} {y-4} Q31 {y+4} 10 {y-5+tail} L0 {y+2+tail} Q33 {y+20} {cx+3} {y+5}Z','#b8494d')
        body+=path(f'M{cx-8} {y+1} Q33 {y+17} 18 {y+28+tail} L4 {y+29+tail} Q28 {y+3} {cx-2} {y-3}Z','#752e3a')
    # Back leg, sheath, skirt.
    body+=path(f'M59 78 L{54-step} 96 L{48-step} 111 L{35-step} 112 L{42-step} 103 L{45-step} 83Z','#101e2b')
    body+=path(f'M{52-step} 99 L{46-step} 110 L{36-step} 110','none','#708b8c',3)
    if not old: body+=path('M45 74 L18 108 L22 112 L51 77Z','#14151e','#798581',1)
    body+=path(f'M{cx-12} {y} L{cx+11} {y} L74 79 L82 92 L54 87 L43 91 L48 72Z',cloth,'#0b1720',2)
    body+=path(f'M{cx-9} {y+2} L{cx+3} {y+13} L53 78 L46 77Z',light)
    body+=path(f'M63 81 L{66+step*.5} 98 L{65+step} 110 L{79+step} 110 L{76+step} 115 L{57+step} 115 L{53+step*.5} 95 L51 81Z',cloth,'#0c1922',2)
    body+=line(61+step*.6,102,69+step*.8,106,'#86a09b',3)
    body+=path('M47 76 L71 75 L75 82 L46 84Z','#8d4544' if hero else '#b1976b')
    body+=rect(58,77,7,6,'#e1b78b')
    # Head, hood and readable eye glint.
    body+=path(f'M{cx-10} {y-23} Q{cx+5} {y-31} {cx+15} {y-16} L{cx+13} {y-5} L{cx+2} {y+2} L{cx-12} {y-7}Z','#101e2c','#496874',1)
    body+=path(f'M{cx+1} {y-18} L{cx+16} {y-16} L{cx+13} {y-8} L{cx} {y-8}Z','#d4ba9b')
    body+=line(cx+8,y-14,cx+15,y-14,'#e9fcdf',2)
    body+=path(f'M{cx-1} {y-8} L{cx+13} {y-7} L{cx+6} {y+1} L{cx-4} {y-1}Z','#14313e' if hero else '#78373d')
    if boss:
        body+=path(f'M{cx-13} {y-21} L{cx-21} {y-35} L{cx-5} {y-29} L{cx} {y-41} L{cx+6} {y-29} L{cx+22} {y-35} L{cx+15} {y-19}Z','#bb9771','#e4c599',1)
        body+=path('M44 58 L30 56 L35 73 L49 76 M73 57 L88 57 L89 69 L73 75','#af6658','#e7b489',1)
        body+=path('M48 83 L36 111 L55 105 L65 119 L81 113 L76 82Z','#622f40','#a45257',1)
    if old:
        body+=path(f'M{cx+4} {y-5} L{cx+16} {y-5} L{cx+7} {y+25} L{cx+2} {y+8}Z','#ced0b8')
    # Arm and sword poses.
    if pose=='attack':
        arm_y=61+(frame-1)*7
        body+=path(f'M{cx+7} {y+5} L84 {arm_y} L96 {arm_y-7}','none',light,8)
        body+=path(f'M91 {arm_y-9} L124 {arm_y-24} L123 {arm_y-19} L94 {arm_y-5}Z','#edfff1')
        body+=line(90,arm_y-14,96,arm_y,'#e2a378',3)
    elif pose=='dash':
        body+=path(f'M{cx+7} {y+5} L90 66 L105 62','none',light,7)
        body+=path('M99 58 L128 49 L128 53 L101 62Z','#e4f5e6')
    else:
        body+=path(f'M{cx+8} {y+6} L{cx+16} 73 L{cx+22} 79','none',light,7)
        if not old:
            body+=path(f'M{cx+20} 75 L116 40 L118 37 L116 46 L{cx+24} 79Z','#d0e8df')
            body+=line(cx+16,74,cx+26,82,'#d9ad7b',3)
    if archer:
        body+=path('M99 39 Q127 72 101 107','none','#bca17b',3)+line(99,39,101,107,'#d7c4a0',1)
    return body
for kind in ['ninja','soldier','archer','magistrate','scribe']:
    for pose,count in [('idle',2),('run',6),('jump',1),('attack',3),('dash',1)]:
        for f in range(count): svg(Path(f'characters/{kind}_{pose}_{f}.svg'),128,128,character(kind,pose,f))
# Sword arcs and detached ink slash.
for f in range(3):
    svg(Path(f'effects/slash_{f}.svg'),240,170,path(f'M8 144 Q{160-f*18} {-72+f*25} 228 {76+f*17} Q140 8 8 144Z','#d2fff2')+path('M19 135 Q138 -3 209 55 Q126 11 19 135Z','#5bcec3'))
svg(Path('effects/spark.svg'),64,64,path('M32 0 L37 25 L64 32 L37 37 L32 64 L26 38 L0 32 L25 27Z','#fff3c3'))
svg(Path('ui/icon.svg'),128,128,rect(0,0,128,128,'#101f2b','rx="24"')+rect(24,20,80,88,'none','stroke="#c15d57" stroke-width="4"')+path('M37 39 L91 39 L91 46 L67 46 L67 90 L57 90 L57 46 L37 46Z M34 62 L94 62 L94 70 L34 70Z','#dca18a')+path('M16 105 L114 17 L107 35 L20 113Z','#e1f3df'))
# Generated ambient soundtrack: sparse minor-pentatonic plucks, bowed drone, soft pulse.
RATE=22050
def save_audio(name,samples,loop=False):
    p=ROOT/'audio'/f'{name}.wav'
    with wave.open(str(p),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
        w.writeframes(b''.join(struct.pack('<h',int(max(-1,min(1,s)) * 32760)) for s in samples))
def hz(midi): return 440*2**((midi-69)/12)
length=16
notes=[50,57,60,62,65,62,60,57,48,55,58,60,63,60,58,55]
a=[]
for i in range(length*RATE):
    t=i/RATE; beat=int(t); phase=t-beat; f=hz(notes[beat])
    pluck=(math.sin(2*math.pi*f*phase)+.3*math.sin(4*math.pi*f*phase)) * math.exp(-phase*5)*.10
    drone=(math.sin(2*math.pi*73.416*t)+.35*math.sin(2*math.pi*110*t))*.042
    pulse=math.sin(2*math.pi*(52+25*math.exp(-phase*14))*phase)*math.exp(-phase*12)*.065 if beat%2==0 else 0
    fade=min(1,t/.2,(length-t)/.5)
    a.append((pluck+drone+pulse)*fade)
save_audio('rain_city',a)
for name,duration in [('slash',.2),('hit',.19),('dash',.28),('jump',.15),('death',.7),('glyph',.55),('bell',2.3),('victory',3.6)]:
    a=[]
    for i in range(int(duration*RATE)):
        t=i/RATE; p=t/duration; noise=rng.uniform(-1,1)
        if name=='slash': s=(noise*.6+math.sin(2*math.pi*(1400-900*p)*t)*.1)*math.sin(math.pi*p)**2*(1-p)
        elif name=='hit': s=(noise*.28+math.sin(2*math.pi*(180-100*p)*t)*.6)*math.exp(-p*8)
        elif name=='dash': s=noise*.22*math.sin(math.pi*p)**2
        elif name=='jump': s=math.sin(2*math.pi*(280+400*p)*t)*.12*(1-p)
        elif name=='death': s=(math.sin(2*math.pi*(160-100*p)*t)*.32+noise*.08)*(1-p)
        elif name=='bell': s=sum(math.sin(2*math.pi*f*t)*v for f,v in [(220,.22),(554,.1),(932,.045)])*math.exp(-p*5)
        elif name=='glyph': s=(math.sin(2*math.pi*146.83*t)*.19+math.sin(2*math.pi*155*t)*.16)*math.sin(math.pi*p)
        else: s=sum(math.sin(2*math.pi*hz(n)*t)*.07 for n in [50,57,62,65,69])*math.sin(math.pi*p)*math.exp(-p*2)
        a.append(s)
    save_audio(name,a)
print('Created',len(list(ROOT.rglob('*.svg'))),'original SVG assets and',len(list(ROOT.rglob('*.wav'))),'synthesized WAV assets.')
