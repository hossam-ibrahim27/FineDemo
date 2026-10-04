import mysql.connector 

class DatabaseHandler:

    def __init__(self, host, user, password, database, port):
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
        self.create_table()

    def get_cursor(self):
        return self.conn.cursor(dictionary=True, buffered=True)

    def create_table(self):
        query_table = """
        CREATE TABLE IF NOT EXISTS inspection_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            track_id INT UNIQUE,
            damage BOOLEAN NOT NULL DEFAULT FALSE,
            image_path VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor = self.get_cursor()
        cursor.execute(query_table)
        cursor.close()

    def log_inspection(self, track_id, damage, image_path=None):
        query = """
        INSERT INTO inspection_logs (track_id, damage, image_path)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            damage = VALUES(damage),
            image_path = VALUES(image_path)
        """
        cursor = self.get_cursor()
        cursor.execute(
            query, (track_id, damage, image_path)
        )
        self.conn.commit()
        cursor.close()

    def get_all_logs(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT id, track_id, damage, image_path, created_at FROM inspection_logs ORDER BY id DESC")
        logs = cursor.fetchall()
        cursor.close()
        return logs

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()