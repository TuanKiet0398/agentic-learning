"""
Main Entry Point for News Agent
Provides CLI interface to run the autonomous news agent.
"""

import argparse
import logging
import sys
from typing import List
from agent import NewsAgent
from config import Config, get_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('news_agent.log')
    ]
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Autonomous AI News Agent - Fetch, analyze, and summarize news articles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default topics
  python main.py
  
  # Run with custom topics
  python main.py --topics "AI" "climate change" "cryptocurrency"
  
  # Run in autonomous mode (continuous)
  python main.py --autonomous --interval 12 --iterations 5
  
  # Fetch trending news
  python main.py --trending --country us --category technology
  
  # Generate HTML report
  python main.py --format html --topics "machine learning"
  
  # Filter by sentiment
  python main.py --sentiment positive --topics "technology"
        """
    )
    
    # Main operation modes
    parser.add_argument(
        '--topics',
        nargs='+',
        help='Topics to search for (e.g., "AI" "technology" "climate change")'
    )
    
    parser.add_argument(
        '--trending',
        action='store_true',
        help='Fetch trending/top headlines instead of topic search'
    )
    
    parser.add_argument(
        '--autonomous',
        action='store_true',
        help='Run in autonomous mode (continuous operation)'
    )
    
    # News fetching options
    parser.add_argument(
        '--days',
        type=int,
        default=1,
        help='Number of days to look back for news (default: 1)'
    )
    
    parser.add_argument(
        '--country',
        type=str,
        default='us',
        help='Country code for trending news (default: us)'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        choices=['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'],
        help='Category for trending news'
    )
    
    # Output options
    parser.add_argument(
        '--format',
        type=str,
        choices=['text', 'markdown', 'html'],
        default='markdown',
        help='Output format for the report (default: markdown)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (optional, defaults to timestamped file)'
    )
    
    # Filtering options
    parser.add_argument(
        '--sentiment',
        type=str,
        choices=['positive', 'negative', 'neutral'],
        help='Filter articles by sentiment'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        help='Filter articles by source name'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of articles to process'
    )
    
    # Autonomous mode options
    parser.add_argument(
        '--interval',
        type=int,
        default=24,
        help='Hours between runs in autonomous mode (default: 24)'
    )
    
    parser.add_argument(
        '--iterations',
        type=int,
        default=1,
        help='Number of iterations in autonomous mode (default: 1)'
    )
    
    # Configuration
    parser.add_argument(
        '--config',
        action='store_true',
        help='Display current configuration and exit'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate configuration and exit'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Load configuration
    config = get_config()
    
    # Display configuration if requested
    if args.config:
        print(config)
        return
    
    # Validate configuration if requested
    if args.validate:
        is_valid, errors = config.validate()
        if is_valid:
            print("✓ Configuration is valid")
            print(config)
        else:
            print("✗ Configuration errors found:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        return
    
    # Validate required API keys
    is_valid, errors = config.validate()
    if not is_valid:
        logger.error("Configuration validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        logger.error("\nPlease set up your .env file with required API keys.")
        logger.error("Copy .env.example to .env and fill in your API keys.")
        sys.exit(1)
    
    # Initialize agent
    logger.info("Initializing News Agent...")
    agent = NewsAgent(config)
    
    try:
        # Determine topics to use
        topics = args.topics if args.topics else config.default_topics
        
        if args.autonomous:
            # Run in autonomous mode
            logger.info(f"Starting autonomous mode with topics: {topics}")
            agent.run_autonomous(
                topics=topics,
                interval_hours=args.interval,
                iterations=args.iterations
            )
        elif args.trending:
            # Fetch trending news
            logger.info(f"Fetching trending news for {args.country}")
            articles = agent.fetcher.fetch_trending(
                country=args.country,
                category=args.category
            )
            
            if articles:
                # Process articles
                processed = agent.process_articles(articles[:args.limit] if args.limit else articles)
                
                # Apply filters
                if args.sentiment:
                    processed = agent.filter_by_sentiment(args.sentiment)
                    logger.info(f"Filtered to {len(processed)} {args.sentiment} articles")
                
                if args.source:
                    processed = agent.filter_by_source(args.source)
                    logger.info(f"Filtered to {len(processed)} articles from {args.source}")
                
                agent.processed_articles = processed
                
                # Generate report
                report = agent.generate_report(format=args.format)
                
                # Save report
                output_file = args.output if args.output else f"trending_report_{config.default_country}.{args.format.replace('text', 'txt')}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                logger.info(f"Report saved to: {output_file}")
                print(f"\n✓ Report generated: {output_file}")
            else:
                logger.warning("No trending articles found")
                
        else:
            # Normal mode: fetch by topics
            logger.info(f"Fetching news for topics: {topics}")
            articles = agent.fetch_news(topics, days_back=args.days)
            
            if articles:
                # Limit articles if specified
                if args.limit:
                    articles = articles[:args.limit]
                
                # Process articles
                processed = agent.process_articles(articles)
                
                # Apply filters
                if args.sentiment:
                    processed = agent.filter_by_sentiment(args.sentiment)
                    logger.info(f"Filtered to {len(processed)} {args.sentiment} articles")
                
                if args.source:
                    processed = agent.filter_by_source(args.source)
                    logger.info(f"Filtered to {len(processed)} articles from {args.source}")
                
                agent.processed_articles = processed
                
                # Generate report
                report = agent.generate_report(format=args.format)
                
                # Save report
                from datetime import datetime
                if args.output:
                    output_file = args.output
                else:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    ext = 'txt' if args.format == 'text' else args.format.replace('markdown', 'md')
                    output_file = f"{config.output_directory}/news_report_{timestamp}.{ext}"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                logger.info(f"Report saved to: {output_file}")
                print(f"\n✓ Report generated: {output_file}")
                print(f"  Total articles processed: {len(processed)}")
                
                # Display summary
                if processed:
                    sentiments = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
                    for article in processed:
                        sentiment = article.get('sentiment', 'Neutral')
                        if sentiment in sentiments:
                            sentiments[sentiment] += 1
                    
                    print(f"\n  Sentiment breakdown:")
                    for sentiment, count in sentiments.items():
                        if count > 0:
                            print(f"    {sentiment}: {count}")
            else:
                logger.warning("No articles found")
                print("\n⚠ No articles found for the specified topics and timeframe.")
                print("  Try adjusting your topics or increasing the --days parameter.")
    
    except KeyboardInterrupt:
        logger.info("\nOperation interrupted by user")
        print("\n\n✓ Operation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
