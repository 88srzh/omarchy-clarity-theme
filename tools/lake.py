import math, zlib, struct, random, sys
W,H=int(sys.argv[1]),int(sys.argv[2]); out=sys.argv[3]; S=H/1080
def rgb(h): h=h.lstrip('#'); return [int(h[i:i+2],16) for i in (0,2,4)]
def mix(a,b,t): return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t]
R=random.Random(7)
HZ=int(0.78*H)  # lake horizon
sky_top,sky_mid,sky_hz=rgb('#E9EDEA'),rgb('#F3EEE4'),rgb('#F2DDBB')
sun_c=rgb('#EDC688'); sx,sy,sr=0.63*W,0.47*H,70*S
cloud_c=rgb('#FBF8F2')
clouds=[(0.20*W,0.20*H,330*S,16*S,0.55),(0.45*W,0.13*H,420*S,12*S,0.45),(0.82*W,0.27*H,300*S,14*S,0.5),(0.70*W,0.36*H,260*S,8*S,0.35),(0.10*W,0.33*H,240*S,9*S,0.35)]
def peaks(base,amps):
    return [base*H-sum(a*S*(1-abs(math.sin(math.pi*x/(wl*W)+ph)))**1.6 for a,wl,ph in amps)
            -sum(a*S*0.25*math.sin(2*math.pi*x/(wl*W*0.37)+ph*3) for a,wl,ph in amps) for x in range(W)]
far=peaks(0.70,[(260,0.42,0.5),(120,0.19,1.3),(40,0.07,2.2)])
mid=peaks(0.74,[(170,0.33,2.4),(80,0.13,0.4),(25,0.05,1.1)])
far_c,mid_c=rgb('#D2D9D6'),rgb('#AABDBD')
# forest ridge: rolling base + pine trees
fb=[0.765*H-S*(28*math.sin(2*math.pi*x/(0.5*W)+1.0)+12*math.sin(2*math.pi*x/(0.13*W)+2.0)) for x in range(W)]
forest=fb[:]
tx=0
while tx<W:
    th=(35+R.random()*65)*S*(1.3 if R.random()<0.15 else 1); tw=th*(0.38+R.random()*0.1)
    c=int(tx); g=fb[min(W-1,c)]
    for x in range(max(0,int(tx-tw/2)),min(W,int(tx+tw/2)+1)):
        d=abs(x-tx)/(tw/2)
        if d<1:
            # slightly layered pine profile
            top=g-th*(1-d)+ (th*0.06)*(math.sin(d*math.pi*4)**2)*(1-d)
            if top<forest[x]: forest[x]=top
    tx+=tw*(0.35+R.random()*0.6)
for_t,for_b=rgb('#5F8189'),rgb('#456A73')
img=[None]*H
for y in range(HZ):
    t=y/HZ
    sky=mix(sky_top,sky_mid,t/0.5) if t<0.5 else mix(sky_mid,sky_hz,(t-0.5)/0.5)
    row=[None]*W; dy2=(y-sy)**2
    for x in range(W):
        p=sky; d=math.sqrt((x-sx)**2+dy2)
        g=0.45*math.exp(-(d/(sr*4))**2)
        if g>0.003: p=mix(p,sun_c,g)
        a=sr-d+0.5
        if a>0: p=mix(p,sun_c,min(1,a)*0.9)
        for cx,cy,cw,ch,s in clouds:
            v=s*math.exp(-((x-cx)/cw)**2-((y-cy)/ch)**2)
            if v>0.003: p=mix(p,cloud_c,v)
        for hh,lc in ((far,far_c),(mid,mid_c)):
            cov=y-hh[x]+0.5
            if cov>0:
                # haze: lighter toward the bottom of each range
                lc2=mix(lc,sky_hz,0.30*min(1,max(0,(y-0.40*H)/(0.38*H))))
                p=mix(p,lc2,min(1,cov))
        cov=y-forest[x]+0.5
        if cov>0: p=mix(p,mix(for_t,for_b,min(1,(y-forest[x])/(H*0.08))),min(1,cov))
        row[x]=p
    img[y]=row
# birds
for bx,by,bs in [(0.50,0.30,1.0),(0.535,0.27,0.8),(0.56,0.315,0.7),(0.47,0.255,0.6),(0.585,0.285,0.55)]:
    cx,cy,sz=bx*W,by*H,22*S*bs; th=1.6*S*bs+0.6; bc=rgb('#4B6670')
    for y in range(int(cy-sz),int(cy+sz)):
        for x in range(int(cx-sz*1.1),int(cx+sz*1.1)):
            u=(x-cx)/sz; 
            wy=cy-sz*0.35*(1-abs(u))**0.6*(1 if abs(u)<1 else 0)+sz*0.25*abs(u)  # wing curve
            if abs(u)<=1:
                d=abs(y-wy)
                a=max(0,min(1,th-d))
                if a>0: img[y][x]=mix(img[y][x],bc,a)
water_c,water_d=rgb('#9DB4B7'),rgb('#5E8088')
for y in range(HZ,H):
    t=(y-HZ)/(H-HZ); row=[None]*W
    for x in range(W):
        ry=2*HZ-y-1
        off=int(3*S*math.sin(y*0.9/S+x*0.002)*(0.3+t))
        xs=min(W-1,max(0,x+off))
        p=mix(img[max(0,ry)][xs],water_c,0.35+0.25*t)
        p=mix(p,water_d,0.35*t)
        # sun glitter column
        gx=abs(x-sx)/(sr*(1.2+3*t))
        if gx<1 and (math.sin(y*1.7/S+math.sin(x*0.05/S)*2)>0.6):
            p=mix(p,rgb('#F6E2BC'),0.55*(1-gx)*(1-0.6*t))
        # faint horizontal ripple lines
        if math.sin(y*0.23/S+4*math.sin(x*0.0011/S+y*0.01))>0.992 and math.sin(x*0.004/S+y*0.3)>0: p=mix(p,rgb('#E9EEEC'),0.22)
        row[x]=p
    img[y]=row
# shoreline highlight
for x in range(W):
    for k in range(int(2*S)+1):
        img[HZ+k][x]=mix(img[HZ+k][x],rgb('#EDE8DC'),0.45)
raw=bytearray()
for y in range(H):
    raw.append(0)
    for p in img[y]:
        n=R.random()-0.5
        raw.extend((int(min(255,max(0,p[0]+n+.5))),int(min(255,max(0,p[1]+n+.5))),int(min(255,max(0,p[2]+n+.5)))))
def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d))
open(out,'wb').write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),6))+chunk(b'IEND',b''))
