import sqlite3
import time
import datetime
import os
import platform
import subprocess
import re
from pathlib import Path

class ScreenTimeTracker:
    def __init__(self):
        """Initialize the screen time tracker with database connection."""
        # Create database directory if it doesn't exist
        db_dir = os.path.join(os.path.expanduser("~"), ".assistant", "databases")
        os.makedirs(db_dir, exist_ok=True)
        
        # Connect to database
        self.db_path = os.path.join(db_dir, "screen_time.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Initialize database if not already set up
        self._initialize_db()
        
        # Platform-specific variables
        self.platform = platform.system()  # 'Windows', 'Darwin' (macOS), or 'Linux'
    
    def _initialize_db(self):
        """Create necessary tables if they don't exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            duration INTEGER,
            date TEXT NOT NULL
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS website_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            url TEXT NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            duration INTEGER,
            date TEXT NOT NULL
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_type TEXT NOT NULL,  -- 'app' or 'website'
            target_name TEXT NOT NULL,  -- app name or domain
            daily_limit INTEGER NOT NULL,  -- in seconds
            is_active BOOLEAN NOT NULL DEFAULT 1
        )
        ''')
        
        self.conn.commit()
    
    def start_tracking(self):
        """Start tracking screen time in the background."""
        # This would ideally be run in a separate thread or process
        print("Screen time tracking started.")
        # Implementation depends on OS - would call platform-specific tracking methods
        return True, "Screen time tracking started successfully. Run in the background."
    
    def stop_tracking(self):
        """Stop the background tracking process."""
        # This would stop the background process
        print("Screen time tracking stopped.")
        return True, "Screen time tracking stopped."
    
    def get_active_window(self):
        """Get the currently active window/application based on the platform."""
        if self.platform == 'Windows':
            try:
                import win32gui
                window = win32gui.GetForegroundWindow()
                active_window_name = win32gui.GetWindowText(window)
                return active_window_name
            except ImportError:
                return "win32gui module not installed"
        
        elif self.platform == 'Darwin':  # macOS
            try:
                cmd = """osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true'"""
                active_window_name = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                return active_window_name
            except Exception as e:
                return f"Error getting active window: {e}"
        
        elif self.platform == 'Linux':
            try:
                cmd = """xprop -id $(xprop -root _NET_ACTIVE_WINDOW | cut -d ' ' -f 5) WM_CLASS | awk -F'"' '{print $4}'"""
                active_window_name = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8').strip()
                return active_window_name
            except Exception:
                return "Error getting active window on Linux"
        
        return "Unknown platform"
    
    def get_active_browser_tab(self):
        """Get the active browser tab URL (implementation would depend on browser and OS)."""
        # This is a placeholder for a more complex implementation
        # Real implementation would need browser extensions or accessibility APIs
        return "browser-tab-tracking-placeholder.com"
    
    def log_app_usage(self, app_name, duration=None):
        """Log application usage time."""
        current_time = datetime.datetime.now()
        current_date = current_time.strftime('%Y-%m-%d')
        
        if duration is None:
            # Start tracking this app
            self.cursor.execute('''
            INSERT INTO app_usage (app_name, start_time, date)
            VALUES (?, ?, ?)
            ''', (app_name, current_time, current_date))
            self.conn.commit()
            return self.cursor.lastrowid
        else:
            # Log with explicit duration (for manual entry)
            end_time = current_time
            start_time = current_time - datetime.timedelta(seconds=duration)
            
            self.cursor.execute('''
            INSERT INTO app_usage (app_name, start_time, end_time, duration, date)
            VALUES (?, ?, ?, ?, ?)
            ''', (app_name, start_time, end_time, duration, current_date))
            self.conn.commit()
            return self.cursor.lastrowid
    
    def log_website_usage(self, domain, url, duration=None):
        """Log website usage time."""
        current_time = datetime.datetime.now()
        current_date = current_time.strftime('%Y-%m-%d')
        
        if duration is None:
            # Start tracking this website
            self.cursor.execute('''
            INSERT INTO website_usage (domain, url, start_time, date)
            VALUES (?, ?, ?, ?)
            ''', (domain, url, current_time, current_date))
            self.conn.commit()
            return self.cursor.lastrowid
        else:
            # Log with explicit duration (for manual entry)
            end_time = current_time
            start_time = current_time - datetime.timedelta(seconds=duration)
            
            self.cursor.execute('''
            INSERT INTO website_usage (domain, url, start_time, end_time, duration, date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (domain, url, start_time, end_time, duration, current_date))
            self.conn.commit()
            return self.cursor.lastrowid
    
    def end_tracking_session(self, session_id, is_app=True):
        """End a tracking session by setting the end time and calculating duration."""
        current_time = datetime.datetime.now()
        
        if is_app:
            # End app tracking session
            self.cursor.execute('''
            SELECT start_time FROM app_usage WHERE id = ?
            ''', (session_id,))
            result = self.cursor.fetchone()
            
            if result:
                start_time = datetime.datetime.fromisoformat(result[0])
                duration = int((current_time - start_time).total_seconds())
                
                self.cursor.execute('''
                UPDATE app_usage SET end_time = ?, duration = ?
                WHERE id = ?
                ''', (current_time, duration, session_id))
                self.conn.commit()
                return True
        else:
            # End website tracking session
            self.cursor.execute('''
            SELECT start_time FROM website_usage WHERE id = ?
            ''', (session_id,))
            result = self.cursor.fetchone()
            
            if result:
                start_time = datetime.datetime.fromisoformat(result[0])
                duration = int((current_time - start_time).total_seconds())
                
                self.cursor.execute('''
                UPDATE website_usage SET end_time = ?, duration = ?
                WHERE id = ?
                ''', (current_time, duration, session_id))
                self.conn.commit()
                return True
        
        return False
    
    def get_app_usage_today(self):
        """Get today's app usage statistics."""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT app_name, SUM(duration)
        FROM app_usage
        WHERE date = ? AND duration IS NOT NULL
        GROUP BY app_name
        ORDER BY SUM(duration) DESC
        ''', (today,))
        
        results = self.cursor.fetchall()
        
        app_usage = []
        for app_name, duration in results:
            # Convert seconds to hours:minutes:seconds format
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            app_usage.append({
                "app_name": app_name,
                "duration": duration,
                "duration_formatted": time_str
            })
        
        return app_usage
    
    def get_website_usage_today(self):
        """Get today's website usage statistics."""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT domain, SUM(duration)
        FROM website_usage
        WHERE date = ? AND duration IS NOT NULL
        GROUP BY domain
        ORDER BY SUM(duration) DESC
        ''', (today,))
        
        results = self.cursor.fetchall()
        
        website_usage = []
        for domain, duration in results:
            # Convert seconds to hours:minutes:seconds format
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            website_usage.append({
                "domain": domain,
                "duration": duration,
                "duration_formatted": time_str
            })
        
        return website_usage
    
    def get_app_usage_summary(self, days=7):
        """Get app usage summary for the specified number of days."""
        # Calculate the date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        self.cursor.execute('''
        SELECT app_name, 
               SUM(duration) as total_duration,
               date,
               COUNT(DISTINCT date) as days_used
        FROM app_usage
        WHERE date BETWEEN ? AND ?
            AND duration IS NOT NULL
        GROUP BY app_name
        ORDER BY total_duration DESC
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        results = self.cursor.fetchall()
        
        app_summary = []
        for app_name, total_duration, date, days_used in results:
            # Convert seconds to hours:minutes:seconds format
            hours, remainder = divmod(total_duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            # Calculate daily average
            daily_avg = total_duration / days_used if days_used > 0 else 0
            avg_hours, avg_remainder = divmod(int(daily_avg), 3600)
            avg_minutes, avg_seconds = divmod(avg_remainder, 60)
            avg_time_str = f"{avg_hours:02}:{avg_minutes:02}:{avg_seconds:02}"
            
            app_summary.append({
                "app_name": app_name,
                "total_duration": total_duration,
                "total_duration_formatted": time_str,
                "days_used": days_used,
                "daily_average": daily_avg,
                "daily_average_formatted": avg_time_str
            })
        
        return app_summary
    
    def get_website_usage_summary(self, days=7):
        """Get website usage summary for the specified number of days."""
        # Calculate the date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        self.cursor.execute('''
        SELECT domain, 
               SUM(duration) as total_duration,
               date,
               COUNT(DISTINCT date) as days_used
        FROM website_usage
        WHERE date BETWEEN ? AND ?
            AND duration IS NOT NULL
        GROUP BY domain
        ORDER BY total_duration DESC
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        results = self.cursor.fetchall()
        
        website_summary = []
        for domain, total_duration, date, days_used in results:
            # Convert seconds to hours:minutes:seconds format
            hours, remainder = divmod(total_duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            # Calculate daily average
            daily_avg = total_duration / days_used if days_used > 0 else 0
            avg_hours, avg_remainder = divmod(int(daily_avg), 3600)
            avg_minutes, avg_seconds = divmod(avg_remainder, 60)
            avg_time_str = f"{avg_hours:02}:{avg_minutes:02}:{avg_seconds:02}"
            
            website_summary.append({
                "domain": domain,
                "total_duration": total_duration,
                "total_duration_formatted": time_str,
                "days_used": days_used,
                "daily_average": daily_avg,
                "daily_average_formatted": avg_time_str
            })
        
        return website_summary
    
    def set_app_limit(self, app_name, daily_limit_minutes):
        """Set daily time limit for an app in minutes."""
        daily_limit_seconds = daily_limit_minutes * 60
        
        # Check if limit already exists
        self.cursor.execute('''
        SELECT id FROM usage_limits
        WHERE target_type = 'app' AND target_name = ?
        ''', (app_name,))
        
        result = self.cursor.fetchone()
        
        if result:
            # Update existing limit
            self.cursor.execute('''
            UPDATE usage_limits
            SET daily_limit = ?, is_active = 1
            WHERE id = ?
            ''', (daily_limit_seconds, result[0]))
        else:
            # Create new limit
            self.cursor.execute('''
            INSERT INTO usage_limits (target_type, target_name, daily_limit)
            VALUES ('app', ?, ?)
            ''', (app_name, daily_limit_seconds))
        
        self.conn.commit()
        return True, f"Set {daily_limit_minutes} minute daily limit for {app_name}"
    
    def set_website_limit(self, domain, daily_limit_minutes):
        """Set daily time limit for a website domain in minutes."""
        daily_limit_seconds = daily_limit_minutes * 60
        
        # Check if limit already exists
        self.cursor.execute('''
        SELECT id FROM usage_limits
        WHERE target_type = 'website' AND target_name = ?
        ''', (domain,))
        
        result = self.cursor.fetchone()
        
        if result:
            # Update existing limit
            self.cursor.execute('''
            UPDATE usage_limits
            SET daily_limit = ?, is_active = 1
            WHERE id = ?
            ''', (daily_limit_seconds, result[0]))
        else:
            # Create new limit
            self.cursor.execute('''
            INSERT INTO usage_limits (target_type, target_name, daily_limit)
            VALUES ('website', ?, ?)
            ''', (domain, daily_limit_seconds))
        
        self.conn.commit()
        return True, f"Set {daily_limit_minutes} minute daily limit for {domain}"
    
    def remove_limit(self, target_type, target_name):
        """Remove a usage limit."""
        self.cursor.execute('''
        UPDATE usage_limits
        SET is_active = 0
        WHERE target_type = ? AND target_name = ?
        ''', (target_type, target_name))
        
        self.conn.commit()
        return True, f"Removed limit for {target_name}"
    
    def get_active_limits(self):
        """Get all active usage limits."""
        self.cursor.execute('''
        SELECT target_type, target_name, daily_limit
        FROM usage_limits
        WHERE is_active = 1
        ORDER BY target_type, target_name
        ''')
        
        results = self.cursor.fetchall()
        
        limits = []
        for target_type, target_name, daily_limit in results:
            # Convert seconds to hours and minutes
            hours, remainder = divmod(daily_limit, 3600)
            minutes = remainder // 60
            
            limits.append({
                "type": target_type,
                "name": target_name,
                "daily_limit_seconds": daily_limit,
                "daily_limit_formatted": f"{hours}h {minutes}m"
            })
        
        return limits
    
    def check_limit_exceeded(self, target_type, target_name):
        """Check if usage limit is exceeded for today."""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Get the limit
        self.cursor.execute('''
        SELECT daily_limit FROM usage_limits
        WHERE target_type = ? AND target_name = ? AND is_active = 1
        ''', (target_type, target_name))
        
        limit_result = self.cursor.fetchone()
        
        if not limit_result:
            # No limit set
            return False, 0, 0
        
        daily_limit = limit_result[0]
        
        # Get current usage
        if target_type == 'app':
            self.cursor.execute('''
            SELECT SUM(duration) FROM app_usage
            WHERE app_name = ? AND date = ? AND duration IS NOT NULL
            ''', (target_name, today))
        else:  # website
            self.cursor.execute('''
            SELECT SUM(duration) FROM website_usage
            WHERE domain = ? AND date = ? AND duration IS NOT NULL
            ''', (target_name, today))
        
        usage_result = self.cursor.fetchone()
        current_usage = usage_result[0] if usage_result[0] else 0
        
        return current_usage >= daily_limit, current_usage, daily_limit
    
    def export_report(self, days=30, format_type='text'):
        """Export screen time report for the specified number of days."""
        # Calculate the date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        # Get app usage data
        app_summary = self.get_app_usage_summary(days)
        
        # Get website usage data
        website_summary = self.get_website_usage_summary(days)
        
        if format_type == 'text':
            # Generate text report
            report = []
            report.append(f"Screen Time Report ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
            report.append("\n=== Application Usage ===")
            
            for app in app_summary[:10]:  # Top 10 apps
                report.append(f"{app['app_name']}: {app['total_duration_formatted']} total, "
                             f"{app['daily_average_formatted']} daily average")
            
            report.append("\n=== Website Usage ===")
            for site in website_summary[:10]:  # Top 10 websites
                report.append(f"{site['domain']}: {site['total_duration_formatted']} total, "
                             f"{site['daily_average_formatted']} daily average")
            
            # Add limits information
            limits = self.get_active_limits()
            if limits:
                report.append("\n=== Active Usage Limits ===")
                for limit in limits:
                    report.append(f"{limit['name']} ({limit['type']}): {limit['daily_limit_formatted']} daily limit")
            
            # Save report to file
            reports_dir = os.path.join(os.path.expanduser("~"), ".assistant", "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            report_file = os.path.join(reports_dir, f"screen_time_report_{end_date.strftime('%Y%m%d')}.txt")
            with open(report_file, 'w') as f:
                f.write('\n'.join(report))
            
            return True, f"Report exported to {report_file}"
        
        elif format_type == 'csv':
            # Generate CSV report
            import csv
            
            reports_dir = os.path.join(os.path.expanduser("~"), ".assistant", "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            # App usage CSV
            app_report_file = os.path.join(reports_dir, f"app_usage_{end_date.strftime('%Y%m%d')}.csv")
            with open(app_report_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['App Name', 'Total Duration (seconds)', 'Total Duration (formatted)', 
                                'Days Used', 'Daily Average (seconds)', 'Daily Average (formatted)'])
                
                for app in app_summary:
                    writer.writerow([
                        app['app_name'],
                        app['total_duration'],
                        app['total_duration_formatted'],
                        app['days_used'],
                        app['daily_average'],
                        app['daily_average_formatted']
                    ])
            
            # Website usage CSV
            web_report_file = os.path.join(reports_dir, f"website_usage_{end_date.strftime('%Y%m%d')}.csv")
            with open(web_report_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Domain', 'Total Duration (seconds)', 'Total Duration (formatted)', 
                                'Days Used', 'Daily Average (seconds)', 'Daily Average (formatted)'])
                
                for site in website_summary:
                    writer.writerow([
                        site['domain'],
                        site['total_duration'],
                        site['total_duration_formatted'],
                        site['days_used'],
                        site['daily_average'],
                        site['daily_average_formatted']
                    ])
            
            return True, f"Reports exported to {app_report_file} and {web_report_file}"
    
    def generate_usage_graphs(self, days=7):
        """Generate graphs for usage data (requires matplotlib)."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Create directory for graphs
            graphs_dir = os.path.join(os.path.expanduser("~"), ".assistant", "reports", "graphs")
            os.makedirs(graphs_dir, exist_ok=True)
            
            # Get data
            app_summary = self.get_app_usage_summary(days)
            website_summary = self.get_website_usage_summary(days)
            
            # App usage pie chart (top 5)
            if app_summary:
                plt.figure(figsize=(10, 6))
                labels = [app['app_name'] for app in app_summary[:5]]
                sizes = [app['total_duration'] for app in app_summary[:5]]
                
                # Add "Other" category if there are more than 5 apps
                if len(app_summary) > 5:
                    labels.append("Other")
                    sizes.append(sum(app['total_duration'] for app in app_summary[5:]))
                
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
                plt.title(f'App Usage Distribution (Last {days} Days)')
                
                app_chart_path = os.path.join(graphs_dir, f"app_usage_pie_{datetime.datetime.now().strftime('%Y%m%d')}.png")
                plt.savefig(app_chart_path)
                plt.close()
                
                # App usage bar chart (top 10)
                plt.figure(figsize=(12, 6))
                apps = [app['app_name'] for app in app_summary[:10]]
                durations = [app['total_duration']/3600 for app in app_summary[:10]]  # Convert to hours
                
                y_pos = np.arange(len(apps))
                plt.barh(y_pos, durations, align='center')
                plt.yticks(y_pos, apps)
                plt.xlabel('Hours')
                plt.title(f'Top App Usage (Last {days} Days)')
                
                app_bar_path = os.path.join(graphs_dir, f"app_usage_bar_{datetime.datetime.now().strftime('%Y%m%d')}.png")
                plt.savefig(app_bar_path)
                plt.close()
            
            # Website usage pie chart (top 5)
            if website_summary:
                plt.figure(figsize=(10, 6))
                labels = [site['domain'] for site in website_summary[:5]]
                sizes = [site['total_duration'] for site in website_summary[:5]]
                
                # Add "Other" category if there are more than 5 websites
                if len(website_summary) > 5:
                    labels.append("Other")
                    sizes.append(sum(site['total_duration'] for site in website_summary[5:]))
                
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
                plt.title(f'Website Usage Distribution (Last {days} Days)')
                
                web_chart_path = os.path.join(graphs_dir, f"web_usage_pie_{datetime.datetime.now().strftime('%Y%m%d')}.png")
                plt.savefig(web_chart_path)
                plt.close()
                
                # Website usage bar chart (top 10)
                plt.figure(figsize=(12, 6))
                sites = [site['domain'] for site in website_summary[:10]]
                durations = [site['total_duration']/3600 for site in website_summary[:10]]  # Convert to hours
                
                y_pos = np.arange(len(sites))
                plt.barh(y_pos, durations, align='center')
                plt.yticks(y_pos, sites)
                plt.xlabel('Hours')
                plt.title(f'Top Website Usage (Last {days} Days)')
                
                web_bar_path = os.path.join(graphs_dir, f"web_usage_bar_{datetime.datetime.now().strftime('%Y%m%d')}.png")
                plt.savefig(web_bar_path)
                plt.close()
                
            return True, "Generated usage graphs in reports/graphs directory"
            
        except ImportError:
            return False, "Matplotlib is required for graph generation. Install with 'pip install matplotlib'"
    
    def close(self):
        """Close the database connection."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

# Function to initialize the tracker
def initialize_screen_tracker():
    """Initialize and return the screen time tracker."""
    return ScreenTimeTracker()