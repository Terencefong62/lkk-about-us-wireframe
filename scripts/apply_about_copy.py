#!/usr/bin/env python3
"""Apply About Us master copy to en.html and zh-hans.html."""
import json
import re
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = Path("/tmp/about_us_copy.json")


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def paras(text: str) -> str:
    parts = [p.strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]
    return "".join(f"<p>{esc(p)}</p>" for p in parts)


def statement_h3_from_row(row: dict, lang: str, kind: str) -> str:
    """Vision/mission card h3: label lives in <span>, h3 is tagline only."""
    if kind == "vision":
        if lang == "en":
            return "Where There Are People<br>There Is Lee Kum Kee"
        return esc("有人的地方，就有李锦记")
    if lang == "en":
        return "Promoting Chinese Culinary<br>Culture Worldwide"
    return esc("发扬中华优秀饮食文化")


def headline_html(text: str, br_after: int | None = None) -> str:
    """Turn excel headline into HTML; optional br after N words for EN flair."""
    text = (text or "").strip()
    if not text:
        return ""
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if len(lines) > 1:
        return "<br>".join(esc(ln) for ln in lines)
    if br_after:
        words = text.split()
        if len(words) > br_after:
            return esc(" ".join(words[:br_after])) + "<br>" + esc(" ".join(words[br_after:]))
    return esc(text)


def load_rows():
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def index_rows(rows):
    timeline = []
    values = []
    leadership = []
    commitments_extra = []
    blocks = {}

    for r in rows:
        mod = r["module"]
        oh = r["en_h"]
        if mod == "Company Overview" and oh == "A Century of Heritage":
            blocks["heritage"] = r
        elif mod == "Company Overview" and oh.startswith("Our Vision"):
            blocks["vision"] = r
        elif mod == "Company Overview" and oh.startswith("Our Mission"):
            blocks["mission"] = r
        elif r.get("order") == 2:
            blocks["milestones_intro"] = r
        elif mod == "Timeline Items" and oh and re.match(r"^\d{4}", oh):
            year, title = oh.split("\n", 1)
            zyear, ztitle = (r["zh_h"] or "").split("\n", 1) if r["zh_h"] else ("", "")
            timeline.append(
                {
                    "year": year.strip(),
                    "en_title": title.strip(),
                    "en_b": r["en_b"],
                    "zh_title": ztitle.strip() if ztitle else r["zh_h"],
                    "zh_b": r["zh_b"],
                }
            )
        elif r.get("order") == 3:
            blocks["unesco"] = r
        elif r.get("order") == 4:
            blocks["fifty_best"] = r
        elif r.get("order") == 5:
            blocks["youth"] = r
        elif r.get("order") == 6:
            blocks["culture_intro"] = r
        elif mod == "Our Values" and oh:
            values.append(r)
        elif mod == "Our Leadership" and oh:
            leadership.append(r)
        elif r.get("order") == 7:
            blocks["commitments_intro"] = r
        elif mod == "Our Commitments" and oh == "100-1=0":
            blocks["commitment_quality"] = r
        elif mod == "Our Commitments" and oh == "Sustainable Development":
            blocks["commitment_sustainability"] = r

    return blocks, timeline, values, leadership


def timeline_cards(timeline, lang: str) -> str:
    out = []
    for i, item in enumerate(timeline):
        focus = " is-focus" if i == 0 else ""
        year = item["year"]
        if lang == "en":
            title = item["en_title"]
            body = item["en_b"]
            aria = f"{year} {title}"
            label = f"ARCHIVAL IMAGE PLACEHOLDER<br>{year}"
        else:
            title = item["zh_title"]
            body = item["zh_b"]
            aria = f"{year} {title}"
            label = f"历史图片占位<br>{year}"
        out.append(
            f"""<article class="timeline-card{focus}" data-year="{esc(year)}" aria-label="{esc(aria)}">
  <div class="timeline-card-inner">
    <header class="timeline-card-head">
      <p class="timeline-card-year">{esc(year)}</p>
      <h3>{esc(title)}</h3>
    </header>
    <div class="media-placeholder timeline-media" role="img" aria-label="{esc(aria)}"><span class="media-label">{label}</span></div>
    <p class="timeline-card-body">{esc(body)}</p>
  </div>
</article>"""
        )
    return "\n".join(out)


def scrubber_links(timeline) -> str:
    years: list[str] = []
    for item in timeline:
        y = item["year"]
        if y not in years:
            years.append(y)
    return "".join(
        f'<a class="timeline-year-link{" is-active" if i == 0 else ""}" href="#year-{esc(y)}">{esc(y)}</a>'
        for i, y in enumerate(years)
    )


def partnership_slide(
    lang: str,
    kicker_en: str,
    kicker_zh: str,
    row: dict,
    reverse: bool,
    gallery_label_en: str,
    gallery_label_zh: str,
    focus: bool,
) -> str:
    kicker = kicker_en if lang == "en" else kicker_zh
    h = headline_html(row["en_h"] if lang == "en" else row["zh_h"], br_after=2 if lang == "en" else None)
    body = paras(row["en_b"] if lang == "en" else row["zh_b"])
    rev = " reverse" if reverse else ""
    focus_cls = " is-focus" if focus else ""
    gid = kicker_en.lower().replace(" ", "-")
    if lang == "en":
        aria = f"{kicker_en} partnership"
        media_label = gallery_label_en
    else:
        aria = f"{kicker_zh}合作"
        media_label = gallery_label_zh
    return f"""<article class="partnership-card{focus_cls}" data-partnership="{esc(gid)}" aria-label="{esc(kicker)}">
  <div class="partnership-card-inner">
    <p class="partnership-kicker">{esc(kicker)}</p>
    <div class="feature-grid{rev}">
      <div class="feature-copy">
        <h2 class="partnership-title">{h}</h2>
        <div class="body-copy">{body}</div>
      </div>
      <div class="feature-media">
        <div class="media-gallery" aria-label="{esc(aria)}">
          <div class="media-gallery-track" tabindex="0" role="region" aria-roledescription="carousel" aria-label="{esc(aria)}">
            <div class="media-placeholder media-gallery-slide" data-media-type="image" role="img" aria-label="{esc(aria)}"><span class="media-label">{media_label}</span></div>
            <div class="media-placeholder media-gallery-slide media-gallery-slide--video" data-media-type="video" aria-hidden="true" aria-label="{esc(aria)}"><video class="media-gallery-video" playsinline preload="none" muted></video><button class="media-gallery-play" type="button" aria-label="Play video"><span aria-hidden="true">▶</span></button><span class="media-label">16:9 FILM · PLAY + CAPTIONS</span></div>
          </div>
          <button class="media-gallery-control prev" type="button" data-direction="-1" aria-label="Previous slide">←</button>
          <button class="media-gallery-control next" type="button" data-direction="1" aria-label="Next slide">→</button>
          <div class="media-gallery-dots" role="tablist" aria-label="Choose slide"><button class="media-gallery-dot is-active" type="button" role="tab" aria-selected="true" aria-label="Slide 1, image"></button><button class="media-gallery-dot" type="button" role="tab" aria-selected="false" aria-label="Slide 2, video"></button></div>
        </div>
      </div>
    </div>
  </div>
</article>"""


def partnerships_section(lang: str, blocks: dict) -> str:
    if lang == "en":
        tag = "03 Recent Activities"
        section_title = "Recent Activities"
        scrub = [
            ("unesco", "UNESCO"),
            ("fifty-best", "50 Best"),
            ("youth", "Youth Immersion"),
        ]
        kickers = [
            ("UNESCO", "联合国教科文组织", blocks["unesco"], False, "IMAGE — UNESCO PARTNERSHIP<br>Forever Flavors Project", "图片 — UNESCO 合作<br>风味传承计划"),
            (
                "50 Best Restaurants",
                "世界50最佳餐厅",
                blocks["fifty_best"],
                True,
                "IMAGE — CHEF PARTNERSHIP<br>Official Sauce &amp; Condiment Partner",
                "图片 — 主厨合作<br>官方酱料合作伙伴",
            ),
            (
                "Global Youth Culinary Immersion",
                "全球青年厨师烹饪体验",
                blocks["youth"],
                False,
                "IMAGE — YOUTH CULINARY PROGRAM<br>Hands-on learning across markets",
                "图片 — 青年厨艺项目<br>跨市场沉浸式体验",
            ),
        ]
        aria_track = "Browse Lee Kum Kee recent activities; swipe or use arrows to see more"
    else:
        tag = "03 企業動向"
        section_title = "企業動向"
        scrub = [
            ("unesco", "UNESCO"),
            ("fifty-best", "50 Best"),
            ("youth", "青年项目"),
        ]
        kickers = [
            ("UNESCO", "联合国教科文组织", blocks["unesco"], False, "IMAGE — UNESCO PARTNERSHIP<br>Forever Flavors Project", "图片 — UNESCO 合作<br>风味传承计划"),
            (
                "50 Best Restaurants",
                "世界50最佳餐厅",
                blocks["fifty_best"],
                True,
                "IMAGE — CHEF PARTNERSHIP<br>Official Sauce &amp; Condiment Partner",
                "图片 — 主厨合作<br>官方酱料合作伙伴",
            ),
            (
                "Global Youth Culinary Immersion",
                "全球青年厨师烹饪体验",
                blocks["youth"],
                False,
                "IMAGE — YOUTH CULINARY PROGRAM<br>Hands-on learning across markets",
                "图片 — 青年厨艺项目<br>跨市场沉浸式体验",
            ),
        ]
        aria_track = "浏览企業動向；左右滑动或使用箭头查看更多"

    slides = []
    for i, (ke, kz, row, rev, le, lz) in enumerate(kickers):
        slides.append(partnership_slide(lang, ke, kz, row, rev, le, lz, i == 0))

    nav = "".join(
        f'<button type="button" class="partnership-jump{" is-active" if i == 0 else ""}" data-partnership="{pid}">{esc(label)}</button>'
        for i, (pid, label) in enumerate(scrub)
    )

    return f"""    <section class="module" id="partnerships" aria-labelledby="partnerships-title"><span class="module-tag">{esc(tag)}</span><div class="section-inner"><h2 id="partnerships-title" class="visually-hidden">{esc(section_title)}</h2><div class="partnership-shell" aria-label="{esc(section_title)}"><div class="partnership-layout"><div class="partnership-stage"><div class="partnership-track" id="partnership-track" tabindex="0" role="region" aria-roledescription="carousel" aria-label="{esc(aria_track)}">
{chr(10).join(slides)}
</div><button class="partnership-edge-control prev" type="button" data-direction="-1" aria-label="Previous partnership">←</button><button class="partnership-edge-control next" type="button" data-direction="1" aria-label="Next partnership">→</button></div><nav class="partnership-jumps" aria-label="Choose partnership">{nav}</nav></div></div></div></section>"""


PARTNERSHIP_CSS = """
.visually-hidden{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
#partnerships{--partnership-card-width:min(88%,1080px);--partnership-peek-gap:clamp(12px,2vw,20px)}
#partnerships .partnership-shell{margin-top:clamp(8px,2vw,20px);overflow:visible}
#partnerships .partnership-stage{position:relative;margin-inline:0;padding-inline:clamp(36px,3vw,48px);overflow:hidden}
#partnerships .partnership-track{display:grid;grid-auto-flow:column;grid-auto-columns:var(--partnership-card-width);gap:var(--partnership-peek-gap);overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;scroll-behavior:smooth;scrollbar-width:none;overscroll-behavior-inline:contain;scroll-padding-inline:0;padding-inline:0;align-items:stretch}
#partnerships .partnership-track::-webkit-scrollbar{display:none}
#partnerships .partnership-card{scroll-snap-align:start;scroll-snap-stop:normal;opacity:1;filter:none;transform:none;transition:opacity .28s ease,filter .28s ease;min-width:0;max-width:100%}
#partnerships .partnership-card:not(.is-focus){opacity:.45;filter:saturate(.85)}
#partnerships .partnership-card.is-focus{opacity:1;filter:none}
#partnerships .partnership-card-inner{border:0;background:transparent;padding:0;min-width:0}
#partnerships .partnership-kicker{margin:0 0 clamp(10px,1.6vw,16px);text-transform:uppercase;letter-spacing:.14em;font-size:10px;font-weight:800;color:var(--muted)}
#partnerships .partnership-title{margin-bottom:var(--heading-copy-gap)}
#partnerships .feature-grid{align-items:stretch;gap:clamp(24px,3.5vw,48px);grid-template-columns:minmax(0,1fr) minmax(0,1.12fr)}
#partnerships .feature-grid.reverse{grid-template-columns:minmax(0,1.12fr) minmax(0,1fr)}
#partnerships .feature-copy{border:1px solid var(--ink);background:var(--paper);padding:clamp(20px,2.5vw,32px);min-width:0}
#partnerships .feature-media{align-self:stretch;min-width:0}
#partnerships .feature-media .media-gallery{width:100%}
#partnerships .feature-media .media-gallery-slide.media-placeholder{min-height:0;border:0;background:var(--soft)}
#partnerships .feature-media .media-placeholder:before,#partnerships .feature-media .media-placeholder:after{display:none}
#partnerships .partnership-edge-control{position:absolute;z-index:9;top:42%;width:52px;height:52px;border:1px solid var(--ink);border-radius:50%;background:rgba(255,255,255,.96);display:grid;place-items:center;transform:translateY(-50%);font-size:24px;line-height:1;cursor:pointer;box-shadow:0 3px 16px rgba(0,0,0,.12)}
#partnerships .partnership-edge-control.prev{left:6px}
#partnerships .partnership-edge-control.next{right:6px}
#partnerships .partnership-edge-control:disabled{opacity:.22;cursor:default}
#partnerships .partnership-jumps{margin-top:clamp(18px,3vw,28px);display:flex;flex-wrap:wrap;justify-content:center;gap:10px}
#partnerships .partnership-jump{min-height:40px;padding:10px 16px;border:1px solid var(--ink);background:var(--paper);text-transform:uppercase;letter-spacing:.06em;font-size:10px;font-weight:800;cursor:pointer}
#partnerships .partnership-jump.is-active{background:var(--ink);color:var(--paper)}
@media(min-width:701px){#partnerships{--partnership-card-width:min(1240px,94%)}#partnerships .partnership-stage{padding-inline:clamp(52px,4vw,72px)}#partnerships .partnership-edge-control.prev{left:0}#partnerships .partnership-edge-control.next{right:0}}
@media(max-width:700px){#partnerships{--partnership-card-width:min(100%,96%)}#partnerships .partnership-stage{padding-inline:clamp(44px,var(--page-pad),52px)}#partnerships .partnership-edge-control{width:44px;height:44px;top:36%}#partnerships .feature-grid,#partnerships .feature-grid.reverse{grid-template-columns:1fr}#partnerships .feature-copy{border-width:1px 0 0}}
"""

PARTNERSHIP_JS = """;(()=>{const track=document.getElementById('partnership-track');if(!track)return;const cards=[...track.querySelectorAll('.partnership-card')];const jumps=[...document.querySelectorAll('#partnerships .partnership-jump')];const controls=[...document.querySelectorAll('#partnerships .partnership-edge-control')];const scrollBehaviour=matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth';let activeIndex=0;const update=index=>{activeIndex=Math.max(0,Math.min(cards.length-1,index));cards.forEach((card,i)=>{card.classList.toggle('is-focus',i===activeIndex);card.setAttribute('aria-hidden',i===activeIndex?'false':'true')});jumps.forEach((btn,i)=>btn.classList.toggle('is-active',i===activeIndex));if(controls[0])controls[0].disabled=activeIndex===0;if(controls[1])controls[1].disabled=activeIndex===cards.length-1};const goTo=index=>{const target=Math.max(0,Math.min(cards.length-1,index));const card=cards[target];track.scrollTo({left:card.offsetLeft-(track.clientWidth-card.offsetWidth)/2,behavior:scrollBehaviour});update(target)};controls.forEach(button=>button.addEventListener('click',()=>goTo(activeIndex+Number(button.dataset.direction))));jumps.forEach((button,index)=>button.addEventListener('click',()=>goTo(index)));track.addEventListener('keydown',event=>{if(event.key==='ArrowLeft'){event.preventDefault();goTo(activeIndex-1)}if(event.key==='ArrowRight'){event.preventDefault();goTo(activeIndex+1)}});let ticking=false;track.addEventListener('scroll',()=>{if(ticking)return;ticking=true;requestAnimationFrame(()=>{const center=track.scrollLeft+track.clientWidth/2;let nearest=0;let distance=Infinity;cards.forEach((card,index)=>{const d=Math.abs(card.offsetLeft+card.offsetWidth/2-center);if(d<distance){distance=d;nearest=index}});update(nearest);ticking=false})},{passive:true});goTo(0)})()"""


def principle_cards(values, leadership, lang: str) -> tuple[str, str]:
    val_html = []
    for r in values:
        h = r["en_h"] if lang == "en" else r["zh_h"]
        b = r["en_b"] if lang == "en" else r["zh_b"]
        val_html.append(
            f'<article class="principle-card"><div class="principle-icon" aria-hidden="true">{"Icon" if lang=="en" else "图标占位"}</div><div class="principle-body"><h3>{esc(h)}</h3><p>{esc(b)}</p></div></article>'
        )
    lead_html = []
    for r in leadership:
        h = r["en_h"] if lang == "en" else r["zh_h"]
        b = r["en_b"] if lang == "en" else r["zh_b"]
        lead_html.append(
            f'<article class="principle-card leadership-card"><div class="principle-icon" aria-hidden="true">{"Icon" if lang=="en" else "图标占位"}</div><div class="principle-body"><h3>{esc(h)}</h3><p>{esc(b)}</p></div></article>'
        )
    return "\n".join(val_html), "\n".join(lead_html)


def apply_file(path: Path, lang: str, blocks, timeline, values, leadership):
    text = path.read_text(encoding="utf-8")

    heritage = blocks["heritage"]
    if lang == "en":
        h1 = headline_html(heritage["en_h"])
        overview_body = paras(heritage["en_b"])
        vision_h = statement_h3_from_row(blocks["vision"], lang, "vision")
        mission_h = statement_h3_from_row(blocks["mission"], lang, "mission")
        mi = blocks["milestones_intro"]
        milestones_h2 = headline_html(mi["en_h"], br_after=2)
        milestones_body = f'<p class="body-copy">{esc(mi["en_b"])}</p>'
        culture = blocks["culture_intro"]
        culture_h2 = headline_html(culture["en_h"], br_after=2)
        culture_body = paras(culture["en_b"])
        ci = blocks["commitments_intro"]
        commit_h2 = headline_html(ci["en_h"], br_after=2)
        commit_intro = f'<p class="body-copy">{esc(ci["en_b"])}</p>'
        cq = blocks["commitment_quality"]
        cs = blocks["commitment_sustainability"]
        culture_tag = "04 Company Culture"
        commit_tag = "05 Our Commitments"
        values_label = "Our Values"
        leadership_label = "Our Leadership"
        sustain_h = "Sustainable Development"
        sustain_cta = cs["en_cta"] or "Download Report"
    else:
        h1 = esc(heritage["zh_h"])
        overview_body = paras(heritage["zh_b"])
        vision_h = statement_h3_from_row(blocks["vision"], lang, "vision")
        mission_h = statement_h3_from_row(blocks["mission"], lang, "mission")
        mi = blocks["milestones_intro"]
        milestones_h2 = esc(mi["zh_h"])
        milestones_body = f'<p class="body-copy">{esc(mi["zh_b"])}</p>'
        culture = blocks["culture_intro"]
        culture_h2 = esc(culture["zh_h"])
        culture_body = paras(culture["zh_b"])
        ci = blocks["commitments_intro"]
        commit_h2 = esc(ci["zh_h"])
        commit_intro = f'<p class="body-copy">{esc(ci["zh_b"])}</p>'
        cq = blocks["commitment_quality"]
        cs = blocks["commitment_sustainability"]
        culture_tag = "04 企业文化"
        commit_tag = "05 我们的承诺"
        values_label = "我们的价值观"
        leadership_label = "我们的领导力"
        sustain_h = cs["zh_h"]
        sustain_cta = cs["zh_cta"] or "下载报告"

    text = re.sub(
        r"(<h1 id=\"overview-title\">)(.*?)(</h1>)",
        lambda m: m.group(1) + h1 + m.group(3),
        text,
        count=1,
    )
    text = re.sub(
        r"(<div class=\"overview-body\">)(.*?)(</div></div><div class=\"statement-grid\">)",
        lambda m: m.group(1) + overview_body + m.group(3),
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<article class="statement-card"><div class="media-placeholder statement-media"[^>]*>.*?</div><div class="statement-copy"><span>)(.*?)(</span><h3>)(.*?)(</h3></div></article><article class="statement-card"><div class="media-placeholder statement-media"[^>]*>.*?</div><div class="statement-copy"><span>)(.*?)(</span><h3>)(.*?)(</h3></div></article>)',
        lambda m: (
            m.group(1)
            + ("Our Vision" if lang == "en" else "我们的愿景")
            + m.group(3)
            + vision_h
            + m.group(4)
            + m.group(5)
            + ("Our Mission" if lang == "en" else "我们的使命")
            + m.group(7)
            + mission_h
            + m.group(9)
        ),
        text,
        count=1,
        flags=re.DOTALL,
    )

    text = re.sub(
        r'(<h2 id="milestones-title">)(.*?)(</h2>)',
        lambda m: m.group(1) + milestones_h2 + m.group(3),
        text,
        count=1,
    )
    text = re.sub(
        r'(<div class="section-intro milestones-intro"><h2 id="milestones-title">.*?</h2>)(.*?)(</div><div class="timeline-shell")',
        lambda m: m.group(1) + milestones_body + m.group(3),
        text,
        count=1,
        flags=re.DOTALL,
    )

    cards_html = timeline_cards(timeline, lang)
    text = re.sub(
        r'(<div class="timeline-track" id="timeline-track"[^>]*>)(.*?)(</div><button class="timeline-edge-control prev")',
        lambda m: m.group(1) + cards_html + m.group(3),
        text,
        count=1,
        flags=re.DOTALL,
    )
    links = scrubber_links(timeline)
    text = re.sub(
        r'(<nav class="timeline-year-nav milestone-scrubber-track">)(.*?)(</nav>)',
        lambda m: m.group(1) + links + m.group(3),
        text,
        count=1,
        flags=re.DOTALL,
    )

    new_partnerships = partnerships_section(lang, blocks)
    text = re.sub(
        r'\s*<section class="module" id="unesco"[\s\S]*?</section>\s*<section class="module" id="fifty-best"[\s\S]*?</section>',
        "\n" + new_partnerships + "\n",
        text,
        count=1,
    )

    text = re.sub(
        r'(<section class="module" id="company-culture"[^>]*><span class="module-tag">)(.*?)(</span>)',
        lambda m: m.group(1) + esc(culture_tag) + m.group(3),
        text,
        count=1,
    )
    text = re.sub(
        r'(<h2 id="culture-title">)(.*?)(</h2><div class="body-copy">)(.*?)(</div></div><div class="culture-groups">)',
        lambda m: m.group(1) + culture_h2 + m.group(3) + culture_body + m.group(5),
        text,
        count=1,
        flags=re.DOTALL,
    )

    val_cards, lead_cards = principle_cards(values, leadership, lang)
    text = re.sub(
        r'(<div class="group-label">)(Our Values|我们的价值观)(</div><div class="principle-grid values">)(.*?)(</div></div><div class="culture-group"><div class="group-label">)',
        lambda m: m.group(1) + values_label + m.group(3) + val_cards + m.group(5),
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<div class="group-label">)(Our Leadership|我们的领导力)(</div><div class="principle-grid leadership">)(.*?)(</div></div></div></div></section>)',
        lambda m: m.group(1) + leadership_label + m.group(3) + lead_cards + m.group(5),
        text,
        count=1,
        flags=re.DOTALL,
    )

    text = re.sub(
        r'(<section class="module" id="commitments"[^>]*><span class="module-tag">)(.*?)(</span>)',
        lambda m: m.group(1) + esc(commit_tag) + m.group(3),
        text,
        count=1,
    )
    text = re.sub(
        r'(<h2 id="commitments-title">)(.*?)(</h2>)',
        lambda m: m.group(1) + commit_h2 + m.group(3),
        text,
        count=1,
    )
    text = re.sub(
        r'(<div class="intro-grid"><h2 id="commitments-title">.*?</h2>)(.*?)(</div><div class="commitment-grid">)',
        lambda m: m.group(1) + commit_intro + m.group(3),
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<div class="commitment-copy"><h3>100-1=0</h3><p>)(.*?)(</p></div></article>)',
        lambda m: m.group(1) + esc(cq["en_b"] if lang == "en" else cq["zh_b"]) + m.group(3),
        text,
        count=1,
    )
    text = re.sub(
        r'(<div class="sustainability-copy"><h3>)(.*?)(</h3><p>)(.*?)(</p><a class="sustainability-cta"[^>]*>)(.*?)(</a>)',
        lambda m: (
            m.group(1)
            + esc(sustain_h)
            + m.group(3)
            + esc(cs["en_b"] if lang == "en" else cs["zh_b"])
            + m.group(5)
            + esc(sustain_cta)
            + m.group(7)
        ),
        text,
        count=1,
        flags=re.DOTALL,
    )

    if PARTNERSHIP_CSS.strip() not in text:
        text = text.replace(
            "#milestones .timeline-edge-control.next{right:2px}}",
            "#milestones .timeline-edge-control.next{right:2px}}"
            + PARTNERSHIP_CSS,
            1,
        )

    if "partnership-track" in text and "getElementById('partnership-track')" not in text:
        text = text.replace("</script>\n</body>", PARTNERSHIP_JS + "</script>\n</body>", 1)

    path.write_text(text, encoding="utf-8")


def main():
    rows = load_rows()
    blocks, timeline, values, leadership = index_rows(rows)
    apply_file(ROOT / "en.html", "en", blocks, timeline, values, leadership)
    apply_file(ROOT / "zh-hans.html", "zh", blocks, timeline, values, leadership)
    print("Updated en.html and zh-hans.html")
    print(f"Timeline items: {len(timeline)}")


if __name__ == "__main__":
    main()
