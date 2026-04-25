# components/particles.py — Theme-adaptive animated particle network
import streamlit as st


def inject_particle_background():
    is_dark = st.session_state.get("theme", "dark") == "dark"
    dot_color = "rgba(110,231,183,0.55)" if is_dark else "rgba(99,102,241,0.3)"
    line_color_base = "110,231,183" if is_dark else "99,102,241"
    opacity = "0.35" if is_dark else "0.25"

    st.markdown(f"""
<canvas id="particles-bg" style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;opacity:{opacity}"></canvas>
<script>
(function(){{
const c=document.getElementById('particles-bg');
if(!c)return;
const ctx=c.getContext('2d');
let w=c.width=window.innerWidth,h=c.height=window.innerHeight;
window.addEventListener('resize',()=>{{w=c.width=window.innerWidth;h=c.height=window.innerHeight}});
const pts=Array.from({{length:60}},()=>({{
x:Math.random()*w,y:Math.random()*h,
vx:(Math.random()-0.5)*0.2,vy:(Math.random()-0.5)*0.2,
r:Math.random()*1.4+0.4
}}));
function draw(){{
ctx.clearRect(0,0,w,h);
pts.forEach(p=>{{
p.x+=p.vx;p.y+=p.vy;
if(p.x<0)p.x=w;if(p.x>w)p.x=0;
if(p.y<0)p.y=h;if(p.y>h)p.y=0;
ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
ctx.fillStyle='{dot_color}';ctx.fill();
}});
pts.forEach((p,i)=>pts.slice(i+1).forEach(q=>{{
const dx=p.x-q.x,dy=p.y-q.y,d=Math.sqrt(dx*dx+dy*dy);
if(d<120){{
ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);
ctx.strokeStyle='rgba({line_color_base},'+(0.08*(1-d/120))+')';
ctx.lineWidth=0.5;ctx.stroke();
}}
}}));
requestAnimationFrame(draw);
}}
draw();
}})();
</script>
""", unsafe_allow_html=True)
