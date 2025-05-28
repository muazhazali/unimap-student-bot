import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Telegram configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUPS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if os.getenv("TELEGRAM_CHAT_IDS") else []

# Course configuration
# Replace these with your actual course codes and URLs from UniMAP e-learning portal
# To find course URLs: Go to your course page and copy the URL
# Course ID is the number after "id=" in the URL
# Use the exact course name as it is in the e-learning portal
COURSES = {
    "COURSE_CODE_1": {
        "name": "Course Name 1(Sem X-YYYY/YYYY)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=XXXX"
    },
    "COURSE_CODE_2": {
        "name": "Course Name 2(Sem X-YYYY/YYYY)", 
        "url": "https://elearning.unimap.edu.my/course/view.php?id=YYYY"
    },
    "COURSE_CODE_3": {
        "name": "Course Name 3(Sem X-YYYY/YYYY)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=ZZZZ"
    },
    # Add more courses as needed
    # "COURSE_CODE_4": {
    #     "name": "Course Name 4(Sem X-YYYY/YYYY)",
    #     "url": "https://elearning.unimap.edu.my/course/view.php?id=AAAA"
    # }
} 