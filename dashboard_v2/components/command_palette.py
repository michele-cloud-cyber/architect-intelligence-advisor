"""Keyboard-only navigation palette backed by the central module registry."""

from __future__ import annotations
import html, json
import streamlit.components.v1 as components
from v2.modules.unified_shell.registry import MODULE_REGISTRY


def render_command_palette(language: str="it") -> None:
    items=[{"id":m.module_id,"name":m.name(language),"description":m.description(language),"destination":m.destination,"badge":m.badge,"keywords":" ".join(m.keywords)} for m in MODULE_REGISTRY]
    payload=json.dumps(items,ensure_ascii=False).replace("</","<\\/")
    placeholder="Cerca comando…" if language=="it" else "Search command…"
    components.html(f"""<script>
const pd=parent.document;pd.getElementById('aia-palette')?.remove();pd.getElementById('aia-palette-style')?.remove();
const style=pd.createElement('style');style.id='aia-palette-style';style.textContent=`#aia-palette{{display:none;position:fixed;z-index:2147483647;inset:8% 15% auto;background:#101c2b;color:#fff;border:1px solid #3b536f;border-radius:14px;padding:16px;box-shadow:0 24px 80px #000a;font-family:system-ui}}#aia-search{{width:100%;box-sizing:border-box;padding:12px;background:#0b1420;color:#fff;border:1px solid #4b6584;border-radius:8px}}.aia-item{{padding:10px;border-radius:8px;margin-top:6px;cursor:pointer}}.aia-item.active{{background:#2563eb}}.aia-meta{{font-size:12px;color:#b8c5d6}}`;pd.head.appendChild(style);
const palette=pd.createElement('div');palette.id='aia-palette';palette.innerHTML=`<input id="aia-search" placeholder="{html.escape(placeholder)}"/><div id="aia-results"></div><div class="aia-meta">Ctrl+K / · ↑↓ · Enter · Esc</div>`;pd.body.appendChild(palette);
const items={payload}; const input=pd.getElementById('aia-search'); const results=pd.getElementById('aia-results'); let selected=0; let filtered=[];
function draw(){{const q=input.value.toLowerCase();filtered=items.filter(x=>(x.name+' '+x.description+' '+x.keywords).toLowerCase().includes(q));selected=Math.min(selected,Math.max(0,filtered.length-1));results.innerHTML=filtered.slice(0,8).map((x,i)=>`<div class="aia-item ${{i===selected?'active':''}}" data-id="${{x.id}}"><b>${{x.name}}</b> <span class="aia-meta">${{x.badge}}</span><div>${{x.description}}</div><div class="aia-meta">${{x.destination}}</div></div>`).join('');[...results.children].forEach(e=>e.onclick=()=>go(e.dataset.id));}}
function openPalette(){{palette.style.display='block';input.value='';selected=0;draw();input.focus();}} function closePalette(){{palette.style.display='none';}}
function go(id){{const target=[...pd.querySelectorAll('button')].find(button=>button.innerText.trim()==='navigate::'+id);if(target){{closePalette();target.click();}}}}
pd.addEventListener('keydown',e=>{{const tag=(e.target.tagName||'').toLowerCase();const editable=['input','textarea','select'].includes(tag)||e.target.isContentEditable;const opened=palette.style.display==='block';if(opened&&e.key==='ArrowDown'){{e.preventDefault();selected=Math.min(selected+1,filtered.length-1);draw();return;}}if(opened&&e.key==='ArrowUp'){{e.preventDefault();selected=Math.max(0,selected-1);draw();return;}}if(opened&&e.key==='Enter'&&filtered[selected]){{e.preventDefault();go(filtered[selected].id);return;}}if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){{e.preventDefault();openPalette();}}else if(e.key==='/'&&!editable){{e.preventDefault();openPalette();}}else if(e.key==='Escape')closePalette();}},true);
input.addEventListener('input',()=>{{selected=0;draw();}});input.addEventListener('keydown',e=>{{if(e.key==='ArrowDown'){{selected=Math.min(selected+1,filtered.length-1);draw();}}if(e.key==='ArrowUp'){{selected=Math.max(0,selected-1);draw();}}if(e.key==='Enter'&&filtered[selected])go(filtered[selected].id);if(e.key==='Escape')closePalette();}});
</script>""",height=0)
