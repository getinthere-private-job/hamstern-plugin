#!/usr/bin/env python3
"""
inject_html_adapter.py — Open Skill Diary HTML simulator adapter

Reads an arbitrary HTML file (typically a dark-themed simulator) and writes
a transformed copy that:
  - Removes max-width constraints so the simulator fills the viewport
  - Wraps body content in #osd-content-wrapper so a CSS filter can produce a
    light-mode variant on demand without touching simulator-internal styles
  - Injects a floating navigation bar (back to blog + theme toggle) that
    sits above the inverted region (z-index: 2147483647)
  - Persists theme via localStorage('blog-theme'), shared with the host blog

Usage:
    python inject_html_adapter.py --src <input.html> --dst <output.html> --title "..."
    python inject_html_adapter.py --src-dir <dir> --dst-dir <posts/> [--map JSON]
    python inject_html_adapter.py --src <in.html> --dst <out.html> --title "..." --no-theme

When --no-theme is set, only the full-width override + floating bar are
injected (no light/dark filter). The simulator keeps its original colors.
"""

import argparse
import json
import os
import re
import sys

ADAPTER_STYLE_FULL = r"""
<!-- ======= Open Skill Diary theme adapter (injected) ======= -->
<style id="osd-theme-adapter">
  /* Full-width override: clear max-width on common layout containers */
  html, body { max-width: 100% !important; }
  body { padding-top: 56px !important; }
  .layout, .simulator, .container, main, .wrap, .wrapper, .page, .app, .root,
  [class*="container"], [class*="wrapper"] {
    max-width: 100% !important;
    width: 100% !important;
  }

  /* Light mode: invert + hue-rotate gives a faithful light variant of any
     dark page. Applied to a wrapper so the floating bar stays unaffected. */
  html[data-osd-theme="light"] body { background: #f7f8fb !important; }
  html[data-osd-theme="light"] #osd-content-wrapper {
    filter: invert(0.92) hue-rotate(180deg);
    min-height: 100vh;
  }
  html[data-osd-theme="light"] #osd-content-wrapper img,
  html[data-osd-theme="light"] #osd-content-wrapper svg,
  html[data-osd-theme="light"] #osd-content-wrapper video,
  html[data-osd-theme="light"] #osd-content-wrapper canvas {
    filter: invert(1) hue-rotate(180deg);
  }

  /* Floating top bar — fixed, very high z-index, sits above wrapper */
  #osd-bar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 2147483647;
    display: flex; align-items: center; justify-content: space-between;
    gap: 12px; padding: 10px 16px;
    background: rgba(15, 22, 36, 0.85);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.12);
    color: #e8eef9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Pretendard",
                 "Noto Sans KR", sans-serif;
    font-size: 13px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.25);
  }
  html[data-osd-theme="light"] #osd-bar {
    background: rgba(255,255,255,0.92);
    border-bottom: 1px solid #e3e8ef;
    color: #1a2332;
    box-shadow: 0 1px 3px rgba(20,30,50,0.06), 0 4px 16px rgba(20,30,50,0.04);
  }
  #osd-bar a, #osd-bar button {
    color: inherit; background: transparent; border: 1px solid currentColor;
    border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 600;
    text-decoration: none; cursor: pointer;
    opacity: 0.85; transition: opacity .15s, transform .15s;
    font-family: inherit;
  }
  #osd-bar a:hover, #osd-bar button:hover { opacity: 1; transform: translateY(-1px); }
  #osd-bar .osd-bar__title { font-weight: 700; letter-spacing: -0.2px; opacity: 0.9;
    flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
  #osd-bar .osd-bar__actions { display: flex; gap: 8px; flex-shrink: 0; }
  #osd-bar .osd-bar__brand { font-weight: 700; font-size: 13px; opacity: 0.7; flex-shrink: 0; }
  @media (max-width: 640px) {
    #osd-bar { padding: 8px 10px; font-size: 12px; }
    #osd-bar .osd-bar__title { display: none; }
  }
</style>
<script>
  (function(){
    try {
      var t = localStorage.getItem('blog-theme') || 'dark';
      document.documentElement.setAttribute('data-osd-theme', t);
    } catch(e){}
  })();
</script>
<!-- ======= /theme adapter ======= -->
"""

# Lite version: only full-width + floating bar, no filter inversion
ADAPTER_STYLE_NOTHEME = r"""
<!-- ======= Open Skill Diary adapter (no-theme) ======= -->
<style id="osd-theme-adapter">
  html, body { max-width: 100% !important; }
  body { padding-top: 56px !important; }
  .layout, .simulator, .container, main, .wrap, .wrapper, .page, .app, .root,
  [class*="container"], [class*="wrapper"] {
    max-width: 100% !important;
    width: 100% !important;
  }
  #osd-bar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 2147483647;
    display: flex; align-items: center; justify-content: space-between;
    gap: 12px; padding: 10px 16px;
    background: rgba(15, 22, 36, 0.85);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.12);
    color: #e8eef9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Pretendard",
                 "Noto Sans KR", sans-serif;
    font-size: 13px;
  }
  #osd-bar a { color: inherit; background: transparent; border: 1px solid currentColor;
    border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 600;
    text-decoration: none; opacity: 0.85; }
  #osd-bar a:hover { opacity: 1; }
  #osd-bar .osd-bar__title { font-weight: 700; flex: 1; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; min-width: 0; }
  #osd-bar .osd-bar__actions { display: flex; gap: 8px; }
  #osd-bar .osd-bar__brand { font-weight: 700; opacity: 0.7; }
</style>
<!-- ======= /adapter ======= -->
"""

WRAP_SCRIPT = r"""
<script>
  // Wrap body content so the light-mode filter applies only to wrapper, not to floating bar
  (function(){
    function wrap(){
      var bar = document.getElementById('osd-bar');
      var wrapper = document.createElement('div');
      wrapper.id = 'osd-content-wrapper';
      wrapper.style.cssText = 'transition: filter .25s;';
      var nodes = Array.prototype.slice.call(document.body.childNodes);
      nodes.forEach(function(n){ if (n === bar) return; wrapper.appendChild(n); });
      document.body.appendChild(wrapper);
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', wrap, { once: true });
    } else { wrap(); }
  })();
</script>
"""

THEME_TOGGLE_SCRIPT = r"""
<script>
  (function(){
    var btn = document.getElementById('osd-theme-toggle');
    if (!btn) return;
    btn.addEventListener('click', function(){
      var cur = document.documentElement.getAttribute('data-osd-theme') || 'dark';
      var next = cur === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-osd-theme', next);
      try { localStorage.setItem('blog-theme', next); } catch(e){}
    });
  })();
</script>
"""


def make_bar(title: str, with_theme: bool) -> str:
    theme_btn = '<button type="button" id="osd-theme-toggle" aria-label="테마 전환">테마</button>' if with_theme else ''
    return f'''
<!-- ======= OSD floating bar (injected) ======= -->
<div id="osd-bar" role="navigation" aria-label="블로그 네비게이션">
  <a href="../index.html" class="osd-bar__brand" title="블로그 홈">◆ Diary</a>
  <div class="osd-bar__title">{title}</div>
  <div class="osd-bar__actions">
    <a href="../index.html">← 목록</a>
    {theme_btn}
  </div>
</div>
<!-- ======= /OSD floating bar ======= -->
'''


def inject(html: str, title: str, with_theme: bool = True) -> str:
    style = ADAPTER_STYLE_FULL if with_theme else ADAPTER_STYLE_NOTHEME
    bar = make_bar(title, with_theme)

    # Insert adapter style+script right after <head>
    new = re.sub(r'(<head\b[^>]*>)', r'\1' + style, html, count=1, flags=re.IGNORECASE)
    if new == html:
        new = '<head>' + style + '</head>' + html

    # Insert bar + scripts right after <body>
    body_payload = bar + (WRAP_SCRIPT if with_theme else '') + (THEME_TOGGLE_SCRIPT if with_theme else '')
    new2 = re.sub(r'(<body\b[^>]*>)', r'\1' + body_payload, new, count=1, flags=re.IGNORECASE)
    if new2 == new:
        new2 = '<body>' + body_payload + new + '</body>'
    return new2


def slugify(name: str) -> str:
    base = os.path.splitext(os.path.basename(name))[0]
    s = re.sub(r'[^\w\s-]', '', base, flags=re.UNICODE).strip().lower()
    s = re.sub(r'[-\s_]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s or 'post'


def extract_title(html: str, fallback: str) -> str:
    m = re.search(r'<title>(.*?)</title>', html, flags=re.IGNORECASE | re.DOTALL)
    if m:
        t = re.sub(r'\s+', ' ', m.group(1)).strip()
        if t:
            return t
    m = re.search(r'<h1\b[^>]*>(.*?)</h1>', html, flags=re.IGNORECASE | re.DOTALL)
    if m:
        t = re.sub(r'<[^>]+>', '', m.group(1))
        t = re.sub(r'\s+', ' ', t).strip()
        if t:
            return t
    return fallback


def main(argv=None):
    ap = argparse.ArgumentParser(description='Inject OSD theme adapter into HTML simulator')
    ap.add_argument('--src', help='Single source HTML file')
    ap.add_argument('--dst', help='Destination HTML path (with --src)')
    ap.add_argument('--title', help='Title to display in floating bar (with --src)')
    ap.add_argument('--src-dir', help='Source directory (batch)')
    ap.add_argument('--dst-dir', help='Destination directory (batch)')
    ap.add_argument('--map', help='JSON file: [{"src":"a.html","dst":"slug.html","title":"..."}, ...]')
    ap.add_argument('--no-theme', action='store_true', help='Skip light/dark adapter, only full-width + bar')
    args = ap.parse_args(argv)

    with_theme = not args.no_theme
    jobs = []

    if args.map:
        with open(args.map, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
    elif args.src and args.dst:
        jobs = [{'src': args.src, 'dst': args.dst, 'title': args.title or extract_title(open(args.src, encoding='utf-8').read(), slugify(args.src))}]
    elif args.src_dir and args.dst_dir:
        for fn in sorted(os.listdir(args.src_dir)):
            if not fn.lower().endswith('.html'):
                continue
            src_path = os.path.join(args.src_dir, fn)
            slug = slugify(fn)
            dst_path = os.path.join(args.dst_dir, f'{slug}.html')
            with open(src_path, 'r', encoding='utf-8') as f:
                title = extract_title(f.read(), slug)
            jobs.append({'src': src_path, 'dst': dst_path, 'title': title})
    else:
        ap.error('Provide --src+--dst, --src-dir+--dst-dir, or --map')

    ok = 0
    for j in jobs:
        with open(j['src'], 'r', encoding='utf-8') as f:
            html = f.read()
        out = inject(html, j['title'], with_theme=with_theme)
        os.makedirs(os.path.dirname(os.path.abspath(j['dst'])), exist_ok=True)
        with open(j['dst'], 'w', encoding='utf-8') as f:
            f.write(out)
        print(f'OK  {j["src"]}  ->  {j["dst"]}  (title="{j["title"]}", {len(out)} bytes)')
        ok += 1
    print(f'\n{ok}/{len(jobs)} files processed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
