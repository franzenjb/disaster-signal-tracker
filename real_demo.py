import requests
import feedparser
import json
from datetime import datetime, timedelta
import re

def demo_reddit_monitoring():
    """Show real Reddit disaster monitoring in action"""
    print("🔍 LIVE REDDIT MONITORING DEMO")
    print("=" * 50)
    
    # Monitor key disaster subreddits
    subreddits = ['news', 'worldnews', 'CatastrophicFailure', 'NaturalDisasters']
    disaster_keywords = ['earthquake', 'fire', 'flood', 'hurricane', 'tornado', 'disaster', 'emergency', 'evacuation']
    
    live_discussions = []
    
    for sub in subreddits:
        print(f"\n📡 Scanning r/{sub}...")
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=25"
            headers = {'User-Agent': 'DisasterDemo/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                found_count = 0
                
                for post in data['data']['children']:
                    post_data = post['data']
                    title = post_data.get('title', '').lower()
                    selftext = post_data.get('selftext', '').lower()
                    
                    # Check for disaster keywords
                    text_to_scan = f"{title} {selftext}"
                    found_keywords = [kw for kw in disaster_keywords if kw in text_to_scan]
                    
                    if found_keywords:
                        found_count += 1
                        live_discussions.append({
                            'subreddit': sub,
                            'title': post_data.get('title', ''),
                            'score': post_data.get('score', 0),
                            'comments': post_data.get('num_comments', 0),
                            'url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'keywords': found_keywords,
                            'created': datetime.fromtimestamp(post_data.get('created_utc', 0)),
                            'hours_ago': (datetime.now() - datetime.fromtimestamp(post_data.get('created_utc', 0))).total_seconds() / 3600
                        })
                
                print(f"   Found {found_count} disaster-related posts")
            else:
                print(f"   ❌ Failed to access r/{sub}")
                
        except Exception as e:
            print(f"   ❌ Error with r/{sub}: {e}")
    
    # Show top results
    if live_discussions:
        print(f"\n🎯 TOP LIVE DISASTER DISCUSSIONS ({len(live_discussions)} total found):")
        print("-" * 80)
        
        # Sort by engagement (score + comments)
        live_discussions.sort(key=lambda x: x['score'] + x['comments'], reverse=True)
        
        for i, discussion in enumerate(live_discussions[:10], 1):
            hours = int(discussion['hours_ago'])
            print(f"\n{i}. 📊 {discussion['score']} upvotes, {discussion['comments']} comments ({hours}h ago)")
            print(f"   📍 r/{discussion['subreddit']}")
            print(f"   📰 {discussion['title'][:80]}...")
            print(f"   🔍 Keywords: {', '.join(discussion['keywords'])}")
            print(f"   🔗 {discussion['url']}")
    
    return live_discussions

def demo_rss_monitoring():
    """Show real RSS feed monitoring in action"""
    print("\n\n📰 LIVE RSS FEED MONITORING DEMO")
    print("=" * 50)
    
    # Real RSS feeds from major news sources
    feeds = {
        'BBC Breaking': 'http://feeds.bbci.co.uk/news/rss.xml',
        'CNN Breaking': 'http://rss.cnn.com/rss/edition.rss',
        'Reuters Top': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
        'AP Breaking': 'https://rsshub.app/ap/topics/apf-topnews',
        'USGS Earthquakes': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.atom'
    }
    
    disaster_keywords = ['earthquake', 'fire', 'flood', 'hurricane', 'tornado', 'disaster', 'emergency', 'storm', 'wildfire', 'tsunami', 'evacuation']
    breaking_news = []
    
    for source, feed_url in feeds.items():
        print(f"\n📡 Fetching {source}...")
        try:
            feed = feedparser.parse(feed_url)
            found_count = 0
            
            for entry in feed.entries[:15]:  # Check latest 15 items
                title = entry.get('title', '')
                summary = entry.get('summary', entry.get('description', ''))
                
                # Check for disaster content
                text_to_scan = f"{title} {summary}".lower()
                found_keywords = [kw for kw in disaster_keywords if kw in text_to_scan]
                
                if found_keywords:
                    found_count += 1
                    published = entry.get('published', '')
                    
                    breaking_news.append({
                        'source': source,
                        'title': title,
                        'summary': summary[:150] + '...' if len(summary) > 150 else summary,
                        'url': entry.get('link', ''),
                        'published': published,
                        'keywords': found_keywords
                    })
            
            print(f"   Found {found_count} disaster-related stories")
            
        except Exception as e:
            print(f"   ❌ Error fetching {source}: {e}")
    
    # Show breaking news
    if breaking_news:
        print(f"\n🚨 BREAKING DISASTER NEWS ({len(breaking_news)} stories found):")
        print("-" * 80)
        
        for i, story in enumerate(breaking_news[:8], 1):
            print(f"\n{i}. 📺 {story['source']}")
            print(f"   📰 {story['title']}")
            print(f"   📝 {story['summary']}")
            print(f"   🔍 Keywords: {', '.join(story['keywords'])}")
            print(f"   🔗 {story['url']}")
            if story['published']:
                print(f"   📅 {story['published']}")
    
    return breaking_news

def demonstrate_correlation():
    """Show how we can correlate social media discussions with news"""
    print("\n\n🔗 CORRELATION ANALYSIS DEMO")
    print("=" * 50)
    
    reddit_data = demo_reddit_monitoring()
    news_data = demo_rss_monitoring()
    
    # Find common disaster topics
    reddit_keywords = set()
    news_keywords = set()
    
    for item in reddit_data:
        reddit_keywords.update(item['keywords'])
    
    for item in news_data:
        news_keywords.update(item['keywords'])
    
    common_topics = reddit_keywords.intersection(news_keywords)
    
    if common_topics:
        print(f"\n🎯 TRENDING DISASTER TOPICS (mentioned in both news AND social media):")
        for topic in common_topics:
            reddit_mentions = len([r for r in reddit_data if topic in r['keywords']])
            news_mentions = len([n for n in news_data if topic in n['keywords']])
            print(f"   🔥 {topic.upper()}: {news_mentions} news stories, {reddit_mentions} Reddit discussions")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'reddit_discussions': len(reddit_data),
        'news_stories': len(news_data),
        'trending_topics': list(common_topics),
        'sample_reddit': reddit_data[:3],
        'sample_news': news_data[:3]
    }
    
    with open('live_demo_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Demo results saved to live_demo_results.json")
    print(f"📊 SUMMARY: {len(reddit_data)} Reddit posts + {len(news_data)} news stories monitored")

if __name__ == "__main__":
    print("🚨 REAL-TIME DISASTER INTELLIGENCE DEMO")
    print("🕐 Starting live monitoring...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    demonstrate_correlation()