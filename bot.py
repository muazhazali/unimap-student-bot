# Load environment variables first before any other imports
from dotenv import load_dotenv
load_dotenv()

import logging
import asyncio
import signal
import sys
import os
import json
import time
import datetime
import pytz
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Application, CommandHandler
from config import TELEGRAM_BOT_TOKEN, GROUPS, COURSES
from assignment_tracker import (
    check_assignment_updates, 
    format_assignment_notification,
    format_tracked_assignments_summary,
    get_active_assignments
)

# Set up logging for errors and important info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Constants and configuration
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS").split(",")
CHECK_TIMES = [(7, 0), (19, 0)]  # Check times: 7:00 AM and 7:00 PM (GMT+8)
TIMEZONE = pytz.timezone('Asia/Kuala_Lumpur')  # GMT+8 timezone
STATE_FILE = "previous_state.json"  # File to store previous state for comparison

# Initialize bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot = application.bot

# Function to load previous state
def load_previous_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

# Function to save current state
def save_current_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# Function to check for updates
def check_for_updates(current_state, previous_state):
    updates = {}
    for course_code, course_data in current_state.items():
        course_updates = {
            'new_sections': [],
            'modified_sections': [],
            'new_activities': [],
            'modified_activities': []
        }
        
        # Check if this is a new course
        if course_code not in previous_state:
            updates[course_code] = course_data
            continue
            
        prev_course_data = previous_state[course_code]
        
        # Compare sections
        for section_id, section in course_data.items():
            # New section
            if section_id not in prev_course_data:
                course_updates['new_sections'].append(section)
                continue
                
            prev_section = prev_course_data[section_id]
            
            # Compare activities within sections
            current_activities = {act['name']: act for act in section['activities']}
            previous_activities = {act['name']: act for act in prev_section['activities']}
            
            # Find new activities
            for act_name, activity in current_activities.items():
                if act_name not in previous_activities:
                    course_updates['new_activities'].append(activity)
                else:
                    # Check if activity was modified
                    prev_activity = previous_activities[act_name]
                    if activity != prev_activity:
                        course_updates['modified_activities'].append({
                            'name': act_name,
                            'old': prev_activity,
                            'new': activity
                        })
        
        # Only include course in updates if there are actual changes
        if any(updates for updates in course_updates.values()):
            updates[course_code] = course_updates
    
    return updates

# Function to format notification message
def format_notification(updates):
    message = "📚 UniMAP E-Learning Updates\n\n"
    
    for course_code, course_updates in updates.items():
        message += f"Course: {COURSES[course_code]['name']}\n"
        message += "----------------------------------------\n"
        
        if isinstance(course_updates, dict) and 'new_sections' in course_updates:
            # New sections
            if course_updates['new_sections']:
                message += "🆕 New Sections:\n"
                for section in course_updates['new_sections']:
                    message += f"• {section['name']}\n"
            
            # New activities
            if course_updates['new_activities']:
                message += "\n🆕 New Activities:\n"
                for activity in course_updates['new_activities']:
                    message += f"• {activity['name']}\n"
                    message += f"  Status: {activity['status']}\n"
            
            # Modified activities
            if course_updates['modified_activities']:
                message += "\n📝 Modified Activities:\n"
                for change in course_updates['modified_activities']:
                    message += f"• {change['name']}\n"
                    if change['old']['status'] != change['new']['status']:
                        message += f"  Status changed: {change['old']['status']} ➡️ {change['new']['status']}\n"
        else:
            # Handle case where entire course is new
            message += "New/Updated Activities:\n"
            for section in course_updates.values():
                for activity in section['activities']:
                    message += f"• {activity['name']}\n"
                    message += f"  Status: {activity['status']}\n"
        
        message += "----------------------------------------\n\n"
    
    return message

# Function to scrape a single course
def scrape_course(session, course_code):
    url = COURSES[course_code]['url']
    response = session.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    sections = {}
    for section in soup.find_all("li", class_="section main clearfix"):
        section_id = section.get("id")
        section_name = section.find("h3", class_="sectionname")
        if section_name:
            section_name = section_name.text.strip()
        else:
            continue
        
        activities = []
        for activity in section.find_all("li", class_="activity"):
            name_elem = activity.find("span", class_="instancename")
            if name_elem:
                activity_name = name_elem.text.strip()
                activity_status = activity.find("img", alt=True)["alt"] if activity.find("img", alt=True) else "Unknown"
                activities.append({
                    "name": activity_name,
                    "status": activity_status
                })
        
        sections[section_id] = {
            "name": section_name,
            "activities": activities
        }
    
    return sections

# Function to scrape all courses
def scrape_portal():
    try:
        session = requests.Session()
        base_url = "https://elearning.unimap.edu.my"
        login_url = f"{base_url}/login/index.php"
        
        # Check if credentials are set
        username = os.getenv("PORTAL_USERNAME")
        password = os.getenv("PORTAL_PASSWORD")
        
        if not username or not password:
            raise ValueError("Portal credentials not found in .env file")
        
        logging.info("Attempting to log in to portal...")
        
        # Get the login page
        initial_response = session.get(login_url)
        if initial_response.status_code != 200:
            raise ValueError(f"Failed to access login page. Status code: {initial_response.status_code}")
            
        # Log initial cookies
        logging.info("Initial cookies:")
        for cookie in session.cookies:
            logging.info(f"Cookie {cookie.name}: {cookie.value}")
        
        # Parse the login form
        soup = BeautifulSoup(initial_response.text, 'html.parser')
        login_form = soup.find('form', id='login')
        
        if not login_form:
            logging.error("Login form structure:")
            logging.error(soup.prettify())
            raise ValueError("Login form not found on page - page structure logged above")
        
        # Get login form action URL
        form_action = login_form.get('action', login_url)
        if not form_action.startswith('http'):
            form_action = base_url + form_action
        logging.info(f"Login form action URL: {form_action}")
        
        # Get all form inputs including hidden fields
        form_inputs = login_form.find_all('input')
        logging.info(f"Found {len(form_inputs)} form inputs")
        
        # Build the login payload with all form fields
        payload = {}
        
        # Add any hidden fields to payload first
        for input_field in form_inputs:
            input_name = input_field.get('name')
            input_value = input_field.get('value', '')
            input_type = input_field.get('type')
            
            if input_name:
                logging.info(f"Found form field: {input_name} (type: {input_type})")
                if input_type != 'submit':
                    payload[input_name] = input_value
        
        # Now add our login credentials
        payload.update({
            "username": username,
            "password": password,
            "anchor": ""  # Required by Moodle
        })
        
        logging.info(f"Final payload keys: {', '.join(payload.keys())}")
        
        # Set proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': base_url,
            'Referer': login_url,
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Try to login
        logging.info("Sending login request...")
        response = session.post(form_action, data=payload, headers=headers, allow_redirects=True)
        logging.info(f"Login response status code: {response.status_code}")
        logging.info(f"Login response URL: {response.url}")
        
        # Log cookies after login attempt
        logging.info("Cookies after login attempt:")
        for cookie in session.cookies:
            logging.info(f"Cookie {cookie.name}: {cookie.value}")
        
        # Log response headers
        logging.info("Response headers:")
        for header, value in response.headers.items():
            logging.info(f"{header}: {value}")
        
        # Verify login success by checking if redirected to dashboard
        logging.info("Checking login success...")
        dashboard_check = session.get(f"{base_url}/my/")
        logging.info(f"Dashboard check URL: {dashboard_check.url}")
        
        if "login/index.php" in dashboard_check.url:
            # Get any error messages
            error_soup = BeautifulSoup(dashboard_check.text, 'html.parser')
            
            # Check for different types of error messages
            error_msg = error_soup.find('div', {'class': 'loginerrors'})
            if not error_msg:
                error_msg = error_soup.find('div', {'class': 'alert-danger'})
            if not error_msg:
                error_msg = error_soup.find('div', {'class': 'alert'})
            if not error_msg:
                error_msg = error_soup.find('div', {'id': 'notice'})
                
            error_text = error_msg.text.strip() if error_msg else "No specific error message found"
            
            # Log the page content for debugging
            logging.error("Login page content after failed attempt:")
            logging.error(error_soup.prettify())
            
            raise ValueError(f"Login failed: {error_text}")
        
        logging.info("Login successful!")
        
        # Scrape all courses
        all_courses_data = {}
        for course_code in COURSES:
            try:
                logging.info(f"Scraping course {course_code}...")
                all_courses_data[course_code] = scrape_course(session, course_code)
                logging.info(f"Successfully scraped course {course_code}")
            except Exception as e:
                logging.error(f"Error scraping course {course_code}: {str(e)}")
                continue
        
        return all_courses_data, session
        
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error details: {str(e)}")
        raise ValueError("Failed to connect to the portal. Please check your internet connection.")
    except requests.exceptions.Timeout as e:
        logging.error(f"Timeout error details: {str(e)}")
        raise ValueError("Portal request timed out. Please try again later.")
    except Exception as e:
        logging.error(f"Unexpected error in scrape_portal: {str(e)}")
        raise

# Function to send messages to all groups
async def send_message_to_all_groups(message):
    """Send a message to all groups in the GROUPS list"""
    for group_id in GROUPS:
        try:
            await bot.send_message(group_id, message)
        except Exception as e:
            logging.error(f"Failed to send message to group {group_id}: {e}")
            continue

# Signal handler for graceful shutdown
async def shutdown_handler(signal, loop):
    try:
        # Send shutdown notification to all groups
        shutdown_message = "🔴 Bot is shutting down. Service will be unavailable until restart."
        await send_message_to_all_groups(shutdown_message)
        
        # Close the event loop
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")
    finally:
        loop.stop()

def get_next_check_time():
    """Get the next check time from the defined schedule"""
    # Get current time in GMT+8
    now = datetime.datetime.now(TIMEZONE)
    today = now.replace(second=0, microsecond=0)
    
    # Convert check times to full datetime objects for today
    check_times = [today.replace(hour=h, minute=m, second=0, microsecond=0) for h, m in CHECK_TIMES]
    
    # Add tomorrow's times if needed
    tomorrow = today + datetime.timedelta(days=1)
    tomorrow_times = [tomorrow.replace(hour=h, minute=m, second=0, microsecond=0) for h, m in CHECK_TIMES]
    all_times = check_times + tomorrow_times
    
    # Find the next check time
    next_time = min((t for t in all_times if t > now), default=tomorrow_times[0])
    return next_time

# Main function
async def main():
    retry_count = 0
    max_retries = 3
    
    try:
        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_running_loop()
        if os.name != 'nt':  # Only set up signal handlers on non-Windows systems
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown_handler(s, loop)))
        else:
            logging.info("Signal handlers not supported on Windows, using basic keyboard interrupt handling")

        logging.info("Starting bot...")
        
        # Check if environment variables are set
        if not os.getenv("TELEGRAM_BOT_TOKEN"):
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        if not os.getenv("TELEGRAM_CHAT_IDS"):
            raise ValueError("TELEGRAM_CHAT_IDS not found in environment variables")
        if not os.getenv("PORTAL_USERNAME"):
            raise ValueError("PORTAL_USERNAME not found in environment variables")
        if not os.getenv("PORTAL_PASSWORD"):
            raise ValueError("PORTAL_PASSWORD not found in environment variables")
            
        # Send startup message
        startup_message = "🤖 Bot is now connected and monitoring courses!\n\n"
        startup_message += "📚 Tracked Courses:\n"
        for code, course in COURSES.items():
            startup_message += f"• {course['name']} ({code})\n"
        startup_message += f"\n⏰ Checking at 7:00 AM and 7:00 PM daily (GMT+8)\n"
        await send_message_to_all_groups(startup_message)
        
        # Try to get initial assignments
        try:
            logging.info("Getting initial assignments...")
            # Create a session and scrape portal
            session = requests.Session()
            base_url = "https://elearning.unimap.edu.my"
            login_url = f"{base_url}/login/index.php"
            
            # Check if credentials are set
            username = os.getenv("PORTAL_USERNAME")
            password = os.getenv("PORTAL_PASSWORD")
            
            if not username or not password:
                raise ValueError("Portal credentials not found in .env file")
            
            logging.info("Attempting to log in to portal...")
            
            # Get the login page
            initial_response = session.get(login_url)
            if initial_response.status_code != 200:
                raise ValueError(f"Failed to access login page. Status code: {initial_response.status_code}")
            
            # Parse the login form
            soup = BeautifulSoup(initial_response.text, 'html.parser')
            login_form = soup.find('form', id='login')
            
            if not login_form:
                raise ValueError("Login form not found on page")
            
            # Get login form action URL
            form_action = login_form.get('action', login_url)
            if not form_action.startswith('http'):
                form_action = base_url + form_action
            
            # Get all form inputs including hidden fields
            form_inputs = login_form.find_all('input')
            
            # Build the login payload with all form fields
            payload = {}
            
            # Add any hidden fields to payload first
            for input_field in form_inputs:
                input_name = input_field.get('name')
                input_value = input_field.get('value', '')
                input_type = input_field.get('type')
                
                if input_name:
                    if input_type != 'submit':
                        payload[input_name] = input_value
            
            # Now add our login credentials
            payload.update({
                "username": username,
                "password": password,
                "anchor": ""  # Required by Moodle
            })
            
            # Set proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': base_url,
                'Referer': login_url,
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            # Try to login
            response = session.post(form_action, data=payload, headers=headers, allow_redirects=True)
            
            # Verify login success
            dashboard_check = session.get(f"{base_url}/my/")
            if "login/index.php" in dashboard_check.url:
                raise ValueError("Login failed")
            
            if session:
                current_assignments = get_active_assignments(session)
                if current_assignments:
                    initial_message = "🔍 Found active assignments:\n\n"
                    for assignment in current_assignments.values():
                        initial_message += f"📝 {assignment.course_name}\n"
                        initial_message += f"• {assignment.name}\n"
                        if assignment.due_date:
                            now = datetime.datetime.now(TIMEZONE)
                            time_until_due = assignment.due_date - now
                            days = time_until_due.days
                            hours = time_until_due.seconds // 3600
                            minutes = (time_until_due.seconds % 3600) // 60
                            
                            # Format time remaining
                            time_str = []
                            if days > 0:
                                time_str.append(f"{days} days")
                            if hours > 0 or days == 0:  # Show hours if less than a day or if there are hours
                                time_str.append(f"{hours} hours")
                            if minutes > 0 and days == 0:  # Show minutes only if less than a day
                                time_str.append(f"{minutes} minutes")
                            
                            initial_message += f"• **Due: {assignment.due_date.strftime('%d %B %Y, %I:%M %p')}**\n"
                            initial_message += f"• Time remaining: {', '.join(time_str)}\n"
                        initial_message += "----------------------------------------\n"
                    await send_message_to_all_groups(initial_message)
        except Exception as e:
            logging.error(f"Error getting initial assignments: {str(e)}")
            await send_message_to_all_groups("⚠️ Could not fetch initial assignments. Will retry on next check.")
        
        # Send initial assignment summary
        summary = format_tracked_assignments_summary()
        await send_message_to_all_groups(summary)
        
        while True:  # Continuous loop
            try:
                # Calculate time until next check
                next_check = get_next_check_time()
                now = datetime.datetime.now(TIMEZONE)
                wait_seconds = (next_check - now).total_seconds()
                
                logging.info(f"Next check scheduled for {next_check.strftime('%Y-%m-%d %H:%M:%S')}")
                logging.info(f"Waiting {wait_seconds/3600:.2f} hours")
                
                # Wait until next check time
                await asyncio.sleep(wait_seconds)
                
                # Load previous state
                previous_state = load_previous_state()
                
                # Scrape all courses and get session
                logging.info("Starting portal scrape...")
                current_state, session = scrape_portal()
                logging.info("Portal scrape completed successfully")
                
                # Reset retry count on successful scrape
                retry_count = 0
                
                # Check for course updates
                updates = check_for_updates(current_state, previous_state)
                
                # Send notifications if updates are found
                if updates:
                    message = format_notification(updates)
                    await send_message_to_all_groups(message)
                
                # Check for assignment updates
                new_assignments, modified_assignments, _ = check_assignment_updates(session)
                
                # Send notifications for new assignments
                for assignment in new_assignments:
                    message = "🆕 New Assignment!\n" + format_assignment_notification(assignment)
                    await send_message_to_all_groups(message)
                
                # Send notifications for modified assignments
                for assignment in modified_assignments:
                    message = "📝 Assignment Updated!\n" + format_assignment_notification(assignment)
                    await send_message_to_all_groups(message)
                
                # Save the current state
                save_current_state(current_state)
                
            except Exception as e:
                retry_count += 1
                logging.error(f"Error during monitoring (attempt {retry_count}/{max_retries}): {str(e)}")
                
                if retry_count >= max_retries:
                    error_message = f"❌ Failed after {max_retries} attempts. Last error: {str(e)}\nBot will now restart..."
                    await send_message_to_all_groups(error_message)
                    # Exit the script to allow process manager to restart it
                    sys.exit(1)
                else:
                    error_message = f"An error occurred during monitoring: {str(e)}\nRetrying in 1 minute... (attempt {retry_count}/{max_retries})"
                    await send_message_to_all_groups(error_message)
                    await asyncio.sleep(60)  # Wait 1 minute before retrying
                
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logging.critical(f"Critical error occurred: {str(e)}\nTraceback:\n{error_traceback}")
        error_message = f"❌ Critical error occurred: {str(e)}\nBot has stopped. Please restart manually."
        await send_message_to_all_groups(error_message)
    finally:
        try:
            logging.info("Bot shutting down...")
            await send_message_to_all_groups("🔴 Bot has stopped running. Service will be unavailable until restart.")
        except:
            logging.error("Failed to send shutdown message")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot shutdown requested by user...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        print("Bot has stopped running.")