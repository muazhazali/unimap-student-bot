# UniMAP Portal Bot

A Telegram bot that monitors UniMAP's e-learning portal for updates and sends notifications. The bot automatically tracks course changes, assignments, and due dates, helping students stay updated with their coursework.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-22.0-blue.svg)

## ✨ Features

- 🔄 **Real-time Course Monitoring**
  - Automatic detection of new course content
  - Notifications for course updates and modifications
  - Tracks multiple courses simultaneously

- 📚 **Assignment Tracking**
  - Automatic detection of new assignments
  - Due date monitoring and reminders
  - Smart urgency indicators (🔥 < 1hr, ⏰ < 24hrs, 🚨 < 2 days, ⚠️ < 5 days)
  - Submission status tracking

- ⏰ **Scheduled Checks**
  - Regular portal checks at 7 AM and 7 PM (GMT+8)
  - Configurable check intervals
  - Automatic error recovery and retries

- 🔔 **Smart Notifications**
  - Telegram group notifications
  - Formatted messages with emojis for better readability
  - Different notification types for various updates

## 📩 Sample Output

![image](https://github.com/user-attachments/assets/6a3c58ee-f07f-4556-bc55-bc99274618b5)

![image](https://github.com/user-attachments/assets/e23207dc-f786-41e3-9d8d-9de7e62896cb)

![image](https://github.com/user-attachments/assets/4ba55b6b-2e51-4c2c-b3d4-a539f9f6be39)


## 🏗️ Architecture

The bot is built with a modular architecture:

- `bot.py`: Main bot logic and Telegram integration
- `assignment_tracker.py`: Assignment monitoring and notification formatting
- `config.py`: Configuration management and course definitions
- `models.py`: Data models for assignments and courses
- `get_chat_id.py`: Utility to find Telegram chat IDs

## 📋 Prerequisites

- Python 3.7 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- UniMAP Portal credentials
- Internet connection

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/unimap-student-bot.git
cd unimap-student-bot
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Edit the `.env` file with your actual values:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_IDS=your_chat_id_1,your_chat_id_2

# UniMAP Portal Credentials
PORTAL_USERNAME=your_unimap_username
PORTAL_PASSWORD=your_unimap_password
```

### 5. Configure Your Courses

Edit `config.py` to add your specific courses:

```python
COURSES = {
    "YOUR_COURSE_CODE": {
        "name": "Your Course Name (Sem X-YYYY/YYYY)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=YOUR_COURSE_ID"
    },
    # Add more courses as needed
}
```

**How to find course URLs:**
1. Go to your UniMAP e-learning portal
2. Navigate to your course
3. Copy the URL from the address bar
4. The course ID is the number after `id=` in the URL

### 6. Get Your Telegram Chat ID

```bash
python get_chat_id.py
```

This will help you find the chat IDs for your Telegram groups.

### 7. Run the Bot

```bash
python bot.py
```

## 🔧 Configuration

### Course Configuration

In `config.py`, define your courses:

```python
COURSES = {
    "SMP25503": {
        "name": "Advanced Mathematics (Sem 2-2024/2025)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7360"
    },
    "SMP22203": {
        "name": "Data Structures (Sem 2-2024/2025)", 
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7357"
    }
}
```

### Notification Settings

- Bot checks for updates every 12 hours (7 AM and 7 PM GMT+8)
- Multiple Telegram chat IDs can be specified for notifications
- Assignment urgency levels are automatically determined based on due dates

## 🚀 Deployment

### Deploy to DigitalOcean

1. **Create and connect to your droplet:**
   ```bash
   ssh root@your_droplet_ip
   ```

2. **Install Python and required tools:**
   ```bash
   apt update
   apt install python3-pip python3-venv git
   ```

3. **Clone and setup the repository:**
   ```bash
   git clone https://github.com/yourusername/unimap-student-bot.git
   cd unimap-student-bot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   nano .env
   # Add your actual values
   ```

5. **Run with screen (persistent session):**
   ```bash
   screen -S unimap-bot
   python bot.py
   ```
   
   - To detach: Press `Ctrl+A` then `D`
   - To reattach: `screen -r unimap-bot`

### Deploy with Docker (Alternative)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
```

Build and run:

```bash
docker build -t unimap-bot .
docker run -d --env-file .env unimap-bot
```

## 🔍 Troubleshooting

### Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| **Login Failures** | Incorrect credentials | Check `PORTAL_USERNAME` and `PORTAL_PASSWORD` in `.env` |
| **Bot Not Responding** | Invalid bot token | Verify `TELEGRAM_BOT_TOKEN` in `.env` |
| **No Notifications** | Wrong chat IDs | Use `get_chat_id.py` to find correct chat IDs |
| **Course Not Found** | Invalid course URL/ID | Check course URLs in `config.py` |

### Debug Mode

Enable detailed logging by modifying the logging level in `bot.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Log Files

- `bot.log`: Main application logs
- `assignment_tracker.log`: Assignment tracking specific logs

## 🔒 Security Notes

- **Never commit your `.env` file** - It contains sensitive credentials
- **Use environment variables** for all sensitive data
- **Regularly rotate your bot token** if compromised
- **Keep your portal credentials secure**

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Web scraping with [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- Powered by the [Telegram Bot API](https://core.telegram.org/bots/api)

## 📞 Support

- 🐛 [Report Issues](https://github.com/yourusername/unimap-student-bot/issues)
- 💡 [Request Features](https://github.com/yourusername/unimap-student-bot/issues)
- 📖 [Documentation](https://github.com/yourusername/unimap-student-bot/wiki)

## ⭐ Star History

If this project helped you, please consider giving it a star! ⭐

---

**Disclaimer:** This bot is not officially affiliated with UniMAP. Use responsibly and in accordance with your institution's policies. 
