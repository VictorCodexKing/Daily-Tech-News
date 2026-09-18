"""Sample feed fixtures for offline parsing tests."""

# A small, well-formed RSS 2.0 feed with three entries. One title contains
# HTML-special characters so escaping behaviour can be exercised downstream.
SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Sample Tech News</title>
    <link>https://example.com/</link>
    <description>Sample feed for tests</description>
    <item>
      <title>First headline about Rust &amp; Go</title>
      <link>https://example.com/articles/1</link>
      <pubDate>Mon, 01 Jan 2024 08:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Second headline &lt;breaking&gt;</title>
      <link>https://example.com/articles/2</link>
      <pubDate>Mon, 01 Jan 2024 09:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Third headline</title>
      <link>https://example.com/articles/3</link>
      <pubDate>Mon, 01 Jan 2024 10:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""

# Content that feedparser cannot turn into any usable entries.
MALFORMED_FEED = "this is not a feed at all <<<>>> &&& %%%"

# A well-formed RSS 2.0 feed whose entries all lack a usable title or link,
# so parse_feed drops every one and returns an empty list (without raising).
EMPTY_ENTRIES_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Sample Tech News</title>
    <link>https://example.com/</link>
    <description>Feed whose entries are all unusable</description>
    <item>
      <link>https://example.com/articles/1</link>
      <pubDate>Mon, 01 Jan 2024 08:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Has a title but no link</title>
      <pubDate>Mon, 01 Jan 2024 09:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""
