"""
Example Configuration File for UniMAP Student Bot

This file shows you how to configure your courses for the bot.
Copy this file to config.py and modify it with your actual course information.

How to get your course information:
1. Log into your UniMAP e-learning portal
2. Navigate to each of your courses
3. Copy the URL from the address bar
4. Extract the course ID from the URL (the number after 'id=')
5. Replace the example data below with your actual course codes, names, and IDs

Example URL: https://elearning.unimap.edu.my/course/view.php?id=7360
Course ID: 7360
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Telegram configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUPS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if os.getenv("TELEGRAM_CHAT_IDS") else []

# Course configuration
# Replace these with your actual course codes and URLs from UniMAP e-learning portal
COURSES = {
    # Example: Mathematics course
    "SMP25503": {
        "name": "Advanced Mathematics(Sem 2-2024/2025)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7360"
    },
    
    # Example: Computer Science course
    "SCS22203": {
        "name": "Data Structures & Algorithms(Sem 2-2024/2025)", 
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7357"
    },
    
    # Example: Engineering course
    "SEE22003": {
        "name": "Digital Logic Design(Sem 2-2024/2025)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7356"
    },
    
    # Example: General course
    "SGS11603": {
        "name": "Malaysian Studies(Sem 2-2024/2025)",
        "url": "https://elearning.unimap.edu.my/course/view.php?id=7350"
    },
    
    # Add more courses following the same pattern:
    # "YOUR_COURSE_CODE": {
    #     "name": "Your Course Name (Sem X-YYYY/YYYY)",
    #     "url": "https://elearning.unimap.edu.my/course/view.php?id=YOUR_COURSE_ID"
    # },
}

# Configuration tips:
# 1. Course codes should match exactly with UniMAP's course codes
# 2. Include semester information in the course name for clarity
# 3. Double-check the course IDs in the URLs
# 4. You can have as many courses as you want
# 5. Remove or comment out courses you don't want to monitor 