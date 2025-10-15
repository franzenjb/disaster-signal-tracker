import requests
import pandas as pd
import feedparser
import json
from datetime import datetime, timedelta
import re
from urllib.parse import urlencode

class DisasterNewsIntelligence:
    """Real-time news and social media monitoring for disaster events"""
    
    def __init__(self):
        self.disaster_keywords = [
            'earthquake', 'wildfire', 'hurricane', 'tornado', 'flood', 'tsunami',
            'evacuation', 'emergency', 'disaster', 'storm', 'fire', 'quake',
            'landslide', 'mudslide', 'blizzard', 'drought', 'cyclone'
        ]
        
        # Major news RSS feeds
        self.news_feeds = {
            'CNN Breaking': 'http://rss.cnn.com/rss/edition.rss',
            'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml',
            'Reuters': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
            'AP News': 'https://rsshub.app/ap/topics/apf-topnews',
            'Weather Channel': 'https://feeds.weather.com/weather/rss/news',
            'USGS Earthquakes': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.atom'
        }
        
        self.reddit_disaster_subs = [
            'news', 'worldnews', 'CatastrophicFailure', 'NaturalDisasters',
            'weather', 'Wildfire', 'earthquake', 'TropicalWeather'
        ]

    def fetch_rss_news(self):
        """Fetch breaking news from RSS feeds and filter for disaster content"""
        news_items = []
        
        for source, url in self.news_feeds.items():
            try:
                print(f"📰 Fetching {source}...")
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:10]:  # Last 10 items per feed
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    link = entry.get('link', '')
                    published = entry.get('published', '')
                    
                    # Check if disaster-related
                    text_to_check = f"{title} {summary}".lower()
                    if any(keyword in text_to_check for keyword in self.disaster_keywords):
                        news_items.append({
                            'source': source,
                            'type': 'RSS_NEWS',
                            'title': title,
                            'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                            'url': link,
                            'published': published,
                            'keywords_found': [kw for kw in self.disaster_keywords if kw in text_to_check],
                            'timestamp': datetime.now().isoformat()
                        })
                        
            except Exception as e:
                print(f"❌ Error fetching {source}: {e}")
                continue
        
        return news_items

    def search_reddit_disasters(self):
        """Search Reddit for disaster discussions"""
        reddit_posts = []
        
        for subreddit in self.reddit_disaster_subs:
            try:
                # Use Reddit's JSON API (no auth required for public posts)
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"
                headers = {'User-Agent': 'DisasterTracker/1.0'}
                
                print(f"🔍 Searching r/{subreddit}...")
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for post in data['data']['children']:
                        post_data = post['data']
                        title = post_data.get('title', '')
                        selftext = post_data.get('selftext', '')
                        
                        text_to_check = f"{title} {selftext}".lower()
                        if any(keyword in text_to_check for keyword in self.disaster_keywords):
                            reddit_posts.append({
                                'source': f'r/{subreddit}',
                                'type': 'REDDIT',
                                'title': title,
                                'summary': selftext[:200] + '...' if len(selftext) > 200 else selftext,
                                'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                'score': post_data.get('score', 0),
                                'comments': post_data.get('num_comments', 0),
                                'keywords_found': [kw for kw in self.disaster_keywords if kw in text_to_check],
                                'timestamp': datetime.now().isoformat()
                            })
                
            except Exception as e:
                print(f"❌ Error searching r/{subreddit}: {e}")
                continue
        
        return reddit_posts

    def search_news_api(self, query="natural disaster OR earthquake OR wildfire OR hurricane"):
        """Search news using web search for recent disaster coverage"""
        news_results = []
        
        try:
            # Using firecrawl search since it's available
            from mcp__firecrawl__firecrawl_search import firecrawl_search
            
            print(f"🔍 Searching news for: {query}")
            
            # Search for recent disaster news
            results = firecrawl_search(
                query=f"{query} site:reuters.com OR site:cnn.com OR site:bbc.com OR site:apnews.com",
                limit=20,
                sources=[{"type": "news"}]
            )
            
            for result in results.get('data', []):
                news_results.append({
                    'source': 'NEWS_SEARCH',
                    'type': 'WEB_NEWS',
                    'title': result.get('title', ''),
                    'summary': result.get('description', '')[:200] + '...',
                    'url': result.get('url', ''),
                    'published': result.get('publishedAt', ''),
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"❌ News search error: {e}")
        
        return news_results

    def correlate_with_disasters(self, news_data, disaster_data):
        """Correlate news reports with actual disaster data"""
        correlations = []
        
        # Load disaster data
        disasters_df = pd.read_csv(disaster_data)
        
        for news_item in news_data:
            title_text = news_item.get('title', '').lower()
            summary_text = news_item.get('summary', '').lower()
            
            # Look for location matches
            for _, disaster in disasters_df.iterrows():
                disaster_area = str(disaster.get('area', '')).lower()
                disaster_place = str(disaster.get('place', '')).lower()
                
                # Simple correlation based on location mentions
                if (disaster_area and any(word in title_text + summary_text 
                                        for word in disaster_area.split() if len(word) > 3)) or \
                   (disaster_place and any(word in title_text + summary_text 
                                         for word in disaster_place.split() if len(word) > 3)):
                    
                    correlations.append({
                        'news_title': news_item['title'],
                        'news_source': news_item['source'],
                        'news_url': news_item['url'],
                        'disaster_type': disaster.get('event', ''),
                        'disaster_source': disaster.get('source', ''),
                        'disaster_location': disaster_area or disaster_place,
                        'disaster_coords': f"{disaster.get('lat', '')}, {disaster.get('lon', '')}",
                        'correlation_strength': 'LOCATION_MATCH',
                        'timestamp': datetime.now().isoformat()
                    })
        
        return correlations

    def generate_intelligence_report(self):
        """Generate comprehensive disaster intelligence report"""
        print("🚨 GENERATING DISASTER INTELLIGENCE REPORT...")
        
        # Fetch all news sources
        rss_news = self.fetch_rss_news()
        reddit_posts = self.search_reddit_disasters()
        web_news = self.search_news_api()
        
        all_news = rss_news + reddit_posts + web_news
        
        # Correlate with disaster data
        correlations = self.correlate_with_disasters(all_news, 'combined_disaster_feed.csv')
        
        # Generate report
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_news_items': len(all_news),
            'rss_items': len(rss_news),
            'reddit_items': len(reddit_posts),
            'web_news_items': len(web_news),
            'correlations_found': len(correlations),
            'news_items': all_news,
            'correlations': correlations
        }
        
        # Save to files
        with open('disaster_intelligence_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Create CSV for easy analysis
        if all_news:
            news_df = pd.DataFrame(all_news)
            news_df.to_csv('disaster_news_feed.csv', index=False)
        
        if correlations:
            corr_df = pd.DataFrame(correlations)
            corr_df.to_csv('news_disaster_correlations.csv', index=False)
        
        return report

if __name__ == "__main__":
    intelligence = DisasterNewsIntelligence()
    report = intelligence.generate_intelligence_report()
    
    print("\n📊 DISASTER INTELLIGENCE SUMMARY:")
    print(f"📰 News items collected: {report['total_news_items']}")
    print(f"🔗 Correlations found: {report['correlations_found']}")
    print(f"📡 RSS feeds: {report['rss_items']}")
    print(f"🗨️ Reddit posts: {report['reddit_items']}")
    print(f"🌐 Web news: {report['web_news_items']}")
    
    if report['correlations_found'] > 0:
        print("\n🎯 TOP CORRELATIONS:")
        for corr in report['correlations'][:5]:
            print(f"  • {corr['news_title'][:60]}... → {corr['disaster_type']} in {corr['disaster_location']}")
    
    print("\n✅ Intelligence report saved to disaster_intelligence_report.json")