"""
Configuration Module
Manages settings and environment variables for the News Agent.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class for the News Agent.
    Loads settings from environment variables with sensible defaults.
    """
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        
        # API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.newsapi_key = os.getenv('NEWSAPI_KEY', '')
        
        # OpenAI Settings
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
        
        # News Fetcher Settings
        self.default_language = os.getenv('DEFAULT_LANGUAGE', 'en')
        self.default_country = os.getenv('DEFAULT_COUNTRY', 'us')
        self.max_articles_per_topic = int(os.getenv('MAX_ARTICLES_PER_TOPIC', '50'))
        
        # Agent Settings
        self.default_topics = os.getenv('DEFAULT_TOPICS', 'technology,AI,machine learning').split(',')
        self.report_format = os.getenv('REPORT_FORMAT', 'markdown')  # text, markdown, html
        self.output_directory = os.getenv('OUTPUT_DIRECTORY', 'reports')
        
        # Autonomous Mode Settings
        self.autonomous_interval_hours = int(os.getenv('AUTONOMOUS_INTERVAL_HOURS', '24'))
        self.autonomous_iterations = int(os.getenv('AUTONOMOUS_ITERATIONS', '1'))
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_directory, exist_ok=True)
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate the configuration.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is not set")
        
        if not self.newsapi_key:
            errors.append("NEWSAPI_KEY is not set (optional but recommended for better results)")
        
        if self.openai_temperature < 0 or self.openai_temperature > 1:
            errors.append("OPENAI_TEMPERATURE must be between 0 and 1")
        
        if self.max_articles_per_topic < 1:
            errors.append("MAX_ARTICLES_PER_TOPIC must be at least 1")
        
        if self.report_format not in ['text', 'markdown', 'html']:
            errors.append("REPORT_FORMAT must be 'text', 'markdown', or 'html'")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def __str__(self) -> str:
        """String representation of configuration (hides API keys)."""
        return f"""
News Agent Configuration:
========================
OpenAI Model: {self.openai_model}
OpenAI Temperature: {self.openai_temperature}
OpenAI API Key: {'[SET]' if self.openai_api_key else '[NOT SET]'}
NewsAPI Key: {'[SET]' if self.newsapi_key else '[NOT SET]'}
Default Language: {self.default_language}
Default Country: {self.default_country}
Max Articles Per Topic: {self.max_articles_per_topic}
Default Topics: {', '.join(self.default_topics)}
Report Format: {self.report_format}
Output Directory: {self.output_directory}
Autonomous Interval: {self.autonomous_interval_hours} hours
Log Level: {self.log_level}
"""


# Singleton instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get the singleton configuration instance.
    
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
