import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from models import Assignment
from typing import List, Dict
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('assignment_tracker.log'),
        logging.StreamHandler()
    ]
)

# Import course configuration from config.py
from config import COURSES

# Constants
TIMEZONE = pytz.timezone('Asia/Kuala_Lumpur')  # GMT+8

# File to store assignments
ASSIGNMENTS_FILE = "assignments.json"

def load_assignments() -> Dict:
    """Load saved assignments from file"""
    try:
        logging.info("Loading assignments from assignments.json")
        if not os.path.exists(ASSIGNMENTS_FILE):
            logging.info("assignments.json not found, creating new file")
            return {}
        with open(ASSIGNMENTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading assignments: {str(e)}")
        return {}

def save_assignments(assignments: Dict[str, Assignment]):
    """Save assignments to file"""
    try:
        logging.info("Saving assignments to assignments.json")
        with open(ASSIGNMENTS_FILE, 'w') as f:
            json.dump({k: v.to_dict() for k, v in assignments.items()}, f, indent=4)
        logging.info("Successfully saved assignments")
    except Exception as e:
        logging.error(f"Error saving assignments: {str(e)}")

def parse_assignment_page(html: str, url: str, course_code: str) -> Assignment:
    """Parse assignment details from assignment page HTML"""
    try:
        logging.info(f"Parsing assignment page: {url}")
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get assignment name and try to extract due date from title
        name = soup.find('h2').text.strip() if soup.find('h2') else ""
        
        # Check if we have a due date in the URL fragment
        title_date = None
        if '#title=' in url:
            title = url.split('#title=')[-1]
            # Try to extract date from title
            import re
            date_patterns = [
                r'Due (\d{1,2}/\d{1,2}/\d{2,4})',  # matches "Due 03/05/25"
                r'due (\d{1,2}/\d{1,2}/\d{2,4})',  # matches "due 03/05/25"
                r'Due (\d{1,2} [A-Za-z]+ \d{4})',  # matches "Due 14 May 2025"
                r'due (\d{1,2} [A-Za-z]+ \d{4})'   # matches "due 14 May 2025"
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, title)
                if match:
                    try:
                        date_str = match.group(1)
                        if '/' in date_str:
                            title_date = datetime.strptime(date_str, '%d/%m/%y').replace(tzinfo=TIMEZONE)
                        else:
                            title_date = datetime.strptime(date_str, '%d %B %Y').replace(tzinfo=TIMEZONE)
                        break
                    except ValueError:
                        continue
        
        # Get description
        intro = soup.find('div', {'id': 'intro'})
        description = intro.text.strip() if intro else ""
        
        # Get submission details
        submission_table = soup.find('table', {'class': 'generaltable'})
        details = {}
        
        if submission_table:
            rows = submission_table.find_all('tr')
            for row in rows:
                header = row.find('th')
                value = row.find('td')
                if header and value:
                    details[header.text.strip()] = value.text.strip()
        
        # Try to parse due date from details, fallback to title date
        due_date = None
        try:
            if 'Due date' in details:
                due_date = datetime.strptime(details['Due date'], '%A, %d %B %Y, %I:%M %p').replace(tzinfo=TIMEZONE)
        except ValueError:
            pass
        
        if due_date is None:
            due_date = title_date
        
        if due_date is None:
            # If we still don't have a date, try to find it in the description or name
            date_text = description if description else name
            for pattern in date_patterns:
                match = re.search(pattern, date_text)
                if match:
                    try:
                        date_str = match.group(1)
                        if '/' in date_str:
                            due_date = datetime.strptime(date_str, '%d/%m/%y').replace(tzinfo=TIMEZONE)
                        else:
                            due_date = datetime.strptime(date_str, '%d %B %Y').replace(tzinfo=TIMEZONE)
                        break
                    except ValueError:
                        continue
        
        # Extract assignment ID from URL
        assignment_id = url.split('id=')[1].split('#')[0]
        
        logging.info(f"Successfully parsed assignment: {name}")
        return Assignment(
            course_code=course_code,
            course_name=COURSES[course_code]['name'],
            name=name,
            due_date=due_date,
            time_remaining=details.get('Time remaining', ''),
            submission_status=details.get('Submission status', 'No attempt'),
            grading_status=details.get('Grading status', 'Not graded'),
            description=description,
            url=url.split('#')[0],  # Remove the title fragment
            last_modified=details.get('Last modified', '-'),
            id=assignment_id
        )
    except Exception as e:
        logging.error(f"Error parsing assignment page: {str(e)}")
        return None

def find_assignments_in_course(session: requests.Session, course_code: str) -> List[str]:
    """Find all assignment URLs in a course page"""
    try:
        logging.info(f"Finding assignments in course {course_code}")
        url = COURSES[course_code]['url']
        logging.debug(f"Checking course {course_code} at URL: {url}")
        
        response = session.get(url)
        logging.debug(f"Response status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        assignment_urls = []
        
        # Find assignments by looking for the assignment activity type
        assignments = soup.find_all('li', class_='activity assign modtype_assign')
        logging.debug(f"Found {len(assignments)} potential assignments in {course_code}")
        
        for assignment in assignments:
            # Get the assignment link
            link = assignment.find('a', class_='aalink')
            if link and 'href' in link.attrs:
                assignment_urls.append(link['href'])
                logging.debug(f"Found assignment URL: {link['href']}")
                
            # Also try to extract due date from title if available
            title = link.find('span', class_='instancename')
            if title:
                title_text = title.text.strip()
                logging.debug(f"Assignment title: {title_text}")
                # Store this for later use in parse_assignment_page
                if 'Due' in title_text or 'due' in title_text:
                    assignment_urls[-1] = f"{assignment_urls[-1]}#title={title_text}"
        
        logging.info(f"Found {len(assignment_urls)} assignments in course {course_code}")
        return assignment_urls
    except Exception as e:
        logging.error(f"Error finding assignments in course {course_code}: {str(e)}")
        return []

def get_active_assignments(session: requests.Session) -> Dict[str, Assignment]:
    """Get all active assignments from all courses"""
    try:
        logging.info("Getting active assignments from all courses")
        current_assignments = {}
        
        for course_code in COURSES:
            logging.debug(f"\nProcessing course: {course_code}")
            # Find all assignments in the course
            assignment_urls = find_assignments_in_course(session, course_code)
            logging.debug(f"Found {len(assignment_urls)} assignment URLs in {course_code}")
            
            # Process each assignment
            for url in assignment_urls:
                logging.debug(f"\nFetching assignment details from: {url}")
                response = session.get(url)
                try:
                    assignment = parse_assignment_page(response.text, url, course_code)
                    logging.debug(f"Parsed assignment: {assignment.name}")
                    logging.debug(f"Due date: {assignment.due_date}")
                    logging.debug(f"Submission status: {assignment.submission_status}")
                    
                    # Only include if not submitted and not past due date
                    if assignment.submission_status == "No attempt":
                        now = datetime.now(TIMEZONE)
                        if assignment.due_date and assignment.due_date > now:
                            current_assignments[assignment.id] = assignment
                            logging.debug("Assignment added to tracking")
                        else:
                            logging.debug("Assignment excluded: Past due date")
                    else:
                        logging.debug("Assignment excluded: Already attempted")
                except Exception as e:
                    logging.error(f"Error processing assignment {url}: {str(e)}")
        
        logging.info(f"\nTotal active assignments found: {len(current_assignments)}")
        return current_assignments
    except Exception as e:
        logging.error(f"Error getting active assignments: {str(e)}")
        return {}

def format_assignment_notification(assignment: Assignment) -> str:
    """Format assignment details for Telegram notification"""
    now = datetime.now(TIMEZONE)
    time_until_due = assignment.due_date - now if assignment.due_date else None
    
    message = f"""📚 Assignment Details

Course: {assignment.course_name}
----------------------------------------
Name: {assignment.name}
Due Date: {assignment.due_date.strftime('%d %B %Y, %I:%M %p') if assignment.due_date else 'Not specified'}
"""

    if time_until_due:
        days = time_until_due.days
        hours = time_until_due.seconds // 3600
        minutes = (time_until_due.seconds % 3600) // 60
        
        # Create urgency indicator
        if days > 5:
            urgency = "📆"  # Calendar emoji for plenty of time
        elif days > 2:
            urgency = "⚠️"  # Warning for less than 5 days
        elif days > 0:
            urgency = "🚨"  # Alert for less than 2 days
        elif hours > 1:
            urgency = "⏰"  # Alarm for hours remaining
        else:
            urgency = "🔥"  # Fire for less than 1 hour
            
        time_str = []
        if days > 0:
            time_str.append(f"{days} days")
        if hours > 0 or days == 0:  # Show hours if less than a day or if there are hours
            time_str.append(f"{hours} hours")
        if minutes > 0 and days == 0:  # Show minutes only if less than a day
            time_str.append(f"{minutes} minutes")
            
        message += f"\n{urgency} Time Remaining: {', '.join(time_str)}\n"
        
        # Add extra warning for urgent assignments
        if days == 0:
            if hours < 1:
                message += "❗️VERY URGENT: Less than 1 hour remaining!\n"
            elif hours < 6:
                message += "❗️URGENT: Less than 6 hours remaining!\n"
            elif hours < 12:
                message += "⚠️ Due today - less than 12 hours remaining!\n"
    
    message += f"""Status: {assignment.submission_status}
Grading: {assignment.grading_status}

Description:
{assignment.description if assignment.description else 'No description available'}

Link: {assignment.url}
----------------------------------------"""

    return message

def format_tracked_assignments_summary() -> str:
    """Format a summary of all currently tracked assignments"""
    assignments = load_assignments()
    if not assignments:
        return "No active assignments being tracked."
    
    # Sort assignments by due date
    sorted_assignments = sorted(
        assignments.values(), 
        key=lambda x: x.due_date
    )
    
    message = "📋 Currently Tracked Assignments\n\n"
    
    # Group assignments by course
    course_assignments = {}
    for assignment in sorted_assignments:
        if assignment.course_code not in course_assignments:
            course_assignments[assignment.course_code] = []
        course_assignments[assignment.course_code].append(assignment)
    
    # Format message by course
    for course_code, assignments in course_assignments.items():
        message += f"📚 {COURSES[course_code]['name']}\n"
        message += "----------------------------------------\n"
        for assignment in assignments:
            message += f"• {assignment.name}\n"
            message += f"  Due: {assignment.due_date.strftime('%d %b %Y, %I:%M %p')}\n"
            message += f"  Remaining: {assignment.time_remaining}\n"
            message += f"  Status: {assignment.submission_status}\n\n"
        message += "----------------------------------------\n\n"
    
    return message

def check_assignment_updates(session):
    """
    Check for new and modified assignments.
    Returns (new_assignments, modified_assignments, [])
    """
    current_assignments = get_active_assignments(session)
    previous_assignments = load_assignments()
    
    # Find new assignments
    new_assignments = []
    for assignment_id, assignment in current_assignments.items():
        if assignment_id not in previous_assignments:
            new_assignments.append(assignment)
    
    # Find modified assignments
    modified_assignments = []
    for assignment_id, assignment in current_assignments.items():
        if assignment_id in previous_assignments:
            prev_assignment = previous_assignments[assignment_id]
            if assignment != prev_assignment:
                modified_assignments.append(assignment)
    
    # Save current assignments
    save_assignments(current_assignments)
    
    return new_assignments, modified_assignments, []  # Empty list for upcoming assignments 