# 🤖 Autonomous AI News Agent

An intelligent, autonomous news aggregation and analysis system powered by AI. This agent fetches news from multiple sources, processes articles using LangChain and OpenAI, and generates comprehensive reports with summaries, key points, and sentiment analysis.

## ✨ Features

- **Multi-Source News Fetching**: Aggregates news from NewsAPI and RSS feeds
- **AI-Powered Analysis**: Uses OpenAI GPT models via LangChain for intelligent summarization
- **Sentiment Analysis**: Automatically classifies articles as positive, negative, or neutral
- **Key Points Extraction**: Identifies the most important information from each article
- **Multiple Report Formats**: Generates reports in text, Markdown, or HTML
- **Autonomous Mode**: Runs continuously at specified intervals
- **Flexible Filtering**: Filter by sentiment, source, topic, and more
- **Topic-Based Search**: Search for news on any topic
- **Trending News**: Fetch top headlines by country and category

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- NewsAPI key (optional but recommended, [Get one here](https://newsapi.org/register))

### Installation

1. **Clone or navigate to the News_agent directory**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# Required:
OPENAI_API_KEY=your-openai-api-key-here

# Optional but recommended:
NEWSAPI_KEY=your-newsapi-key-here
```

4. **Validate your configuration**
```bash
python main.py --validate
```

## 📖 Usage

### Web Interface (Streamlit)

**Launch the interactive web UI:**
```bash
streamlit run streamlit_app.py
```

This will open a browser with an intuitive interface where you can:
- Search for news on any topic or fetch trending headlines
- View AI-generated summaries and key points
- Filter by sentiment (positive/negative/neutral)
- Visualize sentiment distribution and sources
- Download reports in multiple formats
- Process articles with real-time progress tracking

### Command Line Interface

### Basic Usage

**Fetch news on default topics:**
```bash
python main.py
```

**Search specific topics:**
```bash
python main.py --topics "artificial intelligence" "climate change" "cryptocurrency"
```

**Fetch trending news:**
```bash
python main.py --trending --country us --category technology
```

### Advanced Usage

**Autonomous mode (runs continuously):**
```bash
# Run every 12 hours, 5 iterations
python main.py --autonomous --interval 12 --iterations 5
```

**Filter by sentiment:**
```bash
python main.py --topics "technology" --sentiment positive
```

**Generate HTML report:**
```bash
python main.py --topics "AI" --format html --output my_report.html
```

**Limit number of articles:**
```bash
python main.py --topics "machine learning" --limit 10
```

**Search news from past week:**
```bash
python main.py --topics "AI breakthroughs" --days 7
```

### Command Line Options

```
Main Options:
  --topics TOPICS [TOPICS ...]    Topics to search for
  --trending                      Fetch trending/top headlines
  --autonomous                    Run in autonomous mode

News Fetching:
  --days DAYS                     Days to look back (default: 1)
  --country COUNTRY               Country code for trending (default: us)
  --category CATEGORY             Category for trending news

Output:
  --format {text,markdown,html}   Report format (default: markdown)
  --output OUTPUT                 Custom output file path

Filtering:
  --sentiment {positive,negative,neutral}  Filter by sentiment
  --source SOURCE                 Filter by source name
  --limit LIMIT                   Limit articles to process

Autonomous Mode:
  --interval HOURS                Hours between runs (default: 24)
  --iterations N                  Number of iterations (default: 1)

Configuration:
  --config                        Display configuration
  --validate                      Validate configuration
```

## 📁 Project Structure

```
News_agent/
├── agent.py              # Main NewsAgent class
├── news_fetcher.py       # News fetching from multiple sources
├── summarizer.py         # AI-powered summarization and analysis
├── config.py             # Configuration management
├── main.py               # CLI entry point
├── streamlit_app.py      # Streamlit web UI
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables
├── .env                  # Your environment variables (create this)
└── reports/              # Generated reports (auto-created)
```

## 🔧 Configuration

All configuration is managed through environment variables in the `.env` file:

### Required Settings
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional Settings
- `NEWSAPI_KEY`: NewsAPI key (recommended for better results)
- `OPENAI_MODEL`: Model to use (default: gpt-3.5-turbo)
- `OPENAI_TEMPERATURE`: Temperature for generation (default: 0.7)
- `DEFAULT_TOPICS`: Comma-separated default topics
- `REPORT_FORMAT`: Default report format (text/markdown/html)
- `OUTPUT_DIRECTORY`: Directory for reports (default: reports)
- `LOG_LEVEL`: Logging level (default: INFO)

## 📊 Example Output

The agent generates comprehensive reports including:

- **Article Title & Metadata**: Source, publication date
- **AI-Generated Summary**: Concise 2-3 sentence summary
- **Key Points**: Bullet list of important information
- **Sentiment Analysis**: Positive, negative, or neutral
- **Full Article Link**: Link to original article

### Sample Markdown Report

```markdown
# News Report - 2025-11-17 10:30:45

**Total Articles:** 5

---

## 1. Breaking: Major AI Breakthrough Announced

**Source:** TechCrunch | **Published:** 2025-11-17T08:15:00Z
**Sentiment:** Positive

### Summary
Researchers at leading AI lab announced a breakthrough in natural language 
understanding that could revolutionize human-computer interaction. The new 
model demonstrates unprecedented accuracy in complex reasoning tasks.

### Key Points
- New model achieves 95% accuracy on reasoning benchmarks
- Technology could be deployed in consumer products within 6 months
- Represents significant advancement over previous approaches

[Read full article](https://example.com/article)

---
```

## 🎨 Streamlit UI Features

The web interface provides:

- **🎯 Interactive Dashboard**: Real-time statistics and visualizations
- **🔍 Flexible Search**: Topic-based or trending news modes
- **📊 Visual Analytics**: Sentiment distribution charts and source breakdowns
- **🎨 Beautiful Cards**: Each article displayed in an elegant, readable format
- **⚡ Progress Tracking**: Real-time updates during article processing
- **💾 One-Click Downloads**: Export reports in multiple formats
- **🎛️ Smart Filters**: Filter by sentiment, limit results, customize output
- **📱 Responsive Design**: Works on desktop, tablet, and mobile

## 🤝 Use Cases

- **Research**: Stay updated on specific topics for academic research
- **Business Intelligence**: Monitor industry news and trends
- **Content Creation**: Gather information for articles or reports
- **Personal Learning**: Keep informed on topics of interest
- **Competitive Analysis**: Track news about competitors or market trends

## 🛠️ Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8 .
```

## 📝 Notes

- The agent respects API rate limits and includes error handling
- RSS feeds are used as backup when NewsAPI is unavailable
- Reports are saved with timestamps for easy organization
- The autonomous mode includes intelligent error recovery

## 🐛 Troubleshooting

**"Configuration validation failed"**
- Make sure you've created `.env` file from `.env.example`
- Verify your OpenAI API key is correct

**"No articles found"**
- Try different topics or increase `--days` parameter
- Check if your NewsAPI key is valid
- RSS feeds may have limited coverage for specific topics

**Rate limit errors**
- NewsAPI free tier has daily limits (100 requests/day)
- Consider spacing out autonomous runs or upgrading NewsAPI plan

## 📄 License

This project is provided as-is for educational and personal use.

## 🙏 Acknowledgments

- Built with [LangChain](https://python.langchain.com/)
- Powered by [OpenAI](https://openai.com/)
- News data from [NewsAPI](https://newsapi.org/) and RSS feeds

---

**Happy News Hunting! 🎯**
