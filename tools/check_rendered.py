"""Structural checks of built HTML; deliberately not a visual/browser test."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'textbook'
DIST = ROOT / '.vitepress/dist'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links = set(), []
        self.details = self.summaries = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'id' in values:
            self.ids.add(values['id'])
        if tag == 'a' and 'href' in values:
            self.links.append(values['href'])
        self.details += tag == 'details'
        self.summaries += tag == 'summary'


def main():
    rows = json.loads((ROOT.parent / 'curriculum.json').read_text())['chapters']
    paths = [r['file'].removesuffix('.md') + '.html' for r in rows] + ['index.html']
    paths += [p.stem + '.html' for p in ROOT.glob('appendix-*.md')]
    pages = {p.name: Page(p.read_text()) for p in DIST.glob('*.html')}
    count = 0
    for name in paths:
        page = pages[name]
        assert page.details == page.summaries, (name, 'answer summaries')
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = unquote(url.path).removeprefix('/economic-history/').removeprefix('./') or name
            if url.path in ('/economic-history/', './', '/'):
                target = 'index.html'
            if target.startswith('/') or not target.endswith('.html'):
                continue
            assert target in pages, (name, 'missing target', link)
            if url.fragment:
                assert unquote(url.fragment) in pages[target].ids, (name, 'missing anchor', link)
            count += 1
    print(f'{len(paths)} built reading pages: {count} local links/anchors and answer elements checked.')
    print('This does not execute redirects/search or verify visual layout.')


if __name__ == '__main__':
    main()
