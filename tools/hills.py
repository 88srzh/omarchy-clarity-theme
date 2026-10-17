import math, zlib, struct, random, sys
W,H = int(sys.argv[1]), int(sys.argv[2]); out=sys.argv[3]
S=H/1080
def rgb(h): h=h.lstrip('#'); return [int(h[i:i+2],16) for i in (0,2,4)]
def mix(a,b,t): return [a[i]+(b[i]-a[i])*t for i in range(3)]
sky_top, sky_bot = rgb('#F3F0E9'), rgb('#ECE3D3')
sun_c=rgb('#E9C996'); sx,sy,sr=0.70*W,0.40*H,95*S
# layers far->near: (base y frac, [(amp px@1080, wavelength frac of W, phase)], top color, bottom color)
layers=[(0.58,[(70,0.55,0.3),(30,0.21,1.7),(12,0.09,0.4)],rgb('#D6DBD6'),rgb('#CDD3CF')),
        (0.66,[(60,0.47,2.1),(28,0.17,0.9),(10,0.07,2.6)],rgb('#AFC0BF'),rgb('#A3B5B5')),
        (0.75,[(55,0.61,4.0),(25,0.23,3.1),(9,0.08,1.2)],rgb('#7E9A9E'),rgb('#6F8D93')),
        (0.86,[(45,0.52,5.3),(22,0.19,0.2),(8,0.06,3.9)],rgb('#4B7079'),rgb('#3C6670'))]
heights=[]
for base,waves,_,_ in layers:
    heights.append([base*H+sum(a*S*math.sin(2*math.pi*x/(wl*W)+ph) for a,wl,ph in waves) for x in range(W)])
rnd=random.Random(2); raw=bytearray()
for y in range(H):
    t=y/(H-1); sky=mix(sky_top,sky_bot,t)
    row=bytearray(1+W*3); j=1
    dy2=(y-sy)**2
    for x in range(W):
        d=math.sqrt((x-sx)**2+dy2)
        p=sky
        glow=0.35*math.exp(-(d/(sr*3.2))**2)
        if glow>0.003: p=mix(p,sun_c,glow)
        a=min(1,max(0,sr-d+0.5))
        if a>0: p=mix(p,sun_c,a*0.85)
        for k,(base,_,ct,cb) in enumerate(layers):
            h=heights[k][x]
            cov=y-h+0.5
            if cov>0:
                lc=mix(ct,cb,min(1,(y-h)/(H*0.25)))
                p=mix(p,lc,min(1,cov))
        n=rnd.random()-0.5
        row[j]=int(min(255,max(0,p[0]+n+0.5))); row[j+1]=int(min(255,max(0,p[1]+n+0.5))); row[j+2]=int(min(255,max(0,p[2]+n+0.5)))
        j+=3
    raw+=row
def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d))
open(out,'wb').write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),6))+chunk(b'IEND',b''))
