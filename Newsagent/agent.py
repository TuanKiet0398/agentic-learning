"""
Autonomous News Agent
Main agent class that orchestrates news fetching, processing, and summarization.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from news_fetcher import NewsFetcher
from summarizer import NewsSummarizer
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsAgent:
    """
    Autonomous AI News Agent that fetches, processes, and summarizes news articles.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the News Agent.
        
        Args:
            config: Configuration object. If None, uses default Config.
        """
        self.config = config or Config()
        self.fetcher = NewsFetcher(self.config)
        self.summarizer = NewsSummarizer(self.config)
        self.processed_articles = []
        
    def fetch_news(self, topics: List[str], days_back: int = 1) -> List[Dict]:
        """
        Fetch news articles for given topics.
        
        Args:
            topics: List of topics to search for
            days_back: How many days back to fetch news (default: 1)
            
        Returns:
            List of news articles
        """
        logger.info(f"Fetching news for topics: {topics}")
        all_articles = []
        
        for topic in topics:
            articles = self.fetcher.fetch_by_topic(topic, days_back=days_back)
            all_articles.extend(articles)
            logger.info(f"Found {len(articles)} articles for topic: {topic}")
        
        # Remove duplicates based on URL
        unique_articles = self._deduplicate_articles(all_articles)
        logger.info(f"Total unique articles: {len(unique_articles)}")
        
        return unique_articles
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on URL."""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles
    
    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Process and enrich articles with AI-generated summaries and analysis.
        
        Args:
            articles: List of news articles to process
            
        Returns:
            List of processed articles with summaries and metadata
        """
        logger.info(f"Processing {len(articles)} articles...")
        processed = []
        
        for i, article in enumerate(articles, 1):
            try:
                logger.info(f"Processing article {i}/{len(articles)}: {article.get('title', 'Untitled')}")
                
                # Generate summary
                summary = self.summarizer.summarize_article(article)
                
                # Extract key information
                key_points = self.summarizer.extract_key_points(article)
                
                # Determine sentiment
                sentiment = self.summarizer.analyze_sentiment(article)
                
                # Create processed article
                processed_article = {
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'published_at': article.get('publishedAt', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'ai_summary': summary,
                    'key_points': key_points,
                    'sentiment': sentiment,
                    'processed_at': datetime.now().isoformat()
                }
                
                processed.append(processed_article)
                
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                continue
        
        self.processed_articles = processed
        logger.info(f"Successfully processed {len(processed)} articles")
        return processed
    
    def filter_by_sentiment(self, sentiment: str) -> List[Dict]:
        """
        Filter processed articles by sentiment.
        
        Args:
            sentiment: Sentiment to filter by ('positive', 'negative', 'neutral')
            
        Returns:
            Filtered list of articles
        """
        return [
            article for article in self.processed_articles
            if article.get('sentiment', '').lower() == sentiment.lower()
        ]
    
    def filter_by_source(self, source: str) -> List[Dict]:
        """
        Filter processed articles by source.
        
        Args:
            source: Source name to filter by
            
        Returns:
            Filtered list of articles
        """
        return [
            article for article in self.processed_articles
            if source.lower() in article.get('source', '').lower()
        ]
    
    def get_top_articles(self, n: int = 5) -> List[Dict]:
        """
        Get top N articles (sorted by relevance).
        
        Args:
            n: Number of articles to return
            
        Returns:
            Top N articles
        """
        return self.processed_articles[:n]
    
    def generate_report(self, format: str = 'text') -> str:
        """
        Generate a formatted report of processed articles.
        
        Args:
            format: Output format ('text', 'markdown', 'html')
            
        Returns:
            Formatted report string
        """
        if not self.processed_articles:
            return "No articles to report."
        
        if format == 'markdown':
            return self._generate_markdown_report()
        elif format == 'html':
            return self._generate_html_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate plain text report."""
        report = []
        report.append("=" * 80)
        report.append(f"NEWS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Articles: {len(self.processed_articles)}")
        report.append("=" * 80)
        report.append("")
        
        for i, article in enumerate(self.processed_articles, 1):
            report.append(f"\n[{i}] {article['title']}")
            report.append(f"Source: {article['source']} | Published: {article['published_at']}")
            report.append(f"Sentiment: {article['sentiment']}")
            report.append(f"\nSummary: {article['ai_summary']}")
            report.append(f"\nKey Points:")
            for point in article.get('key_points', []):
                report.append(f"  • {point}")
            report.append(f"\nRead more: {article['url']}")
            report.append("-" * 80)
        
        return "\n".join(report)
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown report."""
        report = []
        report.append(f"# News Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Total Articles:** {len(self.processed_articles)}\n")
        report.append("---\n")
        
        for i, article in enumerate(self.processed_articles, 1):
            report.append(f"## {i}. {article['title']}\n")
            report.append(f"**Source:** {article['source']} | **Published:** {article['published_at']}")
            report.append(f"**Sentiment:** {article['sentiment']}\n")
            report.append(f"### Summary\n{article['ai_summary']}\n")
            report.append(f"### Key Points\n")
            for point in article.get('key_points', []):
                report.append(f"- {point}")
            report.append(f"\n[Read full article]({article['url']})\n")
            report.append("---\n")
        
        return "\n".join(report)
    
    def _generate_html_report(self) -> str:
        """Generate HTML report."""
        report = []
        report.append("<!DOCTYPE html>")
        report.append("<html><head><title>News Report</title>")
        report.append("<style>")
        report.append("body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }")
        report.append("h1 { color: #333; }")
        report.append(".article { border: 1px solid #ddd; padding: 15px; margin: 20px 0; border-radius: 5px; }")
        report.append(".meta { color: #666; font-size: 0.9em; }")
        report.append(".sentiment { display: inline-block; padding: 3px 8px; border-radius: 3px; }")
        report.append(".positive { background-color: #d4edda; color: #155724; }")
        report.append(".negative { background-color: #f8d7da; color: #721c24; }")
        report.append(".neutral { background-color: #d1ecf1; color: #0c5460; }")
        report.append("</style></head><body>")
        report.append(f"<h1>News Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h1>")
        report.append(f"<p><strong>Total Articles:</strong> {len(self.processed_articles)}</p>")
        
        for i, article in enumerate(self.processed_articles, 1):
            sentiment_class = article['sentiment'].lower()
            report.append(f"<div class='article'>")
            report.append(f"<h2>{i}. {article['title']}</h2>")
            report.append(f"<p class='meta'>Source: {article['source']} | Published: {article['published_at']}</p>")
            report.append(f"<p>Sentiment: <span class='sentiment {sentiment_class}'>{article['sentiment']}</span></p>")
            report.append(f"<h3>Summary</h3><p>{article['ai_summary']}</p>")
            report.append(f"<h3>Key Points</h3><ul>")
            for point in article.get('key_points', []):
                report.append(f"<li>{point}</li>")
            report.append(f"</ul>")
            report.append(f"<p><a href='{article['url']}' target='_blank'>Read full article</a></p>")
            report.append("</div>")
        
        report.append("</body></html>")
        return "\n".join(report)
    
    def run_autonomous(self, topics: List[str], interval_hours: int = 24, iterations: int = 1):
        """
        Run the agent autonomously for specified iterations.
        
        Args:
            topics: List of topics to monitor
            interval_hours: Hours between each run
            iterations: Number of times to run (None for infinite)
        """
        import time
        
        logger.info(f"Starting autonomous mode for topics: {topics}")
        logger.info(f"Will run every {interval_hours} hours for {iterations} iteration(s)")
        
        for i in range(iterations):
            try:
                logger.info(f"\n{'='*80}")
                logger.info(f"Iteration {i+1}/{iterations}")
                logger.info(f"{'='*80}")
                
                # Fetch news
                articles = self.fetch_news(topics, days_back=1)
                
                # Process articles
                if articles:
                    self.process_articles(articles)
                    
                    # Generate and save report
                    report = self.generate_report(format='markdown')
                    report_filename = f"news_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    
                    with open(report_filename, 'w', encoding='utf-8') as f:
                        f.write(report)
                    
                    logger.info(f"Report saved to: {report_filename}")
                else:
                    logger.warning("No articles found in this iteration")
                
                # Wait for next iteration
                if i < iterations - 1:
                    sleep_seconds = interval_hours * 3600
                    logger.info(f"Sleeping for {interval_hours} hours until next run...")
                    time.sleep(sleep_seconds)
                    
            except KeyboardInterrupt:
                logger.info("Autonomous mode interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in autonomous mode: {str(e)}")
                if i < iterations - 1:
                    logger.info("Continuing to next iteration...")
        
        logger.info("Autonomous mode completed")
