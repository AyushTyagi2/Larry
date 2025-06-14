import sqlite3
import os
import datetime


class ScreenTimeDatabase:
    """Helper class for screen time database operations"""
    
    def __init__(self):
        """Initialize database connection"""
        # Create database directory if it doesn't exist
        db_dir = os.path.join(os.path.expanduser("~"), ".assistant", "databases")
        os.makedirs(db_dir, exist_ok=True)
        
        # Connect to database
        self.db_path = os.path.join(db_dir, "screen_time.db")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
        
        # Initialize database if not already set up
        self._initialize_db()
    
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
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracking_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            is_active BOOLEAN NOT NULL DEFAULT 1
        )
        ''')
        
        self.conn.commit()
    
    def start_tracking_session(self):
        """Record the start of a tracking session."""
        current_time = datetime.datetime.now()
        
        self.cursor.execute('''
        INSERT INTO tracking_sessions (start_time, is_active)
        VALUES (?, 1)
        ''', (current_time,))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def end_tracking_session(self, session_id=None):
        """End a tracking session or all active sessions."""
        current_time = datetime.datetime.now()
        
        if session_id:
            # End specific session
            self.cursor.execute('''
            UPDATE tracking_sessions
            SET end_time = ?, is_active = 0
            WHERE id = ? AND is_active = 1
            ''', (current_time, session_id))
        else:
            # End all active sessions
            self.cursor.execute('''
            UPDATE tracking_sessions
            SET end_time = ?, is_active = 0
            WHERE is_active = 1
            ''', (current_time,))
        
        self.conn.commit()
        return self.cursor.rowcount > 0
    
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
    
    def end_app_tracking(self, app_id):
        """End a tracking session for an app by setting the end time and calculating duration."""
        current_time = datetime.datetime.now()
        
        self.cursor.execute('''
        SELECT start_time FROM app_usage WHERE id = ?
        ''', (app_id,))
        result = self.cursor.fetchone()
        
        if result:
            start_time = datetime.datetime.fromisoformat(result['start_time'])
            duration = int((current_time - start_time).total_seconds())
            
            self.cursor.execute('''
            UPDATE app_usage SET end_time = ?, duration = ?
            WHERE id = ?
            ''', (current_time, duration, app_id))
            self.conn.commit()
            return True, duration
        
        return False, 0
    
    def end_website_tracking(self, website_id):
        """End a tracking session for a website by setting the end time and calculating duration."""
        current_time = datetime.datetime.now()
        
        self.cursor.execute('''
        SELECT start_time FROM website_usage WHERE id = ?
        ''', (website_id,))
        result = self.cursor.fetchone()
        
        if result:
            start_time = datetime.datetime.fromisoformat(result['start_time'])
            duration = int((current_time - start_time).total_seconds())
            
            self.cursor.execute('''
            UPDATE website_usage SET end_time = ?, duration = ?
            WHERE id = ?
            ''', (current_time, duration, website_id))
            self.conn.commit()
            return True, duration
        
        return False, 0
    
    def get_app_usage_today(self):
        """Get today's app usage statistics."""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT app_name, SUM(duration) as total_duration
        FROM app_usage
        WHERE date = ? AND duration IS NOT NULL
        GROUP BY app_name
        ORDER BY total_duration DESC
        ''', (today,))
        
        results = self.cursor.fetchall()
        
        app_usage = []
        for row in results:
            # Convert seconds to hours:minutes:seconds format
            duration = row['total_duration']
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            app_usage.append({
                "app_name": row['app_name'],
                "duration": duration,
                "duration_formatted": time_str
            })
        
        return app_usage
    
    def get_website_usage_today(self):
        """Get today's website usage statistics."""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT domain, SUM(duration) as total_duration
        FROM website_usage
        WHERE date = ? AND duration IS NOT NULL
        GROUP BY domain
        ORDER BY total_duration DESC
        ''', (today,))
        
        results = self.cursor.fetchall()
        
        website_usage = []
        for row in results:
            # Convert seconds to hours:minutes:seconds format
            duration = row['total_duration']
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            website_usage.append({
                "domain": row['domain'],
                "duration": duration,
                "duration_formatted": time_str
            })
        
        return website_usage
    
    def get_app_usage_by_date_range(self, start_date, end_date):
        """Get app usage for a specific date range."""
        self.cursor.execute('''
        SELECT app_name, SUM(duration) as total_duration,
               COUNT(DISTINCT date) as days_used
        FROM app_usage
        WHERE date BETWEEN ? AND ?
            AND duration IS NOT NULL
        GROUP BY app_name
        ORDER BY total_duration DESC
        ''', (start_date, end_date))
        
        results = self.cursor.fetchall()
        
        app_summary = []
        for row in results:
            # Convert seconds to hours:minutes:seconds format
            total_duration = row['total_duration']
            hours, remainder = divmod(total_duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            # Calculate daily average
            days_used = row['days_used']
            daily_avg = total_duration / days_used if days_used > 0 else 0
            avg_hours, avg_remainder = divmod(int(daily_avg), 3600)
            avg_minutes, avg_seconds = divmod(avg_remainder, 60)
            avg_time_str = f"{avg_hours:02}:{avg_minutes:02}:{avg_seconds:02}"
            
            app_summary.append({
                "app_name": row['app_name'],
                "total_duration": total_duration,
                "total_duration_formatted": time_str,
                "days_used": days_used,
                "daily_average": daily_avg,
                "daily_average_formatted": avg_time_str
            })
        
        return app_summary
    
    def get_website_usage_by_date_range(self, start_date, end_date):
        """Get website usage for a specific date range."""
        self.cursor.execute('''
        SELECT domain, SUM(duration) as total_duration,
               COUNT(DISTINCT date) as days_used
        FROM website_usage
        WHERE date BETWEEN ? AND ?
            AND duration IS NOT NULL
        GROUP BY domain
        ORDER BY total_duration DESC
        ''', (start_date, end_date))
        
        results = self.cursor.fetchall()
        
        website_summary = []
        for row in results:
            # Convert seconds to hours:minutes:seconds format
            total_duration = row['total_duration']
            hours, remainder = divmod(total_duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            # Calculate daily average
            days_used = row['days_used']
            daily_avg = total_duration / days_used if days_used > 0 else 0
            avg_hours, avg_remainder = divmod(int(daily_avg), 3600)
            avg_minutes, avg_seconds = divmod(avg_remainder, 60)
            avg_time_str = f"{avg_hours:02}:{avg_minutes:02}:{avg_seconds:02}"
            
            website_summary.append({
                "domain": row['domain'],
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
            ''', (daily_limit_seconds, result['id']))
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
            ''', (daily_limit_seconds, result['id']))
        else:
            # Create new limit
            self.cursor.execute('''
            INSERT INTO usage_limits (target_type, target_name, daily_limit)
            VALUES ('website', ?, ?)
            ''', (domain, daily_limit_seconds))
        
        self.conn.commit()
        return True, f"Set {daily_limit_minutes} minute daily limit for {domain}"
    
    def disable_limit(self, target_type, target_name):
        """Disable a usage limit."""
        self.cursor.execute('''
        UPDATE usage_limits
        SET is_active = 0
        WHERE target_type = ? AND target_name = ?
        ''', (target_type, target_name))
        
        self.conn.commit()
        return True, f"Disabled limit for {target_name}"
    
    def delete_limit(self, target_type, target_name):
        """Completely remove a usage limit."""
        self.cursor.execute('''
        DELETE FROM usage_limits
        WHERE target_type = ? AND target_name = ?
        ''', (target_type, target_name))
        
        self.conn.commit()
        return True, f"Deleted limit for {target_name}"
    
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
        for row in results:
            # Convert seconds to hours and minutes
            daily_limit = row['daily_limit']
            hours, remainder = divmod(daily_limit, 3600)
            minutes = remainder // 60
            
            limits.append({
                "type": row['target_type'],
                "name": row['target_name'],
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
        
        daily_limit = limit_result['daily_limit']
        
        # Get current usage
        if target_type == 'app':
            self.cursor.execute('''
            SELECT SUM(duration) as total_usage FROM app_usage
            WHERE app_name = ? AND date = ? AND duration IS NOT NULL
            ''', (target_name, today))
        else:  # website
            self.cursor.execute('''
            SELECT SUM(duration) as total_usage FROM website_usage
            WHERE domain = ? AND date = ? AND duration IS NOT NULL
            ''', (target_name, today))
        
        usage_result = self.cursor.fetchone()
        current_usage = usage_result['total_usage'] if usage_result['total_usage'] else 0
        
        return current_usage >= daily_limit, current_usage, daily_limit
    
    def get_unfinished_sessions(self):
        """Get any app or website tracking sessions that haven't been finished."""
        self.cursor.execute('''
        SELECT id, app_name, start_time
        FROM app_usage
        WHERE end_time IS NULL
        ORDER BY start_time DESC
        ''')
        unfinished_apps = self.cursor.fetchall()
        
        self.cursor.execute('''
        SELECT id, domain, url, start_time
        FROM website_usage
        WHERE end_time IS NULL
        ORDER BY start_time DESC
        ''')
        unfinished_websites = self.cursor.fetchall()
        
        return {
            "apps": unfinished_apps,
            "websites": unfinished_websites
        }
    
    def get_tracking_status(self):
        """Check if there are any active tracking sessions."""
        self.cursor.execute('''
        SELECT COUNT(*) as active_count
        FROM tracking_sessions
        WHERE is_active = 1
        ''')
        
        result = self.cursor.fetchone()
        is_tracking = result['active_count'] > 0
        
        return is_tracking
    
    def get_daily_summary(self, date=None):
        """Get a summary of app and website usage for a specific date."""
        if date is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Get total app usage
        self.cursor.execute('''
        SELECT SUM(duration) as total_app_time
        FROM app_usage
        WHERE date = ? AND duration IS NOT NULL
        ''', (date,))
        app_result = self.cursor.fetchone()
        total_app_time = app_result['total_app_time'] if app_result['total_app_time'] else 0
        
        # Get total website usage
        self.cursor.execute('''
        SELECT SUM(duration) as total_web_time
        FROM website_usage
        WHERE date = ? AND duration IS NOT NULL
        ''', (date,))
        web_result = self.cursor.fetchone()
        total_web_time = web_result['total_web_time'] if web_result['total_web_time'] else 0
        
        # Calculate formatted times
        total_time = total_app_time + total_web_time
        
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        hours, remainder = divmod(total_app_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        app_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        hours, remainder = divmod(total_web_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        web_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        return {
            "date": date,
            "total_time": total_time,
            "total_time_formatted": total_formatted,
            "app_time": total_app_time,
            "app_time_formatted": app_formatted,
            "web_time": total_web_time,
            "web_time_formatted": web_formatted
        }
    
    def clean_up_incomplete_entries(self, older_than_hours=24):
        """Clean up incomplete tracking entries older than the specified hours."""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=older_than_hours)
        
        # End incomplete app sessions
        self.cursor.execute('''
        SELECT id, start_time
        FROM app_usage
        WHERE end_time IS NULL AND start_time < ?
        ''', (cutoff_time,))
        
        for row in self.cursor.fetchall():
            app_id = row['id']
            start_time = datetime.datetime.fromisoformat(row['start_time'])
            duration = int((cutoff_time - start_time).total_seconds())
            
            self.cursor.execute('''
            UPDATE app_usage
            SET end_time = ?, duration = ?
            WHERE id = ?
            ''', (cutoff_time, duration, app_id))
        
        # End incomplete website sessions
        self.cursor.execute('''
        SELECT id, start_time
        FROM website_usage
        WHERE end_time IS NULL AND start_time < ?
        ''', (cutoff_time,))
        
        for row in self.cursor.fetchall():
            web_id = row['id']
            start_time = datetime.datetime.fromisoformat(row['start_time'])
            duration = int((cutoff_time - start_time).total_seconds())
            
            self.cursor.execute('''
            UPDATE website_usage
            SET end_time = ?, duration = ?
            WHERE id = ?
            ''', (cutoff_time, duration, web_id))
        
        # End incomplete tracking sessions
        self.cursor.execute('''
        UPDATE tracking_sessions
        SET end_time = ?, is_active = 0
        WHERE is_active = 1 AND start_time < ?
        ''', (cutoff_time, cutoff_time))
        
        self.conn.commit()
        return True
    
    def close(self):
        """Close the database connection."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()