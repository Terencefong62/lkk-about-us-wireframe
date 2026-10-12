#!/usr/bin/env python3
"""Apply vertical-tab Recent Activities layout to en.html and zh-hans.html."""
import re
from pathlib import Path

PARTNERSHIPS_CSS_ORPHAN = re.compile(
    r"#partnerships \.partnership-track\{.*?\}#partnerships \.feature-copy\{border-width:1px\}\}\s*",
    re.DOTALL,
)

ACTIVITIES_CSS = r"""
#partnerships .partnership-shell{margin-top:clamp(12px,2vw,24px)}
#partnerships .activities-heading{margin:0 0 clamp(28px,4vw,48px);font-family:var(--font-flare);font-size:clamp(42px,5.2vw,76px);line-height:.98;letter-spacing:-.04em;font-weight:400;text-transform:uppercase}
#partnerships .activities-layout{display:grid;grid-template-columns:minmax(148px,220px) minmax(0,1fr);gap:clamp(18px,2.8vw,28px);align-items:stretch}
#partnerships .activities-nav{display:flex;flex-direction:column;gap:10px}
#partnerships .activities-tab{display:flex;align-items:center;gap:10px;width:100%;min-height:54px;padding:14px 16px;border:1px solid var(--line);background:var(--paper);text-align:left;cursor:pointer;font:inherit;font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--ink);transition:background .2s ease,color .2s ease,border-color .2s ease}
#partnerships .activities-tab__num{font-family:var(--font-flare);font-size:16px;font-weight:400;letter-spacing:-.02em;line-height:1;min-width:1.75em}
#partnerships .activities-tab.is-active{background:var(--ink);border-color:var(--ink);color:var(--paper)}
#partnerships{--activities-gallery-peek:clamp(16px,2.4vw,32px);--activities-gallery-gap:clamp(8px,1.2vw,14px)}
#partnerships .activities-panels{min-width:0;max-width:none;border:0;background:transparent}
#partnerships .activities-panel{display:none}
#partnerships .activities-panel.is-active{display:grid;grid-template-columns:minmax(0,1.02fr) minmax(0,.98fr);gap:clamp(28px,4.5vw,64px);align-items:center}
#partnerships .activities-panel__body{min-width:0;padding:0;max-width:none}
#partnerships .activities-panel__tag{display:none}
#partnerships .activities-panel__title{margin:0 0 clamp(18px,2.4vw,28px);width:100%;max-width:none;font-family:var(--font-flare);font-size:clamp(28px,3.4vw,46px);line-height:1.04;letter-spacing:-.03em;font-weight:400;text-transform:uppercase}
#partnerships .activities-panel__body .body-copy{width:100%;max-width:none;font-size:clamp(14px,1.05vw,15px);line-height:1.62}
#partnerships .activities-cta{display:none}
#partnerships .activities-panel__media{position:relative;min-width:0;aspect-ratio:auto;max-height:none;background:transparent;border:0;overflow:visible}
#partnerships .activities-panel__media .media-gallery.media-gallery--peek{width:100%}
#partnerships .activities-panel__media .media-gallery--peek .media-gallery-track{display:flex;gap:var(--activities-gallery-gap);overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;scroll-behavior:smooth;scrollbar-width:none;overscroll-behavior-inline:contain}
#partnerships .activities-panel__media .media-gallery--peek .media-gallery-track::-webkit-scrollbar{display:none}
#partnerships .activities-panel__media .media-gallery--peek .media-gallery-slide{flex:0 0 calc(100% - var(--activities-gallery-peek));width:auto;min-height:clamp(280px,36vw,460px);aspect-ratio:4/5;scroll-snap-align:start;scroll-snap-stop:always}
#partnerships .activities-panel__media .media-gallery--peek.is-at-end .media-gallery-slide:last-child{flex-basis:100%}
#partnerships .activities-panel__media .media-gallery-slide.media-placeholder{height:auto;border:1px solid var(--line);background:var(--soft)}
#partnerships .activities-panel__media .media-placeholder:before,#partnerships .activities-panel__media .media-placeholder:after{display:none}
#partnerships .activities-panel__media .media-gallery-control{width:48px;height:48px;font-size:22px;top:50%;transform:translateY(-50%);box-shadow:0 2px 12px rgba(0,0,0,.08)}
#partnerships .activities-panel__media .media-gallery-control.prev{left:10px}
#partnerships .activities-panel__media .media-gallery-control.next{right:10px}
#partnerships .activities-panel__media .media-gallery-dots{position:static;transform:none;margin-top:clamp(14px,2vw,20px);padding:0;background:transparent;border:0}
#partnerships .activities-scroll-hint{margin-top:clamp(36px,5vw,60px);display:flex;justify-content:center}
#partnerships .activities-scroll-hint a,.partnerships .activities-scroll-hint button{width:48px;height:48px;border:1px solid var(--ink);border-radius:50%;background:var(--paper);display:grid;place-items:center;font-size:18px;line-height:1;color:inherit;text-decoration:none}
#partnerships .activities-scroll-hint a:focus-visible,#partnerships .activities-scroll-hint button:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
@media(max-width:900px){#partnerships .activities-panel.is-active{grid-template-columns:1fr;gap:clamp(22px,4vw,32px)}#partnerships .activities-panel__media .media-gallery--peek .media-gallery-slide{min-height:clamp(240px,52vw,360px)}}
@media(max-width:800px){#partnerships .activities-layout{grid-template-columns:1fr}#partnerships .activities-nav{flex-direction:row;flex-wrap:wrap}#partnerships .activities-tab{flex:1 1 calc(33.333% - 8px);min-width:120px}}
""".strip()

ACTIVITIES_JS = r""";(()=>{const root=document.getElementById('partnerships');if(!root)return;const tabs=[...root.querySelectorAll('.activities-tab')];const panels=[...root.querySelectorAll('.activities-panel')];const activate=index=>{const i=Math.max(0,Math.min(panels.length-1,index));tabs.forEach((tab,n)=>{const on=n===i;tab.classList.toggle('is-active',on);tab.setAttribute('aria-selected',on?'true':'false')});panels.forEach((panel,n)=>{const on=n===i;panel.classList.toggle('is-active',on);panel.hidden=!on})};tabs.forEach((tab,index)=>tab.addEventListener('click',()=>activate(index)));activate(0)})()"""


def parse_slides(html: str) -> list[dict]:
    slides = []
    for block in re.findall(
        r'<article class="activity-slide partnership-card[^"]*"[^>]*>(.*?)</article>',
        html,
        flags=re.DOTALL,
    ):
        num = re.search(r'activity-slide__index">(\d+)', block)
        tag = re.search(r'activity-slide__tag">([^<]+)', block)
        title = re.search(r'activity-slide__title">(.*?)</h2>', block, re.DOTALL)
        body = re.search(r'<div class="body-copy">(.*?)</div>\s*</div>\s*<div class="activity-slide__visual">', block, re.DOTALL)
        gallery = re.search(
            r'(<div class="media-gallery"[^>]*>.*?<div class="media-gallery-dots"[^>]*>.*?</div>\s*</div>)',
            block,
            re.DOTALL,
        )
        data = re.search(r'data-partnership="([^"]+)"', block)
        slides.append(
            {
                "num": num.group(1) if num else "",
                "tab_label": tag.group(1).strip() if tag else "",
                "title": title.group(1).strip() if title else "",
                "body": body.group(1).strip() if body else "",
                "gallery": gallery.group(1).strip() if gallery else "",
                "data": data.group(1) if data else "",
            }
        )
    return slides


def tab_short_label(tab_label: str, lang: str) -> str:
    if lang == "en":
        mapping = {
            "50 Best Restaurants": "50 Best",
            "Global Youth Culinary Immersion": "Youth Immersion",
        }
        return mapping.get(tab_label, tab_label)
    mapping = {
        "世界50最佳餐厅": "50 Best",
        "全球青年厨师烹饪体验": "Youth Immersion",
    }
    return mapping.get(tab_label, tab_label)


def section_html(slides: list[dict], lang: str) -> str:
    if lang == "en":
        tag = "03 Recent Activities"
        heading = "Recent Activities"
        shell_label = "Recent Activities"
        cta = "Read full story"
        scroll_label = "Go to company culture section"
        scroll_target = "#company-culture"
    else:
        tag = "03 企業動向"
        heading = "企業動向"
        shell_label = "企業動向"
        cta = "阅读全文"
        scroll_label = "前往企业文化部分"
        scroll_target = "#company-culture"

    tabs = []
    panels = []
    for i, s in enumerate(slides):
        active = " is-active" if i == 0 else ""
        short = tab_short_label(s["tab_label"], lang)
        tabs.append(
            f'<button type="button" class="activities-tab{active}" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-controls="activity-panel-{i}" id="activity-tab-{i}"><span class="activities-tab__num">{s["num"]}</span><span class="activities-tab__label">{short}</span></button>'
        )
        panels.append(
            f"""<article class="activities-panel{active}" id="activity-panel-{i}" role="tabpanel" aria-labelledby="activity-tab-{i}" data-partnership="{s["data"]}"{" hidden" if i else ""}>
  <div class="activities-panel__media">
    {s["gallery"]}
  </div>
  <div class="activities-panel__body">
    <p class="activities-panel__tag">{s["tab_label"]}</p>
    <h3 class="activities-panel__title">{s["title"]}</h3>
    <div class="body-copy">{s["body"]}</div>
    <a class="activities-cta" href="#">{cta}</a>
  </div>
</article>"""
        )

    return f"""    <section class="module" id="partnerships" aria-labelledby="partnerships-title"><span class="module-tag">{tag}</span><div class="section-inner"><h2 id="partnerships-title" class="activities-heading">{heading}</h2><div class="partnership-shell" aria-label="{shell_label}"><div class="activities-layout"><nav class="activities-nav" role="tablist" aria-label="{shell_label}">
{chr(10).join(tabs)}
</nav><div class="activities-panels">
{chr(10).join(panels)}
</div></div><div class="activities-scroll-hint"><a href="{scroll_target}" aria-label="{scroll_label}">↓</a></div></div></div></section>"""


def apply(path: Path) -> None:
    lang = "zh" if "zh-hans" in path.name else "en"
    html = path.read_text(encoding="utf-8")
    slides = parse_slides(html)
    if len(slides) != 3:
        raise SystemExit(f"{path}: expected 3 slides, got {len(slides)}")

    html = re.sub(
        r"#partnerships\{.*?\}(?:@media\(min-width:901px\)\{[^}]+\})?(?:@media\(max-width:900px\)[^}]+\})?(?:@media\(max-width:700px\)\{[^}]+\})?[^}]*\}[^}]*\}[^}]*\}?",
        ACTIVITIES_CSS,
        html,
        count=1,
        flags=re.DOTALL,
    )
    if ACTIVITIES_CSS not in html:
        html = re.sub(
            r"#partnerships\{.*?@media\(max-width:700px\)\{[^}]+\}[^}]*\}[^}]*\}[^}]*\}[^}]*\}?",
            ACTIVITIES_CSS,
            html,
            count=1,
            flags=re.DOTALL,
        )

    html = PARTNERSHIPS_CSS_ORPHAN.sub("", html)

    new_section = section_html(slides, lang)
    html = re.sub(
        r'<section class="module" id="partnerships"[\s\S]*?</section>\s*\n\s*<section class="module" id="company-culture"',
        new_section + "\n\n    <section class=\"module\" id=\"company-culture\"",
        html,
        count=1,
    )

    html = re.sub(
        r"\;\(\(\)=>\{const track=document\.getElementById\('partnership-track'\)[\s\S]*?goTo\(0\)\}\)\(\)",
        ACTIVITIES_JS,
        html,
        count=1,
    )

    path.write_text(html, encoding="utf-8")
    print(f"Updated {path.name}")


def main():
    root = Path(__file__).resolve().parents[1]
    for name in ("en.html", "zh-hans.html"):
        apply(root / name)


if __name__ == "__main__":
    main()
