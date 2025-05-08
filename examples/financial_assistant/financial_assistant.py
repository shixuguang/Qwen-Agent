"""A financial assistant agent for stock market queries using yfinance"""

import json
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os
import webbrowser
from pathlib import Path
from typing import Dict, Any

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
from qwen_agent.tools.base import BaseTool, register_tool


@register_tool('stock_query')
class StockQuery(BaseTool):
    description = 'Query stock information by company symbol for today or a specific date'
    parameters = [{
        'name': 'symbol',
        'type': 'string',
        'description': 'Stock symbol (e.g., AAPL for Apple)',
        'required': True,
    }, {
        'name': 'date',
        'type': 'string',
        'description': 'Date in YYYY-MM-DD format. Use "today" for current data',
        'required': True,
    }]

    def call(self, params: str, **kwargs) -> str:
        params_dict = json.loads(params)
        symbol = params_dict['symbol']
        date = params_dict['date']

        try:
            stock = yf.Ticker(symbol)
            if date.lower() == 'today':
                # Get today's data
                hist = stock.history(period='1d')
            else:
                # Get specific date data
                hist = stock.history(start=date, end=date)

            if hist.empty:
                return json.dumps({
                    'error': f'No data available for {symbol} on {date}'
                })

            data = hist.iloc[0]
            return json.dumps({
                'symbol': symbol,
                'date': date,
                'open': round(data['Open'], 2),
                'high': round(data['High'], 2),
                'low': round(data['Low'], 2),
                'close': round(data['Close'], 2),
                'volume': int(data['Volume']),
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'error': f'Error querying {symbol}: {str(e)}'})


@register_tool('market_performance')
class MarketPerformance(BaseTool):
    description = 'Query best or worst performing stocks from major indices for the day'
    parameters = [{
        'name': 'performance_type',
        'type': 'string',
        'description': 'Type of performance to query: "best" or "worst"',
        'required': True,
    }, {
        'name': 'limit',
        'type': 'number',
        'description': 'Number of stocks to return (1-10)',
        'required': True,
    }]

    def call(self, params: str, **kwargs) -> str:
        params_dict = json.loads(params)
        performance_type = params_dict['performance_type']
        limit = min(max(1, int(params_dict['limit'])), 10)

        try:
            # Using S&P 500 components as example
            sp500 = '^GSPC'
            sp500_ticker = yf.Ticker(sp500)
            components = pd.DataFrame()  # This is simplified, in real implementation we'd need to get actual components

            # For demonstration, we'll use a few major tech stocks
            sample_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA']
            performance_data = []

            for symbol in sample_stocks:
                stock = yf.Ticker(symbol)
                hist = stock.history(period='1d')
                if not hist.empty:
                    data = hist.iloc[0]
                    daily_return = ((data['Close'] - data['Open']) / data['Open']) * 100
                    performance_data.append({
                        'symbol': symbol,
                        'return': daily_return,
                        'close': data['Close'],
                        'change': data['Close'] - data['Open']
                    })

            # Sort based on performance type
            performance_data.sort(key=lambda x: x['return'], 
                                reverse=(performance_type.lower() == 'best'))
            
            return json.dumps({
                'performance_type': performance_type,
                'stocks': performance_data[:limit]
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'error': f'Error getting market performance: {str(e)}'})


@register_tool('moving_average')
class MovingAverage(BaseTool):
    description = 'Generate 200-day moving average graph for a given stock'
    parameters = [{
        'name': 'symbol',
        'type': 'string',
        'description': 'Stock symbol (e.g., AAPL for Apple)',
        'required': True,
    }]

    def call(self, params: str, **kwargs) -> str:
        params_dict = json.loads(params)
        symbol = params_dict['symbol']

        try:
            # Get stock data
            stock = yf.Ticker(symbol)
            hist = stock.history(period='1y')  # Get 1 year of data

            if hist.empty:
                return json.dumps({'error': f'No data available for {symbol}'})

            # Calculate 200-day moving average
            ma200 = hist['Close'].rolling(window=200).mean()

            # Create the plot
            plt.figure(figsize=(12, 6))
            plt.plot(hist.index, hist['Close'], label='Stock Price')
            plt.plot(hist.index, ma200, label='200-day MA')
            plt.title(f'{symbol} Stock Price and 200-day Moving Average')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.legend()
            plt.grid(True)

            # Convert plot to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            # Create a temporary HTML file to display the graph
            image_data = f'data:image/png;base64,{image_base64}'
            html_content = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>{symbol} - 200-day Moving Average</title>
                    <style>
                        body {{
                            margin: 0;
                            padding: 20px;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            background: #f0f0f0;
                            font-family: Arial, sans-serif;
                        }}
                        h1 {{
                            color: #333;
                            margin-bottom: 20px;
                        }}
                        img {{
                            max-width: 100%;
                            height: auto;
                            border-radius: 8px;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                        }}
                    </style>
                </head>
                <body>
                    <h1>{symbol} - 200-day Moving Average</h1>
                    <img src="{image_data}" alt="Moving Average Graph">
                </body>
            </html>
            """
            
            # Create workspace directory if it doesn't exist
            temp_dir = Path('workspace/financial_assistant/temp')
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Save and open the HTML file
            html_path = temp_dir / f'{symbol}_moving_average.html'
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            # Open in browser
            webbrowser.open(f'file://{html_path.absolute()}')

            return json.dumps({
                'symbol': symbol,
                'message': f'Moving average graph for {symbol} has been opened in your default browser.',
                'html_path': str(html_path)
            })
        except Exception as e:
            return json.dumps({'error': f'Error generating moving average graph: {str(e)}'})


def init_agent_service():
    llm_cfg = {
        'model_type': 'oai',
        'model': 'deepseek-chat',
        'api_key': 'sk-b25e7a4155094be38a551cb63b7f6922',
        'api_base': 'https://api.deepseek.com/v1',
    }
    system = (
        "You are a financial assistant specialized in stock market analysis. "
        "You can help users with:\n"
        "1. Querying stock information by company symbol\n"
        "2. Finding best/worst performing stocks of the day\n"
        "3. Analyzing stock trends using 200-day moving averages\n"
        "Use the available tools to provide accurate and helpful information. "
        "When users ask about stocks, always provide clear explanations along with the data."
    )

    tools = [
        'stock_query',
        'market_performance',
        'moving_average',
    ]

    bot = Assistant(
        llm=llm_cfg,
        name='Financial Assistant',
        description='Stock market analysis and information service',
        system_message=system,
        function_list=tools,
    )

    return bot


def app_gui():
    bot = init_agent_service()
    chatbot_config = {
        'prompt.suggestions': [
            'What is the current stock price of AAPL?',
            'Show me the best performing stocks today',
            'Generate a 200-day moving average graph for TSLA',
            'How is Microsoft stock (MSFT) performing today?',
        ]
    }
    WebUI(
        bot,
        chatbot_config=chatbot_config,
    ).run()


if __name__ == '__main__':
    app_gui()