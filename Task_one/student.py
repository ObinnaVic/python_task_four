from datetime import datetime
from typing import Optional

class Student:
    def __init__(self, name: str, student_id: Optional[str] = None):
        self.name = name
        self.student_id = student_id or f"STU{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.subjects = {}
        self.version_history = []
        self.created_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
    
    def add_subject_score(self, subject: str, score: float):
        if not (0 <= score <= 100):
            raise ValueError("Score must be between 0 and 100")
        
        old_score = self.subjects.get(subject)
        self.subjects[subject] = score
        
        # Record version history
        self.version_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'score_update' if old_score is not None else 'score_add',
            'subject': subject,
            'old_score': old_score,
            'new_score': score
        })
        
        self.last_updated = datetime.now().isoformat()
    
    def remove_subject(self, subject: str):
        if subject in self.subjects:
            old_score = self.subjects.pop(subject)
            self.version_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'score_remove',
                'subject': subject,
                'old_score': old_score,
                'new_score': None
            })
            self.last_updated = datetime.now().isoformat()
    
    def calculate_average(self) -> float:
        if not self.subjects:
            return 0.0
        return sum(self.subjects.values()) / len(self.subjects)
    
    def get_grade(self) -> str:
        avg = self.calculate_average()
        if avg >= 90:
            return 'A'
        elif avg >= 80:
            return 'B'
        elif avg >= 70:
            return 'C'
        elif avg >= 60:
            return 'D'
        else:
            return 'F'
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'student_id': self.student_id,
            'subjects': self.subjects,
            'version_history': self.version_history,
            'created_at': self.created_at,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create student from dictionary"""
        student = cls(data['name'], data.get('student_id'))
        student.subjects = data.get('subjects', {})
        student.version_history = data.get('version_history', [])
        student.created_at = data.get('created_at', datetime.now().isoformat())
        student.last_updated = data.get('last_updated', datetime.now().isoformat())
        return student

