# Financial Assistant Agent

A stock market analysis assistant built with Qwen-Agent that provides real-time stock information and analysis through a web interface.

## Features

- Real-time stock price queries by company symbol
- Best/worst performing stocks analysis
- 200-day moving average visualization
- Interactive web interface for natural language queries

## Prerequisites

- Python 3.8 or higher
- Qwen-Agent library
- DeepSeek API key (configured in the code)
- Additional dependencies listed in `requirements.txt`

## Model Configuration

This implementation uses the DeepSeek Chat model for natural language processing. The API key is configured in `financial_assistant.py`. If you need to use a different API key, modify the `llm_cfg` dictionary in the `init_agent_service()` function:

```python
llm_cfg = {
    'model': 'deepseek-chat',
    'api_key': 'your-api-key-here',
    'api_base': 'https://api.deepseek.com/v1',
}
```

## Installation

1. Make sure you have Qwen-Agent installed and set up properly
2. Install additional dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Financial Assistant:
   ```bash
   python financial_assistant.py
   ```

2. Access the web interface through your browser (default: http://localhost:7860)

3. Example queries:
   - "What is the current stock price of AAPL?"
   - "Show me the best performing stocks today"
   - "Generate a 200-day moving average graph for TSLA"
   - "How is Microsoft stock (MSFT) performing today?"

## Tools Available

1. **Stock Query**
   - Get current or historical stock data for any company
   - Usage: Provide stock symbol and date (use "today" for current data)

2. **Market Performance**
   - Find best or worst performing stocks
   - Shows performance metrics for top stocks

3. **Moving Average**
   - Generate 200-day moving average visualization
   - Includes price history and trend analysis
   - Opens interactive graph in your default web browser
   - Saves temporary visualization files in `workspace/financial_assistant/temp` directory

Note: The moving average visualization feature will create temporary HTML files in the `temp` directory. These files contain the generated graphs and will be opened automatically in your default web browser when you request a moving average analysis.

## Data Source

This assistant uses Yahoo Finance (through yfinance library) as its data source, providing:
- Real-time stock quotes
- Historical data
- Basic company information

## Notes

- Stock data is provided with a slight delay (typically 15-20 minutes for real-time data)
- Historical data availability may vary by stock
- Market performance analysis focuses on major indices and popular stocks