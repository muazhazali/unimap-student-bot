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
        title: Assignment title/name
        due_date: When the assignment is due (if available)
        status: Current status (e.g., "Submitted", "Not submitted")
        url: Direct link to the assignment
        description: Assignment description (if available)
        last_modified: When the assignment was last updated
    """
    course_code: str
    title: str
    due_date: Optional[datetime] = None
    status: str = "Unknown"
    url: str = ""
    description: str = ""
    last_modified: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert assignment to dictionary for JSON serialization."""
        return {
            'course_code': self.course_code,
            'title': self.title,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'url': self.url,
            'description': self.description,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Assignment':
        """Create assignment from dictionary."""
        assignment = cls(
            course_code=data['course_code'],
            title=data['title'],
            status=data.get('status', 'Unknown'),
            url=data.get('url', ''),
            description=data.get('description', '')
        )
        
        # Parse dates if they exist
        if data.get('due_date'):
            assignment.due_date = datetime.fromisoformat(data['due_date'])
        if data.get('last_modified'):
            assignment.last_modified = datetime.fromisoformat(data['last_modified'])
            
        return assignment 