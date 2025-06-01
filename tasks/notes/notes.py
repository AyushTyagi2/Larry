# tasks/notes/note_manager.py
import os
import json
from datetime import datetime

NOTES_FILE = "notes.json"

def _load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'r') as f:
            return json.load(f)
    return []

def _save_notes(notes):
    with open(NOTES_FILE, 'w') as f:
        json.dump(notes, f, indent=2)

def create_note(title, content):
    notes = _load_notes()
    note_id = len(notes) + 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_note = {
        "id": note_id,
        "title": title,
        "content": content,
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    notes.append(new_note)
    _save_notes(notes)
    print(f"Note '{title}' created successfully!")
    return note_id

def list_notes():
    notes = _load_notes()
    if not notes:
        print("No notes found.")
        return []
    
    print("\nYour Notes:")
    for note in notes:
        print(f"{note['id']}. {note['title']} - {note['created_at']}")
    
    return notes

def view_note(note_id):
    notes = _load_notes()
    for note in notes:
        if note['id'] == note_id:
            print(f"\nTitle: {note['title']}")
            print(f"Created: {note['created_at']}")
            print(f"Updated: {note['updated_at']}")
            print(f"\n{note['content']}")
            return note
    
    print(f"Note with ID {note_id} not found.")
    return None

def edit_note(note_id, new_title=None, new_content=None):
    notes = _load_notes()
    for note in notes:
        if note['id'] == note_id:
            if new_title:
                note['title'] = new_title
            if new_content:
                note['content'] = new_content
            note['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _save_notes(notes)
            print(f"Note updated successfully!")
            return True
    
    print(f"Note with ID {note_id} not found.")
    return False

def delete_note(note_id):
    notes = _load_notes()
    for i, note in enumerate(notes):
        if note['id'] == note_id:
            removed = notes.pop(i)
            _save_notes(notes)
            print(f"Note '{removed['title']}' deleted successfully!")
            return True
    
    print(f"Note with ID {note_id} not found.")
    return False