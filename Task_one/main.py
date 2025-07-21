import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from student import Student

class StudentReportCardApp:
    
    def __init__(self, data_file: str = 'students_data.json'):
        self.data_file = data_file
        self.students = {}
        self.load_data()
    
    def save_data(self):
        try:
            data = {
                'students': {sid: student.to_dict() for sid, student in self.students.items()},
                'last_backup': datetime.now().isoformat()
            }
            
            # Create backup of existing file
            if os.path.exists(self.data_file):
                backup_file = f"{self.data_file}.backup"
                os.rename(self.data_file, backup_file)
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Data saved successfully to {self.data_file}")
            
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                student_data = data.get('students', {})
                for sid, sdata in student_data.items():
                    self.students[sid] = Student.from_dict(sdata)
                
                print(f"✅ Loaded {len(self.students)} students from {self.data_file}")
            else:
                print(f"📁 No existing data file found. Starting fresh.")
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            print("Starting with empty database.")
    
    def add_student(self, name: str) -> str:
        student = Student(name)
        self.students[student.student_id] = student
        print(f"✅ Added student: {name} (ID: {student.student_id})")
        return student.student_id
    
    def find_student(self, identifier: str) -> Optional[Student]:
        # find by ID first
        if identifier in self.students:
            return self.students[identifier]
        
        # Then find by name
        for student in self.students.values():
            if student.name.lower() == identifier.lower():
                return student
        
        return None
    
    def add_score(self, student_identifier: str, subject: str, score: float):
        student = self.find_student(student_identifier)
        if not student:
            print(f"❌ Student '{student_identifier}' not found")
            return
        
        try:
            student.add_subject_score(subject, score)
            print(f"✅ Added {subject}: {score} for {student.name}")
        except ValueError as e:
            print(f"❌ Error: {e}")
    
    def view_student(self, student_identifier: str):
        student = self.find_student(student_identifier)
        if not student:
            print(f"❌ Student '{student_identifier}' not found")
            return
        
        print(f"\n{'='*50}")
        print(f"📊 STUDENT REPORT CARD")
        print(f"{'='*50}")
        print(f"Name: {student.name}")
        print(f"ID: {student.student_id}")
        print(f"Created: {student.created_at}")
        print(f"Last Updated: {student.last_updated}")
        print(f"\n📚 SUBJECTS & SCORES:")
        print(f"{'-'*30}")
        
        if student.subjects:
            for subject, score in student.subjects.items():
                print(f"{subject:<20} {score:>6.1f}")
            
            print(f"{'-'*30}")
            print(f"{'Average':<20} {student.calculate_average():>6.1f}")
            print(f"{'Letter Grade':<20} {student.get_letter_grade():>6}")
        else:
            print("No subjects recorded yet.")
        
        print(f"{'='*50}\n")
    
    def view_all_students(self):
        if not self.students:
            print("📂 No students in database")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 ALL STUDENTS SUMMARY")
        print(f"{'='*80}")
        print(f"{'Name':<20} {'ID':<15} {'Subjects':<10} {'Average':<10} {'Grade':<8}")
        print(f"{'-'*80}")
        
        for student in sorted(self.students.values(), key=lambda x: x.name):
            avg = student.calculate_average()
            grade = student.get_letter_grade()
            subject_count = len(student.subjects)
            
            print(f"{student.name:<20} {student.student_id:<15} {subject_count:<10} {avg:<10.1f} {grade:<8}")
        
        print(f"{'='*80}\n")
    
    def view_version_history(self, student_identifier: str):
        student = self.find_student(student_identifier)
        if not student:
            print(f"❌ Student '{student_identifier}' not found")
            return
        
        if not student.version_history:
            print(f"📜 No version history for {student.name}")
            return
        
        print(f"\n{'='*60}")
        print(f"📜 VERSION HISTORY: {student.name}")
        print(f"{'='*60}")
        
        for i, entry in enumerate(reversed(student.version_history), 1):
            timestamp = entry['timestamp']
            action = entry['action']
            subject = entry['subject']
            old_score = entry.get('old_score')
            new_score = entry.get('new_score')
            
            print(f"{i}. {timestamp}")
            if action == 'score_add':
                print(f"   ➕ Added {subject}: {new_score}")
            elif action == 'score_update':
                print(f"   ✏️  Updated {subject}: {old_score} → {new_score}")
            elif action == 'score_remove':
                print(f"   ❌ Removed {subject} (was: {old_score})")
            print()
        
        print(f"{'='*60}\n")
    
    def update_student_name(self, student_identifier: str, new_name: str):
        student = self.find_student(student_identifier)
        if not student:
            print(f"❌ Student '{student_identifier}' not found")
            return
        
        old_name = student.name
        student.name = new_name
        student.last_updated = datetime.now().isoformat()
        
        student.version_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'name_update',
            'old_name': old_name,
            'new_name': new_name
        })
        
        print(f"✅ Updated student name: {old_name} → {new_name}")
    
    def remove_student(self, student_identifier: str):
        student = self.find_student(student_identifier)
        if not student:
            print(f"❌ Student '{student_identifier}' not found")
            return
        
        confirm = input(f"⚠️  Are you sure you want to remove {student.name}? (y/N): ").lower()
        if confirm == 'y':
            del self.students[student.student_id]
            print(f"✅ Removed student: {student.name}")
        else:
            print("❌ Operation cancelled")
    
    def run(self):
        print("🎓 Welcome to Student Report Card Manager!")
        print("Type 'help' for available commands or 'quit' to exit.\n")
        
        while True:
            try:
                command = input("📝 Enter command: ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    self.save_data()
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    self.show_help()
                
                elif command == 'add':
                    name = input("Enter student name: ").strip()
                    if name:
                        self.add_student(name)
                    else:
                        print("❌ Name cannot be empty")
                
                elif command == 'score':
                    student_id = input("Enter student name or ID: ").strip()
                    subject = input("Enter subject: ").strip()
                    try:
                        score = float(input("Enter score (0-100): "))
                        self.add_score(student_id, subject, score)
                    except ValueError:
                        print("❌ Invalid score. Please enter a number.")
                
                elif command == 'view':
                    student_id = input("Enter student name or ID: ").strip()
                    self.view_student(student_id)
                
                elif command == 'list':
                    self.view_all_students()
                
                elif command == 'history':
                    student_id = input("Enter student name or ID: ").strip()
                    self.view_version_history(student_id)
                
                elif command == 'update':
                    student_id = input("Enter student name or ID: ").strip()
                    new_name = input("Enter new name: ").strip()
                    if new_name:
                        self.update_student_name(student_id, new_name)
                    else:
                        print("❌ Name cannot be empty")
                
                elif command == 'remove':
                    student_id = input("Enter student name or ID: ").strip()
                    self.remove_student(student_id)
                
                elif command == 'save':
                    self.save_data()
                
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                self.save_data()
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    app = StudentReportCardApp()
    app.run()
