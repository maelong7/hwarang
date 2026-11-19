"""Extract chapters from the manuscript artifact page into chapters.json. usage: extract.py <artifact index.html> <out.json>"""
import re, json, html, sys
s=open(sys.argv[1],encoding='utf-8').read()
chapters=[]
for m in re.finditer(r'<section class="chapter" id="ch(\d+)"><header>.*?<h2>(.*?)</h2></header><div class="text">(.*?)</div></section>',s,re.S):
    items=[]
    for pm in re.finditer(r'<p class="brk"[^>]*>.*?</p>|<p id="(c[\d\-]+)"(?: data-n="[^"]*")?(?: class="(\w+)")?>(.*?)</p>',m.group(3),re.S):
        if pm.group(0).startswith('<p class="brk"'): items.append(['brk'])
        else: items.append([pm.group(1), html.unescape(pm.group(3)), 1 if pm.group(2)=='say' else 0])
    chapters.append({'n':int(m.group(1)),'title':html.unescape(m.group(2)),'items':items})
json.dump(chapters,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False)
paras=sum(1 for c in chapters for i in c['items'] if i[0]!='brk')
print('chapters',len(chapters),'paragraphs',paras,'breaks',sum(1 for c in chapters for i in c['items'] if i[0]=='brk'),'source <p id> count',s.count('<p id="c'))
