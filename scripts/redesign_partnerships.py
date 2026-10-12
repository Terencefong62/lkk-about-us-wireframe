#!/usr/bin/env python3
"""Redesign Recent Activities carousel in en.html and zh-hans.html."""
import re
from pathlib import Path

NEW_CSS = r"""
#partnerships{--activity-slide-width:min(100%,1120px);--activity-peek:clamp(14px,2.2vw,24px)}
#partnerships .partnership-shell{margin-top:clamp(12px,2vw,24px)}
#partnerships .activity-carousel{position:relative}
#partnerships .partnership-stage{padding:0 clamp(44px,3.5vw,56px);margin:0}
#partnerships .partnership-track{display:flex;gap:var(--activity-peek);overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;scroll-behavior:smooth;scrollbar-width:none;overscroll-behavior-inline:contain;padding:2px 0 6px}
#partnerships .partnership-track::-webkit-scrollbar{display:none}
#partnerships .activity-slide{flex:0 0 calc(100% - var(--activity-peek));min-width:0;scroll-snap-align:start;scroll-snap-stop:always;border-top:1px solid var(--ink);padding-top:clamp(16px,2.2vw,24px);transition:opacity .25s ease}
#partnerships .activity-slide:not(.is-focus){opacity:.38}
#partnerships .activity-slide.is-focus{opacity:1}
#partnerships .activity-slide__head{display:flex;align-items:baseline;gap:14px;margin-bottom:clamp(16px,2.4vw,24px)}
#partnerships .activity-slide__index{font-family:var(--font-flare);font-size:clamp(22px,2.4vw,30px);line-height:1;letter-spacing:-.02em}
#partnerships .activity-slide__tag{text-transform:uppercase;letter-spacing:.14em;font-size:10px;font-weight:800;color:var(--muted)}
#partnerships .activity-slide__body{display:grid;grid-template-columns:minmax(0,1.02fr) minmax(0,.98fr);gap:clamp(20px,3.2vw,40px);align-items:start}
#partnerships .activity-slide__body--media-left .activity-slide__visual{order:-1}
#partnerships .activity-slide__content{min-width:0;padding-right:clamp(0px,1vw,8px)}
#partnerships .activity-slide__title{margin:0 0 var(--heading-copy-gap);font-family:var(--font-flare);font-size:clamp(28px,3.2vw,44px);line-height:1.05;letter-spacing:-.03em;font-weight:400;text-transform:uppercase}
#partnerships .activity-slide__content .body-copy{font-size:clamp(14px,1.05vw,15px);line-height:1.6;max-width:56ch}
#partnerships .activity-slide__visual{min-width:0;width:100%}
#partnerships .activity-slide__visual .media-gallery{position:relative;width:100%}
#partnerships .activity-slide__visual .media-gallery-track{display:grid;grid-auto-flow:column;grid-auto-columns:100%;border-radius:0}
#partnerships .activity-slide__visual .media-gallery-slide.media-placeholder{aspect-ratio:16/9;min-height:0!important;width:100%;border:0;background:var(--soft)}
#partnerships .activity-slide__visual .media-placeholder:before,#partnerships .activity-slide__visual .media-placeholder:after{display:none}
#partnerships .activity-slide__visual .media-gallery-control{width:44px;height:44px;font-size:20px}
#partnerships .activity-slide__visual .media-gallery-dots{margin-top:12px}
#partnerships .partnership-edge-control{position:absolute;z-index:10;top:42%;width:48px;height:48px;border:1px solid var(--ink);border-radius:50%;background:var(--paper);display:grid;place-items:center;transform:translateY(-50%);font-size:22px;line-height:1;cursor:pointer;box-shadow:0 2px 12px rgba(0,0,0,.08)}
#partnerships .partnership-edge-control.prev{left:0}
#partnerships .partnership-edge-control.next{right:0}
#partnerships .partnership-edge-control:disabled{opacity:.2;cursor:default}
#partnerships .partnership-jumps{margin-top:clamp(20px,3vw,32px);display:flex;flex-wrap:wrap;justify-content:flex-start;gap:8px}
#partnerships .partnership-jump{min-height:38px;padding:9px 14px;border:1px solid var(--line);background:var(--paper);text-transform:uppercase;letter-spacing:.06em;font-size:10px;font-weight:800;cursor:pointer;color:var(--muted)}
#partnerships .partnership-jump.is-active{border-color:var(--ink);color:var(--ink);background:var(--paper)}
@media(min-width:901px){#partnerships .activity-slide{flex:0 0 min(92%,1040px)}}
@media(max-width:900px){#partnerships .activity-slide__body{grid-template-columns:1fr;gap:20px}#partnerships .activity-slide__body--media-left .activity-slide__visual{order:0}}
@media(max-width:700px){#partnerships .partnership-stage{padding:0 clamp(36px,9vw,44px)}#partnerships .partnership-edge-control{width:40px;height:40px;font-size:18px;top:38%}#partnerships .activity-slide{flex:0 0 calc(100% - 12px)}}
""".strip()


def extract_slides(html: str) -> list[dict]:
    slides = []
    for block in re.findall(
        r'<article class="partnership-card[^"]*"[^>]*>(.*?)</article>',
        html,
        flags=re.DOTALL,
    ):
        kicker = re.search(r'class="partnership-kicker">([^<]+)', block)
        title = re.search(r'class="partnership-title">(.*?)</h2>', block, re.DOTALL)
        body = re.search(r'<div class="body-copy">(.*?)</div>\s*</div>\s*<div class="feature-media">', block, re.DOTALL)
        gallery = re.search(
            r'(<div class="media-gallery"[^>]*>.*?</div>\s*<div class="media-gallery-dots"[^>]*>.*?</div>\s*</div>)',
            block,
            re.DOTALL,
        )
        reverse = "feature-grid reverse" in block
        data_attr = re.search(r'data-partnership="([^"]+)"', block)
        aria = re.search(r'aria-label="([^"]+)"', block)
        slides.append(
            {
                "kicker": kicker.group(1) if kicker else "",
                "title": title.group(1).strip() if title else "",
                "body": body.group(1).strip() if body else "",
                "gallery": gallery.group(1) if gallery else "",
                "reverse": reverse,
                "data": data_attr.group(1) if data_attr else "",
                "aria": aria.group(1) if aria else "",
            }
        )
    return slides


def build_slides_html(slides: list[dict]) -> str:
    out = []
    for i, s in enumerate(slides):
        focus = " is-focus" if i == 0 else ""
        body_mod = " activity-slide__body--media-left" if s["reverse"] else ""
        idx = f"{i+1:02d}"
        out.append(
            f"""<article class="activity-slide partnership-card{focus}" data-partnership="{s['data']}" aria-label="{s['aria']}">
  <header class="activity-slide__head"><span class="activity-slide__index">{idx}</span><span class="activity-slide__tag">{s['kicker']}</span></header>
  <div class="activity-slide__body{body_mod}">
    <div class="activity-slide__content">
      <h2 class="activity-slide__title">{s['title']}</h2>
      <div class="body-copy">{s['body']}</div>
    </div>
    <div class="activity-slide__visual">
      {s['gallery']}
    </div>
  </div>
</article>"""
        )
    return "\n".join(out)


def apply(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    slides = extract_slides(html)
    if len(slides) != 3:
        raise SystemExit(f"{path}: expected 3 slides, got {len(slides)}")
    new_slides = build_slides_html(slides)

    html = re.sub(
        r"#partnerships\{.*?\}\s*@media\(max-width:700px\)\{#partnerships\{[^}]+\}[^}]*\}[^}]*\}[^}]*\}[^}]*\}[^}]*\}",
        NEW_CSS,
        html,
        count=1,
        flags=re.DOTALL,
    )
    # fallback: replace from #partnerships{ to before .media-gallery{
    if NEW_CSS not in html:
        html = re.sub(
            r"#partnerships\{.*?@media\(max-width:700px\)\{#partnerships[^}]+\}[^}]+\}[^}]+\}[^}]+\}[^}]+\}[^}]+\}",
            NEW_CSS,
            html,
            count=1,
            flags=re.DOTALL,
        )

    html = re.sub(
        r"<article class=\"partnership-card.*?</article>\s*<article class=\"partnership-card.*?</article>\s*<article class=\"partnership-card.*?</article>",
        new_slides,
        html,
        count=1,
        flags=re.DOTALL,
    )

    # Wrap stage in activity-carousel class
    html = html.replace(
        '<div class="partnership-shell" aria-label="Recent Activities"><div class="partnership-layout"><div class="partnership-stage">',
        '<div class="partnership-shell" aria-label="Recent Activities"><div class="partnership-layout"><div class="activity-carousel"><div class="partnership-stage">',
        1,
    )
    html = html.replace(
        '<div class="partnership-shell" aria-label="企業動向"><div class="partnership-layout"><div class="partnership-stage">',
        '<div class="partnership-shell" aria-label="企業動向"><div class="partnership-layout"><div class="activity-carousel"><div class="partnership-stage">',
        1,
    )
    html = html.replace(
        '</button></div><nav class="partnership-jumps"',
        '</button></div></div><nav class="partnership-jumps"',
        1,
    )

    path.write_text(html, encoding="utf-8")
    print(f"Updated {path.name}")


def main():
    root = Path(__file__).resolve().parents[1]
    for name in ("en.html", "zh-hans.html"):
        apply(root / name)


if __name__ == "__main__":
    main()
