"""Render cv.yaml as a plain HTML page (no JavaScript) at dist/index.html.

RenderCV makes the PDF; this makes the web page from the same data.
Run through build.sh, which provides PyYAML.
"""
import datetime
import html
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
PDF = 'afonso-azaruja-cv.pdf'
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
NETWORKS = {'LinkedIn': 'https://www.linkedin.com/in/{}', 'GitHub': 'https://github.com/{}'}


def inline(text: str) -> str:
    """The Markdown RenderCV accepts in our fields: [links](url) and **bold**."""
    out = html.escape(str(text), quote=False)
    out = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', out)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', out)


def plain(text: str) -> str:
    return re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', str(text)).replace('**', '')


def month(value) -> str:
    if str(value) == 'present':
        return 'present'
    year, _, m = str(value).partition('-')
    return f'{MONTHS[int(m) - 1]} {year}' if m else year


def when(entry: dict) -> str:
    if entry.get('date'):
        return month(entry['date'])
    return f"{month(entry['start_date'])} – {month(entry['end_date'])}"


def entry(title: str, entry: dict, sub: str = '') -> str:
    parts = [f'<article><header><h3>{inline(title)}</h3><time>{when(entry)}</time></header>']
    if sub:
        parts.append(f'<p class="sub">{inline(sub)}</p>')
    if entry.get('summary'):
        parts.append(f'<p>{inline(entry["summary"])}</p>')
    if entry.get('highlights'):
        parts.append('<ul>' + ''.join(f'<li>{inline(h)}</li>' for h in entry['highlights']) + '</ul>')
    return ''.join(parts) + '</article>'


def main() -> None:
    cv = yaml.safe_load((ROOT / 'cv.yaml').read_text())['cv']
    s = cv['sections']
    profiles = [(n['network'], NETWORKS[n['network']].format(n['username'])) for n in cv['social_networks']]

    links = [f'<a href="mailto:{cv["email"]}">{cv["email"]}</a>',
             f'<a href="{cv["website"]}">{cv["website"].split("//")[1].rstrip("/")}</a>',
             *(f'<a href="{url}">{name}</a>' for name, url in profiles)]

    sections = [
        ('Experience', [entry(e['company'], e, e['position']) for e in s['experience']]),
        ('Education', [entry(e['institution'], e, f"{e['degree']} in {e['area']}") for e in s['education']]),
        ('Projects', [entry(p['name'], p) for p in s['projects']]),
    ]
    body = ''.join(f'<section><h2>{t}</h2>{"".join(items)}</section>' for t, items in sections)
    body += '<section><h2>Skills</h2><dl>' + ''.join(
        f'<div><dt>{inline(k["label"])}</dt><dd>{inline(k["details"])}</dd></div>' for k in s['skills']) + '</dl></section>'

    job = s['experience'][0]
    school = s['education'][0]
    person = {
        '@context': 'https://schema.org',
        '@type': 'Person',
        'name': cv['name'],
        'jobTitle': cv['headline'],
        'url': cv['website'],
        'email': f'mailto:{cv["email"]}',
        'homeLocation': {'@type': 'Place', 'name': cv['location']},
        'worksFor': {'@type': 'Organization', 'name': plain(job['company'])},
        'alumniOf': {'@type': 'CollegeOrUniversity', 'name': plain(school['institution'])},
        'knowsAbout': [x.strip() for k in s['skills'] if k['label'] != 'Spoken' for x in k['details'].split(',')],
        'sameAs': [url for _, url in profiles],
    }

    page = (ROOT / 'template.html').read_text()
    for key, value in {
        'name': html.escape(cv['name']),
        'headline': html.escape(cv['headline']),
        'location': html.escape(cv['location']),
        'links': ' · '.join(links),
        'pdf': PDF,
        'body': body,
        'updated': datetime.date.today().strftime('%B %Y'),
        'jsonld': json.dumps(person, ensure_ascii=False).replace('</', '<\\/'),
    }.items():
        page = page.replace('{{' + key + '}}', value)
    (ROOT / 'dist' / 'index.html').write_text(page)


if __name__ == '__main__':
    main()
