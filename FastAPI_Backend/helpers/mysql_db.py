import threading
import mysql.connector

class DatabaseHandler:
    def __init__(self, host, user, password, database, port):
        # REMOVE HOSTNAME 
        clean_host = (
            str(host)
            .replace("http://", "")
            .replace("https://", "")
            .split(":")[0]
            .strip()
        )
        self.conn = mysql.connector.connect(
            host=clean_host,
            user=user,
            password=password,
            database=database,
            port=int(port),
            autocommit=True,
        )
        self._lock = threading.Lock()
        self.create_table()

    def get_cursor(self):
        return self.conn.cursor(dictionary=True, buffered=True)

    def create_table(self):
        query_table = """
        CREATE TABLE IF NOT EXISTS inspection_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            track_id INT,
            defective BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        with self._lock:
            cursor = self.get_cursor()
            cursor.execute(query_table)
            cursor.close()
            
    def log_many(self, rows):
        """rows: list of (track_id, defective, created_at)"""
        query = (
            "INSERT INTO inspection_logs (track_id, defective, created_at) "
            "VALUES (%s, %s, %s)"
        )
        with self._lock:
            cursor = self.get_cursor()
            cursor.executemany(query, rows)
            cursor.close()
            return len(rows)
    def get_all_logs(self):
        with self._lock:
            cursor = self.get_cursor()
            cursor.execute(
                "SELECT id, track_id, defective, created_at "
                "FROM inspection_logs ORDER BY id DESC"
            )
            logs = cursor.fetchall()
            cursor.close()
            return logs

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()