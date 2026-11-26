"""为示例商品生成本地扁平风格插图（仅用于演示数据）"""
import os
import json
from PIL import Image, ImageDraw, ImageFont

SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
W, H = 640, 480

FONTS = [
    r'C:\Windows\Fonts\msyhbd.ttc',
    r'C:\Windows\Fonts\msyh.ttc',
]


def font(size):
    for path in FONTS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(c1, c2):
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    a, b = hex2rgb(c1), hex2rgb(c2)
    for y in range(H):
        t = y / H
        color = tuple(int(p + (q - p) * t) for p, q in zip(a, b))
        d.line([(0, y), (W, y)], fill=color)
    return img


def soft_shadow_circle(d, cx, cy, r, fill=(255, 255, 255), alpha_img=None):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


# ---------- 各商品绘图 ----------
def draw_tablet(d):
    d.rounded_rectangle([210, 120, 430, 360], radius=22, fill='#3b3f4a')
    d.rounded_rectangle([228, 138, 412, 342], radius=8, fill='#7dd3fc')
    d.ellipse([310, 345, 330, 353], fill='#64748b')
    d.rounded_rectangle([248, 160, 392, 240], radius=6, fill='#e0f2fe')
    d.rounded_rectangle([248, 256, 392, 272], radius=4, fill='#ffffff')
    d.rounded_rectangle([248, 282, 360, 298], radius=4, fill='#ffffff')


def draw_books(d):
    colors = ['#f87171', '#fbbf24', '#34d399', '#60a5fa']
    x0, y0 = 200, 300
    for i, c in enumerate(colors):
        y = y0 - i * 42
        d.rounded_rectangle([x0 + i * 6, y - 38, x0 + 250 - i * 4, y], radius=6, fill=c)
        d.rectangle([x0 + i * 6 + 18, y - 38, x0 + i * 6 + 26, y], fill='#ffffff55')
    d.polygon([(430, 120), (470, 190), (390, 190)], fill='#fbbf24')


def draw_lamp(d):
    d.arc([230, 90, 420, 280], start=180, end=300, width=18, fill='#475569')
    d.line([400, 185, 400, 330], width=16, fill='#475569')
    d.rounded_rectangle([300, 330, 480, 352], radius=10, fill='#475569')
    d.ellipse([340, 150, 420, 230], fill='#fde68a')
    d.ellipse([360, 170, 400, 210], fill='#fef9c3')


def draw_pingpong(d):
    d.ellipse([210, 110, 400, 300], fill='#ef4444')
    d.ellipse([235, 135, 375, 275], fill='#f87171')
    d.rounded_rectangle([292, 290, 318, 400], radius=10, fill='#d97706')
    d.ellipse([420, 150, 475, 205], fill='#ffffff', outline='#e2e8f0', width=3)
    d.ellipse([440, 260, 485, 305], fill='#ffffff', outline='#e2e8f0', width=3)


def draw_mouse(d):
    d.rounded_rectangle([250, 120, 390, 360], radius=70, fill='#1e293b')
    d.rounded_rectangle([255, 125, 385, 240], radius=60, fill='#334155')
    d.line([320, 130, 320, 235], width=6, fill='#0f172a')
    d.ellipse([295, 150, 345, 175], fill='#22d3ee')
    d.ellipse([285, 190, 355, 215], fill='#a78bfa')
    d.line([270, 360, 270, 420], width=8, fill='#334155')


def draw_jacket(d):
    d.polygon([(250, 150), (320, 130), (390, 150), (420, 220), (390, 250), (390, 380),
               (250, 380), (250, 250), (220, 220)], fill='#1e40af')
    d.polygon([(320, 130), (320, 380)], width=6, fill='#1e3a8a')
    d.line([285, 140, 285, 375], width=5, fill='#1e3a8a')
    d.line([355, 140, 355, 375], width=5, fill='#1e3a8a')
    d.ellipse([300, 110, 340, 150], fill='#fcd34d')


def draw_bike(d):
    d.ellipse([160, 250, 320, 410], outline='#334155', width=14)
    d.ellipse([360, 250, 520, 410], outline='#334155', width=14)
    d.line([240, 330, 330, 220], width=12, fill='#12b76a')
    d.line([330, 220, 440, 330], width=12, fill='#12b76a')
    d.line([440, 330, 240, 330], width=12, fill='#12b76a')
    d.line([330, 220, 320, 180], width=12, fill='#12b76a')
    d.line([290, 180, 350, 180], width=12, fill='#334155')
    d.line([240, 330, 200, 300], width=10, fill='#334155')


def draw_papers(d):
    for i in range(4):
        off = i * 12
        d.rounded_rectangle([240 - off, 140 + off, 460 - off, 360 + off], radius=6,
                            fill='#ffffff', outline='#cbd5e1', width=2)
    for y in range(180, 340, 28):
        d.line([270, y, 430, y], width=6, fill='#e2e8f0')
    d.rounded_rectangle([420, 90, 445, 220], radius=6, fill='#f59e0b')
    d.polygon([(420, 220), (445, 220), (432, 250)], fill='#fbbf24')


DRAWERS = {
    'product1': ('iPad 9代 64G', draw_tablet, ('#e0f2fe', '#bae6fd')),
    'product2': ('高等数学教材', draw_books, ('#fef3c7', '#fde68a')),
    'product3': ('LED 护眼台灯', draw_lamp, ('#ede9fe', '#ddd6fe')),
    'product4': ('红双喜乒乓拍', draw_pingpong, ('#fee2e2', '#fecaca')),
    'product5': ('罗技G102鼠标', draw_mouse, ('#e2e8f0', '#cbd5e1')),
    'product6': ('冬季羽绒服', draw_jacket, ('#dbeafe', '#bfdbfe')),
    'product7': ('捷安特自行车', draw_bike, ('#dcfce7', '#bbf7d0')),
    'product8': ('四级真题试卷', draw_papers, ('#f1f5f9', '#e2e8f0')),
}

result = {}
for name, (label, drawer, (c1, c2)) in DRAWERS.items():
    img = gradient(c1, c2)
    d = ImageDraw.Draw(img)
    # 白色圆形底板
    d.ellipse([140, 60, 520, 440], fill='#ffffff')
    drawer(d)
    # 底部标签
    f = font(30)
    bbox = d.textbbox((0, 0), label, font=f)
    tw = bbox[2] - bbox[0]
    d.rounded_rectangle([(W - tw) // 2 - 20, H - 62, (W + tw) // 2 + 20, H - 14],
                        radius=12, fill='#12b76a')
    d.text(((W - tw) // 2, H - 58), label, font=f, fill='white')
    path = os.path.join(SAVE, name + '.jpg')
    img.save(path, quality=90)
    result[name] = '/uploads/' + name + '.jpg'
    print(name, 'OK')

os.remove(os.path.join(SAVE, '_map.json'))
with open(os.path.join(SAVE, '_map.json'), 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)
print('all done')
