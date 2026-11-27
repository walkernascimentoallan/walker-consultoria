"""Gera o site da Walker Consultoria a partir dos arquivos em content/.
Rode: python3 build.py   (o resultado fica em public/)
O conteúdo é editado pelo painel /admin (Decap CMS)."""
import json, os, re, shutil, html, glob, datetime
import markdown, yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'public')
C = os.path.join(ROOT, 'content')
FONTE = os.path.join(ROOT, '_fonte')
CUR = ' aria-current="page"'
NL = '\n'
BS = '\\'
URL = 'https://walkerconsultoria.com.br/'


def J(name):
    return json.load(open(os.path.join(C, name), encoding='utf-8'))


def e(x):
    return html.escape(str(x or ''), quote=True)


def paras(x, cls=''):
    c = f' class="{cls}"' if cls else ''
    return ''.join(f'<p{c}>{e(p.strip())}</p>' for p in str(x or '').split('\n\n') if p.strip())


def li(items, key='texto'):
    return ''.join(f'<li>{e(i.get(key) if isinstance(i, dict) else i)}</li>' for i in (items or []))


def lk(u):
    u = (u or '').strip()
    return u


SITE = J('site.json')
IX = open(os.path.join(FONTE, 'index.html'), encoding='utf-8').read()
CU = open(os.path.join(FONTE, 'cursos.html'), encoding='utf-8').read()
FAVICON = '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png"><link rel="icon" type="image/png" sizes="64x64" href="/favicon-64.png">'
MARK = '<img class="mark" src="/marca-wn-128.png" alt="" width="46" height="46">'
GA = re.search(r'<script>\s*/\* Funil e contador.*?</script>', IX, re.S).group(0)
PROMO_JS = re.search(r"<script>\s*\(\(\)=>\{const st=document.getElementById\('promo'\).*?</script>", IX, re.S).group(0).replace('go(i+1),6000)', 'go(i+1),' + str(int(float(J('banners.json').get('tempo_segundos') or 9) * 1000)) + ')')
MAPA_SEC = re.search(r'<section class="band dark" id="mapa">.*?</section>', IX, re.S).group(0)
MAPA_SEC = re.sub(r'(<path [^>]*?)>\s*<title>([^<]*)</title>\s*</path>', r'\1 data-nome="\2" aria-label="\2"></path>', MAPA_SEC)
UF_TIP_JS = "(function(){var t=document.createElement('div');t.className='uf-tip';document.body.appendChild(t);document.querySelectorAll('#mapa path[data-nome]').forEach(function(p){p.addEventListener('mousemove',function(ev){t.textContent=p.getAttribute('data-nome');t.style.left=(ev.clientX+14)+'px';t.style.top=(ev.clientY+14)+'px';t.style.opacity='1'});p.addEventListener('mouseleave',function(){t.style.opacity='0'})})})();"

DATA_JS = re.search(r'<script>\s*\{\s*const svcs=.*?</script>', IX, re.S).group(0)
UFS_JS = re.search(r"/\* Estados da trajetória \*/.*?show\('mg'\);", DATA_JS, re.S).group(0)
FORM_JS = re.search(r"const form=document.getElementById\('form'\).*?ok.classList.add\('show'\);\n  \}\);", DATA_JS, re.S).group(0)
CONTATO_SEC = re.search(r'<section class="band dark" id="contato">.*?</section>', IX, re.S).group(0)
CHECK_FORM = re.search(r'<form class="wait" name="checklist".*?</form>', IX, re.S).group(0)
MODAL = re.search(r'<dialog id="cursoModal".*?</dialog>', open(os.path.join(FONTE, 'cursos_modal.html'), encoding='utf-8').read(), re.S).group(0)
MODAL_STYLE_JS = open(os.path.join(FONTE, 'cursos_modal.html'), encoding='utf-8').read().split('</dialog>', 1)[1]

WA_NUM = SITE['whatsapp']
WA = f'''<a class="wa-float" href="https://wa.me/{WA_NUM}?text=Ol%C3%A1%2C%20Prof.%20Walker%2C%20vim%20pelo%20site" target="_blank" rel="noopener" aria-label="Conversar no WhatsApp"><svg viewBox="0 0 32 32" width="28" height="28" aria-hidden="true"><path fill="#fff" d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.6c-2 0-3.9-.5-5.6-1.5l-.4-.2-3.9 1 1-3.8-.3-.4A10.6 10.6 0 1 1 16 26.6zm5.8-7.9c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2l-1 1.2c-.2.2-.4.2-.7.1a8.7 8.7 0 0 1-4.3-3.8c-.3-.6.3-.5 1-1.7.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6a1.2 1.2 0 0 0-.9.4 3.7 3.7 0 0 0-1.1 2.7 6.5 6.5 0 0 0 1.3 3.4 14.8 14.8 0 0 0 5.7 5c2.1.9 2.9 1 4 .8.6-.1 1.9-.8 2.2-1.5.3-.8.3-1.4.2-1.5l-.6-.4z"/></svg></a>
<style>.wa-float{{position:fixed;right:18px;bottom:18px;z-index:50;width:58px;height:58px;border-radius:50%;background:#1f8f4e;display:grid;place-items:center;box-shadow:0 8px 24px rgba(0,0,0,.25)}}.wa-float:hover{{background:#18763f}}</style>
<script>document.querySelector('.wa-float').addEventListener('click',()=>{{try{{gtag('event','clique_whatsapp',{{origem:'botao_flutuante'}})}}catch(e){{}}}})</script>'''

_NAV_PADRAO = [('sobre.html', 'Sobre'), ('publicacoes.html', 'Publicações'), ('onde-atuei.html', 'Onde atuei'), ('consultoria.html', 'Consultoria'), ('novo-marco.html', 'Novo Marco'),
       ('legislacao.html', 'Legislação'), ('cursos.html', 'Cursos'), ('eventos.html', 'Eventos'), ('radar.html', 'Radar')]
def _limpa(p):
    return (p or '').strip().lstrip('/')
try:
    NAV = []
    for a in J('menu.json').get('abas', []):
        if a.get('mostrar', True) is False:
            continue
        sub = [(_limpa(x['pagina']), x.get('nome') or x['pagina']) for x in (a.get('subitens') or []) if x.get('pagina')]
        if sub or a.get('pagina'):
            NAV.append({'nome': a.get('nome') or a.get('pagina'), 'pagina': _limpa(a.get('pagina')), 'sub': sub})
    NAV = NAV or [{'nome': t, 'pagina': h, 'sub': []} for h, t in _NAV_PADRAO]
except FileNotFoundError:
    NAV = [{'nome': t, 'pagina': h, 'sub': []} for h, t in _NAV_PADRAO]

NAME_FIX = [('Walker Soares do Nascimento', 'Prof. Walker Nascimento'), ('Prof. Me. Walker Nascimento', 'Prof. Walker Nascimento'),
            ('>Falar com Walker<', '>Falar com o Prof. Walker<'), ('Walker é um dos organizadores', 'O Prof. Walker é um dos organizadores'),
            ('Walker é coautor', 'o Prof. Walker é coautor'), ('onde Walker atuou', 'onde o Prof. Walker atuou')]

SERV = J('servicos.json')


def header(active):
    links = ''
    for i, it in enumerate(NAV):
        if not it['sub']:
            links += f'<a href="/{e(it["pagina"])}"{CUR if it["pagina"] == active else ""}>{e(it["nome"])}</a>'
            continue
        hit = next((h for h, t in it['sub'] if h.split('#')[0] == active), None)
        subs = ''.join(f'<a href="/{e(h)}"{CUR if h == hit else ""}>{e(t)}</a>' for h, t in it['sub'])
        links += (f'<div class="dd"><button class="dd-btn{" is-current" if hit else ""}" type="button" aria-expanded="false" aria-controls="dd{i}">{e(it["nome"])}'
                  f'<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>'
                  f'<div class="dd-menu" id="dd{i}">{subs}</div></div>')
    return f'''<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header><div class="bar">
<a class="brand" href="/" aria-label="Walker Consultoria Educacional, página inicial">{MARK}<span>Walker Consultoria<small>Educacional</small></span></a>
<button class="theme-btn" type="button" aria-label="Ativar modo noturno" title="Modo noturno"><svg class="ic-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" fill="currentColor"/></svg><svg class="ic-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.5" fill="currentColor"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></g></svg></button>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="mainnav"><span class="mb-ico" aria-hidden="true"></span><span class="mb-txt">Menu</span></button>
<nav id="mainnav" aria-label="Principal">{links}<a class="cta" href="/contato.html"{CUR if active == "contato.html" else ""}>Agendar conversa</a></nav>
</div></header>'''


def footer():
    return f'''<footer class="site-foot"><div class="wrap foot-grid">
<div class="foot-brand"><a class="brand" href="/" aria-label="Walker Consultoria Educacional, página inicial">{MARK}<span>Walker Consultoria<small>Educacional</small></span></a>
<p>{e(SITE['rodape'])}</p><p class="foot-loc">{e(SITE['cidade'])}</p></div>
<form class="foot-news" name="radar" method="POST" action="/obrigado.html?f=radar" data-netlify="true" netlify-honeypot="empresa-site">
<input type="hidden" name="form-name" value="radar"><p class="hp"><label>Não preencha: <input name="empresa-site" tabindex="-1" autocomplete="off"></label></p>
<b>Radar do Novo Marco</b><p>Portarias novas, prazos e o que muda na sua IES. Um e-mail a cada quinze dias.</p>
<div class="fn-row"><input name="nome" placeholder="Seu nome" required autocomplete="name" aria-label="Seu nome"><input name="email" type="email" placeholder="Seu e-mail" required autocomplete="email" aria-label="Seu e-mail"></div>
<label class="consent"><input type="checkbox" name="consentimento" value="sim" required> Autorizo o envio do boletim por e-mail, conforme a LGPD. Posso cancelar quando quiser.</label>
<button class="btn gold" type="submit">Assinar o boletim</button></form>
<div class="foot-col"><b>O site</b><a href="/sobre.html">Sobre o Prof. Walker</a><a href="/consultoria.html">Consultoria</a><a href="/novo-marco.html">Guia do Novo Marco</a><a href="/legislacao.html">Legislação do novo marco</a><a href="/novo-marco.html#diagnostico">Diagnóstico gratuito</a><a href="/onde-atuei.html">Onde atuei</a><a href="/publicacoes.html">Publicações</a><a href="/cursos.html">Cursos e e-book</a><a href="/eventos.html">Eventos</a><a href="/radar.html">Radar e biblioteca</a></div>
<div class="foot-col"><b>Contato</b><a href="https://wa.me/{WA_NUM}" target="_blank" rel="noopener">WhatsApp {e(SITE['whatsapp_texto'])}</a><a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a><a href="{e(SITE['linkedin'])}" target="_blank" rel="noopener">LinkedIn</a><a href="{e(SITE['instagram'])}" target="_blank" rel="noopener">Instagram</a><a href="/contato.html">Agendar conversa</a></div>
</div><div class="wrap foot-legal"><span>© {datetime.date.today().year} Walker Consultoria Educacional</span><a href="/politica-de-privacidade.html">Política de privacidade</a></div></footer>'''


_BREVO = (J('site.json').get('brevo_form') or '').strip()
_BREVO_JS = ("(()=>{const U=" + json.dumps(_BREVO) + ";if(!U)return;document.addEventListener('submit',e=>{const f=e.target;if(!f||!f.getAttribute('name'))return;const m=f.querySelector('input[type=email]');if(!m||!m.value||!f.checkValidity())return;const c=f.querySelector('input[type=checkbox][required]');if(c&&!c.checked)return;const d=new FormData();d.append('EMAIL',m.value.trim());const nm=f.querySelector('input[name=nome],input[name=name],input[name*=nome]');if(nm&&nm.value)d.append('NOME',nm.value.trim());d.append('email_address_check','');d.append('locale','pt');d.append('html_type','simple');try{fetch(U,{method:'POST',mode:'no-cors',body:d,keepalive:true})}catch(_){}},true)})();") if _BREVO else ''
PAGE_JS = '''<script>'''+_BREVO_JS+'''(()=>{document.addEventListener('click',e=>{const a=e.target.closest('a');if(a&&(a.classList.contains('cta')||/Agendar conversa/i.test(a.textContent))){try{gtag('event','clique_agendar',{pagina:location.pathname})}catch(_){}}},true)})();(()=>{const tb=document.querySelector('.theme-btn');if(!tb)return;const r=document.documentElement;const sync=()=>{const d=r.dataset.theme==='dark';tb.setAttribute('aria-pressed',d);tb.setAttribute('aria-label',d?'Ativar modo claro':'Ativar modo noturno');tb.title=d?'Modo claro':'Modo noturno'};sync();tb.addEventListener('click',()=>{r.dataset.theme=r.dataset.theme==='dark'?'light':'dark';try{localStorage.setItem('tema',r.dataset.theme)}catch(e){}sync()})})();(()=>{const b=document.querySelector('.menu-btn'),n=document.getElementById('mainnav');if(!b)return;
b.addEventListener('click',()=>{const o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)});
document.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&n.classList.contains('open')){n.classList.remove('open');b.setAttribute('aria-expanded','false');b.focus()}})})();
(()=>{const dds=[...document.querySelectorAll('#mainnav .dd')];const shut=x=>{dds.forEach(d=>{if(d!==x){d.classList.remove('open');d.querySelector('.dd-btn').setAttribute('aria-expanded','false')}})};
dds.forEach(d=>{const bt=d.querySelector('.dd-btn');bt.addEventListener('click',()=>{const o=d.classList.toggle('open');bt.setAttribute('aria-expanded',o);shut(d)});
d.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&d.classList.contains('open')){d.classList.remove('open');bt.setAttribute('aria-expanded','false');bt.focus()}});
d.addEventListener('focusout',ev=>{if(!d.contains(ev.relatedTarget)){d.classList.remove('open');bt.setAttribute('aria-expanded','false')}})});
document.addEventListener('click',ev=>{if(!ev.target.closest('#mainnav .dd'))shut(null)})})();</script>'''
COUNT_JS = f'''<script>(()=>{{const start=new Date('{SITE['prazo_inicio']}T00:00:00'),end=new Date('{SITE['prazo_fim']}T00:00:00'),now=new Date();const d=document.getElementById('days');if(!d)return;
const left=Math.max(0,Math.ceil((end-now)/864e5)),pct=Math.min(100,Math.max(0,(now-start)/(end-start)*100));
d.innerHTML=left.toLocaleString('pt-BR')+'<span>dias</span>';document.getElementById('now').style.left=pct+'%';
document.getElementById('rule').setAttribute('aria-label',Math.round(pct)+'% do prazo de transição já decorrido');
requestAnimationFrame(()=>requestAnimationFrame(()=>{{document.getElementById('fill').style.width=pct+'%'}}))}})();</script>'''
DEADLINE = re.search(r'<div class="deadline".*?</ul>\s*</div>\s*</div>', IX, re.S).group(0)

PAGES = []


def page(fname, title, desc, body, active=None, tail='', head='', noindex=False):
    canon = URL + ('' if fname == 'index.html' else fname)
    doc = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
{FAVICON}
{'<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{canon}">'}
<meta name="description" content="{e(desc)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Walker Consultoria Educacional"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}"><meta property="og:locale" content="pt_BR"><meta property="og:image" content="{URL}foto-walker.jpg"><meta name="twitter:card" content="summary_large_image">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Albert+Sans:wght@400;500;700;800&display=swap" rel="stylesheet">
<script>try{{var t=localStorage.getItem("tema");if(t==="dark"||t==="light")document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<link rel="stylesheet" href="/style.css">
{head}
</head>
<body>
{header(active)}
<main id="conteudo">
{body}
</main>
{footer()}
{GA}
{PAGE_JS}
{tail}
{WA}
</body>
</html>
'''
    for a, b in NAME_FIX:
        doc = doc.replace(a, b)
    doc = doc.replace('Prof. Prof. ', 'Prof. ').replace('index.html#contato', 'contato.html')
    _m = doc.find('<main')
    _n = [0]
    def _lazy(mt):
        _n[0] += 1
        tag = mt.group(0)
        if _n[0] <= 2 or 'loading=' in tag:
            return tag
        return tag[:-1].rstrip('/').rstrip() + ' loading="lazy" decoding="async">'
    doc = doc[:_m] + re.sub(r'<img\b[^>]*>', _lazy, doc[_m:])
    open(os.path.join(OUT, fname), 'w', encoding='utf-8').write(doc)
    if not noindex:
        PAGES.append(fname)


def hero(crumb, h1, lead, btns='', extra=''):
    c = ' / '.join(f'<a href="{h}">{t}</a>' if h else e(t) for h, t in crumb)
    return f'''<section class="page-hero"><div class="wrap"><p class="crumb"><a href="/">Início</a> / {c}</p><h1>{e(h1)}</h1>{paras(lead, 'lead')}{f'<div class="btns">{btns}</div>' if btns else ''}{extra}</div></section>'''


def btn(text, link, cls='gold'):
    if not (text and link):
        return ''
    ext = link.startswith('http')
    return f'<a class="btn {cls}" href="{e(link)}"{" target=\"_blank\" rel=\"noopener\"" if ext else ""}>{e(text)}</a>'


def icon(d):
    return f'<svg viewBox="0 0 48 48" width="48" height="48" aria-hidden="true"><rect width="48" height="48" rx="12" fill="#0e3b3d"/><path d="{e(d)}" fill="none" stroke="#c9a24a" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def cta_band(h):
    return f'<section class="band dark"><div class="wrap cta-band"><h2>{e(h)}</h2><div class="btns" style="margin:0"><a class="btn gold" href="/contato.html">Agendar conversa</a><a class="btn ghost" href="/novo-marco.html#diagnostico">Fazer o diagnóstico gratuito</a></div></div></section>'


def steps(items):
    return '<ol class="steps">' + ''.join(f'<li><h3>{e(i["titulo"])}</h3><p>{e(i["texto"])}</p></li>' for i in items) + '</ol>'


def svc_cards():
    return '<div class="cards">' + ''.join(f'<a class="card svc-card" href="/{e(s["slug"])}.html">{icon(s.get("icone", ""))}<h3>{e(s["titulo"])}</h3><p>{e(s["resumo"])}</p><span class="go">Ver o serviço</span></a>' for s in SERV['servicos']) + '</div>'


# ---------- artigos ----------
def load_articles():
    arts = []
    for f in sorted(glob.glob(os.path.join(C, 'radar', '*.md'))):
        raw = open(f, encoding='utf-8').read()
        m = re.match(r'---\n(.*?)\n---\n?(.*)', raw, re.S)
        fm = yaml.safe_load(m.group(1)) or {}
        body = m.group(2)
        slug = os.path.splitext(os.path.basename(f))[0]
        if fm.get('rascunho'):
            continue
        d = str(fm.get('data', ''))[:10]
        arts.append(dict(fm, slug='radar-' + slug, body=markdown.markdown(body, extensions=['tables', 'sane_lists']), data=d))
    arts.sort(key=lambda a: a['data'], reverse=True)
    return arts


def data_br(d):
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    try:
        y, m, dd = d.split('-')
        return f'{int(dd)} de {meses[int(m) - 1]} de {y}'
    except Exception:
        return d


ARTS = load_articles()


def art_cards(limit=3, exclude=None):
    lst = [a for a in ARTS if a['slug'] != exclude][:limit]
    return '<div class="cards">' + ''.join(f'<a class="card" href="/{a["slug"]}.html"><span class="meta">{e(a.get("tema", ""))} · {data_br(a["data"])}</span><h3>{e(a["titulo"])}</h3><p>{e(a.get("resumo", ""))}</p><span class="go">Ler o artigo</span></a>' for a in lst) + '</div>'


# ---------- banners ----------
def banners():
    bl = [b for b in J('banners.json')['banners'] if b.get('ativo', True)]
    out = []
    bgs = ['s1', 's2', 's3', 'ssv']
    for i, b in enumerate(bl):
        on = ' on' if i == 0 else ''
        lbl = f'{i + 1} de {len(bl)}'
        mod = b.get('modelo', 'capa')
        btns = btn(b.get('botao1_texto'), b.get('botao1_link')) + btn(b.get('botao2_texto'), b.get('botao2_link'), 'ghost')
        btns = f'<div class="btns" style="margin-top:18px">{btns}</div>' if btns else ''
        nums = b.get('numeros') or []
        facts = ('<div class="s0-facts">' + ''.join(f'<div><b>{e(n["valor"])}</b><span>{e(n["rotulo"])}</span></div>' for n in nums) + '</div>') if nums else ''
        text = f'<p class="kick">{e(b.get("selo"))}</p><h2 class="{"sh-title" if mod == "fundo" else "s0-name"}">{e(b.get("titulo"))}</h2><p class="txt">{e(b.get("texto"))}</p>{facts}{btns}'
        img = b.get('imagem') or ''
        if mod == 'fundo':
            out.append(f'<article class="slide sh big{on}" aria-roledescription="slide" aria-label="{lbl}"><img class="sh-bg" src="{e(img or "/universidade.svg")}" alt="" aria-hidden="true"><div class="sh-text">{text}</div></article>')
            continue
        if mod == 'foto':
            cap = f'<figcaption><b>{e(b.get("legenda_titulo"))}</b><span>{e(b.get("legenda_texto"))}</span></figcaption>' if b.get('legenda_titulo') else ''
            art = f'<figure class="s0-photo"><img src="{e(img)}" alt="{e(b.get("legenda_titulo") or b.get("titulo"))}" loading="lazy">{cap}</figure>'
            cls = 's0'
        elif mod == 'redonda':
            art = f'<img class="round" src="{e(img)}" alt="" loading="lazy">'
            cls = bgs[i % 3]
        elif mod == 'arte':
            art = f'<img class="plain" src="{e(img)}" alt="" loading="lazy">'
            cls = bgs[i % 3]
        elif mod == 'lista':
            its = b.get('itens') or []
            if any(x.get('link') for x in its):
                art = '<ul class="svc-chips">' + ''.join(f'<li><a href="{e(x.get("link") or "#")}">{e(x.get("texto"))}</a></li>' for x in its) + '</ul>'
                cls = 'ssv'
            else:
                art = f'<div class="doc" aria-hidden="true"><b>{e(b.get("legenda_titulo"))}</b>' + ''.join(f'<span>{e(x.get("texto"))}</span>' for x in its) + '</div>'
                cls = bgs[i % 3]
        else:  # capa
            art = f'<img src="{e(img)}" alt="{e(b.get("titulo"))}" loading="lazy">' if img else ''
            cls = bgs[i % 3]
        out.append(f'<article class="slide {cls}{on}" aria-roledescription="slide" aria-label="{lbl}"><div>{text}</div><div class="art">{art}</div></article>')
    return f'''<section class="promo promo-top" aria-roledescription="carrossel" aria-label="Destaques"><div class="wrap"><div class="stage" id="promo">{''.join(out)}</div>
<div class="ctrl"><button type="button" id="pPrev" aria-label="Banner anterior">&#8249;</button><div class="dots" id="pDots"></div><button type="button" id="pNext" aria-label="Próximo banner">&#8250;</button><button type="button" id="pPause" aria-label="Pausar banners">&#10074;&#10074;</button></div></div></section>'''


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, 'static'), OUT)
    css = open(os.path.join(FONTE, 'style.css'), encoding='utf-8').read() + EXTRA_CSS
    open(os.path.join(OUT, 'style.css'), 'w', encoding='utf-8').write(css)
    ini = J('inicio.json')
    EV = J('eventos.json')
    NM = J('novo_marco.json')
    SO = J('sobre.json')
    CUR = J('cursos.json')
    LG = J('legislacao.json')
    DG = J('diagnostico.json')

    # ----- início -----
    nums = '<section class="numbers"><div class="wrap num-grid">' + ''.join(f'<div><b>{e(n["valor"])}</b><span>{e(n["rotulo"])}</span></div>' for n in ini['numeros']) + '</div></section>'
    ev = next((x for x in EV['eventos'] if x.get('ativo', True)), None)
    agenda = ''
    if ev:
        agenda = f'''<section class="band tint"><div class="wrap agenda-home"><div><p class="eyebrow-num">Próximo evento · {e(ev["data"])}</p><h2>{e(ev["titulo"])}</h2><p class="soft" style="margin-top:12px">{e(ev["texto"])}</p></div>
<div class="btns" style="margin:0"><a class="btn gold" href="/eventos.html">{"Fazer inscrição" if ev.get("link_inscricao") else "Quero ser avisado"}</a><a class="btn line" href="/eventos.html#palestras">Palestras e workshops</a></div></div></section>'''
    cursos_cards = '<div class="cards">' + ''.join(
        f'<a class="card" href="/cursos.html#{e(c["id"])}"><span class="meta">{e(c["selo"])}{" · " + e(c["preco"]) if c.get("preco") else ""}</span><h3>{e(c["titulo"])}</h3><p>{e(c["texto"])}</p><span class="go">{"Conhecer" if c.get("status") == "venda" else "Entrar na lista de espera"}</span></a>'
        for c in CUR['cursos'][:3]) + '</div>'
    badges = '<ul class="badges">' + ''.join(f'<li><b>{e(x["titulo"])}</b><span>{e(x["texto"])}</span></li>' for x in ini['academia']) + '</ul>'
    body = f'''{banners()}
<section class="band dark deadline-band"><div class="wrap">{DEADLINE}</div></section>
{nums}
<section class="band tint"><div class="wrap"><div class="sec-head"><div><h2>{e(ini["consultoria_titulo"])}</h2><p class="soft">{e(ini["consultoria_texto"])}</p></div><a class="more-link" href="/consultoria.html">Como o trabalho acontece</a></div>{svc_cards()}</div></section>
<section class="band"><div class="wrap"><div class="sec-head"><div><h2>{e(ini["radar_titulo"])}</h2><p class="soft">{e(ini["radar_texto"])}</p></div><a class="more-link" href="/radar.html">Ver todos os artigos</a></div>{art_cards()}</div></section>
<section class="band"><div class="wrap who"><img src="{e(ini["quem_foto"])}" alt="Prof. Walker Nascimento" width="320" height="320" loading="lazy"><div><h2>{e(ini["quem_titulo"])}</h2><div class="soft" style="margin-top:14px">{paras(ini["quem_texto"])}</div>
<div class="btns"><a class="btn gold" href="/sobre.html">Conhecer a trajetória</a><a class="btn line" href="/sobre.html#livros">Ver os livros</a></div></div></div></section>
{agenda}
<section class="band"><div class="wrap"><div class="sec-head"><div><h2>{e(ini["cursos_titulo"])}</h2><p class="soft">{e(ini["cursos_texto"])}</p></div><a class="more-link" href="/cursos.html">Ver todos os cursos</a></div>{cursos_cards}</div></section>
<section class="band"><div class="wrap"><div class="sec-head"><div><h2>{e(ini["academia_titulo"])}</h2><p class="soft">{e(ini["academia_texto"])}</p></div></div>{badges}</div></section>
{cta_band(ini["chamada_final"])}'''
    page('index.html', 'Walker Consultoria Educacional | Novo marco regulatório do ensino superior',
         'Consultoria do Prof. Walker Nascimento para faculdades, centros universitários e universidades se adequarem ao novo marco regulatório (Decreto nº 12.456/2025).',
         body, tail=COUNT_JS + PROMO_JS)

    # ----- consultoria -----
    b = hero([(None, 'Consultoria')], 'Consultoria em regulação e gestão do ensino superior', 'Cada frente pode ser contratada sozinha ou como parte de um plano de adequação completo, com cronograma alinhado ao calendário do e-MEC.',
             '<a class="btn gold" href="/contato.html">Agendar conversa</a><a class="btn ghost" href="/novo-marco.html#diagnostico">Fazer o diagnóstico gratuito</a>')
    b += f'''<section class="band"><div class="wrap"><div class="sec-head"><div><h2>Serviços</h2></div></div>{svc_cards()}</div></section>
<section class="band tint"><div class="wrap"><div class="sec-head"><div><h2>Como o trabalho acontece</h2><p class="soft">Um percurso curto e documentado. Cada etapa termina com uma entrega que a direção pode levar ao conselho, à mantenedora ou ao procurador institucional.</p></div></div>{steps(SERV["metodo"])}</div></section>
<section class="band"><div class="wrap for-who"><div><h2>Para quem é</h2><ul class="checks">{li(SERV["para_quem"])}</ul></div><div><h2>Como é cobrado</h2><div class="soft">{paras(SERV["como_cobra"])}</div></div></div></section>{cta_band("Vamos olhar a sua instituição?")}'''
    page('consultoria.html', 'Consultoria | Walker Consultoria Educacional', 'Diagnóstico de conformidade, reenquadramento de cursos, PPCs, modelo acadêmico, polos e preparação para avaliação do INEP.', b, active='consultoria.html')
    for s in SERV['servicos']:
        others = ''.join(f'<li><a href="/{e(o["slug"])}.html">{e(o["titulo"])}</a></li>' for o in SERV['servicos'] if o is not s)
        b = hero([('/consultoria.html', 'Consultoria'), (None, s['titulo'])], s['titulo'], s['abertura'], '<a class="btn gold" href="/contato.html">Conversar sobre este serviço</a>')
        b += f'''<section class="band"><div class="wrap svc-detail"><div class="svc-main">
<div class="svc-block"><h2>Quando faz sentido</h2><ul class="checks">{li(s["quando"])}</ul></div>
<div class="svc-block"><h2>O que eu faço</h2><ul class="checks">{li(s["faco"])}</ul></div>
<div class="svc-block"><h2>O que você recebe</h2><ul class="deliver">{li(s["entregas"])}</ul></div></div>
<aside class="svc-side"><div class="side-box"><b>Conversa inicial sem custo</b><p>Em 30 minutos, entendo o cenário e digo com franqueza se este serviço resolve o seu caso.</p><a class="btn gold" href="/contato.html">Agendar conversa</a></div>
<div class="side-box plain"><b>Outros serviços</b><ul>{others}</ul></div></aside></div></section>
<section class="band tint"><div class="wrap"><div class="sec-head"><div><h2>Como o trabalho acontece</h2></div></div>{steps(SERV["metodo"])}</div></section>{cta_band("Vamos olhar a sua instituição?")}'''
        page(s['slug'] + '.html', f'{s["titulo"]} | Walker Consultoria Educacional', s['resumo'], b, active='consultoria.html')

    # ----- novo marco -----
    qs = ''.join(f'''<fieldset class="dq" id="q{i + 1}"><legend><span class="dq-n">{i + 1}</span>{e(q["texto"])}</legend>
<div class="dq-opts"><label><input type="radio" name="q{i}" value="2" required> Sim</label><label><input type="radio" name="q{i}" value="1"> Em parte</label><label><input type="radio" name="q{i}" value="0"> Não</label></div></fieldset>''' for i, q in enumerate(DG['perguntas']))
    diag = f'''<section class="band tint" id="diagnostico"><div class="wrap diag-wrap"><div class="diag-intro"><p class="eyebrow-num">Diagnóstico Walker do Novo Marco</p><h2>{e(DG["titulo"])}</h2><p class="soft" style="margin-top:12px">{e(DG["texto"])}</p></div>
<form id="diagForm" class="diag" novalidate>{qs}<p class="ok" id="diagMsg" role="status"></p><button class="btn gold" type="submit">Ver meu resultado</button></form>
<div id="diagResult" class="diag-result" hidden tabindex="-1"><div class="dr-top"><div class="dr-score"><b id="drPct">0%</b><span>de prontidão</span></div><div><p class="dr-level" id="drLevel"></p><p id="drText" class="soft"></p></div></div>
<div class="dr-bar"><div id="drFill"></div></div><h3>Pontos que pedem atenção</h3><ul id="drGaps" class="gaps"></ul>
<form class="wait dr-lead" name="diagnostico" method="POST" action="/obrigado.html?f=diagnostico" data-netlify="true" netlify-honeypot="empresa-site"><input type="hidden" name="form-name" value="diagnostico"><p class="hp"><label>Não preencha: <input name="empresa-site"></label></p>
<input type="hidden" name="nota" id="drNota"><input type="hidden" name="respostas" id="drResp"><b>Quer que eu analise o seu resultado?</b><p>Eu leio as suas respostas e devolvo, sem custo, as três prioridades para a sua instituição.</p>
<div class="frow"><input name="nome" placeholder="Seu nome" required autocomplete="name" aria-label="Seu nome"><input name="whatsapp" placeholder="WhatsApp com DDD" required autocomplete="tel" aria-label="WhatsApp com DDD"></div>
<div class="frow"><input name="email" type="email" placeholder="Seu e-mail" required autocomplete="email" aria-label="Seu e-mail"><input name="instituicao" placeholder="Instituição" required aria-label="Instituição"></div>
<label class="consent"><input type="checkbox" name="consentimento" value="sim" required> Autorizo o contato por WhatsApp e e-mail sobre este diagnóstico, conforme a LGPD.</label><button class="btn gold" type="submit">Receber a análise</button><p class="nocomp">Sem compromisso de contratação.</p></form>
<button type="button" class="linkbtn" id="drAgain">Refazer o diagnóstico</button></div></div></section>'''
    Q = json.dumps([q['texto'] for q in DG['perguntas']], ensure_ascii=False)
    diag_js = '''<script>(()=>{const f=document.getElementById('diagForm');if(!f)return;const Q=''' + Q + ''';const r=document.getElementById('diagResult'),msg=document.getElementById('diagMsg');
f.addEventListener('submit',ev=>{ev.preventDefault();const v=[];for(let i=0;i<Q.length;i++){const c=f.querySelector('input[name=q'+i+']:checked');if(!c){msg.textContent='Falta responder a pergunta '+(i+1)+'.';msg.classList.add('show');f.querySelector('input[name=q'+i+']').focus();return}v.push(+c.value)}
msg.classList.remove('show');const pct=Math.round(v.reduce((a,b)=>a+b,0)/(Q.length*2)*100);let lvl,txt;
if(pct>=80){lvl='Bem encaminhada';txt='A base está feita. O risco agora é de detalhe: documentos que não conversam com a prática e polos que não aguentam uma visita.'}else if(pct>=50){lvl='Atenção';txt='Parte do caminho foi feita, mas há frentes abertas que costumam travar na reta final. Vale priorizar agora.'}else{lvl='Risco alto';txt='Há decisões importantes ainda por tomar. Com o prazo correndo, o melhor momento para montar o plano é este.'}
document.getElementById('drPct').textContent=pct+'%';document.getElementById('drLevel').textContent=lvl;document.getElementById('drText').textContent=txt;r.dataset.level=pct>=80?'ok':pct>=50?'mid':'low';
const gaps=Q.map((q,i)=>v[i]<2?'<li><span class="g-tag">'+(v[i]===1?'Em parte':'Não')+'</span>'+q.replace(/</g,'&lt;')+'</li>':'').join('');document.getElementById('drGaps').innerHTML=gaps||'<li>Nenhum ponto em aberto nas respostas. Parabéns à equipe.</li>';
document.getElementById('drNota').value=pct+'% ('+lvl+')';document.getElementById('drResp').value=Q.map((q,i)=>(i+1)+': '+['Não','Em parte','Sim'][v[i]]).join(' | ');
f.hidden=true;r.hidden=false;requestAnimationFrame(()=>{document.getElementById('drFill').style.width=pct+'%'});r.focus();r.scrollIntoView({behavior:'smooth',block:'start'});try{gtag('event','diagnostico_concluido',{nota:pct})}catch(e){}});
document.getElementById('drAgain').addEventListener('click',()=>{f.reset();r.hidden=true;f.hidden=false;document.getElementById('drFill').style.width='0';f.scrollIntoView({behavior:'smooth'})});})();</script>'''
    changes = '<div class="changes">' + ''.join(f'<article><h3>{e(c["titulo"])}</h3><p>{e(c["texto"])}</p></article>' for c in NM['mudancas']) + '</div>'
    fmts = '<div class="fmt-grid">' + ''.join(f'<article><h3>{e(x["titulo"])}</h3><p class="big">{e(x["numero"])}</p><p>{e(x["texto"])}</p></article>' for x in NM['formatos']) + '</div>'
    check = CHECK_FORM
    faq = ''.join(f'<details><summary>{e(q["pergunta"])}</summary><p>{e(q["resposta"])}</p></details>' for q in NM['faq'])
    b = hero([(None, 'Novo Marco')], NM['titulo'], NM['texto'], '<a class="btn gold" href="#diagnostico">Fazer o diagnóstico</a><a class="btn ghost" href="#checklist">Baixar o checklist</a>', DEADLINE)
    b += f'''<section class="band"><div class="wrap"><div class="sec-head"><div><h2>{e(NM["muda_titulo"])}</h2><p class="soft">{e(NM["muda_texto"])}</p></div><a class="more-link" href="/legislacao.html">Ver toda a legislação</a></div>{changes}</div></section>
<section class="band"><div class="wrap"><div class="sec-head"><div><h2>{e(NM["formatos_titulo"])}</h2><p class="soft">{e(NM["formatos_texto"])}</p></div></div>{fmts}<p class="sources" style="margin-top:18px">{e(NM["formatos_nota"])}</p></div></section>
{diag}
<section class="band" id="checklist"><div class="wrap lead-box"><div><p class="who-line" style="color:var(--goldtx)">Material gratuito</p><h2>{e(NM["checklist_titulo"])}</h2><p class="soft" style="margin-top:14px">{e(NM["checklist_texto"])}</p></div>{check}</div></section>
<section class="band tint"><div class="wrap"><div class="sec-head"><div><h2>Para aprofundar</h2></div><a class="more-link" href="/radar.html">Todos os artigos</a></div>{art_cards()}</div></section>
<section class="band" id="duvidas"><div class="wrap faq"><h2 style="margin-bottom:28px">Dúvidas frequentes</h2>{faq}</div></section>{cta_band("Vamos olhar a sua instituição?")}'''
    page('novo-marco.html', 'Guia do Novo Marco Regulatório (Decreto 12.456/2025) | Walker Consultoria',
         'O essencial do Decreto nº 12.456/2025: formatos de oferta, cursos vedados em EAD, mediador pedagógico, polos e o prazo de maio de 2027. Com diagnóstico gratuito.',
         b, active='novo-marco.html', tail=COUNT_JS + diag_js)

    # ----- legislação -----
    years = []
    for n in LG['normas']:
        if n['ano'] not in years:
            years.append(n['ano'])
    b = hero([('/novo-marco.html', 'Novo Marco'), (None, 'Legislação')], 'Legislação do novo marco regulatório',
             'Todas as normas do novo marco da educação a distância na graduação, em ordem, com um resumo de cada uma e o link para o texto oficial.',
             '<a class="btn gold" href="#normas">Ver as normas</a><a class="btn ghost" href="/novo-marco.html#diagnostico">Fazer o diagnóstico</a>')
    b += f'<section class="band" id="normas"><div class="wrap"><p class="nm-upd">Atualizado em {e(LG["atualizado_em"])}. Saiu norma nova? <a href="/contato.html">Me avise</a>.</p>'
    for y in years:
        b += f'<h2 class="nm-year">{e(y)}</h2><div class="norms">' + ''.join(
            f'''<article class="norm"><div class="nm-date"><b>{e(n["data"])}</b><span>{e(n["tipo"])}</span></div><div class="nm-body"><h3>{e(n["numero"])}<span>{e(n["assunto"])}</span></h3><p>{e(n["resumo"])}</p>{f'<p class="nm-rel">{e(n["relacao"])}</p>' if n.get("relacao") else ''}{f'<a class="btn line nm-btn" href="{e(n["link"])}" target="_blank" rel="noopener">Ler na fonte ({e(n.get("fonte") or "oficial")})</a>' if n.get("link") else ''}</div></article>'''
            for n in LG['normas'] if n['ano'] == y) + '</div>'
    b += '<p class="note" style="margin-top:36px">Os resumos são informativos e não substituem a leitura do texto oficial nem a análise do caso da sua instituição.</p></div></section>'
    b += f'<section class="band tint"><div class="wrap"><div class="sec-head"><div><h2>O que essas normas mudam na prática</h2></div><a class="more-link" href="/radar.html">Todos os artigos</a></div>{art_cards()}</div></section>' + cta_band('Vamos olhar a sua instituição?')
    page('legislacao.html', 'Legislação do novo marco regulatório (Decreto 12.456 e portarias) | Walker Consultoria',
         'Decreto nº 12.456/2025 e portarias do MEC: resumo de cada norma do novo marco da EAD e link para o texto oficial.', b, active='legislacao.html')

    # ----- radar -----
    allcards = art_cards(limit=999)
    biblio = '''<section class="band" id="biblioteca"><div class="wrap"><div class="head"><h2>Biblioteca: leituras recomendadas</h2><p class="soft">Textos e livros em PDF que indico para gestores do ensino superior. Clique no arquivo para ler ou baixar.</p></div>
<div class="lib"><iframe src="https://drive.google.com/embeddedfolderview?id=1e4q8lFrM0XI9UOtewbYyW3W5x3-MIeGa#list" title="Leituras recomendadas em PDF" loading="lazy"></iframe></div>
<p class="sample">Se a lista não aparecer, <a href="https://drive.google.com/drive/folders/1e4q8lFrM0XI9UOtewbYyW3W5x3-MIeGa" target="_blank" rel="noopener">abra a biblioteca no Google Drive</a>.</p></div></section>'''
    b = hero([(None, 'Radar')], 'Radar do Novo Marco', 'Análises curtas sobre o Decreto nº 12.456/2025, as portarias do MEC e o que elas mudam na gestão da sua instituição.', '<a class="btn gold" href="#assinar">Assinar o boletim</a>')
    b += f'''<section class="band"><div class="wrap"><div class="sec-head"><div><h2>Artigos</h2></div></div>{allcards}</div></section>
<section class="band tint" id="assinar"><div class="wrap lead-box"><div><p class="eyebrow-num">Boletim quinzenal</p><h2>Receba o Radar no seu e-mail</h2><p class="soft" style="margin-top:12px">Portarias novas, prazos que se aproximam e o que cada mudança significa para a sua IES. Um e-mail a cada quinze dias, sem spam.</p></div>
<form class="wait" name="radar" method="POST" action="/obrigado.html?f=radar" data-netlify="true" netlify-honeypot="empresa-site"><input type="hidden" name="form-name" value="radar"><p class="hp"><label>Não preencha: <input name="empresa-site"></label></p>
<b>Assinar o boletim</b><input name="nome" placeholder="Seu nome" required autocomplete="name" aria-label="Seu nome"><input name="email" type="email" placeholder="Seu e-mail" required autocomplete="email" aria-label="Seu e-mail">
<label class="consent"><input type="checkbox" name="consentimento" value="sim" required> Autorizo o envio do boletim por e-mail, conforme a LGPD. Posso cancelar quando quiser.</label><button class="btn gold" type="submit">Assinar</button></form></div></section>
{biblio}{cta_band("Vamos olhar a sua instituição?")}'''
    page('radar.html', 'Radar do Novo Marco | Walker Consultoria Educacional', 'Artigos e boletim quinzenal sobre o novo marco regulatório da educação superior, com biblioteca de leituras recomendadas.', b, active='radar.html')
    for a in ARTS:
        fontes = a.get('fontes') or []
        srcl = ''.join(f'<li><a href="{e(f.get("link"))}" target="_blank" rel="noopener">{e(f.get("titulo"))}</a></li>' for f in fontes)
        b = f'''<article><section class="page-hero art-hero"><div class="wrap"><p class="crumb"><a href="/">Início</a> / <a href="/radar.html">Radar</a> / {e(a.get("tema", ""))}</p>
<h1>{e(a["titulo"])}</h1><p class="lead">{e(a.get("resumo", ""))}</p><p class="byline"><img src="/foto-walker-quadrada.jpg" alt="" width="44" height="44"><span><b>{e(a.get("autor") or "Prof. Walker Nascimento")}</b>{data_br(a["data"])}</span></p></div></section>
<section class="band"><div class="wrap"><div class="prose">{f'<img class="art-cover" src="{e(a["imagem"])}" alt="">' if a.get("imagem") else ''}{a["body"]}
<p class="note">Este texto é informativo e não substitui a leitura das normas nem a análise do caso concreto da sua instituição.</p>
{f'<h2 style="font-size:20px">Fontes</h2><ul class="sources">{srcl}</ul>' if srcl else ''}
<div class="art-cta"><b>Quer saber como isso se aplica à sua IES?</b><p>Faça o diagnóstico gratuito ou agende uma conversa de 30 minutos.</p><div class="btns" style="margin:0"><a class="btn gold" href="/novo-marco.html#diagnostico">Fazer o diagnóstico</a><a class="btn line" href="/contato.html">Agendar conversa</a></div></div>
</div></div></section></article>
<section class="band tint"><div class="wrap"><div class="sec-head"><div><h2>Leia também</h2></div><a class="more-link" href="/radar.html">Todos os artigos</a></div>{art_cards(3, a["slug"])}</div></section>'''
        ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": a['titulo'], "description": a.get('resumo', ''), "author": {"@type": "Person", "name": "Walker Nascimento"}, "datePublished": a['data'], "inLanguage": "pt-BR"}, ensure_ascii=False)
        page(a['slug'] + '.html', f'{a["titulo"]} | Radar do Novo Marco', a.get('resumo', ''), b, active='radar.html', head=f'<script type="application/ld+json">{ld}</script>')

    # ----- eventos -----
    evs = [x for x in EV['eventos'] if x.get('ativo', True)]
    evhtml = ''.join(f'''<article class="event"><div class="ev-date"><b>{e(x["data"])}</b><span>{e(x.get("data_detalhe"))}</span></div><div><span class="meta">{e(x.get("tipo"))}</span><h3>{e(x["titulo"])}</h3><p class="soft">{e(x["texto"])}</p><ul class="checks">{li(x.get("itens"))}</ul>
{f'<div class="btns"><a class="btn gold" href="{e(x["link_inscricao"])}" target="_blank" rel="noopener">Fazer inscrição</a></div>' if x.get("link_inscricao") else ''}</div></article>''' for x in evs) or '<p class="soft">Nenhum evento marcado no momento. Cadastre-se abaixo para receber o aviso do próximo.</p>'
    pal = '<div class="cards">' + ''.join(f'<div class="card"><h3>{e(p["titulo"])}</h3><p>{e(p["texto"])}</p></div>' for p in EV['palestras']) + '</div>'
    b = hero([(None, 'Eventos')], 'Agenda de eventos', 'Lives abertas, palestras e workshops sobre o novo marco regulatório e a gestão do ensino superior.', '<a class="btn gold" href="#aviso">Quero ser avisado</a><a class="btn ghost" href="#palestras">Levar para a minha IES</a>')
    b += f'''<section class="band"><div class="wrap"><div class="sec-head"><div><h2>Próximos eventos</h2></div></div><div class="ev-list">{evhtml}</div></div></section>
<section class="band tint" id="aviso"><div class="wrap lead-box"><div><h2>Receba o aviso dos próximos eventos</h2><p class="soft" style="margin-top:12px">Assim que uma data for definida, você recebe o convite com o link de inscrição.</p></div>
<form class="wait" name="eventos" method="POST" action="/obrigado.html?f=eventos" data-netlify="true" netlify-honeypot="empresa-site"><input type="hidden" name="form-name" value="eventos"><p class="hp"><label>Não preencha: <input name="empresa-site"></label></p>
<b>Quero ser avisado</b><input name="nome" placeholder="Seu nome" required autocomplete="name" aria-label="Seu nome"><input name="email" type="email" placeholder="Seu e-mail" required autocomplete="email" aria-label="Seu e-mail"><input name="whatsapp" placeholder="WhatsApp com DDD" autocomplete="tel" aria-label="WhatsApp com DDD"><input name="instituicao" placeholder="Instituição" aria-label="Instituição">
<label class="consent"><input type="checkbox" name="consentimento" value="sim" required> Autorizo o contato por e-mail e WhatsApp sobre eventos, conforme a LGPD.</label><button class="btn gold" type="submit">Quero ser avisado</button></form></div></section>
<section class="band" id="palestras"><div class="wrap"><div class="sec-head"><div><h2>Palestras e workshops na sua instituição</h2><p class="soft">Formatos fechados para equipes de direção, coordenação, NDE, polos e conselhos.</p></div></div>{pal}<div class="btns" style="margin-top:26px"><a class="btn gold" href="/contato.html">Pedir uma proposta</a></div></div></section>'''
    page('eventos.html', 'Eventos e palestras | Walker Consultoria Educacional', 'Lives gratuitas, palestras e workshops do Prof. Walker Nascimento sobre o novo marco regulatório da educação superior.', b, active='eventos.html')

    # ----- contato -----
    ct = CONTATO_SEC.replace('<section class="band dark" id="contato">', '<section class="band" id="contato">').replace('<h2>Vamos olhar a sua instituição</h2>', '<h2>Escreva para mim</h2>')
    ct = ct.replace('<li><a href="#checklist">Checklist gratuito do novo marco</a><small>PDF para baixar</small></li>', '<li><a href="/novo-marco.html#diagnostico">Diagnóstico gratuito do novo marco</a><small>Resultado na hora</small></li>')
    ct = ct.replace('https://wa.me/5531984054927', f'https://wa.me/{WA_NUM}').replace('WhatsApp (31) 98405-4927', f'WhatsApp {e(SITE["whatsapp_texto"])}')
    b = hero([(None, 'Contato')], 'Vamos olhar a sua instituição', 'A primeira conversa é sem custo. Serve para entender o cenário e dizer com franqueza se faz sentido trabalharmos juntos.') + ct
    b += '''<section class="band tint"><div class="wrap"><div class="sec-head"><div><h2>O que acontece depois</h2></div></div><ol class="steps"><li><h3>Você envia a mensagem</h3><p>Pelo formulário ou direto no WhatsApp, com o essencial do seu cenário.</p></li><li><h3>Eu respondo</h3><p>Em dias úteis, para marcar uma conversa de 30 minutos por vídeo.</p></li><li><h3>Conversamos</h3><p>Entendo a situação dos cursos, polos e documentos e aponto as prioridades.</p></li><li><h3>Proposta</h3><p>Se fizer sentido, você recebe escopo, prazo e valor fechados.</p></li></ol></div></section>'''
    page('contato.html', 'Contato | Walker Consultoria Educacional', 'Agende uma conversa sem custo com o Prof. Walker Nascimento sobre a adequação da sua instituição ao novo marco regulatório.', b, active='contato.html',
         tail='<script>{' + FORM_JS.replace('5531984054927', WA_NUM) + '}</script>')

    # ----- sobre -----
    S = SO
    facts = '<div class="facts">' + ''.join(f'<div><b>{e(n["valor"])}</b><span>{e(n["rotulo"])}</span></div>' for n in S['numeros']) + '</div>'
    form = ''.join(f'<li{" class=\"top\"" if i == 0 else ""}>{f"<span class=\"yr\">{e(f["periodo"])}</span>" if f.get("periodo") else ""}<b>{e(f["titulo"])}</b>{f"<span>{e(f["texto"])}</span>" if f.get("texto") else ""}</li>' for i, f in enumerate(S['formacao']))
    pesq = ''.join(f'<div class="role"><b>{e(p["titulo"])}</b><span>{e(p["texto"])}</span></div>' for p in S['pesquisa'])
    car = ''.join(f'<li>{f"<span class=\"yr\">{e(c["periodo"])}</span>" if c.get("periodo") else ""}<b>{e(c["instituicao"])}</b><p>{e(c["texto"])}</p>{f"<small>{e(c["local"])}</small>" if c.get("local") else ""}</li>' for c in S['carreira'])
    award_svg = '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="13" r="9" fill="none" stroke="#c9a24a" stroke-width="2.4"/><path d="M11 20l-3 9 8-4 8 4-3-9" fill="none" stroke="#c9a24a" stroke-width="2.4" stroke-linejoin="round"/></svg>'
    aw = ''.join(f'<div class="award">{award_svg}<div><b>{e(a["titulo"])}</b><p>{e(a["texto"])}</p></div></div>' for a in S['reconhecimentos'])
    books = ''.join(f'''<article class="book"><div class="cover has-img"><img src="{e(bk["capa"])}" alt="Capa do livro {e(bk["titulo"])}"></div><div><b>{e(bk["titulo"])}</b><br><span>{e(bk.get("subtitulo"))}</span><br><span class="meta">{e(bk.get("detalhes"))}</span>{f'<br><a class="btn gold buy" href="{e(bk.get("link_compra") or bk.get("link"))}" target="_blank" rel="noopener">{e(bk.get("texto_botao") or "Saiba mais")}</a>' if (bk.get("link_compra") or bk.get("link")) else ''}</div></article>''' for bk in S['livros'])
    nb = S.get('proximo_livro') or {}
    nbh = f'''<article class="next-book"><img src="{e(nb.get("capa"))}" alt="Capa do livro {e(nb.get("titulo"))}" width="600" height="900"><div><p class="nb-tag">{e(nb.get("selo"))}</p><h3>{e(nb.get("titulo"))}</h3><p class="nb-sub">{e(nb.get("subtitulo"))}</p><p>{e(nb.get("texto"))}</p></div></article>''' if nb.get('ativo') else ''
    fd = S.get('foto_destaque') or {}
    fdh = f'<figure class="launch"><img src="{e(fd.get("imagem"))}" alt="{e(fd.get("titulo"))}" width="800" height="720"><figcaption><b>{e(fd.get("titulo"))}</b><span>{e(fd.get("texto"))}</span></figcaption></figure>' if fd.get('ativo') else ''
    mapa = MAPA_SEC[:MAPA_SEC.rfind('</section>')] + '<p class="wrap" style="font-size:13px;color:#9fc1be;margin-top:24px">Mapa: <a href="https://github.com/VictorCazanave/svg-maps" target="_blank" rel="noopener" style="color:#cfe0de">SVG Maps</a>, licença CC BY 4.0</p></section>'
    b = f'''<section class="band dark"><div class="wrap hero"><div><p class="who-line">{e(S["selo"])}</p><h1>{e(S["nome"])}</h1><p class="lead">{e(S["texto"])}</p>{facts}
<div class="btns"><a class="btn gold" href="/contato.html">Falar com o Prof. Walker</a><a class="btn ghost" href="{e(SITE["lattes"])}" target="_blank" rel="noopener">Currículo Lattes</a></div></div>
<figure class="portrait" style="margin:0"><div class="frame"></div><div class="photo"><img src="{e(S["foto"])}" alt="Prof. Walker Nascimento" width="720" height="900"></div><figcaption class="tag"><b>{e(S["foto_legenda_titulo"])}</b><span>{e(S["foto_legenda_texto"])}</span></figcaption></figure></div></section>
<section class="band" id="formacao"><div class="wrap titles"><div><h2 style="margin-bottom:28px">Formação acadêmica</h2><ul class="tl">{form}</ul></div><div><h2 style="margin-bottom:28px">Pesquisa</h2><div class="roles">{pesq}</div></div></div></section>
<section class="band tint" id="carreira"><div class="wrap"><div class="head"><h2>{e(S["carreira_titulo"])}</h2><p class="soft">{e(S["carreira_texto"])}</p></div><ol class="career">{car}</ol></div></section>
<section class="band tint" id="reconhecimentos" style="padding-top:0"><div class="wrap"><div class="head"><h2>{e(S["reconhecimentos_titulo"])}</h2><p class="soft">{e(S["reconhecimentos_texto"])}</p></div><div class="awards">{aw}</div>
<div class="btns" style="margin-top:28px"><a class="btn gold" href="{e(SITE["lattes"])}" target="_blank" rel="noopener">Ver o Currículo Lattes completo</a><a class="btn line" href="/onde-atuei.html">Ver o mapa de onde atuei</a></div></div></section>
<section class="band" id="livros"><div class="wrap"><div class="head"><h2>{e(S["livros_titulo"])}</h2><p class="soft">{e(S["livros_texto"])}</p></div>{nbh}<div class="books">{books}</div><div class="btns" style="margin-top:28px"><a class="btn line" href="/publicacoes.html">Ver todas as publicações</a></div>{fdh}</div></section>
{mapa}
<section class="band dark"><div class="wrap closing"><h2>{e(S["chamada_final"])}</h2><div class="btns" style="margin-top:0"><a class="btn gold" href="/contato.html">Agendar diagnóstico</a><a class="btn ghost" href="/onde-atuei.html">Ver onde já atuei</a></div></div></section>'''
    page('sobre.html', 'Prof. Walker Nascimento, trajetória | Walker Consultoria Educacional', 'Reitor, diretor e vice-diretor acadêmico, avaliador do BASis/INEP, pesquisador da Cátedra UNESCO Metodista e autor de seis livros.', b, active='sobre.html', tail='<script>{' + UFS_JS + '}' + UF_TIP_JS + '</script>')

    # ----- publicações -----
    PB = J('publicacoes.json')
    grupos = ''
    for gi, g in enumerate(PB.get('grupos', [])):
        itens = ''.join(f'''<li><span class="pub-ano">{e(it.get("ano"))}</span><div><b>{f'<a href="{e(it["link"])}" target="_blank" rel="noopener">{e(it["titulo"])}</a>' if it.get("link") else e(it["titulo"])}</b><span>{e(it.get("onde"))}{(" " + e(it["coautores"]) + ".") if it.get("coautores") else ""}</span></div></li>''' for it in g.get('itens', []))
        grupos += f'<section class="band{" tint" if gi % 2 == 0 else ""}"><div class="wrap"><div class="head"><h2>{e(g["titulo"])}</h2></div><ol class="pubs">{itens}</ol></div></section>'
    b = hero([('/sobre.html', 'Sobre'), (None, PB.get('titulo') or 'Publicações')], PB.get('titulo') or 'Publicações', PB.get('texto'),
             f'<a class="btn gold" href="#livros">Ver os livros</a><a class="btn ghost" href="{e(SITE["lattes"])}" target="_blank" rel="noopener">Currículo Lattes</a>')
    b += f'<section class="band" id="livros"><div class="wrap"><div class="head"><h2>{e(PB.get("livros_titulo") or "Livros")}</h2><p class="soft">{e(PB.get("livros_texto"))}</p></div>{nbh}<div class="books">{books}</div></div></section>'
    b += grupos + cta_band('Quer levar esse conteúdo para a sua instituição?')
    page('publicacoes.html', 'Publicações do Prof. Walker Nascimento | Walker Consultoria Educacional',
         'Livros, capítulos, trabalhos em anais de congressos e apresentações do Prof. Walker Nascimento sobre gestão do ensino superior, comunicação e captação de recursos.', b, active='publicacoes.html')
    b = hero([('/sobre.html', 'Sobre'), (None, 'Onde atuei')], 'Onde atuei', 'Faculdades, redes e polos em seis estados brasileiros. Toque em um estado no mapa para ver a atuação.',
             f'<a class="btn gold" href="/sobre.html">Voltar à trajetória</a><a class="btn ghost" href="{e(SITE["lattes"])}" target="_blank" rel="noopener">Currículo Lattes</a>') + mapa + cta_band('Vamos olhar a sua instituição?')
    page('onde-atuei.html', 'Onde atuei | Prof. Walker Nascimento', 'Mapa dos estados onde o Prof. Walker Nascimento atuou na gestão do ensino superior.', b, active='onde-atuei.html', tail='<script>{' + UFS_JS + '}' + UF_TIP_JS + '</script>')

    # ----- cursos -----
    cards = ''
    modal_data = {}
    for c in CUR['cursos']:
        top = ''.join(f'<li>{e(t["texto"])}</li>' for t in c.get('topicos') or [])
        if c.get('status') == 'venda':
            side = f'<div class="wait"><b>{e(c.get("preco"))}</b><p>Pagamento por Pix, cartão ou boleto. O acesso chega no seu e-mail.</p><a class="btn gold" href="{e(c.get("link_compra"))}" target="_blank" rel="noopener">Comprar agora</a></div>'
        else:
            side = f'''<form class="wait" name="lista-{e(c["id"])}" method="POST" action="/obrigado.html" data-netlify="true" netlify-honeypot="empresa-site"><input type="hidden" name="form-name" value="lista-{e(c["id"])}"><p class="hp"><label>Não preencha: <input name="empresa-site"></label></p>
<b>Entrar na lista de espera</b><p>Você recebe o aviso de abertura das inscrições e uma condição de lançamento.</p><input name="nome" placeholder="Seu nome" required autocomplete="name" aria-label="Seu nome"><input name="email" type="email" placeholder="Seu e-mail" required autocomplete="email" aria-label="Seu e-mail"><input name="whatsapp" placeholder="WhatsApp com DDD" autocomplete="tel" aria-label="WhatsApp com DDD"><input type="hidden" name="curso" value="{e(c["titulo"])}">
<label class="consent"><input type="checkbox" name="consentimento" value="sim" required> Autorizo o contato por e-mail e WhatsApp sobre este curso, conforme a LGPD.</label><button class="btn gold" type="submit">Quero ser avisado</button><p class="nocomp">Sem compromisso de matrícula.</p></form>'''
        cards += f'''<article class="course" id="{e(c["id"])}"><div><span class="tag">{e(c["selo"])}</span><h3>{e(c["titulo"])}</h3><p class="soft">{e(c["texto"])}</p>{f'<ul>{top}</ul>' if top else ''}<p class="for">{e(c.get("publico"))}</p><button type="button" class="more" data-curso="{e(c["id"])}">Ver detalhes do curso</button></div>{side}</article>'''
        modal_data[c['id']] = {'t': c['titulo'], 'dur': c.get('duracao', ''), 'fmt': c.get('formato', ''), 'ini': c.get('inicio', ''), 'pub': c.get('para_quem', ''), 'uso': [x['texto'] for x in c.get('resultados') or []]}
        if c.get('status') == 'venda':
            modal_data[c['id']]['cta'] = [f'Comprar agora, {c.get("preco", "")}'.strip(', '), c.get('link_compra', '')]
    steps_s = ''.join(f'<li><div><b>{e(p["titulo"])}</b><br><span class="soft">{e(p["texto"])}</span></div></li>' for p in CUR['passos'])
    b = f'''<section class="band dark"><div class="wrap"><p class="who-line">Cursos Walker Consultoria Educacional</p><h1 style="max-width:820px">{e(CUR["titulo"])}</h1><p class="lead" style="max-width:720px">{e(CUR["texto"])}</p><div class="btns"><a class="btn gold" href="#cursos">Ver os cursos</a><a class="btn ghost" href="#aluno">Área do aluno</a></div></div></section>
<section class="band" id="cursos"><div class="wrap"><div class="head"><h2>Cursos</h2><p class="soft">{e(CUR["lista_texto"])}</p></div><div class="course-list">{cards}</div></div></section>
<section class="band tint" id="aluno"><div class="wrap aluno"><div><h2>Área do aluno</h2><p class="soft" style="margin-top:14px">{e(CUR["aluno_texto"])}</p><div class="btns"><a class="btn gold" href="{e(SITE["area_aluno"])}" target="_blank" rel="noopener">Entrar na área do aluno</a></div></div><ol class="steps-simple">{steps_s}</ol></div></section>
<section class="band dark"><div class="wrap closing" style="display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap;align-items:center"><h2 style="max-width:640px">{e(CUR["chamada_final"])}</h2><a class="btn gold" href="/contato.html">Falar com o Prof. Walker</a></div></section>'''
    mjs = re.sub(r'const D=\{.*?\};const m=', 'const D=' + json.dumps(modal_data, ensure_ascii=False) + ';const m=', MODAL_STYLE_JS, flags=re.S)
    page('cursos.html', 'Cursos e e-book | Walker Consultoria Educacional', 'Cursos online e e-book do Prof. Walker Nascimento para gestores do ensino superior.', b, active='cursos.html', tail=MODAL + mjs)

    # ----- obrigado / 404 / privacidade -----
    ob = '''<section class="band dark" style="min-height:62vh;display:grid;align-items:center"><div class="wrap" style="max-width:780px"><p class="who-line">Recebido</p><h1 id="obT">Obrigado! Seus dados chegaram.</h1>
<p class="lead" id="obL">Se você pediu o checklist, ele já está liberado abaixo. Se entrou numa lista de espera, você recebe o aviso assim que as inscrições abrirem.</p>
<div class="btns"><a class="btn gold" id="obB" href="''' + e(NM['checklist_pdf']) + '''" target="_blank" rel="noopener">Baixar o checklist (PDF)</a><a class="btn ghost" href="/">Voltar ao site</a></div></div></section>'''
    ob_js = '''<script>(()=>{const f=new URLSearchParams(location.search).get('f'),T=document.getElementById('obT'),L=document.getElementById('obL'),B=document.getElementById('obB');
if(f==='radar'){T.textContent='Assinatura confirmada.';L.textContent='Você vai receber o Radar do Novo Marco no seu e-mail a cada quinze dias. Enquanto isso, os artigos já publicados estão no site.';B.textContent='Ler os artigos';B.href='/radar.html';B.removeAttribute('target')}
else if(f==='diagnostico'){T.textContent='Recebi o seu diagnóstico.';L.textContent='Vou ler as suas respostas e retorno pelo WhatsApp ou e-mail com as três prioridades para a sua instituição.';B.textContent='Conhecer a consultoria';B.href='/consultoria.html';B.removeAttribute('target')}
else if(f==='eventos'){T.textContent='Inscrição recebida.';L.textContent='Assim que a data do próximo evento for definida, você recebe o convite com o link.';B.textContent='Ver a agenda';B.href='/eventos.html';B.removeAttribute('target')}})();</script>'''
    page('obrigado.html', 'Obrigado | Walker Consultoria Educacional', 'Seus dados chegaram.', ob, tail=ob_js, noindex=True)
    nf = '''<section class="band dark" style="min-height:62vh;display:grid;align-items:center"><div class="wrap" style="max-width:780px"><p class="who-line">Página não encontrada</p><h1>Este endereço não existe ou mudou de lugar.</h1><p class="lead">Comece pela página inicial ou vá direto ao que procura.</p>
<div class="btns"><a class="btn gold" href="/">Ir para a página inicial</a><a class="btn ghost" href="/novo-marco.html">Guia do novo marco</a><a class="btn ghost" href="/contato.html">Contato</a></div></div></section>'''
    page('404.html', 'Página não encontrada | Walker Consultoria Educacional', 'Página não encontrada.', nf, noindex=True)
    pv = hero([(None, 'Política de privacidade')], 'Política de privacidade', 'Como os seus dados são tratados neste site, em linguagem direta e de acordo com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).')
    pv += open(os.path.join(FONTE, 'privacidade.html'), encoding='utf-8').read().replace('walkernascimento@gmail.com', e(SITE['email']))
    page('politica-de-privacidade.html', 'Política de privacidade | Walker Consultoria Educacional', 'Como a Walker Consultoria Educacional trata os dados enviados pelos formulários do site, de acordo com a LGPD.', pv)

    today = datetime.date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{URL}{"" if p == "index.html" else p}</loc><lastmod>{today}</lastmod></url>\n' for p in PAGES) + '</urlset>\n'
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(sm)
    print('ok', len(PAGES), 'páginas')


EXTRA_CSS = '''
.brand img.mark{width:46px;height:46px;flex:none;display:block}
@media(max-width:480px){.brand img.mark{width:40px;height:40px}}
@view-transition{navigation:auto}
header{view-transition-name:topo}
::view-transition-old(root){animation:vt-out .18s ease-in both}
::view-transition-new(root){animation:vt-in .26s ease-out both}
@keyframes vt-out{to{opacity:0}}
@keyframes vt-in{from{opacity:0;transform:translateY(8px)}}
@media(prefers-reduced-motion:reduce){@view-transition{navigation:none}}
.dd{position:relative}
.dd-btn{font:inherit;font-size:15px;color:#d6e6e4;background:transparent;border:0;border-radius:8px;padding:10px 10px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}
.dd-btn:hover,.dd.open .dd-btn{color:#fff}
.dd-btn svg{width:12px;height:12px;transition:transform .15s}
.dd.open .dd-btn svg{transform:rotate(180deg)}
.dd-btn.is-current{color:#fff;box-shadow:inset 0 -2px 0 var(--gold);border-radius:0}
.dd-menu{display:none;position:absolute;top:calc(100% + 8px);left:0;min-width:230px;background:var(--pet2);border:1px solid #1f5254;border-radius:12px;padding:8px;box-shadow:0 18px 40px -12px rgba(0,0,0,.55);z-index:30}
.dd-menu::before{content:"";position:absolute;left:0;right:0;top:-10px;height:10px}
.dd.open .dd-menu{display:block}
@media(hover:hover) and (min-width:1261px){.dd:hover .dd-menu{display:block}}
#mainnav .dd-menu a{display:block;padding:10px 12px;border-radius:8px;white-space:nowrap}
#mainnav .dd-menu a:hover{background:#123f41;color:#fff}
#mainnav .dd-menu a[aria-current=page]{box-shadow:inset 3px 0 0 var(--gold);border-radius:0 8px 8px 0;color:#fff}
@media(max-width:1260px){.dd-btn{display:block;width:100%;text-align:left;padding:16px 6px 4px;font-size:13px;color:#9fc1be;pointer-events:none;box-shadow:none!important}.dd-btn svg{display:none}.dd-menu{display:block;position:static;min-width:0;background:none;border:0;box-shadow:none;padding:0 0 0 12px}.dd-menu::before{display:none}}
.channels small{color:var(--soft)}
.dark .channels small{color:#b4cfcc}
.btn.gold,.btn.gold:visited,.book .btn.gold{color:#10292a}
:root[data-theme=dark] form:not([method=dialog]){background:var(--panel);color:var(--ink);border:1px solid var(--line)}
:root[data-theme=dark] form[method=dialog]{background:none;border:0}
:root[data-theme=dark] form legend,:root[data-theme=dark] form label,:root[data-theme=dark] form b{color:var(--ink)}
:root[data-theme=dark] input,:root[data-theme=dark] select,:root[data-theme=dark] textarea{background:#0f3436;color:var(--ink);border-color:#2b5c5e}
:root[data-theme=dark] input::placeholder,:root[data-theme=dark] textarea::placeholder{color:#8fb0ad}
:root[data-theme=dark] input:focus,:root[data-theme=dark] select:focus,:root[data-theme=dark] textarea:focus{border-color:var(--gold)}
:root[data-theme=dark] img{opacity:.96}
:root[data-theme=dark] form .fnote,:root[data-theme=dark] form .note,:root[data-theme=dark] form small{color:var(--soft)}
.theme-btn{order:5;display:inline-grid;place-items:center;width:40px;height:40px;flex:none;border-radius:50%;border:1.5px solid #3f6d6f;background:transparent;color:#e6efee;cursor:pointer;padding:0}
.theme-btn:hover{border-color:var(--gold);color:var(--gold)}
.theme-btn svg{width:19px;height:19px}
.theme-btn .ic-sun{display:none}
:root[data-theme=dark] .theme-btn .ic-sun{display:block}:root[data-theme=dark] .theme-btn .ic-moon{display:none}
@media(max-width:1260px){.theme-btn{order:0;margin-left:auto}.menu-btn{order:0}#mainnav{order:6}}
@media(max-width:400px){.mb-txt{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}.menu-btn{padding:10px}}
@media(max-width:480px){.bar{gap:8px}.theme-btn{width:38px;height:38px}.menu-btn{padding:8px 10px;gap:6px}}
.pubs{list-style:none;margin:0;padding:0;display:grid;gap:0;max-width:900px}
.pubs li{display:grid;grid-template-columns:72px 1fr;gap:18px;padding:18px 0;border-bottom:1px solid var(--line)}
.band.dark .pubs li{border-color:#1f5254}
.pub-ano{font-weight:800;color:var(--goldtx);font-size:17px;padding-top:2px}
.pubs b{display:block;font-size:17px;line-height:1.4;margin-bottom:4px}
.pubs b a{color:inherit}
.pubs li span:not(.pub-ano){color:var(--soft);font-size:15px;line-height:1.5}
@media(max-width:560px){.pubs li{grid-template-columns:1fr;gap:4px}}
@media(min-width:1261px){.bar{flex-wrap:nowrap;max-width:1400px;padding-left:clamp(16px,3.5vw,48px);padding-right:clamp(16px,3.5vw,48px)}#mainnav a{padding:10px 10px}}
@media(min-width:1261px) and (max-width:1380px){#mainnav a{padding:10px 7px;font-size:14.5px}.bar{gap:10px}}
.uf-tip{position:fixed;z-index:60;pointer-events:none;background:#0a2c2e;color:#fff;font-size:14px;font-weight:600;padding:6px 10px;border-radius:8px;border:1px solid #c9a24a;opacity:0;transition:opacity .12s;white-space:nowrap}
#mapa path[data-nome]{cursor:pointer}
.promo .art img.plain{box-shadow:none!important;border-radius:0!important;max-height:300px}
.art-cover{width:100%;height:auto;border-radius:14px;margin-bottom:24px}
.ev-list{display:grid;gap:18px}
.dq{scroll-margin-top:110px}
'''

if __name__ == '__main__':
    main()
