# tasks/calendar/events.py
import os
import json
from datetime import datetime, timedelta

CALENDAR_FILE = "calendar_events.json"

def _load_events():
    if os.path.exists(CALENDAR_FILE):
        with open(CALENDAR_FILE, 'r') as f:
            return json.load(f)
    return []

def _save_events(events):
    with open(CALENDAR_FILE, 'w') as f:
        json.dump(events, f, indent=2)

def add_event(title, date_str, time_str=None, description=None, location=None):
    events = _load_events()
    
    try:
        # Parse date
        event_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Parse time if provided
        event_time = None
        if time_str:
            time_obj = datetime.strptime(time_str, "%H:%M")
            event_date = event_date.replace(hour=time_obj.hour, minute=time_obj.minute)
            event_time = time_str
        
        event_id = len(events) + 1
        
        new_event = {
            "id": event_id,
            "title": title,
            "date": date_str,
            "time": event_time,
            "description": description,
            "location": location
        }
        
        events.append(new_event)
        _save_events(events)
        
        print(f"Event '{title}' added for {date_str}{' at ' + time_str if time_str else ''}!")
        return event_id
    
    except ValueError:
        print("Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time.")
        return None

def list_events(filter_date=None):
    events = _load_events()
    
    if not events:
        print("No events found.")
        return []
    
    filtered_events = events
    if filter_date:
        try:
            target_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
            filtered_events = [e for e in events if datetime.strptime(e['date'], "%Y-%m-%d").date() == target_date]
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return []
    
    print("\nUpcoming Events:")
    for event in sorted(filtered_events, key=lambda x: (x['date'], x['time'] or '23:59')):
        time_info = f" at {event['time']}" if event['time'] else ""
        location_info = f" - {event['location']}" if event['location'] else ""
        print(f"{event['id']}. {event['title']} on {event['date']}{time_info}{location_info}")
    
    return filtered_events

def view_event(event_id):
    events = _load_events()
    for event in events:
        if event['id'] == event_id:
            print(f"\nEvent: {event['title']}")
            print(f"Date: {event['date']}")
            if event['time']:
                print(f"Time: {event['time']}")
            if event['location']:
                print(f"Location: {event['location']}")
            if event['description']:
                print(f"Description: {event['description']}")
            return event
    
    print(f"Event with ID {event_id} not found.")
    return None

def delete_event(event_id):
    events = _load_events()
    for i, event in enumerate(events):
        if event['id'] == event_id:
            removed = events.pop(i)
            _save_events(events)
            print(f"Event '{removed['title']}' deleted successfully!")
            return True
    
    print(f"Event with ID {event_id} not found.")
    return False

def get_today_events():
    today = datetime.now().strftime("%Y-%m-%d")
    return list_events(today)