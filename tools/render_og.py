"""Link preview (og.png) built from img/cover.jpg. usage: render_og.py <site dir>"""
import sys, asyncio, base64, os
from playwright.async_api import async_playwright
out = sys.argv[1]
b64 = base64.b64encode(open(os.path.join(out, 'img', 'cover.jpg'), 'rb').read()).decode()
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Nanum+Myeongjo:wght@800&display=block">'
html = f'''<html><head>{FONTS}</head><body style="margin:0">
<div style="width:1200px;height:630px;position:relative;overflow:hidden;background:#11131d">
  <div style="position:absolute;inset:-40px;background:url(data:image/jpeg;base64,{b64}) center 30%/cover;filter:blur(28px) brightness(.45)"></div>
  <div style="position:absolute;inset:0;display:flex;align-items:center;gap:58px;padding:0 90px">
    <img src="data:image/jpeg;base64,{b64}" style="height:560px;border-radius:6px;box-shadow:0 18px 50px rgba(0,0,0,.6)">
    <div style="color:#f3ece0">
      <div style="font:800 112px/1.02 'Nanum Myeongjo';letter-spacing:-1px">화랑화살</div>
      <div style="font:700 36px 'Gowun Batang';color:#d9cdb8;margin-top:20px">1부 · 과녁 뒤의 아이</div>
      <div style="font:400 29px/1.6 'Gowun Batang';margin-top:30px;color:#efe6d6">못 쏘는 아이가, 남이 버린 화살로,<br>아무도 못 끊는 것을 끊는다.</div>
      <div style="font:400 24px 'Gowun Batang';margin-top:30px;color:#b9ad99">모노로니 지음</div>
    </div>
  </div>
</div></body></html>'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width':1200,'height':630})
        await pg.set_content(html, wait_until='networkidle'); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
        await pg.screenshot(path=os.path.join(out, 'og.jpg'), type='jpeg', quality=88); await b.close()
asyncio.run(main()); print('og ok')
