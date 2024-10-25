# Blum Bot
A bot for automation with multi-threading capabilities.
Automatically check accounts if eligible auto getting some dogs.

## Update Menu Options

### 1. Play Game Every 5 Hours
- Automated gameplay that runs in cycles
- Each cycle includes:
  - Daily reward checking and claiming
  - Automatic Farming Balance
  - Automatic game play for all accounts
  - Waiting period of 5 hours before next cycle
- Perfect for long-term farming
- Single input for points and threads at start
- Continues until manually stopped (Ctrl+C)
- Telegram notifications for each cycle completion

### 2. Play Game (One Time)
- Single session gameplay
- Play until all tickets are used
- Stops automatically when complete
- Needs manual restart for new session
- Fresh input for points and threads each time
- Good for short-term or controlled farming
- Telegram notification on completion

The main difference:
- "Play Game Every 5 Hours" is designed for automated, long-term farming with minimal user intervention
- Regular "Play Game" is for single-session farming that requires manual restart
- Both features support multi-threading and Telegram notifications, but differ in automation level

Choose "Play Game Every 5 Hours" if you want:
- Continuous farming with automatic cycles
- Daily reward automation
- Minimal manual intervention
- Long-term operation

Choose "Play Game" if you want:
- More control over each session
- Single-run operations
- Manual management of play sessions
- Short-term farming

## Getting Started

First, join Blum by clicking here:

<div align="justify">
  <a href="https://t.me/blum/app?startapp=ref_eWbRQkPdY2">
    <img src="https://img.shields.io/badge/Join-BLUM-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white&scale=2" height="35" alt="Join Blum"/>
  </a>
</div>

## Requirements

- Python 3.12.2
- pip (Python package installer)

## Installation

1. Check your Python version:
```bash
python --version
```
Make sure it shows `Python 3.12.2`

2. Clone the repository:
```bash
git clone https://github.com/jeremiatoga123/blum-bot.git
cd blum-bot
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Telegram Notifications

The bot supports sending farming summaries to Telegram. To enable this feature:

1. Create a `.env` file in the root directory
2. Add your Telegram credentials:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

When enabled, you'll receive notifications containing:
- Farming duration
- Total points collected
- Total tickets used
- Total profit
- Number of active accounts

If no credentials are provided, the bot will run normally without sending notifications.

## Usage

1. Create a file named `query.txt` in the same directory as the bot
2. Add your queries to `query.txt`
3. Run the bot:
```bash
python blum.py
```

## Features

The bot has several features accessible through a menu system:
1. Play Game (with multi-threading support)
2. Check Account Info
3. Check Daily Reward
4. Exit

## Menu Options

### 1. Play Game Every 5 Hours
- Playing game include farming, and checking daily with looping every 5 hours
- Set minimum and maximum points
- Configure number of threads
- Automated gameplay
- Telegram notifications for farming summary

### 1. Play Game
- Set minimum and maximum points
- Configure number of threads
- Automated gameplay
- Telegram notifications for farming summary

### 2. Check Account Info
- View account balance
- Check ticket availability
- See user details

### 3. Check Daily Reward
- Check daily reward status
- Claim rewards if available

### 4. Exit
- Safely exit the program

## Support & Donations

If you find this bot helpful, you can support the development through:
- DANA    : 082286000280
- SeaBank : 901058100087
- GoPay   : 089524227639
- ETH     : 0xFF4a4601d87b966ce1e437ae95D19116E49ee99e

## Note

Make sure to use Python 3.12.2 for optimal performance. You can download it from [Python's official website](https://www.python.org/downloads/).

## Troubleshooting

If you encounter any issues:

1. Python version mismatch:
```bash
# Windows
py -3.12 blum.py

# Linux/Mac
python3.12 blum.py
```

2. Package installation issues:
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install packages with verbose output
pip install -r requirements.txt -v
```

## Disclaimer

This bot is for educational purposes only. Use at your own risk.
Please don't spam if you don't want the api down

## API Key

This is free Api, but if you need private api key dm me

<div align="justify">
  <a href="https://t.me/ggtogss">
    <img src="https://img.shields.io/badge/@ggtogss-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white&scale=2" height="35" alt="@ggtogss"/>
  </a>
</div>

## Author

Created by Toga