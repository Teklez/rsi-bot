# RSI Trading Bot

A Telegram bot that monitors cryptocurrency markets using RSI to send trading alerts.

## Description

Telegram bot that connects to Binance WebSocket streams, calculates RSI values, and sends notifications when RSI indicates oversold or overbought conditions. Users can subscribe to trading pairs and set custom RSI thresholds.

## Motivation

Automate cryptocurrency market monitoring to identify trading opportunities without constantly watching charts. RSI is a reliable technical indicator for spotting overbought and oversold conditions.

## Quick Start

1. Install dependencies: `uv install`
2. Set environment variables in `.env`:
   - `TELEGRAM_BOT_TOKEN=your_bot_token`
   - `DATABASE_URL=postgresql://user:pass@localhost/db`
3. Run migrations: `uv run alembic upgrade head`
4. Start bot: `uv run main.py`

## Usage

- `/start` - Register with bot
- `/addsymbol` - Subscribe to trading pairs
- `/settings` - Configure RSI thresholds

Set oversold threshold (20-40) for buying alerts and overbought threshold (60-80) for selling alerts.

## Contribution

Submit issues or pull requests for improvements.
