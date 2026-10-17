import sys
# usage: python3 tools/brand.py <unused> backgrounds/2-hills.png out.png  (needs Pillow and the Lato font)
sys.path.insert(0, sys.argv[1])
from PIL import Image, ImageDraw, ImageFont, ImageFilter
base = Image.open(sys.argv[2]).convert('RGB'); out = sys.argv[3]
W, H = base.size; S = H/2160
F = '/usr/share/fonts/truetype/lato/'
word = ImageFont.truetype(F+'Lato-Bold.ttf', int(300*S))
sub = ImageFont.truetype(F+'Lato-Medium.ttf', int(64*S))
txt = Image.new('RGBA', base.size, (0,0,0,0)); d = ImageDraw.Draw(txt)
x, y = int(0.10*W), int(0.20*H)
d.text((x, y), 'omarchy', font=word, fill=(0x1C,0x1B,0x19,255))
bb = d.textbbox((x, y), 'omarchy', font=word)
# spaced subtitle
label = 'C L A R I T Y'
d.text((bb[0]+int(8*S), bb[3]+int(60*S)), label, font=sub, fill=(0x1A,0x5A,0x70,255))
# accent bar between
d.rounded_rectangle((bb[0]+int(8*S), bb[3]+int(30*S), bb[0]+int(150*S), bb[3]+int(40*S)), radius=int(5*S), fill=(0x1A,0x5A,0x70,255))
# very soft shadow for lift
sh = txt.split()[3].filter(ImageFilter.GaussianBlur(18*S)).point(lambda a: int(a*0.10))
shadow = Image.new('RGBA', base.size, (0x5C,0x58,0x4F,0)); shadow.putalpha(sh)
img = Image.alpha_composite(base.convert('RGBA'), shadow)
img = Image.alpha_composite(img, txt).convert('RGB')
img.save(out, optimize=True)
img.resize((1280, int(1280*H/W)), Image.LANCZOS).save(out.replace('.png','-preview.png'))
