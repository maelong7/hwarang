import sys, asyncio
from playwright.async_api import async_playwright
out = sys.argv[1]
import os
inner = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emblem_inner.svg')).read()
PAPER = '#f3ece0'
def icon_html(size, box):
    return f'''<html><body style="margin:0"><div style="width:{size}px;height:{size}px;background:{PAPER};display:flex;align-items:center;justify-content:center">
<svg viewBox="-100 -100 200 200" width="{box}" height="{box}">{inner}</svg></div></body></html>'''
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Nanum+Myeongjo:wght@800&display=block">'
og = f'''<html><head>{FONTS}</head><body style="margin:0">
<div style="width:1200px;height:630px;background:{PAPER};display:flex;align-items:center;gap:56px;padding:0 96px;box-sizing:border-box;color:#221d18;position:relative">
  <svg viewBox="-100 -100 200 200" width="330" height="330" style="flex:none">{inner}</svg>
  <div>
    <div style="font:800 128px/1.02 'Nanum Myeongjo';letter-spacing:-1px">화랑화살</div>
    <div style="font:700 38px 'Gowun Batang';color:#776c60;margin-top:22px">1부 · 과녁 뒤의 아이</div>
    <div style="font:400 30px/1.55 'Gowun Batang';margin-top:30px;max-width:560px;word-break:keep-all">못 쏘는 아이가, 남이 버린 화살로,<br>아무도 못 끊는 것을 끊는다.</div>
  </div>
  <div style="position:absolute;inset:22px;border:2px solid #ddd2c1;border-radius:6px;pointer-events:none"></div>
</div></body></html>'''
jobs = [('icon-512.png',512,430,icon_html(512,430)),('icon-192.png',192,162,icon_html(192,162)),
        ('icon-maskable-512.png',512,400,icon_html(512,400)),('apple-touch-icon.png',180,150,icon_html(180,150)),
        ('favicon-32.png',32,32,icon_html(32,32)),('og.png',1200,630,og)]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, w, _, h in jobs:
            hgt = 630 if name=='og.png' else w
            pg = await b.new_page(viewport={'width':w,'height':hgt}, device_scale_factor=1)
            await pg.set_content(h, wait_until='networkidle')
            await pg.evaluate('document.fonts.ready')
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=f'{out}/{name}', clip={'x':0,'y':0,'width':w,'height':hgt})
            await pg.close()
        await b.close()
asyncio.run(main())
print('ok')
