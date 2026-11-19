#!/usr/bin/env python3
"""Build the static reader site from chapters.json.

usage: python3 build.py <chapters.json> <out_dir> <site_url> <version>
site_url is the absolute address the site will live at (for link previews).
"""
import html, json, sys, os

src, out, site_url, version = sys.argv[1], sys.argv[2], sys.argv[3].rstrip('/') + '/', sys.argv[4]
chapters = json.load(open(src, encoding='utf-8'))
os.makedirs(out, exist_ok=True)

TITLE = '화랑화살'
SUB = '1부 · 과녁 뒤의 아이'
LINE = '못 쏘는 아이가, 남이 버린 화살로, 아무도 못 끊는 것을 끊는다.'
AUTHOR = '모노로니'
esc = html.escape

# optional pictures, copied into <out>/img/ before building
def pic(name):
    path = os.path.join(out, 'img', name)
    if not os.path.exists(path): return None
    from PIL import Image
    w, h = Image.open(path).size
    return {'src': 'img/' + name, 'w': w, 'h': h}
COVER = pic('cover.jpg')
MAPS = [m for m in [(pic('map-route.jpg'), '1부에서 걸은 길'), (pic('map-city.jpg'), '서라벌')] if m[0]]
# appendix after the last chapter: character notes and the five crests (tools/cast.json, pictures in <out>/img/cast/)
_cast_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cast.json')
CAST = json.load(open(_cast_path, encoding='utf-8')) if os.path.exists(_cast_path) else None
if CAST and not pic('cast/sol.jpg'): CAST = None

total = sum(len(i[1]) for c in chapters for i in c['items'] if i[0] != 'brk')

toc_items = ''.join(
    f'<li><a href="#ch{c["n"]}" data-ch="{c["n"]}"><span class="tn">{c["n"]}</span>'
    f'<span class="tt">{esc(c["title"])}</span></a></li>' for c in chapters)
if CAST:
    toc_items += '<li><a href="#cast" data-go="cast"><span class="tn">부록</span><span class="tt">인물 소개</span></a></li>'
    toc_items += '<li><a href="#crests" data-go="crests"><span class="tn">부록</span><span class="tt">오계 문장</span></a></li>'
if MAPS:
    toc_items += '<li><a href="#maps" data-go="maps"><span class="tn">부록</span><span class="tt">지도</span></a></li>'

parts = []
for idx, c in enumerate(chapters):
    n = c['n']
    body = []
    for it in c['items']:
        if it[0] == 'brk':
            body.append('<p class="brk" aria-hidden="true">＊　＊　＊</p>')
        else:
            body.append(f'<p id="{it[0]}">{esc(it[1])}</p>')
    nxt = chapters[idx + 1] if idx + 1 < len(chapters) else None
    if nxt:
        end = (f'<a class="next" href="#ch{nxt["n"]}"><span>다음 장</span>'
               f'<b>{nxt["n"]}장 · {esc(nxt["title"])}</b></a>')
    else:
        end = '<p class="fin">1부 끝</p>'
    parts.append(
        f'<section class="ch" id="ch{n}" data-ch="{n}" data-title="{esc(c["title"])}">'
        f'<header><p class="chn">{n}장</p><h2>{esc(c["title"])}</h2></header>'
        + ''.join(body) + f'<footer class="chend">{end}</footer></section>')

def img_tag(name, alt):
    m = pic('cast/' + name)
    return (f'<a href="{m["src"]}" target="_blank" rel="noopener"><img src="{m["src"]}" width="{m["w"]}" height="{m["h"]}" '
            f'loading="lazy" alt="{esc(alt)}"></a>')
if CAST:
    idx = ''.join(f'<a href="#p-{p["id"]}">{esc(p["name"])}</a>' for p in CAST['people'])
    cards = []
    for p in CAST['people']:
        figs = ''.join(f'<figure>{img_tag(f, p["name"] + " 인물 시트")}' + (f'<figcaption>{esc(cap)}</figcaption>' if cap else '') + '</figure>'
                       for f, cap in p['sheets'])
        facts = ''.join(f'<div><dt>{esc(dt)}</dt><dd>{dd}</dd></div>' for dt, dd in p['facts'])   # dd keeps its <q> quotes
        cards.append(f'<article class="pc" id="p-{p["id"]}"><header><h3>{esc(p["name"])}</h3><p class="rank">{esc(p["rank"])}</p>'
                     f'<p class="who">{esc(p["who"])}</p></header><p class="pline">{p["line"]}</p>{figs}<dl>{facts}</dl></article>')
    parts.append(f'<section class="appx cast" id="cast"><header><p class="chn">부록</p><h2>인물 소개</h2></header>'
                 f'<p class="lead">{esc(CAST["intro"])}</p><nav class="pidx" aria-label="인물 바로 가기">{idx}</nav>' + ''.join(cards) + '</section>')
    C = CAST['crests']
    items = ''.join(f'<figure class="crest">{img_tag(c["img"], c["name"] + " 문장")}<figcaption><b>{esc(c["name"])}</b>'
                    f'<span class="crank">{esc(c["rank"])}</span><span class="cline">{esc(c["line"])}</span><span class="cwho">{esc(c["who"])}</span></figcaption></figure>'
                    for c in C['items'])
    # all five side by side first, so they can be compared at a glance; the notes follow below
    strip = ''.join(f'<figure><img src="{pic("cast/" + c["img"])["src"]}" width="600" height="600" loading="lazy" alt="">'
                    f'<figcaption><b>{esc(c["name"].split(" · ")[0])}</b>{esc(c["rank"].split(" · ")[0])}</figcaption></figure>' for c in C['items'])
    parts.append(f'<section class="appx crests" id="crests"><header><p class="chn">부록</p><h2>오계 문장</h2></header>'
                 f'<p class="lead">{esc(C["lead"])}</p><div class="creststrip" aria-hidden="true">{strip}</div>'
                 f'<p class="sublead">{esc(C["sub"])}</p><div class="crestgrid">{items}</div><p class="cnote">{esc(C["note"])}</p></section>')
if MAPS:
    figs = ''.join(
        f'<figure><a href="{m["src"]}" target="_blank" rel="noopener"><img src="{m["src"]}" width="{m["w"]}" height="{m["h"]}" loading="lazy" alt="{esc(cap)} 지도"></a>'
        f'<figcaption>{esc(cap)} · 누르면 크게 볼 수 있어요</figcaption></figure>' for m, cap in MAPS)
    parts.append(f'<section class="appx maps" id="maps"><header><p class="chn">부록</p><h2>지도</h2></header>{figs}</section>')
chapter_html = '\n'.join(parts)
EMBLEM = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emblem_inner.svg'), encoding='utf-8').read().replace('#221d18', 'currentColor')
BOOK_RATIO = f"{COVER['w'] / COVER['h']:.4f}" if COVER else '0.66'
OG = 'og.jpg' if os.path.exists(os.path.join(out, 'og.jpg')) else 'og.png'
if COVER:
    COVER_HTML = (f'<img class="book" src="{COVER["src"]}" width="{COVER["w"]}" height="{COVER["h"]}" alt="{TITLE} {SUB} 표지">'
                  f'<h1 class="sr">{TITLE}</h1><p class="sr">{SUB}</p>')
else:
    COVER_HTML = (f'<svg class="mark" viewBox="-100 -100 200 200" aria-hidden="true">{EMBLEM}</svg>'
                  f'<h1>{TITLE}</h1><p class="sub">{SUB}</p>')
titles_js = json.dumps({c['n']: c['title'] for c in chapters}, ensure_ascii=False)

page = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE} {SUB}</title>
<meta name="description" content="{esc(LINE)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#f3ece0" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#16130f" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="book">
<meta property="og:title" content="{TITLE} {SUB}">
<meta property="og:description" content="{esc(LINE)}">
<meta property="og:image" content="{site_url}{OG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{site_url}">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png" sizes="192x192">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{TITLE}">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<script>
/* Leave in-app browsers (KakaoTalk, LINE, Instagram, Facebook ...) for the phone's own browser. */
(function(){{
  var ua = navigator.userAgent || '';
  var href = location.href;
  var android = /Android/i.test(ua), ios = /iPhone|iPad|iPod/i.test(ua);
  window.__inapp = '';
  try {{
    if (/KAKAOTALK/i.test(ua)) {{
      window.__inapp = 'kakao';
      location.href = 'kakaotalk://web/openExternal?url=' + encodeURIComponent(href);
      /* close KakaoTalk's own browser once the phone's browser has taken over */
      setTimeout(function(){{ location.href = ios ? 'kakaoweb://closeBrowser' : 'kakaotalk://inappbrowser/close'; }}, 400);
      return;
    }}
    if (/ Line\\//i.test(ua)) {{
      window.__inapp = 'line';
      if (!/[?&]openExternalBrowser=1/.test(href)) {{
        var u = new URL(href); u.searchParams.set('openExternalBrowser', '1'); location.replace(u.toString());
      }}
      return;
    }}
    var other = /FBAN|FBAV|FB_IAB|Instagram|NAVER\\(inapp|DaumApps|everytimeApp|Snapchat|Twitter|; wv\\)/i.test(ua);
    if (other && android) {{
      window.__inapp = 'android';
      location.href = 'intent://' + href.replace(/^https?:\\/\\//, '') + '#Intent;scheme=https;package=com.android.chrome;end';
      return;
    }}
    if (other && ios) window.__inapp = 'ios';
  }} catch (e) {{}}
}})();
/* Theme and font size before first paint, so the page does not flash. */
(function(){{
  try {{
    var t = localStorage.getItem('hrhs-theme'); if (t) document.documentElement.dataset.theme = t;
    var f = localStorage.getItem('hrhs-font'); if (f) document.documentElement.style.setProperty('--fs', f + 'px');
  }} catch (e) {{}}
}})();
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Nanum+Myeongjo:wght@800&display=swap">
<style>
:root {{
  --paper:#f3ece0; --sheet:#fbf7f0; --ink:#221d18; --soft:#776c60; --rule:#ddd2c1; --accent:#8e2f25; --bar:rgba(243,236,224,.94);
  --fs:18px; --measure:34em;
  --body:"Gowun Batang","Noto Serif KR","Apple SD Gothic Neo",serif;
  --display:"Nanum Myeongjo","Gowun Batang",serif;
  --ui:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR","Malgun Gothic",sans-serif;
  color-scheme: light;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --paper:#16130f; --sheet:#1e1a15; --ink:#e7dfd2; --soft:#a3988a; --rule:#3a332a; --accent:#e08a74; --bar:rgba(22,19,15,.94); color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --paper:#16130f; --sheet:#1e1a15; --ink:#e7dfd2; --soft:#a3988a; --rule:#3a332a; --accent:#e08a74; --bar:rgba(22,19,15,.94); color-scheme: dark; }}
* {{ box-sizing:border-box; }}
html {{ -webkit-text-size-adjust:100%; text-size-adjust:100%; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:var(--body); font-size:var(--fs); line-height:1.95;
  word-break:keep-all; overflow-wrap:break-word; -webkit-tap-highlight-color:transparent; }}
a {{ color:inherit; }}
.wrap {{ max-width:var(--measure); margin:0 auto; padding:0 max(20px, env(safe-area-inset-left)) 0 max(20px, env(safe-area-inset-right)); }}

/* top bar */
.bar {{ position:fixed; inset:0 0 auto 0; z-index:20; background:var(--bar); backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px);
  border-bottom:1px solid var(--rule); padding-top:env(safe-area-inset-top); transform:translateY(0); transition:transform .25s; }}
.bar.hide {{ transform:translateY(-110%); }}
.bar .in {{ display:flex; align-items:center; gap:4px; height:48px; max-width:calc(var(--measure) + 120px); margin:0 auto; padding:0 8px; }}
.bar .where {{ flex:1; min-width:0; font-family:var(--ui); font-size:14px; color:var(--soft); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; text-align:center; }}
.btn {{ appearance:none; border:0; background:transparent; color:var(--ink); font:600 14px var(--ui); height:40px; min-width:44px; padding:0 10px; border-radius:8px; cursor:pointer; }}
.btn:active {{ background:var(--rule); }}
.prog {{ position:absolute; left:0; bottom:-1px; height:2px; background:var(--accent); width:0; }}

/* cover */
.cover {{ min-height:100vh; min-height:100svh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:72px 0 40px; }}
.cover .mark {{ width:120px; height:120px; margin:0 auto 28px; }}
.cover h1 {{ font-family:var(--display); font-weight:800; font-size:clamp(44px, 14vw, 72px); line-height:1.05; margin:0; letter-spacing:-.01em; }}
.cover .sub {{ font-family:var(--ui); font-size:15px; color:var(--soft); margin:14px 0 0; letter-spacing:.04em; }}
.cover .line {{ font-size:calc(var(--fs) * 1.05); margin:28px auto 0; max-width:22em; }}
.cover .go {{ display:flex; flex-wrap:wrap; justify-content:center; gap:10px; margin-top:34px; }}
.pill {{ display:inline-flex; align-items:center; justify-content:center; min-height:48px; padding:0 22px; border-radius:999px;
  font:700 16px var(--ui); text-decoration:none; border:1.5px solid var(--ink); background:transparent; color:var(--ink); cursor:pointer; }}
.pill.solid {{ background:var(--ink); color:var(--paper); }}
.cover .book {{ display:block; height:auto; border-radius:4px; box-shadow:0 10px 30px rgba(0,0,0,.25); margin:0 auto 6px;
  width:min(100%, calc((100vh - 170px) * {BOOK_RATIO})); width:min(100%, calc((100svh - 170px) * {BOOK_RATIO})); }}
.sr {{ position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }}
.appx {{ padding:88px 0 3em; border-top:1px solid var(--rule); }}
.appx > header {{ margin-bottom:1.4em; }}
.appx h2 {{ font-family:var(--display); font-weight:800; font-size:calc(var(--fs) * 1.7); margin:0; }}
.appx .lead {{ margin:0 0 1em; }}
.appx .sublead, .appx .cnote {{ font:14px/1.7 var(--ui); color:var(--soft); margin:0 0 1.6em; }}
.pidx {{ display:flex; flex-wrap:wrap; gap:8px; margin:0 0 1em; }}
.pidx a {{ font:600 14px var(--ui); text-decoration:none; padding:7px 12px; border:1px solid var(--rule); border-radius:999px; background:var(--sheet); }}
.pc {{ padding:2.6em 0 1.2em; border-top:1px solid var(--rule); margin-top:1.8em; }}
.pc h3 {{ font-family:var(--display); font-weight:800; font-size:calc(var(--fs) * 1.5); line-height:1.2; margin:0 0 6px; }}
.pc .rank {{ font:600 14px/1.5 var(--ui); margin:0; }}
.pc .who {{ font:14px/1.5 var(--ui); color:var(--soft); margin:2px 0 0; }}
.pc .pline {{ font-family:var(--display); font-weight:800; font-size:calc(var(--fs) * 1.05); line-height:1.6; margin:1em 0 1.1em; }}
.pc figure, .crest {{ margin:0 0 1.1em; }}
.pc img, .crest img {{ display:block; width:100%; height:auto; border-radius:6px; border:1px solid var(--rule); background:#fdeee3; }}
.pc figcaption {{ font:13px var(--ui); color:var(--soft); margin-top:6px; text-align:center; }}
.pc dl {{ margin:0; }}
.pc dl div {{ padding:10px 0; border-top:1px solid var(--rule); }}
.pc dt {{ font:600 12px var(--ui); letter-spacing:.08em; color:var(--soft); margin-bottom:2px; }}
.pc dd {{ margin:0; font-size:calc(var(--fs) * .92); line-height:1.8; }}
.pc dd q, .pc .pline q {{ quotes:'"' '"'; font-weight:700; }}
.creststrip {{ display:grid; grid-template-columns:repeat(5, 1fr); gap:8px; margin:0 0 1.2em; }}
.creststrip figure {{ margin:0; min-width:0; text-align:center; }}
.creststrip img {{ display:block; width:100%; height:auto; border-radius:5px; border:1px solid var(--rule); }}
.creststrip figcaption {{ font:11px/1.4 var(--ui); color:var(--soft); margin-top:5px; }}
.creststrip b {{ display:block; font-family:var(--display); font-weight:800; font-size:calc(var(--fs) * .95); color:var(--ink); }}
.crestgrid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:22px 16px; margin:0 0 1.6em; }}
.crest {{ margin:0; min-width:0; }}
.crest figcaption {{ display:grid; gap:3px; margin-top:8px; }}
.crest b {{ font-family:var(--display); font-weight:800; font-size:calc(var(--fs) * 1.1); }}
.crest .crank {{ font:12px var(--ui); letter-spacing:.08em; color:var(--soft); }}
.crest .cline {{ font-size:calc(var(--fs) * .84); line-height:1.7; }}
.crest .cwho {{ font:13px/1.6 var(--ui); color:var(--soft); }}
.maps {{ padding-bottom:6em; }}
.maps figure {{ margin:0 0 2.4em; }}
.maps img {{ display:block; width:100%; height:auto; border-radius:6px; border:1px solid var(--rule); }}
.maps figcaption {{ font:13px var(--ui); color:var(--soft); margin-top:8px; text-align:center; }}
.cover .meta {{ font-family:var(--ui); font-size:13px; color:var(--soft); margin-top:22px; }}

/* chapters */
.ch {{ padding:88px 0 24px; border-top:1px solid var(--rule); }}
.ch header {{ margin-bottom:2.2em; }}
.chn {{ font-family:var(--ui); font-size:13px; letter-spacing:.14em; color:var(--soft); margin:0 0 6px; }}
.ch h2 {{ font-family:var(--display); font-weight:800; font-size:calc(var(--fs) * 1.7); line-height:1.25; margin:0; }}
.ch p {{ margin:0 0 .9em; }}
.ch p.brk {{ text-align:center; color:var(--soft); margin:2em 0; letter-spacing:.2em; }}
.chend {{ margin:3em 0 1em; }}
.next {{ display:flex; flex-direction:column; gap:2px; padding:18px 20px; border:1px solid var(--rule); border-radius:12px; background:var(--sheet); text-decoration:none; }}
.next span {{ font-family:var(--ui); font-size:13px; color:var(--soft); }}
.next b {{ font-family:var(--display); font-weight:800; font-size:calc(var(--fs) * 1.1); }}
.fin {{ text-align:center; font-family:var(--display); font-weight:800; font-size:calc(var(--fs) * 1.3); margin:2em 0 3em; }}

/* sheets: table of contents, settings */
.scrim {{ position:fixed; inset:0; z-index:30; background:rgba(0,0,0,.35); opacity:0; pointer-events:none; transition:opacity .2s; }}
.scrim.on {{ opacity:1; pointer-events:auto; }}
.sheet {{ position:fixed; z-index:31; left:0; right:0; bottom:0; max-height:82svh; overflow:auto; background:var(--sheet); color:var(--ink);
  border-radius:18px 18px 0 0; padding:10px 20px calc(24px + env(safe-area-inset-bottom)); transform:translateY(105%); transition:transform .25s; }}
.sheet.on {{ transform:translateY(0); }}
.sheet h3 {{ font:700 16px var(--ui); margin:10px 0 12px; }}
.grip {{ width:40px; height:4px; border-radius:2px; background:var(--rule); margin:4px auto 6px; }}
.toc {{ list-style:none; margin:0; padding:0; }}
.toc a {{ display:flex; gap:14px; align-items:baseline; padding:11px 4px; text-decoration:none; border-bottom:1px solid var(--rule); }}
.toc .tn {{ font:600 13px var(--ui); color:var(--soft); width:2.2em; flex:none; text-align:right; }}
.toc .tt {{ font-size:16px; }}
.toc a.cur .tt {{ font-weight:700; color:var(--accent); }}
.toc a.read .tn::after {{ content:" ✓"; }}
.row {{ display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 0; border-bottom:1px solid var(--rule); font:15px var(--ui); }}
.seg {{ display:flex; border:1px solid var(--rule); border-radius:10px; overflow:hidden; }}
.seg button {{ appearance:none; border:0; background:transparent; color:var(--ink); font:600 15px var(--ui); min-width:52px; height:40px; cursor:pointer; }}
.seg button + button {{ border-left:1px solid var(--rule); }}
.seg button[aria-pressed="true"] {{ background:var(--ink); color:var(--sheet); }}

/* toasts and banners */
.toast {{ position:fixed; z-index:25; left:50%; bottom:calc(18px + env(safe-area-inset-bottom)); transform:translate(-50%, 140%); transition:transform .25s;
  width:min(92vw, 30em); background:var(--ink); color:var(--paper); border-radius:14px; padding:12px 14px; display:flex; align-items:center; gap:10px; font:14px/1.45 var(--ui); }}
.toast.on {{ transform:translate(-50%, 0); }}
.toast .msg {{ flex:1; min-width:0; }}
.toast button {{ appearance:none; border:0; background:transparent; color:var(--paper); font:700 14px var(--ui); padding:8px 6px; cursor:pointer; white-space:nowrap; }}
.toast button.x {{ opacity:.7; }}
.guide {{ position:fixed; inset:0; z-index:40; background:rgba(0,0,0,.6); display:none; align-items:flex-end; justify-content:center; }}
.guide.on {{ display:flex; }}
.guide .card {{ width:min(94vw, 26em); margin-bottom:calc(16px + env(safe-area-inset-bottom)); background:var(--sheet); color:var(--ink); border-radius:16px; padding:20px; font:15px/1.6 var(--ui); }}
.guide .card b {{ font-size:17px; display:block; margin-bottom:6px; }}
.guide ol {{ padding-left:1.3em; margin:8px 0 14px; }}
.guide .ico {{ display:inline-block; vertical-align:-4px; width:20px; height:20px; }}
.guide .acts {{ display:flex; gap:8px; justify-content:flex-end; }}
@media (prefers-reduced-motion: reduce) {{ .bar, .sheet, .toast, .scrim {{ transition:none; }} }}
</style>
</head>
<body>
<div class="bar" id="bar"><div class="in">
  <button class="btn" id="openToc" aria-label="목차">목차</button>
  <div class="where" id="where">{TITLE}</div>
  <button class="btn" id="openSet" aria-label="글자와 화면 설정">가</button>
  <div class="prog" id="prog"></div>
</div></div>

<main class="wrap">
  <section class="cover" id="top">
    {COVER_HTML}
    <p class="line">{esc(LINE).replace('화살로, ', '화살로,<br>')}</p>
    <div class="go">
      <a class="pill solid" id="resumeBtn" href="#ch1">처음부터 읽기</a>
      <button class="pill" id="tocBtn2" type="button">목차</button>
    </div>
    <p class="meta">{AUTHOR} 지음 · 34장 · 약 {round(total/10000)}만 자</p>
  </section>
{chapter_html}
</main>

<div class="scrim" id="scrim"></div>
<div class="sheet" id="tocSheet" role="dialog" aria-label="목차"><div class="grip"></div><h3>목차</h3><ol class="toc" id="toc">{toc_items}</ol></div>
<div class="sheet" id="setSheet" role="dialog" aria-label="설정"><div class="grip"></div><h3>읽기 설정</h3>
  <div class="row"><span>글자 크기</span><div class="seg"><button id="fsDown" aria-label="작게">가−</button><button id="fsUp" aria-label="크게">가+</button></div></div>
  <div class="row"><span>화면</span><div class="seg" id="themeSeg"><button data-t="">자동</button><button data-t="light">낮</button><button data-t="dark">밤</button></div></div>
  <div class="row"><span>홈 화면에 추가</span><button class="btn" id="installRow">방법 보기</button></div>
</div>

<div class="toast" id="toast" role="status"><span class="msg" id="toastMsg"></span><button id="toastAct"></button><button class="x" id="toastX" aria-label="닫기">✕</button></div>

<div class="guide" id="guide" role="dialog" aria-modal="true"><div class="card" id="guideCard"></div></div>

<script>
(function(){{
  var TITLES = {titles_js};
  var LS = {{
    get: function(k){{ try {{ return localStorage.getItem(k); }} catch(e) {{ return null; }} }},
    set: function(k,v){{ try {{ localStorage.setItem(k,v); }} catch(e) {{}} }}
  }};
  var $ = function(id){{ return document.getElementById(id); }};
  var bar=$('bar'), where=$('where'), prog=$('prog');
  var ios = /iPhone|iPad|iPod/i.test(navigator.userAgent) || (navigator.platform==='MacIntel' && navigator.maxTouchPoints>1);
  var standalone = window.matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;

  /* --- toast --- */
  var toastTimer;
  function toast(msg, actLabel, act, ms){{
    $('toastMsg').textContent = msg;
    var b=$('toastAct'); b.textContent = actLabel||''; b.style.display = actLabel ? '' : 'none'; b.onclick = function(){{ hideToast(); act && act(); }};
    $('toast').classList.add('on'); clearTimeout(toastTimer);
    if (ms !== 0) toastTimer = setTimeout(hideToast, ms||6000);
  }}
  function hideToast(){{ $('toast').classList.remove('on'); }}
  $('toastX').onclick = hideToast;

  /* --- in-app browser fallback (when escaping did not work) --- */
  if (window.__inapp === 'kakao' || window.__inapp === 'android') {{
    setTimeout(function(){{ toast('휴대폰 기본 브라우저에서 열었어요. 열리지 않았다면 오른쪽 위 메뉴에서 "다른 브라우저로 열기"를 눌러 주세요.', '', null, 9000); }}, 1200);
  }}
  if (window.__inapp === 'ios') {{
    showGuide('<b>Safari에서 열어 주세요</b>이 앱 안의 브라우저에서는 읽던 자리가 잘 남지 않아요.<ol><li>오른쪽 아래나 위의 <b style="display:inline">⋯</b> 또는 공유 버튼을 누르고</li><li>"Safari로 열기" 또는 "브라우저에서 열기"를 고르세요.</li></ol>', [['주소 복사', copyLink], ['그냥 읽기', closeGuide]]);
  }}
  function copyLink(){{
    var u = location.href.split('#')[0];
    if (navigator.clipboard) navigator.clipboard.writeText(u).then(function(){{ toast('주소를 복사했어요. Safari 주소창에 붙여 넣으세요.'); }}, function(){{}});
    closeGuide();
  }}

  /* --- guide modal --- */
  function showGuide(htmlStr, actions){{
    var c=$('guideCard'); c.innerHTML = htmlStr + '<div class="acts"></div>';
    var acts=c.querySelector('.acts');
    actions.forEach(function(a, i){{ var b=document.createElement('button'); b.className = i===actions.length-1 ? 'pill solid' : 'pill'; b.textContent=a[0]; b.onclick=a[1]; acts.appendChild(b); }});
    $('guide').classList.add('on');
  }}
  function closeGuide(){{ $('guide').classList.remove('on'); }}

  /* --- add to home screen --- */
  var deferred = null;
  window.addEventListener('beforeinstallprompt', function(e){{
    e.preventDefault(); deferred = e;
    if (!standalone && !window.__inapp && LS.get('hrhs-install-no') !== '1') {{
      setTimeout(function(){{ toast('홈 화면에 화랑화살을 추가하면 앱처럼 바로 열어 읽을 수 있어요.', '추가', doInstall, 0); }}, 1500);
    }}
  }});
  /* Android browsers that never offer the install prompt (Samsung Internet in some modes, Firefox ...) */
  var android = /Android/i.test(navigator.userAgent);
  if (android && !standalone && !window.__inapp && LS.get('hrhs-install-no') !== '1') {{
    setTimeout(function(){{ if (!deferred) toast('홈 화면에 화랑화살을 추가하면 앱처럼 바로 열어 읽을 수 있어요.', '방법', doInstall, 0); }}, 4500);
  }}
  function doInstall(){{
    if (deferred) {{ deferred.prompt(); deferred.userChoice.then(function(){{ deferred = null; }}); return; }}
    if (ios) return iosGuide();
    showGuide('<b>홈 화면에 추가하기</b><ol><li>브라우저 메뉴(⋮ 또는 ≡)를 누르고</li><li>"홈 화면에 추가" 또는 "앱 설치"를 고르세요.</li></ol>', [['다시 보지 않기', function(){{ LS.set('hrhs-install-no','1'); closeGuide(); }}], ['닫기', closeGuide]]);
  }}
  var shareIco = '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M7 8l5-5 5 5"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg>';
  function iosGuide(){{
    showGuide('<b>홈 화면에 추가하기</b>한 번만 해 두면 아이콘을 눌러 앱처럼 바로 이어 읽을 수 있어요.<ol><li>Safari 아래쪽의 공유 버튼 ' + shareIco + ' 을 누르세요. 안 보이면 ⋯ 버튼 안에 있어요.</li><li>목록에서 "홈 화면에 추가"를 누르세요. 안 보이면 목록을 아래로 내려 보세요.</li></ol>홈 화면 아이콘으로 열면 읽던 자리를 거기서 따로 기억해요. 추가한 뒤에는 아이콘으로 읽어 주세요.',
      [['다시 보지 않기', function(){{ LS.set('hrhs-install-no','1'); closeGuide(); }}], ['알겠어요', closeGuide]]);
  }}
  if (ios && !standalone && !window.__inapp && LS.get('hrhs-install-no') !== '1' && !sessionStorageGet('hrhs-ios-shown')) {{
    setTimeout(function(){{ sessionStorageSet('hrhs-ios-shown','1'); iosGuide(); }}, 1200);
  }}
  function sessionStorageGet(k){{ try {{ return sessionStorage.getItem(k); }} catch(e) {{ return null; }} }}
  function sessionStorageSet(k,v){{ try {{ sessionStorage.setItem(k,v); }} catch(e) {{}} }}
  $('installRow').onclick = function(){{ closeSheets(); doInstall(); }};

  /* --- sheets --- */
  var scrim=$('scrim');
  function openSheet(id){{ closeSheets(); $(id).classList.add('on'); scrim.classList.add('on');
    if (id==='tocSheet') {{ var a=document.querySelector('.toc a.cur'); if (a) a.scrollIntoView({{block:'center'}}); }} }}
  function closeSheets(){{ document.querySelectorAll('.sheet.on').forEach(function(s){{ s.classList.remove('on'); }}); scrim.classList.remove('on'); }}
  scrim.onclick = closeSheets;
  $('openToc').onclick = function(){{ openSheet('tocSheet'); }};
  $('tocBtn2').onclick = function(){{ openSheet('tocSheet'); }};
  $('openSet').onclick = function(){{ openSheet('setSheet'); }};
  $('toc').addEventListener('click', function(e){{ var a=e.target.closest('a'); if (!a) return; e.preventDefault(); closeSheets();
    if (a.dataset.go) {{ var t=$(a.dataset.go); if (t) {{ window.scrollTo({{top: t.getBoundingClientRect().top + window.scrollY - barH() + 40}}); lastY = window.scrollY; }} }}
    else goChapter(+a.dataset.ch); }});

  /* --- settings --- */
  var sizes=[15,16,17,18,19,20,22,24];
  function curFs(){{ return parseInt(getComputedStyle(document.documentElement).getPropertyValue('--fs')) || 18; }}
  function setFs(v){{ var anchor = currentPara(); document.documentElement.style.setProperty('--fs', v+'px'); LS.set('hrhs-font', v); if (anchor) jumpTo(anchor, false); }}
  $('fsUp').onclick = function(){{ var c=curFs(); var n=sizes.find(function(s){{ return s>c; }}); if (n) setFs(n); }};
  $('fsDown').onclick = function(){{ var c=curFs(); var n=sizes.slice().reverse().find(function(s){{ return s<c; }}); if (n) setFs(n); }};
  function paintTheme(){{ var t=document.documentElement.dataset.theme||''; document.querySelectorAll('#themeSeg button').forEach(function(b){{ b.setAttribute('aria-pressed', b.dataset.t===t ? 'true':'false'); }}); }}
  document.querySelectorAll('#themeSeg button').forEach(function(b){{ b.onclick=function(){{ if (b.dataset.t) document.documentElement.dataset.theme=b.dataset.t; else delete document.documentElement.dataset.theme; LS.set('hrhs-theme', b.dataset.t); paintTheme(); }}; }});
  paintTheme();

  /* --- reading position --- */
  function barH(){{ return bar.getBoundingClientRect().height; }}
  function currentPara(){{
    /* probe downward from just under the bar until we hit a paragraph; gaps between paragraphs return the section */
    var x = window.innerWidth/2, y0 = barH() + 20;
    /* elementsFromPoint looks through sheets and toasts that may be sliding over the text */
    for (var dy = 0; dy < 280; dy += 12) {{
      var els = document.elementsFromPoint(x, y0 + dy);
      for (var i = 0; i < els.length; i++) {{
        var el = els[i];
        if (el.tagName==='P' && el.id && /^c\\d+-/.test(el.id)) return el.id;
        if (el.classList && el.classList.contains('cover')) return null;
        if (el.classList && el.classList.contains('appx')) return el.id;
      }}
    }}
    return lastSaved || null;
  }}
  /* setFs keeps the reader on the same paragraph; the maps section is a fine anchor too */
  function chOf(id){{ var m=/^c(\\d+)-/.exec(id||''); return m ? +m[1] : 0; }}
  function jumpTo(id, smooth){{ var el=document.getElementById(id); if (!el) return false;
    var top = el.getBoundingClientRect().top + window.scrollY - barH() - 16; window.scrollTo({{top: top, behavior: smooth ? 'smooth':'auto'}}); lastY = window.scrollY; return true; }}
  function goChapter(n){{ var el=document.getElementById('ch'+n); if (!el) return; window.scrollTo({{top: el.getBoundingClientRect().top + window.scrollY - barH() + 40, behavior:'auto'}}); lastY = window.scrollY; bar.classList.remove('hide'); }}

  var maxRead = +(LS.get('hrhs-max')||0);
  function paintToc(cur){{ document.querySelectorAll('.toc a').forEach(function(a){{ var n=+a.dataset.ch; a.classList.toggle('cur', n===cur); a.classList.toggle('read', n<maxRead); }}); }}

  var lastY = window.scrollY, ticking=false, lastSaved='', restoring=true;
  try {{ history.scrollRestoration = 'manual'; }} catch(e) {{}}
  function onScroll(){{
    var y = window.scrollY;
    if (y > lastY + 6 && y > 200) bar.classList.add('hide'); else if (y < lastY - 6) bar.classList.remove('hide');
    lastY = y;
    var h = document.documentElement.scrollHeight - window.innerHeight; prog.style.width = (h>0 ? (y/h*100) : 0) + '%';
    var id = currentPara(), ch = chOf(id);
    var APPX = {{maps:'부록 · 지도', cast:'부록 · 인물 소개', crests:'부록 · 오계 문장'}};
    where.textContent = APPX[id] ? APPX[id] : ch ? (ch + '장 · ' + TITLES[ch]) : '{TITLE}';
    if (!restoring && ch && id !== lastSaved) {{ lastSaved = id; LS.set('hrhs-pos', id); if (ch > maxRead) {{ maxRead = ch; LS.set('hrhs-max', ch); }} paintToc(ch); }}
    ticking=false;
  }}
  window.addEventListener('scroll', function(){{ if (!ticking) {{ ticking=true; requestAnimationFrame(onScroll); }} }}, {{passive:true}});

  /* tap on the text shows or hides the bar */
  document.querySelector('main').addEventListener('click', function(e){{
    if (e.target.closest('a,button')) return;
    var sel = window.getSelection && window.getSelection(); if (sel && String(sel).length) return;
    bar.classList.toggle('hide');
  }});

  /* links to one person inside the character notes */
  document.addEventListener('click', function(e){{ var a=e.target.closest('a[href^="#p-"]'); if (!a) return; e.preventDefault();
    var t=document.getElementById(a.getAttribute('href').slice(1)); if (!t) return;
    window.scrollTo({{top: t.getBoundingClientRect().top + window.scrollY - barH() - 8}}); lastY = window.scrollY; }});

  /* in-page links (다음 장, 처음부터) */
  document.addEventListener('click', function(e){{ var a=e.target.closest('a[href^="#ch"]'); if (!a || a.closest('.toc')) return; e.preventDefault(); goChapter(+a.getAttribute('href').slice(3)); }});

  /* start: a chapter link (#ch12) wins, then the saved place */
  window.addEventListener('load', function(){{
    var m = /^#ch(\\d+)$/.exec(location.hash);
    var saved = LS.get('hrhs-pos');
    var go = function(){{}};
    if (m) {{ go = function(){{ goChapter(+m[1]); }}; history.replaceState(null,'',location.pathname+location.search); }}
    else if (saved && document.getElementById(saved)) {{
      var ch = chOf(saved);
      lastSaved = saved;
      $('resumeBtn').textContent = '이어 읽기 · ' + ch + '장';
      $('resumeBtn').setAttribute('href', '#' + saved);
      $('resumeBtn').onclick = function(e){{ e.preventDefault(); jumpTo(saved, false); }};
      go = function(){{ jumpTo(saved, false); }};
      toast(ch + '장 「' + TITLES[ch] + '」 읽던 자리에서 이어 읽어요.', '처음으로', function(){{ window.scrollTo(0,0); }});
    }}
    go();
    paintToc(chOf(saved||''));
    var settle = (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve();
    var done = false;
    function finish(){{ if (done) return; done = true; go(); setTimeout(function(){{ go(); restoring = false; bar.classList.remove('hide'); onScroll(); }}, 80); }}
    settle.then(finish, finish);
    setTimeout(finish, 3000);
  }});

  /* offline copy */
  if ('serviceWorker' in navigator) {{ navigator.serviceWorker.register('sw.js').catch(function(){{}}); }}
}})();
</script>
</body>
</html>
'''
open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(page)

manifest = {
    "name": f"{TITLE} {SUB}", "short_name": TITLE, "lang": "ko", "dir": "ltr",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#f3ece0", "theme_color": "#f3ece0",
    "description": LINE,
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
    ]
}
json.dump(manifest, open(os.path.join(out, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

sw = f'''const CACHE = 'hrhs-{version}';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png', 'apple-touch-icon.png'{", 'img/cover.jpg'" if COVER else ''}];
self.addEventListener('install', e => {{ e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); }});
self.addEventListener('activate', e => {{ e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); }});
self.addEventListener('fetch', e => {{
  const req = e.request; if (req.method !== 'GET') return;
  if (req.mode === 'navigate') {{
    // newest text when online, saved copy when offline
    e.respondWith(fetch(req).then(r => {{ const c = r.clone(); caches.open(CACHE).then(x => x.put('index.html', c)); return r; }}).catch(() => caches.match('index.html')));
    return;
  }}
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {{
    if (r.ok || r.type === 'opaque') {{ const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); }}
    return r;
  }}).catch(() => hit)));
}});
'''
open(os.path.join(out, 'sw.js'), 'w', encoding='utf-8').write(sw)
open(os.path.join(out, '.nojekyll'), 'w').write('')
print('built', out, 'chars', total)
