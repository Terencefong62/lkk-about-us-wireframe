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
#partnerships .activities-panels{min-width:0;max-width:min(600px,100%);border:1px solid var(--line);background:var(--paper)}
#partnerships .activities-panel{display:none}
#partnerships .activities-panel.is-active{display:block}
#partnerships .activities-panel__media{position:relative;aspect-ratio:16/9;max-height:min(240px,42vw);min-height:0;background:var(--soft);border-bottom:1px solid var(--line);overflow:hidden}
#partnerships .activities-panel__media .media-gallery{width:100%;height:100%}
#partnerships .activities-panel__media .media-gallery-track{height:100%;display:grid;grid-auto-flow:column;grid-auto-columns:100%}
#partnerships .activities-panel__media .media-gallery-slide.media-placeholder{height:100%;min-height:0!important;aspect-ratio:auto;border:0;background:var(--soft)}
#partnerships .activities-panel__media .media-placeholder:before,#partnerships .activities-panel__media .media-placeholder:after{display:none}
#partnerships .activities-panel__media .media-gallery-control{width:44px;height:44px;font-size:20px}
#partnerships .activities-panel__media .media-gallery-dots{position:absolute;bottom:12px;left:50%;transform:translateX(-50%);margin:0;background:rgba(255,255,255,.92);padding:6px 10px;border:1px solid var(--line)}
#partnerships .activities-panel__body{padding:clamp(16px,2.2vw,22px) clamp(16px,2.4vw,24px) clamp(18px,2.4vw,26px);max-width:min(600px,100%)}
#partnerships .activities-panel__tag{margin:0 0 8px;font-size:10px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
#partnerships .activities-panel__title{margin:0 0 var(--heading-copy-gap);width:100%;max-width:none;font-family:var(--font-flare);font-size:clamp(20px,2.4vw,30px);line-height:1.08;letter-spacing:-.03em;font-weight:400;text-transform:uppercase}
#partnerships .activities-panel__body .body-copy{width:100%;max-width:none;font-size:14px;line-height:1.58}
#partnerships .activities-cta{margin-top:clamp(16px,2.2vw,22px);display:inline-flex;align-items:center;gap:8px;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;color:var(--ink)}
#partnerships .activities-cta::before{content:"▶";font-size:7px;line-height:1}
#partnerships .activities-scroll-hint{margin-top:clamp(36px,5vw,60px);display:flex;justify-content:center}
#partnerships .activities-scroll-hint a,.partnerships .activities-scroll-hint button{width:48px;height:48px;border:1px solid var(--ink);border-radius:50%;background:var(--paper);display:grid;place-items:center;font-size:18px;line-height:1;color:inherit;text-decoration:none}
#partnerships .activities-scroll-hint a:focus-visible,#partnerships .activities-scroll-hint button:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
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
