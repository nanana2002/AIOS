# RSS Connector Node

A MOFA node that provides RSS feed parsing and content extraction functionality. This node can fetch and parse RSS feeds from various sources, extracting news articles and other content with proper URL handling for redirected links.

## Features

- **RSS Feed Parsing**: Parse RSS feeds from any valid RSS URL
- **URL Redirection Handling**: Automatically handles redirected URLs (especially for Sina RSS feeds)
- **Article Extraction**: Extracts title, summary, URL, and publication time
- **JSON Output**: Returns structured JSON data for easy processing
- **Chinese Content Support**: Full support for Chinese characters and encoding
- **Error Resilience**: Robust error handling for malformed URLs and feeds
- **MOFA Integration**: Seamless integration with MOFA agent framework

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `rss_url` | string | Yes | The RSS feed URL to parse and extract content from |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `rss_content` | string (JSON) | Parsed RSS content including articles with title, summary, URL, and time |

## Usage Example

### Basic Dataflow Configuration

```yaml
# hello_rss_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      agent_response: rss_connector-agent/rss_content
  - id: rss_connector-agent
    build: pip install -e ../../agent-hub/rss-connector
    path: rss-connector
    outputs:
      - rss_content
    inputs:
      rss_url: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### Running the Node

1. **Start the MOFA framework:**
   ```bash
   dora up
   ```

2. **Build and start the dataflow:**
   ```bash
   dora build hello_rss_dataflow.yml
   dora start hello_rss_dataflow.yml
   ```

3. **Provide RSS URL:**
   Enter an RSS feed URL (e.g., `http://rss.sina.com.cn/news.xml`) and the node will parse and return the content.

## Code Example

The core functionality is implemented in `main.py`:

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
import feedparser
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote

def extract_real_url(redirect_url):
    """
    Handle redirected URLs, especially for Sina RSS feeds
    Example: http://go.rss.sina.com.cn/redirect.php?url=http%3A%2F%2Fnews.sina.com.cn%2F...
    """
    try:
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)
        encoded_url = params.get('url', [''])[0]
        decoded_url = unquote(encoded_url)
        
        # Handle multiple encoding layers
        while '%' in decoded_url:
            prev_decoded = decoded_url
            decoded_url = unquote(decoded_url)
            if decoded_url == prev_decoded:
                break
                
        return decoded_url or redirect_url
    except Exception as e:
        print(f"URL parsing failed: {e}")
        return redirect_url

def parse_rss(rss_url):
    """Parse RSS feed and extract articles"""
    feed = feedparser.parse(rss_url)
    news_list = []
    
    for entry in feed.entries:
        news_item = {
            "title": entry.get("title", ""),
            "summary": entry.get("description", ""),
            "url": extract_real_url(entry.get("link", "")),
            "time": entry.published
        }
        news_list.append(news_item)
    
    return json.dumps(news_list, ensure_ascii=False, indent=2)

@run_agent
def run(agent: MofaAgent):
    rss_url = agent.receive_parameter('rss_url')
    result_data = parse_rss(rss_url)
    agent.send_output(agent_output_name='rss_content', agent_result=result_data)

def main():
    agent = MofaAgent(agent_name='rss-connector')
    run(agent=agent)
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **feedparser** (6.0.11): RSS feed parsing library
- **mofa**: MOFA framework (automatically available in MOFA environment)

## Key Features

### RSS Feed Support
- **Standard RSS**: Supports RSS 2.0, RSS 1.0, and Atom feeds
- **Multiple Sources**: Compatible with news sites, blogs, and content aggregators
- **Encoding Handling**: Proper handling of various character encodings
- **Feed Validation**: Graceful handling of malformed or incomplete feeds

### URL Processing
- **Redirect Resolution**: Automatically resolves redirected URLs
- **URL Decoding**: Handles URL-encoded parameters and special characters
- **Multi-layer Decoding**: Processes multiple levels of URL encoding
- **Error Recovery**: Falls back to original URL if processing fails

### Content Extraction
- **Article Metadata**: Extracts title, description, URL, and publication time
- **JSON Formatting**: Returns well-structured JSON for easy processing
- **Unicode Support**: Full support for international characters
- **Data Validation**: Ensures extracted data is properly formatted

## Use Cases

### News Aggregation
- **News Monitoring**: Monitor multiple news sources for breaking news
- **Content Curation**: Aggregate content from various RSS feeds
- **Trend Analysis**: Analyze news trends across different sources
- **Alert Systems**: Create alerts based on specific news keywords

### Content Management
- **Blog Aggregation**: Collect blog posts from multiple sources
- **Content Distribution**: Redistribute content from RSS feeds
- **Archive Creation**: Build content archives from RSS sources
- **Feed Analysis**: Analyze feed patterns and publishing schedules

### Research and Monitoring
- **Academic Sources**: Monitor academic publications and research feeds
- **Industry Updates**: Track industry-specific news and updates
- **Competitive Intelligence**: Monitor competitor announcements and updates
- **Market Research**: Gather market intelligence from news sources

## Supported RSS Sources
```bash
# "Google News"
  url: "https://news.google.com/rss"
# "BBC News"
  url: "http://feeds.bbci.co.uk/news/world/rss.xml"
# "纽约时报"
  url: "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
# "36氪"
  url: "https://36kr.com/feed"
# "少数派"
  url: "https://sspai.com/feed"
# "InfoQ"
  url: "https://www.infoq.cn/feed"
# "Hacker News"
  url: "https://news.ycombinator.com/rss"
```
```

## Output Format

The node returns JSON data with the following structure:

```json
[
  {
    "title": "Article Title",
    "summary": "Article summary or description",
    "url": "https://actual-article-url.com/article",
    "time": "Thu, 01 Jan 2024 12:00:00 GMT"
  },
  {
    "title": "Another Article",
    "summary": "Another article description",
    "url": "https://another-url.com/article",
    "time": "Thu, 01 Jan 2024 11:30:00 GMT"
  }
]
```

## Advanced Configuration

### Custom URL Processing
```python
def custom_url_processor(url):
    """Custom URL processing for specific sources"""
    if "custom-site.com" in url:
        # Custom processing logic
        return process_custom_site_url(url)
    return extract_real_url(url)
```

### Feed Filtering
```python
def filter_articles(articles, keywords):
    """Filter articles by keywords"""
    filtered = []
    for article in articles:
        if any(keyword.lower() in article['title'].lower() for keyword in keywords):
            filtered.append(article)
    return filtered
```

## Troubleshooting

### Common Issues
1. **Invalid RSS URLs**: Verify the RSS feed URL is valid and accessible
2. **Network Errors**: Check internet connectivity and feed server status
3. **Encoding Issues**: Some feeds may have character encoding problems
4. **Redirected URLs**: The node handles most redirects, but some may fail

### Debug Tips
- Test RSS URLs in a browser first to verify they're accessible
- Check feed validity using online RSS validators
- Monitor network connectivity during feed parsing
- Use the feedparser library directly for debugging specific feeds

### Feed Validation
```python
# Test if a feed is valid
import feedparser

def validate_feed(url):
    feed = feedparser.parse(url)
    if feed.bozo:
        print(f"Feed has issues: {feed.bozo_exception}")
    return len(feed.entries) > 0
```

## Performance Considerations

### Optimization
- **Caching**: Consider caching feed content for frequently accessed feeds
- **Rate Limiting**: Be respectful of feed server rate limits
- **Parallel Processing**: For multiple feeds, consider parallel processing
- **Error Handling**: Implement timeouts for slow-responding feeds

### Scalability
- **Feed Management**: Keep track of feed update frequencies
- **Resource Usage**: Monitor memory usage for large feeds
- **Network Bandwidth**: Consider bandwidth usage for high-frequency polling
- **Storage**: Plan for storage of historical feed data if needed

## Contributing

1. Add support for additional RSS feed formats
2. Improve URL extraction for more redirect patterns
3. Add content filtering and categorization features
4. Implement feed validation and health checking

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Feedparser Documentation](https://feedparser.readthedocs.io/)
- [RSS Specification](https://www.rssboard.org/rss-specification)