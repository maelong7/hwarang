"""솔의 문양: 먹 붓 고리 + 붉은 실 X 땀. Writes emblem.svg (viewBox -100 -100 200 200)."""
import math, random
INK='#221d18'; RED='#a3352b'
def brush_ring(R=72,w0=11,w1=19,seed=4):
    rnd=random.Random(seed); N=260; ph=rnd.uniform(0,6.28)
    outer=[];inner=[]
    for i in range(N):
        t=2*math.pi*i/N
        w=w0+(w1-w0)*(0.5+0.5*math.sin(t+ph))+1.2*math.sin(5*t+ph*2)
        wob=1.2*math.sin(3*t+ph)+0.6*math.sin(7*t)
        ro=R+wob+w/2; ri=R+wob-w/2
        outer.append((ro*math.sin(t),-ro*math.cos(t))); inner.append((ri*math.sin(t),-ri*math.cos(t)))
    d='M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in outer)+' Z M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in reversed(inner))+' Z'
    return f'<path d="{d}" fill="{INK}" fill-rule="evenodd"/>'
def thread(x0,y0,x1,y1,w=11,seed=1):
    # a stitched thread: slightly bowed, thicker in the middle, with twist marks
    rnd=random.Random(seed); N=40; pts=[]
    dx,dy=x1-x0,y1-y0; L=math.hypot(dx,dy); nx,ny=-dy/L,dx/L
    bow=rnd.uniform(-1.6,1.6)
    up=[];dn=[]
    for i in range(N+1):
        s=i/N; x=x0+dx*s; y=y0+dy*s; b=bow*math.sin(math.pi*s)
        ww=w*(0.72+0.28*math.sin(math.pi*s))/2
        up.append((x+nx*(b+ww),y+ny*(b+ww))); dn.append((x+nx*(b-ww),y+ny*(b-ww)))
    d='M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in up)+' L'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in reversed(dn))+' Z'
    tw=''
    for k in range(1,9):
        s=k/9; x=x0+dx*s+nx*bow*math.sin(math.pi*s); y=y0+dy*s+ny*bow*math.sin(math.pi*s)
        a=w*0.32
        tw+=f'<path d="M{x+nx*a-dx/L*1.6:.2f},{y+ny*a-dy/L*1.6:.2f} L{x-nx*a+dx/L*1.6:.2f},{y-ny*a+dy/L*1.6:.2f}" stroke="#6e1f18" stroke-width="1.1" stroke-linecap="round" opacity=".55"/>'
    return f'<path d="{d}" fill="{RED}"/>'+tw
FILTER=('<filter id="inkf" x="-8%" y="-8%" width="116%" height="116%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="5" result="n"/>'
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="2.2" xChannelSelector="R" yChannelSelector="G"/></filter>')
a=24
x=thread(-a,-a,a,a,seed=2)+thread(a,-a,-a,a,seed=7)
inner=f'<defs>{FILTER}</defs><g filter="url(#inkf)">{brush_ring()}{x}</g>'
open('emblem_inner.svg','w').write(inner)
open('emblem.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200">{inner}</svg>')
print(len(inner))
