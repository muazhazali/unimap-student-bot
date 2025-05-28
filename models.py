"""
Data Models for UniMAP Student Bot

This module defines the data structures used throughout the application
for representing assignments, courses, and other entities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import json

@dataclass
class Assignment:
    """
    Represents an assignment from the UniMAP e-learning portal.
    
    Attributes:
        course_code: The course code (e.g., "SMP25503")
        course_name: The full course name
        name: Assignment title/name
        due_date: When the assignment is due (if available)
        time_remaining: Human readable time until due
        submission_status: Current submission status (e.g., "Submitted", "No attempt")
        grading_status: Current grading status
        description: Assignment description (if available)
        url: Direct link to the assignment
        last_modified: When the assignment was last updated
        id: Assignment ID from the URL
    """
    course_code: str
    course_name: str = ""
    name: str = ""
    due_date: Optional[datetime] = None
    time_remaining: str = ""
    submission_status: str = "No attempt"
    grading_status: str = "Not graded"
    description: str = ""
    url: str = ""
    last_modified: str = ""
    id: str = ""
    
    # Legacy fields for backward compatibility
    title: str = ""
    status: str = "Unknown"
    
    def __post_init__(self):
        """Set legacy fields for backward compatibility"""
        if not self.title and self.name:
            self.title = self.name
        if not self.status and self.submission_status:
            self.status = self.submission_status
    
    def to_dict(self) -> dict:
        """Convert assignment to dictionary for JSON serialization."""
        return {
            'course_code': self.course_code,
            'course_name': self.course_name,
            'name': self.name,
            'title': self.title,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'time_remaining': self.time_remaining,
            'submission_status': self.submission_status,
            'grading_status': self.grading_status,
            'status': self.status,
            'url': self.url,
            'description': self.description,
            'last_modified': self.last_modified,
            'id': self.id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Assignment':
        """Create assignment from dictionary."""
        assignment = cls(
            course_code=data.get('course_code', ''),
            course_name=data.get('course_name', ''),
            name=data.get('name', data.get('title', '')),
            time_remaining=data.get('time_remaining', ''),
            submission_status=data.get('submission_status', data.get('status', 'No attempt')),
            grading_status=data.get('grading_status', 'Not graded'),
            description=data.get('description', ''),
            url=data.get('url', ''),
            last_modified=data.get('last_modified', ''),
            id=data.get('id', '')
        )
        
        # Parse dates if they exist
        if data.get('due_date'):
            assignment.due_date = datetime.fromisoformat(data['due_date'])
            
        return assignment 