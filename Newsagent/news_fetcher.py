"""
News Fetcher Module
Handles fetching news from various sources including NewsAPI and RSS feeds.
"""

import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import feedparser
from config import Config

logger = logging.getLogger(__name__)


class NewsFetcher:
    """
    Fetches news articles from multiple sources.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the News Fetcher.
        
        Args:
            config: Configuration object containing API keys and settings
        """
        self.config = config
        self.newsapi_key = config.newsapi_key
        self.newsapi_url = "https://newsapi.org/v2/everything"
        
    def fetch_by_topic(self, topic: str, days_back: int = 1, language: str = 'en') -> List[Dict]:
        """
        Fetch news articles by topic.
        
        Args:
            topic: Topic to search for
            days_back: Number of days to look back (default: 1)
            language: Language code (default: 'en')
            
        Returns:
            List of news articles
        """
        articles = []
        
        # Try NewsAPI first
        if self.newsapi_key and self.newsapi_key != 'your-newsapi-key-here':
            try:
                newsapi_articles = self._fetch_from_newsapi(topic, days_back, language)
                articles.extend(newsapi_articles)
                logger.info(f"Fetched {len(newsapi_articles)} articles from NewsAPI")
            except Exception as e:
                logger.error(f"Error fetching from NewsAPI: {str(e)}")
        
        # Try RSS feeds as backup or additional source
        try:
            rss_articles = self._fetch_from_rss(topic)
            articles.extend(rss_articles)
            logger.info(f"Fetched {len(rss_articles)} articles from RSS feeds")
        except Exception as e:
            logger.error(f"Error fetching from RSS: {str(e)}")
        
        return articles
    
    def _fetch_from_newsapi(self, topic: str, days_back: int, language: str) -> List[Dict]:
        """
        Fetch articles from NewsAPI.
        
        Args:
            topic: Topic to search for
            days_back: Number of days to look back
            language: Language code
            
        Returns:
            List of articles from NewsAPI
        """
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        params = {
            'q': topic,
            'from': from_date,
            'language': language,
            'sortBy': 'publishedAt',
            'apiKey': self.newsapi_key,
            'pageSize': 100  # Maximum allowed by NewsAPI
        }
        
        try:
            response = requests.get(self.newsapi_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                return articles
            else:
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return []
    
    def _fetch_from_rss(self, topic: str) -> List[Dict]:
        """
        Fetch articles from RSS feeds.
        
        Args:
            topic: Topic to search for (used to select relevant feeds)
            
        Returns:
            List of articles from RSS feeds
        """
        # Common RSS feeds categorized by topic
        rss_feeds = {
            'technology': [
                'https://techcrunch.com/feed/',
                'https://www.theverge.com/rss/index.xml',
                'https://www.wired.com/feed/rss',
            ],
            'business': [
                'https://feeds.bbci.co.uk/news/business/rss.xml',
                'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            ],
            'science': [
                'https://www.sciencedaily.com/rss/all.xml',
                'https://www.nature.com/nature.rss',
            ],
            'general': [
                'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
                'https://feeds.bbci.co.uk/news/rss.xml',
                'https://www.theguardian.com/world/rss',
            ]
        }
        
        # Select feeds based on topic
        feeds_to_check = rss_feeds.get('general', [])
        topic_lower = topic.lower()
        
        for category, feeds in rss_feeds.items():
            if category in topic_lower:
                feeds_to_check = feeds
                break
        
        articles = []
        
        for feed_url in feeds_to_check:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:20]:  # Limit to 20 per feed
                    article = {
                        'title': entry.get('title', ''),
                        'url': entry.get('link', ''),
                        'description': entry.get('summary', ''),
                        'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '',
                        'publishedAt': entry.get('published', datetime.now().isoformat()),
                        'source': {
                            'name': feed.feed.get('title', 'RSS Feed')
                        }
                    }
                    
                    # Filter by topic relevance
                    if self._is_relevant(article, topic):
                        articles.append(article)
                        
            except Exception as e:
                logger.error(f"Error parsing feed {feed_url}: {str(e)}")
                continue
        
        return articles
    
    def _is_relevant(self, article: Dict, topic: str) -> bool:
        """
        Check if an article is relevant to the topic.
        
        Args:
            article: Article dictionary
            topic: Topic to check against
            
        Returns:
            True if relevant, False otherwise
        """
        topic_lower = topic.lower()
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = article.get('content', '').lower()
        
        # Check if topic appears in title, description, or content
        return (topic_lower in title or 
                topic_lower in description or 
                topic_lower in content)
    
    def fetch_from_url(self, url: str) -> Optional[Dict]:
        """
        Fetch a specific article from a URL.
        
        Args:
            url: URL of the article
            
        Returns:
            Article dictionary or None if failed
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Basic article extraction (you might want to use newspaper3k or similar)
            return {
                'url': url,
                'title': 'Article from URL',
                'content': response.text,
                'source': {'name': 'Direct URL'},
                'publishedAt': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching from URL: {str(e)}")
            return None
    
    def fetch_trending(self, country: str = 'us', category: Optional[str] = None) -> List[Dict]:
        """
        Fetch trending/top headlines.
        
        Args:
            country: Country code (default: 'us')
            category: Category (business, entertainment, general, health, science, sports, technology)
            
        Returns:
            List of trending articles
        """
        if not self.newsapi_key or self.newsapi_key == 'your-newsapi-key-here':
            logger.warning("NewsAPI key not configured. Cannot fetch trending articles.")
            return []
        
        url = "https://newsapi.org/v2/top-headlines"
        
        params = {
            'country': country,
            'apiKey': self.newsapi_key,
            'pageSize': 100
        }
        
        if category:
            params['category'] = category
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                return data.get('articles', [])
            else:
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return []
