"""
News Summarizer Module
Uses LangChain and OpenAI to summarize and analyze news articles.
"""

import logging
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import Config
import os

logger = logging.getLogger(__name__)


class NewsSummarizer:
    """
    AI-powered news summarizer using LangChain and OpenAI.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the News Summarizer.
        
        Args:
            config: Configuration object containing API keys and settings
        """
        self.config = config
        
        # Set API key in environment for OpenAI client
        os.environ["OPENAI_API_KEY"] = config.openai_api_key
        
        # Initialize the LLM with minimal parameters
        self.llm = ChatOpenAI(
            model=config.openai_model,
            temperature=config.openai_temperature
        )
        
        # Initialize text splitter for long articles
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Define prompts
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup prompt templates for different tasks."""
        
        # Summary prompt
        self.summary_prompt = PromptTemplate(
            input_variables=["title", "content"],
            template="""You are a professional news analyst. Summarize the following news article in 2-3 concise sentences.
Focus on the key facts, main points, and important implications.

Title: {title}

Content: {content}

Summary:"""
        )
        
        # Key points prompt
        self.key_points_prompt = PromptTemplate(
            input_variables=["title", "content"],
            template="""You are a professional news analyst. Extract 3-5 key points from the following news article.
Each point should be a single, clear sentence highlighting important information.

Title: {title}

Content: {content}

Key Points (return as a numbered list):"""
        )
        
        # Sentiment prompt
        self.sentiment_prompt = PromptTemplate(
            input_variables=["title", "content"],
            template="""Analyze the sentiment of the following news article.
Classify it as either: Positive, Negative, or Neutral.
Consider the overall tone, implications, and context.

Title: {title}

Content: {content}

Sentiment (respond with only one word - Positive, Negative, or Neutral):"""
        )
        
        # Create chains
        self.summary_chain = LLMChain(llm=self.llm, prompt=self.summary_prompt)
        self.key_points_chain = LLMChain(llm=self.llm, prompt=self.key_points_prompt)
        self.sentiment_chain = LLMChain(llm=self.llm, prompt=self.sentiment_prompt)
    
    def _prepare_content(self, article: Dict) -> str:
        """
        Prepare article content for processing.
        
        Args:
            article: Article dictionary
            
        Returns:
            Prepared content string
        """
        content = article.get('content', '')
        description = article.get('description', '')
        
        # Use content if available, otherwise use description
        text = content if content else description
        
        # Truncate if too long
        if len(text) > 6000:
            text = text[:6000] + "..."
        
        return text
    
    def summarize_article(self, article: Dict) -> str:
        """
        Generate a concise summary of the article.
        
        Args:
            article: Article dictionary
            
        Returns:
            Summary string
        """
        try:
            title = article.get('title', 'Untitled')
            content = self._prepare_content(article)
            
            if not content:
                return "No content available to summarize."
            
            result = self.summary_chain.invoke({
                "title": title,
                "content": content
            })
            
            summary = result.get('text', '').strip()
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing article: {str(e)}")
            return "Error generating summary."
    
    def extract_key_points(self, article: Dict) -> List[str]:
        """
        Extract key points from the article.
        
        Args:
            article: Article dictionary
            
        Returns:
            List of key points
        """
        try:
            title = article.get('title', 'Untitled')
            content = self._prepare_content(article)
            
            if not content:
                return ["No content available to analyze."]
            
            result = self.key_points_chain.invoke({
                "title": title,
                "content": content
            })
            
            key_points_text = result.get('text', '').strip()
            
            # Parse the numbered list
            key_points = []
            for line in key_points_text.split('\n'):
                line = line.strip()
                # Remove numbering (e.g., "1.", "1)", "-", "•")
                if line:
                    # Remove common list markers
                    cleaned = line.lstrip('0123456789.-)•-– ').strip()
                    if cleaned:
                        key_points.append(cleaned)
            
            return key_points[:5]  # Return max 5 points
            
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return ["Error extracting key points."]
    
    def analyze_sentiment(self, article: Dict) -> str:
        """
        Analyze the sentiment of the article.
        
        Args:
            article: Article dictionary
            
        Returns:
            Sentiment string (Positive, Negative, or Neutral)
        """
        try:
            title = article.get('title', 'Untitled')
            content = self._prepare_content(article)
            
            if not content:
                return "Neutral"
            
            result = self.sentiment_chain.invoke({
                "title": title,
                "content": content
            })
            
            sentiment = result.get('text', 'Neutral').strip()
            
            # Normalize sentiment
            sentiment_lower = sentiment.lower()
            if 'positive' in sentiment_lower:
                return "Positive"
            elif 'negative' in sentiment_lower:
                return "Negative"
            else:
                return "Neutral"
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return "Neutral"
    
    def generate_insights(self, articles: List[Dict]) -> Dict:
        """
        Generate insights from multiple articles.
        
        Args:
            articles: List of articles
            
        Returns:
            Dictionary containing insights
        """
        try:
            # Prepare combined content
            titles = [a.get('title', '') for a in articles[:10]]  # Limit to 10 articles
            combined_titles = "\n".join([f"- {title}" for title in titles])
            
            insight_prompt = PromptTemplate(
                input_variables=["titles"],
                template="""You are a professional news analyst. Based on these news article titles, 
identify the main themes, trends, and topics being discussed.
Provide a brief analysis (3-4 sentences) of what's currently newsworthy.

Article Titles:
{titles}

Analysis:"""
            )
            
            insight_chain = LLMChain(llm=self.llm, prompt=insight_prompt)
            result = insight_chain.invoke({"titles": combined_titles})
            
            # Count sentiments
            sentiments = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
            for article in articles:
                if 'sentiment' in article:
                    sentiment = article['sentiment']
                    if sentiment in sentiments:
                        sentiments[sentiment] += 1
            
            return {
                'overview': result.get('text', '').strip(),
                'total_articles': len(articles),
                'sentiment_breakdown': sentiments,
                'sources': list(set([a.get('source', {}).get('name', 'Unknown') for a in articles]))
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {
                'overview': 'Error generating insights.',
                'total_articles': len(articles),
                'sentiment_breakdown': {},
                'sources': []
            }
    
    def compare_articles(self, article1: Dict, article2: Dict) -> str:
        """
        Compare two articles and identify similarities/differences.
        
        Args:
            article1: First article
            article2: Second article
            
        Returns:
            Comparison analysis string
        """
        try:
            comparison_prompt = PromptTemplate(
                input_variables=["title1", "content1", "title2", "content2"],
                template="""Compare these two news articles. Identify:
1. Common themes or topics
2. Different perspectives or angles
3. Key differences in coverage

Article 1:
Title: {title1}
Content: {content1}

Article 2:
Title: {title2}
Content: {content2}

Comparison:"""
            )
            
            comparison_chain = LLMChain(llm=self.llm, prompt=comparison_prompt)
            
            result = comparison_chain.invoke({
                "title1": article1.get('title', ''),
                "content1": self._prepare_content(article1)[:1000],
                "title2": article2.get('title', ''),
                "content2": self._prepare_content(article2)[:1000]
            })
            
            return result.get('text', '').strip()
            
        except Exception as e:
            logger.error(f"Error comparing articles: {str(e)}")
            return "Error comparing articles."
