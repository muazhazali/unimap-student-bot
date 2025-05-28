import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Telegram configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUPS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if os.getenv("TELEGRAM_CHAT_IDS") else []

# Course configuration
COURSES = {
    "SMP25503": {
        "name": "SMP25503(Sem 2-2024/2025)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7360"
    },
    "SMP22203": {
        "name": "SMP22203(Sem 2-2024/2025)", 
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7357"
    },
    "SMP22003": {
        "name": "SMP22003(Sem 2-2024/2025)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7356"
    },
    "SMP11603": {
        "name": "SMP11603(Sem 2-2024/2025)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7350"
    },
    "SMP22103": {
        "name": "SMP22103(Sem 2-2024/2025)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7339"
    }
} 