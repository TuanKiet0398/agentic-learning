"""
Streamlit UI for Autonomous AI News Agent
Provides an interactive web interface for the news agent.
"""

import streamlit as st
import logging
from datetime import datetime
import os
from agent import NewsAgent
from config import Config
import pandas as pd

# Configure page
st.set_page_config(
    page_title="AI News Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .article-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .sentiment-positive {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .sentiment-negative {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .sentiment-neutral {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stat-box {
        background-color: #667eea;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_config():
    """Load configuration (cached)."""
    return Config()


@st.cache_resource
def initialize_agent():
    """Initialize the news agent (cached)."""
    config = load_config()
    return NewsAgent(config)


def display_article(article, index):
    """Display a single article in a nice format."""
    sentiment = article.get('sentiment', 'Neutral')
    sentiment_class = f"sentiment-{sentiment.lower()}"
    
    with st.container():
        st.markdown(f"""
        <div class="article-card">
            <h3>📰 {index}. {article['title']}</h3>
            <p style="color: #666; font-size: 0.9rem;">
                <strong>Source:</strong> {article.get('source', 'Unknown')} | 
                <strong>Published:</strong> {article.get('published_at', 'N/A')}
            </p>
            <p><span class="{sentiment_class}">Sentiment: {sentiment}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Summary
        with st.expander("📝 AI Summary", expanded=True):
            st.write(article.get('ai_summary', 'No summary available'))
        
        # Key Points
        with st.expander("🔑 Key Points"):
            key_points = article.get('key_points', [])
            if key_points:
                for point in key_points:
                    st.markdown(f"• {point}")
            else:
                st.write("No key points available")
        
        # Original Content
        with st.expander("📄 Original Description"):
            st.write(article.get('description', 'No description available'))
        
        # Link
        st.markdown(f"[🔗 Read Full Article]({article.get('url', '#')})")
        
        st.markdown("---")


def main():
    """Main Streamlit app."""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI News Agent</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.2rem;'>Autonomous news aggregation powered by AI</p>", unsafe_allow_html=True)
    
    # Initialize session state
    if 'articles' not in st.session_state:
        st.session_state.articles = []
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    
    # Load configuration
    try:
        config = load_config()
        
        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            st.error("⚠️ Configuration Error")
            st.warning("Please set up your API keys in the `.env` file:")
            for error in errors:
                st.write(f"• {error}")
            st.info("Copy `.env.example` to `.env` and add your API keys.")
            st.stop()
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        st.stop()
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Mode selection
        mode = st.radio(
            "Select Mode",
            ["Topic Search", "Trending News"],
            help="Choose between searching specific topics or fetching trending headlines"
        )
        
        st.markdown("---")
        
        # Mode-specific options
        if mode == "Topic Search":
            st.subheader("🔍 Topic Search")
            
            # Topics input
            default_topics = config.default_topics if hasattr(config, 'default_topics') else ['AI', 'technology']
            topics_input = st.text_area(
                "Topics (one per line)",
                value="\n".join(default_topics),
                height=100,
                help="Enter topics to search for, one per line"
            )
            topics = [t.strip() for t in topics_input.split("\n") if t.strip()]
            
            # Days back
            days_back = st.slider(
                "Days to look back",
                min_value=1,
                max_value=7,
                value=1,
                help="Number of days to search back"
            )
            
        else:  # Trending News
            st.subheader("🔥 Trending News")
            
            # Country selection
            country = st.selectbox(
                "Country",
                ["us", "gb", "ca", "au", "in", "de", "fr", "jp"],
                help="Select country for trending news"
            )
            
            # Category selection
            category = st.selectbox(
                "Category",
                ["general", "business", "entertainment", "health", "science", "sports", "technology"],
                help="Select news category"
            )
        
        st.markdown("---")
        
        # Output options
        st.subheader("📊 Output Options")
        
        max_articles = st.number_input(
            "Max articles to process",
            min_value=1,
            max_value=50,
            value=10,
            help="Limit the number of articles to process"
        )
        
        sentiment_filter = st.selectbox(
            "Filter by sentiment",
            ["All", "Positive", "Negative", "Neutral"],
            help="Filter articles by sentiment"
        )
        
        report_format = st.selectbox(
            "Report format",
            ["markdown", "html", "text"],
            help="Format for downloadable report"
        )
        
        st.markdown("---")
        
        # Fetch button
        fetch_button = st.button("🚀 Fetch & Analyze News", type="primary", use_container_width=True)
    
    # Main content area
    if fetch_button:
        st.session_state.processed = False
        
        with st.spinner("🔄 Initializing agent..."):
            try:
                agent = initialize_agent()
            except Exception as e:
                st.error(f"Error initializing agent: {str(e)}")
                st.stop()
        
        # Fetch news
        with st.spinner(f"📡 Fetching news... This may take a moment..."):
            try:
                if mode == "Topic Search":
                    st.info(f"Searching for: {', '.join(topics)}")
                    articles = agent.fetch_news(topics, days_back=days_back)
                else:
                    st.info(f"Fetching trending news from {country.upper()}")
                    articles = agent.fetcher.fetch_trending(country=country, category=category)
                
                if not articles:
                    st.warning("⚠️ No articles found. Try different topics or settings.")
                    st.stop()
                
                # Limit articles
                articles = articles[:max_articles]
                st.success(f"✅ Found {len(articles)} articles!")
                
            except Exception as e:
                st.error(f"Error fetching news: {str(e)}")
                logger.error(f"Fetch error: {str(e)}", exc_info=True)
                st.stop()
        
        # Process articles
        with st.spinner("🤖 Processing articles with AI... This may take a few minutes..."):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                processed_articles = []
                for i, article in enumerate(articles):
                    status_text.text(f"Processing article {i+1}/{len(articles)}: {article.get('title', 'Untitled')[:50]}...")
                    
                    # Process individual article
                    try:
                        summary = agent.summarizer.summarize_article(article)
                        key_points = agent.summarizer.extract_key_points(article)
                        sentiment = agent.summarizer.analyze_sentiment(article)
                        
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
                        
                        processed_articles.append(processed_article)
                        
                    except Exception as e:
                        logger.error(f"Error processing article: {str(e)}")
                        continue
                    
                    progress_bar.progress((i + 1) / len(articles))
                
                status_text.empty()
                progress_bar.empty()
                
                st.session_state.articles = processed_articles
                agent.processed_articles = processed_articles
                st.session_state.processed = True
                
                st.success(f"✅ Successfully processed {len(processed_articles)} articles!")
                
            except Exception as e:
                st.error(f"Error processing articles: {str(e)}")
                logger.error(f"Processing error: {str(e)}", exc_info=True)
                st.stop()
    
    # Display results
    if st.session_state.processed and st.session_state.articles:
        articles = st.session_state.articles
        
        # Apply sentiment filter
        if sentiment_filter != "All":
            articles = [a for a in articles if a.get('sentiment') == sentiment_filter]
        
        # Statistics
        st.markdown("## 📊 Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <h2>{len(articles)}</h2>
                <p>Total Articles</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Count sentiments
        sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
        for article in st.session_state.articles:
            sentiment = article.get('sentiment', 'Neutral')
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
        
        with col2:
            st.markdown(f"""
            <div class="stat-box" style="background-color: #28a745;">
                <h2>{sentiment_counts['Positive']}</h2>
                <p>Positive</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-box" style="background-color: #dc3545;">
                <h2>{sentiment_counts['Negative']}</h2>
                <p>Negative</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-box" style="background-color: #17a2b8;">
                <h2>{sentiment_counts['Neutral']}</h2>
                <p>Neutral</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sentiment distribution chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📈 Sentiment Distribution")
            sentiment_df = pd.DataFrame({
                'Sentiment': list(sentiment_counts.keys()),
                'Count': list(sentiment_counts.values())
            })
            st.bar_chart(sentiment_df.set_index('Sentiment'))
        
        with col2:
            st.markdown("### 📰 Sources")
            sources = {}
            for article in st.session_state.articles:
                source = article.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
            
            source_df = pd.DataFrame({
                'Source': list(sources.keys()),
                'Articles': list(sources.values())
            }).sort_values('Articles', ascending=False)
            
            st.dataframe(source_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Download report
        st.markdown("### 💾 Download Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download Markdown Report", use_container_width=True):
                agent = initialize_agent()
                agent.processed_articles = st.session_state.articles
                report = agent.generate_report(format='markdown')
                st.download_button(
                    label="Download MD",
                    data=report,
                    file_name=f"news_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        
        with col2:
            if st.button("📥 Download HTML Report", use_container_width=True):
                agent = initialize_agent()
                agent.processed_articles = st.session_state.articles
                report = agent.generate_report(format='html')
                st.download_button(
                    label="Download HTML",
                    data=report,
                    file_name=f"news_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
        
        with col3:
            if st.button("📥 Download Text Report", use_container_width=True):
                agent = initialize_agent()
                agent.processed_articles = st.session_state.articles
                report = agent.generate_report(format='text')
                st.download_button(
                    label="Download TXT",
                    data=report,
                    file_name=f"news_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        st.markdown("---")
        
        # Display articles
        st.markdown(f"### 📰 Articles ({len(articles)} displayed)")
        
        if not articles:
            st.info("No articles match the selected filters.")
        else:
            for i, article in enumerate(articles, 1):
                display_article(article, i)
    
    elif not st.session_state.processed:
        # Welcome message
        st.markdown("## 👋 Welcome!")
        st.markdown("""
        This AI News Agent helps you:
        - 🔍 **Search** for news on any topic
        - 🔥 **Discover** trending headlines
        - 🤖 **Analyze** articles with AI
        - 📊 **Visualize** sentiment and trends
        - 💾 **Export** comprehensive reports
        
        ### 🚀 Get Started
        1. Configure your settings in the sidebar
        2. Click **"Fetch & Analyze News"**
        3. Explore the results!
        
        ### ⚙️ Configuration Required
        Make sure you have set up your `.env` file with:
        - `OPENAI_API_KEY` (Required)
        - `NEWSAPI_KEY` (Optional but recommended)
        """)
        
        # Display configuration status
        with st.expander("📋 Current Configuration"):
            st.code(str(config))


if __name__ == "__main__":
    main()
