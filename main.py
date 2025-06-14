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
from tasks.sports.football import get_football_scores, get_cricket_scores_db
from tasks.wikipedia.wiki import search_wikipedia
from tasks.currency_converter.financer import convert_currency, list_common_currencies
from tasks.notes.notes import create_note, list_notes, view_note, edit_note, delete_note
from tasks.calender.cal import add_event, list_events, view_event, delete_event, get_today_events
from tasks.voice.speech import start_voice_thread, queue_speech, listen_for_command, toggle_voice_listening
from tasks.security.password import generate_password, add_password, get_password, initialize_password_manager
from tasks.translator.translate import translate_text, list_common_languages

from tasks.pdfmanipulator.manipulate import merge_pdfs, extract_pdf_pages, rotate_pdf_pages, create_pdf_from_text, extract_text_from_pdf

from tasks.context.context_manager import update_context, get_context, get_related_context, save_context

from tasks.expense_tracker.expense_manager import ExpenseManager
from tasks.calories.calorie_counter import CalorieTracker
from tasks.music_player.music import MusicController,manage_music,initialize_music_controller

from tasks.screen_tracker.screen import ScreenTimeTracker
from tasks.screen_tracker.database import ScreenTimeDatabase
import datetime
import asyncio
import getpass

def handle_music_commands(user_input):
    """Process natural language music commands and call appropriate controller functions"""
    controller = initialize_music_controller()

    
def analyze_input(user_input):
    # First, update the context with the new user input
    update_context(user_input, context_type="user_input")
    controller = initialize_music_controller()

    
    # Now get any related context that might help with this query
    related_info = get_related_context(user_input)
    
    # Check if the input mentions sending an email
    if re.search(r"send email", user_input, re.IGNORECASE):
        # Update context specifically for email task
        update_context("Email task initiated", context_type="task")
        
        print("I detected that you want to send an email!")
        print("would you like to type it or just let your best friend larry handle the matter!!, just tell me")
        recipient = input("Please provide the recipient's email: ")
        subject = input("Please provide the subject: ")
        
        # Check related context for any information about this recipient
        recipient_context = get_related_context(recipient)
        if recipient_context:
            print(f"I see you've previously interacted with {recipient}. Using that information.")
        
        print("say write it for me, and i'll make the body according to the subject")
        choice = input("tell me your choice, pal!")
        if "write it for me" in choice:
            # Use context to generate more relevant email
            context_info = get_context(limit=5)  # Get recent context
            body = generate_email(subject, context=context_info)
            print(body)
            choice = input("would you like to proceed with this?")
            if(choice == "yes"): 
                send_email(recipient, subject, body)
                update_context(f"Sent email to {recipient} with subject: {subject}", context_type="email")
            else: 
                update_context("Email task canceled", context_type="email")
                # Don't use exit here as it would terminate the program
        else:
            body = input("Please provide the body: ")
            send_email(recipient, subject, body)
            update_context(f"Sent email to {recipient} with subject: {subject}", context_type="email")
    
    elif re.search(r"check emails|receive emails", user_input, re.IGNORECASE):
        update_context("Checking emails", context_type="email")
        print("I detected that you want to check your emails!")
        receive_emails()

    elif re.search(r"search for|google", user_input, re.IGNORECASE):
        update_context("Web search initiated", context_type="search")
        print("Got it! You want to search the web.")
        query = input("What would you like to search for? ")
        update_context(f"Searching for: {query}", context_type="search")
        google_search(query)

    elif re.search(r"remind me", user_input, re.IGNORECASE):
        update_context("Reminder creation initiated", context_type="reminder")
        print("Got it! You want to set a reminder.")
        try:
            time_part = input("In how many minutes? (e.g., 1): ")
            message = input("What should I remind you about? ")
            set_reminder(int(time_part), message)
            update_context(f"Set reminder for {message} in {time_part} minutes", context_type="reminder")
        except ValueError:
            print("Please enter a valid number of minutes.")
            update_context("Failed to set reminder - invalid time", context_type="error")

    elif re.search(r"weather in", user_input, re.IGNORECASE):
        update_context("Weather check initiated", context_type="weather")
        print("I detected that you want to know the weather!")
        city = input("Please provide the city: ")
        update_context(f"Checking weather for {city}", context_type="weather")
        get_weather(city)

    elif re.search(r"add task", user_input, re.IGNORECASE):
        update_context("Task addition initiated", context_type="task")
        task_name = input("What task would you like to add? ")
        add_task(task_name)
        update_context(f"Added task: {task_name}", context_type="task")

    elif re.search(r"show tasks", user_input, re.IGNORECASE):
        update_context("Showing tasks", context_type="task")
        get_tasks()

    elif re.search(r"mark task as done", user_input, re.IGNORECASE):
        update_context("Task completion initiated", context_type="task")
        try:
            task_index = int(input("Which task number would you like to mark as done? "))
            mark_done(task_index)
            update_context(f"Marked task #{task_index} as done", context_type="task")
        except ValueError:
            print("Please enter a valid task number.")
            update_context("Failed to mark task - invalid number", context_type="error")

    elif re.search(r"delete task", user_input, re.IGNORECASE):
        update_context("Task deletion initiated", context_type="task")
        try:
            task_index = int(input("Which task number would you like to delete? "))
            delete_task(task_index)
            update_context(f"Deleted task #{task_index}", context_type="task")
        except ValueError:
            print("Please enter a valid task number.")
            update_context("Failed to delete task - invalid number", context_type="error")

    elif re.search(r"find places|tourist places", user_input, re.IGNORECASE):
        update_context("Tourism search initiated", context_type="tourism")
        city_name = input("Which city would you like to know about? ")
        update_context(f"Finding places in {city_name}", context_type="tourism")
        find_places(city_name)

    elif re.search(r"search file", user_input, re.IGNORECASE):
        update_context("File search initiated", context_type="file")
        base_directory = input("Enter base directory to search from (e.g., /home/you or C:\\Users\\you): ")
        file_name = input("Enter the name (or part) of the file you're looking for: ")
        update_context(f"Searching for file '{file_name}' in {base_directory}", context_type="file")

        results = search_files(base_directory, file_name)

        if not results:
            print("No matching files found.")
            update_context("No files found matching search criteria", context_type="file")
        else:
            print("\nFound files:")
            for i, (name, full_path, directory) in enumerate(results):
                print(f"{i+1}. {name} — in {directory}")
            update_context(f"Found {len(results)} files matching search criteria", context_type="file")

            try:
                action = input("\nWould you like to [rename/move/delete/open] one of these? (type 'no' to skip): ").lower()
                if action in ["rename", "move", "delete", "open"]:
                    idx = int(input("Which file number? ")) - 1
                    _, file_path, _ = results[idx]
                    selected_file = os.path.basename(file_path)
                    update_context(f"Selected file: {selected_file}", context_type="file")

                    if action == "rename":
                        new_name = input("Enter the new filename: ")
                        rename_file(file_path, new_name)
                        update_context(f"Renamed {selected_file} to {new_name}", context_type="file")

                    elif action == "move":
                        new_dir = input("Enter the target directory: ")
                        move_file(file_path, new_dir)
                        update_context(f"Moved {selected_file} to {new_dir}", context_type="file")

                    elif action == "delete":
                        confirm = input("Are you sure you want to delete it? (yes/no): ")
                        if confirm.lower() == "yes":
                            delete_file(file_path)
                            update_context(f"Deleted file: {selected_file}", context_type="file")
                        else:
                            update_context(f"Canceled deletion of {selected_file}", context_type="file")

                    elif action == "open":
                        import subprocess
                        subprocess.run(["xdg-open" if os.name != 'nt' else "start", file_path], shell=True)
                        update_context(f"Opened file: {selected_file}", context_type="file")

            except Exception as e:
                print(f"An error occurred: {e}")
                update_context(f"Error in file operation: {str(e)}", context_type="error")

    elif re.search(r"scan text|ocr|extract text", user_input, re.IGNORECASE):
        update_context("OCR scan initiated", context_type="ocr")
        image_path = input("Please provide the path to the image: ")
        update_context(f"Scanning text from image: {os.path.basename(image_path)}", context_type="ocr")
        scan_text_from_image(image_path)

    elif "summarize" in user_input:
        update_context("Text summarization initiated", context_type="text")
        print("Please paste the text you want summarized. Enter a blank line when done:\n")

        lines = []
        while True:
            line = input(">>> ")
            if line.strip() == "":
                break
            lines.append(line)

        long_text = " ".join(lines)
        update_context(f"Summarizing text of length {len(long_text)} characters", context_type="text")
        result = summarize_text(long_text)
        print("\nSummary:", result)
        update_context("Text summarization completed", context_type="text")

    elif re.search(r"match|cricket|game", user_input, re.IGNORECASE):
        update_context("Sports score check initiated", context_type="sports")
        if("cricket" in user_input):
            update_context("Checking cricket scores", context_type="sports")
            get_cricket_scores()
        else:
            update_context("Checking football scores", context_type="sports")
            get_football_scores()

    elif re.search(r"create note|new note|add note", user_input, re.IGNORECASE):
        update_context("Note creation initiated", context_type="note")
        title = input("Enter note title: ")
        print("Enter note content (type END on a new line when finished):")
        
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        
        content = "\n".join(lines)
        create_note(title, content)
        update_context(f"Created note: {title}", context_type="note")

    elif re.search(r"add event|new event|create event", user_input, re.IGNORECASE):
        update_context("Event creation initiated", context_type="event")
        title = input("Enter event title: ")
        date_str = input("Enter date (YYYY-MM-DD): ")
        time_str = input("Enter time (HH:MM) or leave blank: ")
        location = input("Enter location (optional): ")
        description = input("Enter description (optional): ")
        
        add_event(title, date_str, time_str if time_str else None, 
                 description if description else None, 
                 location if location else None)
        update_context(f"Created event: {title} on {date_str}", context_type="event")
    
    elif re.search(r"list events|show events|my events|calendar", user_input, re.IGNORECASE):
        update_context("Calendar events check initiated", context_type="event")
        date_filter = None
        if "today" in user_input.lower():
            update_context("Showing today's events", context_type="event")
            get_today_events()
        else:
            filter_option = input("Show events for a specific date? (Enter date as YYYY-MM-DD or leave blank for all): ")
            if filter_option:
                update_context(f"Showing events for date: {filter_option}", context_type="event")
            else:
                update_context("Showing all events", context_type="event")
                
            events = list_events(filter_option if filter_option else None)
            
            if events:
                action = input("\nWould you like to view details of an event or delete one? (view/delete/no): ").lower()
                
                if action in ["view", "delete"]:
                    try:
                        event_id = int(input("Enter the event ID: "))
                        
                        if action == "view":
                            view_event(event_id)
                            update_context(f"Viewed event #{event_id}", context_type="event")
                        elif action == "delete":
                            confirm = input(f"Are you sure you want to delete event {event_id}? (yes/no): ")
                            if confirm.lower() == "yes":
                                delete_event(event_id)
                                update_context(f"Deleted event #{event_id}", context_type="event")
                            else:
                                update_context(f"Canceled deletion of event #{event_id}", context_type="event")
                    except ValueError:
                        print("Please enter a valid event ID.")
                        update_context("Failed to process event - invalid ID", context_type="error")
    
    elif re.search(r"list notes|show notes|my notes", user_input, re.IGNORECASE):
        update_context("Notes listing initiated", context_type="note")
        notes = list_notes()
        
        if notes:
            update_context(f"Found {len(notes)} notes", context_type="note")
            action = input("\nWould you like to view, edit, or delete a note? (view/edit/delete/no): ").lower()
            
            if action in ["view", "edit", "delete"]:
                try:
                    note_id = int(input("Enter the note ID: "))
                    
                    if action == "view":
                        view_note(note_id)
                        update_context(f"Viewed note #{note_id}", context_type="note")
                    elif action == "edit":
                        print("Enter new content (type END on a new line when finished):")
                        lines = []
                        while True:
                            line = input()
                            if line.strip().upper() == "END":
                                break
                            lines.append(line)
                        
                        new_content = "\n".join(lines)
                        edit_note(note_id, new_content=new_content)
                        update_context(f"Edited note #{note_id}", context_type="note")
                    elif action == "delete":
                        confirm = input(f"Are you sure you want to delete note {note_id}? (yes/no): ")
                        if confirm.lower() == "yes":
                            delete_note(note_id)
                            update_context(f"Deleted note #{note_id}", context_type="note")
                        else:
                            update_context(f"Canceled deletion of note #{note_id}", context_type="note")
                except ValueError:
                    print("Please enter a valid note ID.")
                    update_context("Failed to process note - invalid ID", context_type="error")
    
    elif re.search(r"wiki|wikipedia|what is|who is|define", user_input, re.IGNORECASE):
        update_context("Wikipedia search initiated", context_type="wiki")
        search_term = input("What would you like to look up? ")
        update_context(f"Looking up: {search_term} on Wikipedia", context_type="wiki")
        search_wikipedia(search_term)

    elif re.search(r"convert currency|exchange rate", user_input, re.IGNORECASE):
        update_context("Currency conversion initiated", context_type="finance")
        try:
            amount = float(input("Enter amount to convert: "))
            
            # Show common currencies
            list_common_currencies()
            
            from_currency = input("Convert from (currency code): ")
            to_currency = input("Convert to (currency code): ")
            
            update_context(f"Converting {amount} {from_currency} to {to_currency}", context_type="finance")
            convert_currency(amount, from_currency, to_currency)
        except ValueError:
            print("Please enter a valid number for the amount.")
            update_context("Failed to convert currency - invalid amount", context_type="error")

    elif re.search(r"password manager|manage passwords|passwords", user_input, re.IGNORECASE):
        update_context("Password management initiated", context_type="security")
        print("Password Manager")
        print("1. Initialize password manager")
        print("2. Add a password")
        print("3. Get a password")
        print("4. Generate a random password")
        choice = input("Choose an option (1-4): ")

        if choice == "1":
            initialize_password_manager()
            update_context("Initialized password manager", context_type="security")
        elif choice == "2":
            master_password = getpass.getpass("Enter master password: ")
            service = input("Enter service name (e.g., Gmail, Twitter): ")
            username = input("Enter username or email: ")
            use_generated = input("Generate a password? (y/n): ").lower() == 'y'
            update_context(f"Adding password for service: {service}", context_type="security")
            if use_generated:
                # Password will be generated in the add_password function
                add_password(master_password, service, username)
            else:
                password = getpass.getpass("Enter password: ")
                add_password(master_password, service, username, password)
        elif choice == "3":
            master_password = getpass.getpass("Enter master password: ")
            service = input("Enter service name (or leave blank to see all): ").strip()
            if not service:
                service = None
                update_context("Retrieving all passwords", context_type="security")
            else:
                update_context(f"Retrieving password for: {service}", context_type="security")
            get_password(master_password, service)
        elif choice == "4":
            length = int(input("Password length (default: 16): ") or 16)
            use_uppercase = input("Include uppercase letters? (y/n, default: y): ").lower() != 'n'
            use_digits = input("Include digits? (y/n, default: y): ").lower() != 'n'
            use_symbols = input("Include symbols? (y/n, default: y): ").lower() != 'n'
            update_context(f"Generating random password of length {length}", context_type="security")
            generate_password(length, use_uppercase, use_digits, use_symbols)
        else:
            print("Invalid option.")
            update_context("Invalid password manager option selected", context_type="error")
    elif re.search(r"screen time|screen tracker|track screen|screen usage", user_input, re.IGNORECASE):
        update_context("Screen time tracking initiated", context_type="productivity")
        print("Screen Time Tracker")
        print("1. Start tracking screen time")
        print("2. Stop tracking screen time")
        print("3. View today's app usage")
        print("4. View today's website usage")
        print("5. Set app usage limit")
        print("6. Set website usage limit")
        print("7. View active limits")
        print("8. Export usage report")
        print("9. Generate usage graphs")
        choice = input("Choose an option (1-9): ")

        # Create database directory if it doesn't exist
        db_dir = os.path.join(os.path.expanduser("~"), ".assistant", "databases")
        os.makedirs(db_dir, exist_ok=True)

        # Initialize tracker

    
        if choice == "1":
            tracker = ScreenTimeTracker()
            success, message = tracker.start_tracking()
            print(message)
            update_context("Started screen time tracking", context_type="productivity")
        
        elif choice == "2":
            tracker = ScreenTimeTracker()
            success, message = tracker.stop_tracking()
            print(message)
            update_context("Stopped screen time tracking", context_type="productivity")
        
        elif choice == "3":
            db = ScreenTimeDatabase()
            app_usage = db.get_app_usage_today()
            
            if app_usage:
                print("\nToday's App Usage:")
                for app in app_usage:
                    print(f"{app['app_name']}: {app['duration_formatted']}")
            else:
                print("No app usage recorded today.")
            
            db.close()
            update_context("Viewed today's app usage statistics", context_type="productivity")
        
        elif choice == "4":
            db = ScreenTimeDatabase()
            website_usage = db.get_website_usage_today()
            
            if website_usage:
                print("\nToday's Website Usage:")
                for site in website_usage:
                    print(f"{site['domain']}: {site['duration_formatted']}")
            else:
                print("No website usage recorded today.")
            
            db.close()
            update_context("Viewed today's website usage statistics", context_type="productivity")
        
        elif choice == "5":
            app_name = input("Enter app name: ")
            try:
                limit_minutes = int(input("Enter daily limit in minutes: "))
                tracker = ScreenTimeTracker()
                success, message = tracker.set_app_limit(app_name, limit_minutes)
                print(message)
                tracker.close()
                update_context(f"Set {limit_minutes} minute daily limit for {app_name}", context_type="productivity")
            except ValueError:
                print("Please enter a valid number for minutes.")
                update_context("Invalid input for app usage limit", context_type="error")
        
        elif choice == "6":
            domain = input("Enter website domain: ")
            try:
                limit_minutes = int(input("Enter daily limit in minutes: "))
                tracker = ScreenTimeTracker()
                success, message = tracker.set_website_limit(domain, limit_minutes)
                print(message)
                tracker.close()
                update_context(f"Set {limit_minutes} minute daily limit for {domain}", context_type="productivity")
            except ValueError:
                print("Please enter a valid number for minutes.")
                update_context("Invalid input for website usage limit", context_type="error")
        
        elif choice == "7":
            db = ScreenTimeDatabase()
            limits = db.get_active_limits()
            
            if limits:
                print("\nActive Usage Limits:")
                for limit in limits:
                    print(f"{limit['name']} ({limit['type']}): {limit['daily_limit_formatted']}")
            else:
                print("No active usage limits set.")
            
            db.close()
            update_context("Viewed active usage limits", context_type="productivity")
        
        elif choice == "8":
            try:
                days = int(input("Enter number of days for report (default: 30): ") or "30")
                format_type = input("Export format (text/csv) [default: text]: ").lower() or "text"
                
                if format_type not in ["text", "csv"]:
                    print("Invalid format. Using text format.")
                    format_type = "text"
                
                tracker = ScreenTimeTracker()
                success, message = tracker.export_report(days, format_type)
                print(message)
                tracker.close()
                update_context(f"Exported {days}-day usage report in {format_type} format", context_type="productivity")
            except ValueError:
                print("Please enter a valid number for days.")
                update_context("Invalid input for report days", context_type="error")
        
        elif choice == "9":
            try:
                days = int(input("Enter number of days for graphs (default: 7): ") or "7")
                
                tracker = ScreenTimeTracker()
                success, message = tracker.generate_usage_graphs(days)
                print(message)
                tracker.close()
                update_context(f"Generated usage graphs for the last {days} days", context_type="productivity")
            except ValueError:
                print("Please enter a valid number for days.")
                update_context("Invalid input for graph days", context_type="error")
        

    elif re.search(r"translate", user_input, re.IGNORECASE):
        update_context("Translation initiated", context_type="translate")
        print("I detected that you want to translate text!")
        text = input("Please provide the text you want to translate: ")
        target_language = input("Please provide the target language code (e.g., 'fr' for French): ")
        
        # Optionally, you can ask for a source language
        source_language = input("If you want to specify the source language, enter its code (or press Enter to auto-detect): ")
        
        if not source_language.strip():
            source_language = None  # Use auto-detection if no source language is provided
            update_context(f"Translating text to {target_language} (auto-detect source)", context_type="translate")
        else:
            update_context(f"Translating text from {source_language} to {target_language}", context_type="translate")
        
        # Run the asynchronous translation function
        translated_text = asyncio.run(translate_text(text, target_language, source_language))
        if translated_text:
            print(f"Translated text: {translated_text}")
            update_context("Translation completed successfully", context_type="translate")
    
    elif re.search(r"list languages|common languages", user_input, re.IGNORECASE):
        update_context("Listing language codes", context_type="translate")
        list_common_languages()
    
    # Check for PDF-related tasks
    elif re.search(r"merge pdfs", user_input, re.IGNORECASE):
        update_context("PDF merge initiated", context_type="pdf")
        print("I detected that you want to merge PDFs!")
        input_files = input("Enter the PDF files to merge (comma separated): ").split(',')
        output_file = input("Enter the output merged PDF filename: ")
        update_context(f"Merging {len(input_files)} PDFs to {output_file}", context_type="pdf")
        merge_pdfs(input_files, output_file)

    elif re.search(r"extract pdf pages", user_input, re.IGNORECASE):
        update_context("PDF page extraction initiated", context_type="pdf")
        print("I detected that you want to extract pages from a PDF!")
        input_file = input("Enter the input PDF file: ")
        page_range = input("Enter the page range to extract (e.g., '1-3,5,7-9'): ")
        output_file = input("Enter the output extracted PDF filename: ")
        update_context(f"Extracting pages {page_range} from {input_file} to {output_file}", context_type="pdf")
        extract_pdf_pages(input_file, page_range, output_file)

    elif re.search(r"rotate pdf", user_input, re.IGNORECASE):
        update_context("PDF rotation initiated", context_type="pdf")
        print("I detected that you want to rotate PDF pages!")
        input_file = input("Enter the input PDF file: ")
        rotation_angle = int(input("Enter the rotation angle (90, 180, or 270): "))
        output_file = input("Enter the output rotated PDF filename: ")
        update_context(f"Rotating {input_file} by {rotation_angle} degrees to {output_file}", context_type="pdf")
        rotate_pdf_pages(input_file, rotation_angle, output_file)

    elif re.search(r"create pdf", user_input, re.IGNORECASE):
        update_context("PDF creation initiated", context_type="pdf")
        print("I detected that you want to create a PDF from text!")
        text_content = input("Enter the text content for the PDF: ")
        output_file = input("Enter the output PDF filename: ")
        update_context(f"Creating PDF {output_file} from text", context_type="pdf")
        create_pdf_from_text(text_content, output_file)

    elif re.search(r"extract text from pdf", user_input, re.IGNORECASE):
        update_context("PDF text extraction initiated", context_type="pdf")
        print("I detected that you want to extract text from a PDF!")
        input_file = input("Enter the input PDF file: ")
        update_context(f"Extracting text from PDF: {input_file}", context_type="pdf")
        text = extract_text_from_pdf(input_file)
        if text:
            print("\nExtracted Text: ")
            print(text)
            update_context(f"Successfully extracted text from {input_file}", context_type="pdf")
            
    elif re.search(r"expense tracker|track expense|manage expense", user_input, re.IGNORECASE):
        update_context("Expense tracker initiated", context_type="finance")
        print("Expense Tracker")
        print("1. Add a new expense")
        print("2. List recent expenses")
        print("3. Show expense summary")
        print("4. Generate monthly report")
        print("5. Export expenses")
        print("6. Delete an expense")
        
        expense_manager = ExpenseManager()
        choice = input("Choose an option (1-6): ")
        
        if choice == "1":
            amount = input("Enter amount: ")
            category = input("Enter category (or leave blank to select from list): ").strip() or None
            description = input("Enter description (optional): ").strip() or None
            date = input("Enter date (YYYY-MM-DD) or leave blank for today: ").strip() or None
            
            success, message = expense_manager.add_expense(amount, category, description, date)
            print(message)
            update_context(f"Added expense: {amount} for {category if category else 'selected category'}", context_type="finance")
            
        elif choice == "2":
            print("\nFilter options (leave blank to show all):")
            category = input("Category: ").strip() or None
            start_date = input("Start date (YYYY-MM-DD): ").strip() or None
            end_date = input("End date (YYYY-MM-DD): ").strip() or None
            try:
                limit = int(input("Number of expenses to show: ").strip() or "10")
            except ValueError:
                limit = 10
                
            expense_manager.list_expenses(category, start_date, end_date, limit)
            update_context(f"Listed expenses with filters: {category}, {start_date}, {end_date}", context_type="finance")
            
        elif choice == "3":
            print("\nShow summary for:")
            print("1. Today")
            print("2. This week")
            print("3. This month")
            print("4. This year")
            print("5. All time")
            
            period_choice = input("Choose a period (1-5): ")
            periods = {"1": "day", "2": "week", "3": "month", "4": "year", "5": "all"}
            period = periods.get(period_choice, "month")
            
            expense_manager.show_summary(period)
            update_context(f"Showed expense summary for period: {period}", context_type="finance")
            
        elif choice == "4":
            year = input("Enter year (YYYY) or leave blank for current year: ").strip()
            month = input("Enter month (1-12) or leave blank for current month: ").strip()
            
            success, message = expense_manager.get_monthly_report(year or None, month or None)
            if not success:
                print(message)
            update_context(f"Generated monthly expense report for {month}/{year}", context_type="finance")
            
        elif choice == "5":
            format_choice = input("Export format (csv/json): ").lower() or "csv"
            start_date = input("Start date (YYYY-MM-DD) or leave blank: ").strip() or None
            end_date = input("End date (YYYY-MM-DD) or leave blank: ").strip() or None
            
            success, message = expense_manager.export_data(format_choice, start_date, end_date)
            print(message)
            update_context(f"Exported expenses to {format_choice} format", context_type="finance")
            
        elif choice == "6":
            # First list recent expenses
            expense_manager.list_expenses(limit=5)
            expense_id = input("\nEnter the ID of the expense to delete: ").strip()
            
            if expense_id:
                confirm = input(f"Are you sure you want to delete expense {expense_id}? (yes/no): ")
                if confirm.lower() == "yes":
                    success, message = expense_manager.delete_expense(expense_id)
                    print(message)
                    update_context(f"Deleted expense {expense_id}", context_type="finance")
                else:
                    print("Deletion cancelled.")
                    update_context("Expense deletion cancelled", context_type="finance")
            else:
                print("No expense ID provided.")
        
        else:
            print("Invalid option.")
    elif re.search(r"calorie tracker|track calories|track food|count calories", user_input, re.IGNORECASE):
        update_context("Calorie tracker initiated", context_type="health")
        print("Calorie Tracker")
        print("1. Log a meal")
        print("2. Log weight")
        print("3. Get today's summary")
        print("4. Get summary for specific day")
        print("5. Generate nutrition report")
        print("6. Update nutrition goals")
        print("7. View weight history")
        print("8. Add food to database")
        print("9. Search food database")
        print("10. Delete meal")

        calorie_tracker = CalorieTracker()
        choice = input("Choose an option (1-10): ")

        if choice == "1":
            food = input("Enter food name: ").strip()
            try:
                quantity = float(input("Enter quantity (default: 1): ") or "1")
            except ValueError:
                quantity = 1

            print("Meal types: Breakfast, Lunch, Dinner, Snack, Other")
            meal_type = input("Enter meal type (default: Other): ").strip() or "Other"

            success, message = calorie_tracker.log_meal(food, quantity, meal_type)
            print(message)
            update_context(f"Logged meal: {quantity} {food} as {meal_type}", context_type="health")

        elif choice == "2":
            try:
                weight = float(input("Enter your weight (kg): "))
                success, message = calorie_tracker.log_weight(weight)
                print(message)
                update_context(f"Logged weight: {weight} kg", context_type="health")
            except ValueError:
                print("Please enter a valid weight.")

        elif choice == "3":
            summary = calorie_tracker.get_today_summary()

            print(f"\nSummary for {summary['date']}:")
            print(f"Total Calories: {summary['total_calories']} / {summary['calorie_goal']} ({summary['remaining_calories']} remaining)")
            print(f"Protein: {summary['total_protein']:.1f}g / {summary['protein_goal']}g")
            print(f"Carbs: {summary['total_carbs']:.1f}g / {summary['carbs_goal']}g")
            print(f"Fat: {summary['total_fat']:.1f}g / {summary['fat_goal']}g")

            if summary['meals']:
                print("\nMeals:")
                for meal in summary['meals']:
                    print(f"- {meal['meal_type']}: {meal['food']} ({meal['calories']} cal, {meal['protein']:.1f}g protein)")

            update_context("Retrieved today's calorie summary", context_type="health")

        elif choice == "4":
            date = input("Enter date (YYYY-MM-DD): ")
            try:
                # Validate date format
                datetime.datetime.strptime(date, "%Y-%m-%d")
                summary = calorie_tracker.get_day_summary(date)

                print(f"\nSummary for {summary['date']}:")
                print(f"Total Calories: {summary['total_calories']} / {summary['calorie_goal']} ({summary['remaining_calories']} remaining)")
                print(f"Protein: {summary['total_protein']:.1f}g / {summary['protein_goal']}g")
                print(f"Carbs: {summary['total_carbs']:.1f}g / {summary['carbs_goal']}g")
                print(f"Fat: {summary['total_fat']:.1f}g / {summary['fat_goal']}g")

                if summary['meals']:
                    print("\nMeals:")
                    for meal in summary['meals']:
                        print(f"- {meal['meal_type']}: {meal['food']} ({meal['calories']} cal, {meal['protein']:.1f}g protein)")

                update_context(f"Retrieved calorie summary for {date}", context_type="health")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

        elif choice == "5":
            try:
                days = int(input("Number of days for report (default: 7): ") or "7")
                success, message = calorie_tracker.generate_report(days)
                print(message)
                update_context(f"Generated nutrition report for {days} days", context_type="health")
            except ValueError:
                print("Please enter a valid number of days.")

        elif choice == "6":
            print("Enter new nutrition goals (leave blank to keep current values):")
            try:
                calories_input = input("Daily calorie goal: ")
                calories = int(calories_input) if calories_input.strip() else None

                protein_input = input("Daily protein goal (g): ")
                protein = float(protein_input) if protein_input.strip() else None

                carbs_input = input("Daily carbs goal (g): ")
                carbs = float(carbs_input) if carbs_input.strip() else None

                fat_input = input("Daily fat goal (g): ")
                fat = float(fat_input) if fat_input.strip() else None

                success, message = calorie_tracker.update_goals(calories, protein, carbs, fat)
                print(message)
                update_context("Updated nutrition goals", context_type="health")
            except ValueError:
                print("Please enter valid numeric values.")

        elif choice == "7":
            try:
                days = int(input("Show weight history for how many days? (default: 30): ") or "30")
                weight_history = calorie_tracker.get_weight_history(days)

                if not weight_history:
                    print("No weight entries found for this period.")
                else:
                    print("\nWeight History:")
                    for date, weight in weight_history:
                        print(f"{date}: {weight} kg")

                update_context(f"Viewed weight history for {days} days", context_type="health")
            except ValueError:
                print("Please enter a valid number of days.")

        elif choice == "8":
            food_name = input("Enter food name: ").strip().lower()

            try:
                calories = float(input("Calories per serving: "))
                protein = float(input("Protein (g) per serving: "))
                carbs = float(input("Carbs (g) per serving: "))
                fat = float(input("Fat (g) per serving: "))

                success, message = calorie_tracker.add_food_to_database(food_name, calories, protein, carbs, fat)
                print(message)
                update_context(f"Added {food_name} to food database", context_type="health")
            except ValueError:
                print("Please enter valid nutritional values.")

        elif choice == "9":
            query = input("Enter food name to search: ").strip()
            results = calorie_tracker.search_food(query)

            if not results:
                print(f"No foods found matching '{query}'")
            else:
                print(f"\nFound {len(results)} matching foods:")
                for food, data in results.items():
                    print(f"- {food}: {data['calories']} cal, P: {data['protein']}g, C: {data['carbs']}g, F: {data['fat']}g")

            update_context(f"Searched food database for '{query}'", context_type="health")

        elif choice == "10":
            date_input = input("Date for meal deletion (YYYY-MM-DD, or leave blank for today): ").strip()
            date = date_input if date_input else datetime.datetime.now().strftime("%Y-%m-%d")

            try:
                # Validate date format
                datetime.datetime.strptime(date, "%Y-%m-%d")

                meals = calorie_tracker.get_meals_for_day(date)

                if not meals:
                    print(f"No meals found for {date}")
                else:
                    print(f"\nMeals for {date}:")
                    for meal in meals:
                        print(f"ID {meal['id']}: {meal['meal_type']} - {meal['food']} ({meal['calories']} cal)")

                    try:
                        meal_id = int(input("\nEnter ID of meal to delete: "))
                        confirm = input(f"Are you sure you want to delete meal ID {meal_id}? (yes/no): ")

                        if confirm.lower() == "yes":
                            success, message = calorie_tracker.delete_meal(meal_id)
                            print(message)
                            update_context(f"Deleted meal ID {meal_id}", context_type="health")
                        else:
                            print("Deletion cancelled.")
                    except ValueError:
                        print("Please enter a valid meal ID.")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

        else:
            print("Invalid option.")

        # Close the database connection
        calorie_tracker.close()

    elif re.search(r"play (song|track) (called |titled |named |'|\")?(.*?)(\'|\"|$| by)", user_input, re.IGNORECASE):
        song_title = re.search(r"play (song|track) (called |titled |named |'|\")?(.*?)(\'|\"|$| by)", user_input, re.IGNORECASE).group(3).strip()
        results = controller.search_songs(song_title)
        
        if results:
            success, message = controller.play_song(results[0]["id"])
            print(message)
            update_context(f"Playing song: {results[0]['title']} by {results[0]['artist']}", context_type="music")
        else:
            print(f"Couldn't find the song '{song_title}'")
    
    elif re.search(r"play (music|songs|tracks) by (artist |'|\")?(.*?)(\'|\"|$)", user_input, re.IGNORECASE):
        artist_name = re.search(r"play (music|songs|tracks) by (artist |'|\")?(.*?)(\'|\"|$)", user_input, re.IGNORECASE).group(3).strip()
        results = controller.search_songs(artist_name)
        
        if results:
            # Play the first song by this artist
            success, message = controller.play_song(results[0]["id"])
            print(message)
            update_context(f"Playing music by {artist_name}", context_type="music")
        else:
            print(f"Couldn't find any songs by '{artist_name}'")
    
    elif re.search(r"play playlist (called |titled |named |'|\")?(.*?)(\'|\"|$)", user_input, re.IGNORECASE):
        playlist_name = re.search(r"play playlist (called |titled |named |'|\")?(.*?)(\'|\"|$)", user_input, re.IGNORECASE).group(2).strip()
        success, message = controller.play_playlist(playlist_name)
        print(message)
        update_context(f"Playing playlist: {playlist_name}", context_type="music")
    
    # Control commands
    elif re.search(r"(pause|stop) (music|playback|song|track)", user_input, re.IGNORECASE) or user_input.lower() in ["pause", "stop music", "pause music"]:
        success, message = controller.pause()
        print(message)
        update_context("Paused music playback", context_type="music")
    
    elif re.search(r"resume|continue|play", user_input, re.IGNORECASE) and not re.search(r"play (song|track|playlist|music|songs|tracks)", user_input, re.IGNORECASE):
        success, message = controller.resume()
        print(message)
        update_context("Resumed music playback", context_type="music")
    
    elif re.search(r"next|skip", user_input, re.IGNORECASE):
        success, message = controller.next_song()
        print(message)
        update_context("Skipped to next song", context_type="music")
    
    elif re.search(r"previous|back", user_input, re.IGNORECASE):
        success, message = controller.previous_song()
        print(message)
        update_context("Returned to previous song", context_type="music")
    
    elif re.search(r"volume (up|down|to) (\d+)(%)?", user_input, re.IGNORECASE):
        match = re.search(r"volume (up|down|to) (\d+)(%)?", user_input, re.IGNORECASE)
        direction = match.group(1).lower()
        amount = int(match.group(2))
        
        if direction == "up":
            new_volume = min(controller.volume + amount, 100)
            success, message = controller.set_volume(new_volume)
        elif direction == "down":
            new_volume = max(controller.volume - amount, 0)
            success, message = controller.set_volume(new_volume)
        else:  # to
            success, message = controller.set_volume(amount)
        
        print(message)
        update_context(f"Changed volume to {controller.volume}%", context_type="music")
    
    # Info commands
    elif re.search(r"what('s| is) playing|current song|now playing", user_input, re.IGNORECASE):
        now_playing = controller.get_now_playing()
        
        if now_playing and now_playing.get("song"):
            song = now_playing["song"]
            print(f"Now playing: {song['title']} by {song['artist']}")
            update_context(f"Checked currently playing song: {song['title']}", context_type="music")
        else:
            print("Nothing is currently playing")
    
    elif re.search(r"list (all |my )?(playlists|music)", user_input, re.IGNORECASE):
        playlists = controller.list_playlists()
        
        if playlists:
            print("\nYour Playlists:")
            for i, playlist in enumerate(playlists):
                print(f"{i+1}. {playlist['name']} ({playlist['song_count']} songs)")
            update_context("Listed music playlists", context_type="music")
        else:
            print("You don't have any playlists yet")
    
    # If no command matched, fallback to the menu-based system


# Add this to your main.py to recognize natural language commands

    else:
    # Fallback to chatbot with context awareness
        try:
            # Format the context properly for get_response function
            formatted_context = []
            current_context = get_context(limit=10)  # Get the last 10 context items

            for ctx in current_context:
                # Format each context item based on its type
                if ctx.startswith("User: "):
                    # Keep user inputs as they are
                    formatted_context.append(ctx)
                elif ctx.startswith("Assistant response: "):
                    # Format assistant responses properly
                    formatted_context.append(ctx.replace("Assistant response: ", "Assistant: "))
                # Other context types can be added if needed based on your system

            # Pass formatted context to response generator
            response, context_used = get_response(user_input, context=formatted_context)

            # Update context with the response and what context was used
            update_context(f"Assistant response: {response}", context_type="assistant_response")
            if context_used:
                update_context(f"Used context: {context_used}", context_type="system")

            # If voice mode is active, queue the response for speech
            if mode == "voice":
                queue_speech(response)

            print("Larry:", response)
        except Exception as e:
            print(f"Chatbot failed to respond: {e}")
            update_context(f"Chatbot error: {str(e)}", context_type="error")
            # Provide a basic response when chatbot fails
            print("Larry: I'm sorry, I'm having trouble processing that request. Can you try something else?")
            if mode == "voice":
                queue_speech("I'm sorry, I'm having trouble processing that request. Can you try something else?")

if __name__ == "__main__":
    print("Welcome to your personal assistant bot!")
    
    # Initialize context at startup
    update_context("Session started", context_type="system")
    
    try:
        start_voice_thread()
        mode = input("Choose input mode (text/voice): ").strip().lower()
        update_context(f"Input mode selected: {mode}", context_type="system")

        while True:
            if mode == "voice":
                user_input = listen_for_command()
                if user_input is None:
                    continue  # Try listening again if speech was unclear
            else:
                user_input = input("How can I help you? ").strip()
            
            # Skip empty inputs
            if not user_input:
                continue
                
            # Update context with user input
            update_context(f"User: {user_input}", context_type="user_input")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                update_context("Session ended", context_type="system")
                queue_speech("Goodbye!")  # Let assistant say goodbye
                print("Goodbye!")
                # Save context before exiting
                save_context()
                break
                
            if user_input.lower() in ['what can you do ?', 'what can you do for me']:
                update_context("User asked about capabilities", context_type="system")
                queue_speech("Here is what I can do for you.")
                print("1. Send an email.")
                print("2. Check your emails.")
                print("3. Search the web.")
                print("4. Set reminders.")
                print("5. Check weather information.")
                print("6. Manage your tasks (add, list, complete, delete).")
                print("7. Find tourist places in different cities.")
                print("8. Manage files (search, rename, move, delete).")
                print("9. Summarize long texts.")
                print("10. Create and manage notes.")
                print("11. Keep track of calendar events.")
                print("12. Convert between currencies.")
                print("13. Look up information on Wikipedia :- just type whats the... .")
                print("14. Manage your passwords securely just type :- manage passwords.")
                print("15. Manipulate PDF files (merge, extract pages, rotate, create, extract text).")
                print("16. Translate text between languages:- just type translate.")
                print("Hey fam, I know the features are limited but we're working on it and we've many plan to go ahead, lets see currently we have a working calorie counter, a working expense manager, a working and secure password manager, which you can try the assistant can send and recieve mails, extract text from images manipulate pdfs, convert currencies, help you in your travels")
                continue
                
            try:
                analyze_input(user_input)
                # Save context periodically
                save_context()
            except Exception as e:
                print(f"Error processing your request: {e}")
                update_context(f"Error: {str(e)}", context_type="error")
    
    except KeyboardInterrupt:
        print("\nExiting due to user interrupt...")
        update_context("Session interrupted by user", context_type="system")
        save_context()
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        update_context(f"Critical error: {str(e)}", context_type="error")
        save_context()

        # add NLP
        # rectify the calorie counter and improve it
        # rectify the cricket scores
        # rectify the pdfmanipulator
        # 