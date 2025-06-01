import re
import os
from tasks.mail.send_email import send_email
from tasks.mail.receive_email import receive_emails
from tasks.search.web_search import google_search
from tasks.reminder.reminders import set_reminder
from tasks.weather.weather_info import get_weather
from tasks.to_do.task_manager import add_task, get_tasks, mark_done, delete_task
from tasks.tourism.find_places import find_places
from tasks.file_management.manage_files import search_files, rename_file, move_file, delete_file
from tasks.OCR_scanner.ocr import scan_text_from_image
from tasks.chatbot.response_generator import get_response
from tasks.chatbot.summarize import summarize_text
from tasks.chatbot.email import generate_email
from tasks.sports.cricket import get_cricket_scores
from tasks.sports.football import get_football_scores
from tasks.wikipedia.wiki import search_wikipedia
from tasks.currency_converter.financer import convert_currency, list_common_currencies
from tasks.notes.notes import create_note, list_notes, view_note, edit_note, delete_note
from tasks.calender.cal import add_event, list_events, view_event, delete_event, get_today_events
from tasks.voice.speech import start_voice_thread, queue_speech, listen_for_command, toggle_voice_listening

def analyze_input(user_input):
    if re.search(r"send email", user_input, re.IGNORECASE):
        queue_speech("I detected that you want to send an email! Would you like to type it or let Larry handle it?")
        print("I detected that you want to send an email!")
        print("Would you like to type it or just let your best friend Larry handle it? Just tell me.")
        recipient = input("Please provide the recipient's email: ")
        subject = input("Please provide the subject: ")
        queue_speech("Say write it for me, and I'll make the body according to the subject!")
        choice = input("Tell me your choice, pal: ")
        if "write it for me" in choice.lower():
            body = generate_email(subject)
            print(body)
            choice = input("Would you like to proceed with this? (yes/no): ")
            if choice.lower() == "yes":
                send_email(recipient, subject, body)
                queue_speech("Email sent successfully!")
        else:
            body = input("Please provide the body: ")
            send_email(recipient, subject, body)
            queue_speech("Email sent successfully!")

    elif re.search(r"check emails|receive emails", user_input, re.IGNORECASE):
        queue_speech("Checking your emails!")
        print("I detected that you want to check your emails!")
        receive_emails()

    elif re.search(r"search for|google", user_input, re.IGNORECASE):
        queue_speech("Got it! You want to search the web.")
        print("Got it! You want to search the web.")
        query = input("What would you like to search for? ")
        google_search(query)

    elif re.search(r"remind me", user_input, re.IGNORECASE):
        queue_speech("Setting up a reminder for you.")
        print("Got it! You want to set a reminder.")
        try:
            time_part = input("In how many minutes? (e.g., 1): ")
            message = input("What should I remind you about? ")
            set_reminder(int(time_part), message)
            queue_speech("Reminder set successfully!")
        except ValueError:
            queue_speech("Please enter a valid number of minutes.")
            print("Please enter a valid number of minutes.")

    elif re.search(r"weather in", user_input, re.IGNORECASE):
        queue_speech("Getting weather details!")
        print("I detected that you want to know the weather!")
        city = input("Please provide the city: ")
        get_weather(city)

    elif re.search(r"add task", user_input, re.IGNORECASE):
        task_name = input("What task would you like to add? ")
        add_task(task_name)
        queue_speech(f"Task '{task_name}' added!")

    elif re.search(r"show tasks", user_input, re.IGNORECASE):
        get_tasks()

    elif re.search(r"mark task as done", user_input, re.IGNORECASE):
        try:
            task_index = int(input("Which task number would you like to mark as done? "))
            mark_done(task_index)
            queue_speech(f"Marked task {task_index} as done!")
        except ValueError:
            queue_speech("Invalid task number.")
            print("Please enter a valid task number.")

    elif re.search(r"delete task", user_input, re.IGNORECASE):
        try:
            task_index = int(input("Which task number would you like to delete? "))
            delete_task(task_index)
            queue_speech(f"Deleted task {task_index}!")
        except ValueError:
            queue_speech("Invalid task number.")
            print("Please enter a valid task number.")

    elif re.search(r"find places|tourist places", user_input, re.IGNORECASE):
        city_name = input("Which city would you like to know about? ")
        find_places(city_name)
        queue_speech(f"Found tourist spots in {city_name}.")

    elif re.search(r"search file", user_input, re.IGNORECASE):
        base_directory = input("Enter base directory (e.g., /home/you): ")
        file_name = input("Enter file name or part of it: ")
        results = search_files(base_directory, file_name)
        if not results:
            queue_speech("No matching files found.")
            print("No matching files found.")
        else:
            queue_speech("Files found. Choose an action.")
            print("\nFound files:")
            for i, (name, full_path, directory) in enumerate(results):
                print(f"{i+1}. {name} — in {directory}")
            try:
                action = input("\nWould you like to [rename/move/delete/open] one? (no to skip): ").lower()
                if action in ["rename", "move", "delete", "open"]:
                    idx = int(input("Which file number? ")) - 1
                    _, file_path, _ = results[idx]
                    if action == "rename":
                        new_name = input("Enter the new filename: ")
                        rename_file(file_path, new_name)
                        queue_speech("File renamed.")
                    elif action == "move":
                        new_dir = input("Enter the target directory: ")
                        move_file(file_path, new_dir)
                        queue_speech("File moved.")
                    elif action == "delete":
                        confirm = input("Are you sure you want to delete it? (yes/no): ")
                        if confirm.lower() == "yes":
                            delete_file(file_path)
                            queue_speech("File deleted.")
                    elif action == "open":
                        import subprocess
                        subprocess.run(["xdg-open" if os.name != 'nt' else "start", file_path], shell=True)
                        queue_speech("Opened the file.")
            except Exception as e:
                print(f"An error occurred: {e}")

    elif re.search(r"scan text|ocr|extract text", user_input, re.IGNORECASE):
        image_path = input("Provide the image path: ")
        scan_text_from_image(image_path)
        queue_speech("Text extraction complete!")

    elif "summarize" in user_input:
        queue_speech("Ready to summarize. Paste the text.")
        print("Paste the text you want summarized. Enter blank line when done:")
        lines = []
        while True:
            line = input(">>> ")
            if line.strip() == "":
                break
            lines.append(line)
        long_text = " ".join(lines)
        result = summarize_text(long_text)
        print("\nSummary:", result)
        queue_speech("Here is your summary.")

    elif re.search(r"match|cricket|game", user_input, re.IGNORECASE):
        if "cricket" in user_input:
            get_cricket_scores()
        else:
            get_football_scores()

    elif re.search(r"create note|new note|add note", user_input, re.IGNORECASE):
        title = input("Enter note title: ")
        print("Enter note content (type END on new line when finished):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        content = "\n".join(lines)
        create_note(title, content)
        queue_speech(f"Note '{title}' created.")

    elif re.search(r"list notes|show notes|my notes", user_input, re.IGNORECASE):
        notes = list_notes()
        if notes:
            action = input("\nView, edit, or delete a note? (view/edit/delete/no): ").lower()
            if action in ["view", "edit", "delete"]:
                try:
                    note_id = int(input("Enter the note ID: "))
                    if action == "view":
                        view_note(note_id)
                    elif action == "edit":
                        print("Enter new content (END to finish):")
                        lines = []
                        while True:
                            line = input()
                            if line.strip().upper() == "END":
                                break
                            lines.append(line)
                        new_content = "\n".join(lines)
                        edit_note(note_id, new_content=new_content)
                    elif action == "delete":
                        confirm = input(f"Delete note {note_id}? (yes/no): ")
                        if confirm.lower() == "yes":
                            delete_note(note_id)
                except ValueError:
                    print("Invalid note ID.")

    elif re.search(r"add event|new event|create event", user_input, re.IGNORECASE):
        title = input("Enter event title: ")
        date_str = input("Enter date (YYYY-MM-DD): ")
        time_str = input("Enter time (HH:MM) or blank: ")
        location = input("Enter location (optional): ")
        description = input("Enter description (optional): ")
        add_event(title, date_str, time_str if time_str else None,
                  description if description else None,
                  location if location else None)
        queue_speech("Event added!")

    elif re.search(r"list events|show events|my events|calendar", user_input, re.IGNORECASE):
        if "today" in user_input.lower():
            get_today_events()
        else:
            filter_option = input("Show events for specific date? (YYYY-MM-DD or blank): ")
            events = list_events(filter_option if filter_option else None)

    elif re.search(r"wiki|wikipedia|what is|who is|define", user_input, re.IGNORECASE):
        search_term = input("What would you like to look up? ")
        search_wikipedia(search_term)

    elif re.search(r"convert currency|exchange rate", user_input, re.IGNORECASE):
        try:
            amount = float(input("Enter amount to convert: "))
            list_common_currencies()
            from_currency = input("Convert from (currency code): ")
            to_currency = input("Convert to (currency code): ")
            convert_currency(amount, from_currency, to_currency)
            queue_speech("Currency converted.")
        except ValueError:
            queue_speech("Invalid amount entered.")

    else:
        try:
            response, _ = get_response(user_input)
            print("Larry:", response)
            queue_speech(response)
        except Exception as e:
            print(f"Chatbot failed to respond: {e}")

if __name__ == "__main__":
    print("Welcome to your personal assistant bot!")
    queue_speech("Welcome to your personal assistant!")
    start_voice_thread()
    mode = input("Choose input mode (text/voice): ").strip().lower()

    while True:
        if mode == "voice":
            user_input = listen_for_command()
            if user_input is None:
                continue
        else:
            user_input = input("How can I help you? ").strip()

        if user_input.lower() in ['exit', 'quit', 'bye']:
            queue_speech("Goodbye! Have a nice day.")
            print("Goodbye!")
            break

        if user_input.lower() in ['what can you do ?', 'what can you do for me']:
            queue_speech("Here is what I can do for you.")
            print("""
            1. Send an email.
            2. Check your emails.
            3. Search the web.
            4. Set reminders.
            5. Check weather information.
            6. Manage tasks.
            7. Find tourist places.
            8. Manage files.
            9. Summarize texts.
            10. Create and manage notes.
            11. Manage calendar events.
            12. Convert currencies.
            13. Search Wikipedia.
            14. Manage your expense.
            15. Can keep a log of your calories. 
            """)
            continue

        analyze_input(user_input)
