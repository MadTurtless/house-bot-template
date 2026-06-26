"""
Handles interaction between the bot and the database.
Important: All database actions should go through this class. No SQL in other files!
"""
import logging
import sqlite3
import sys

logger = logging.getLogger("discord")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - %(message)s",
                    handlers=[
                        logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a+"),
                        logging.StreamHandler(stream=sys.stdout)
                    ])

class DatabaseManager:
    def __init__(self):
        """
        Stores the database path and initialises tables.
        """
        self.db_path = "data/db.sqlite"
        self._create_tables()

    def _execute(self, query: str, params: tuple = (), fetch: str = None, size: int = None):
        """
        A centralised wrapper that handles connections safely.
        Automatically commits and closes to prevent database locking.
        """
        # Timeout allows the bot to wait up to 10 seconds if a lock occurs
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)

                if fetch == "one":
                    return cursor.fetchone()
                elif fetch == "many":
                    return cursor.fetchmany(size)
                elif fetch == "all":
                    return cursor.fetchall()

                # Connection automatically commits upon exiting the 'with' block
                return 1
            except Exception as e:
                logger.error(f"Database error on query '{query}': {e}")
                return -1

    def _create_tables(self):
        """Creates the tables in the database if they don't yet exist."""
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            nr_events_attended INTEGER DEFAULT 0,
            lvl INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0
        );"""

        events_table = """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            host_id INTEGER,
            timestamp TEXT,
            channel_id INTEGER,
            msg_id INTEGER,
            FOREIGN KEY (host_id) REFERENCES users (id)
        );"""

        participants_table = """
        CREATE TABLE IF NOT EXISTS event_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (event_id) REFERENCES events (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        );"""

        invites_table = """
        CREATE TABLE IF NOT EXISTS invites (
            id TEXT PRIMARY KEY NOT NULL,
            inviter_id INTEGER NOT NULL
        );
        """

        invites_link_table = """
        CREATE TABLE IF NOT EXISTS invites_link (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invite_id TEXT NOT NULL,
            invitee_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invite_id) REFERENCES invites (id)
        )
        """

        self._execute(users_table)
        self._execute(events_table)
        self._execute(participants_table)
        self._execute(invites_table)
        self._execute(invites_link_table)

    def add_user(self, user_id: int):
        """Adds a user using its id."""
        query = "INSERT OR IGNORE INTO users(id) VALUES (?)"
        return self._execute(query, (user_id,))

    def add_event_participants(self, event_id, participants):
        """Adds a list of participants and updates their event count."""
        try:
            for p_id in participants:
                self.add_user(p_id)

                query_participant = ("INSERT INTO event_participants(event_id, user_id) "
                                     "VALUES (?, ?)")
                self._execute(query_participant, (event_id, p_id))

                query_update_user = ("UPDATE users "
                                     "SET nr_events_attended = nr_events_attended + 1 "
                                     "WHERE id = ?")
                self._execute(query_update_user, (p_id,))
            return 1
        except Exception as e:
            logger.error(e)
            return -1

    def get_event_participants(self, event_id: int):
        """Get a list of participants from the event_participants table."""
        query = ("SELECT user_id "
                 "FROM event_participants "
                 "WHERE event_id = ?")
        return self._execute(query, (event_id,), fetch="all")

    def add_event(self, event):
        """Adds an event to the events table and links participants."""
        query = """
        INSERT INTO events(type, host_id, timestamp, channel_id, msg_id) 
        VALUES (?, ?, ?, ?, ?)
        """
        params = (event["type"], event["host_id"], event["timestamp"].isoformat(), event["channel_id"], event["msg_id"])

        # Open connection manually here so we can grab the lastrowid safely in one atomic step
        try:
            with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                event_id = cursor.lastrowid # Grabs the ID of the row we literally just inserted

            self.add_event_participants(event_id, event["participants"])
            return 1
        except Exception as e:
            logger.error(e)
            return -1

    def update_event_type(self, event_id, event_type):
        query = ("UPDATE events "
                 "SET type = ? "
                 "WHERE id = ?")
        return self._execute(query, (event_type, event_id))

    def get_user(self, user_id: int):
        query = ("SELECT * "
                 "FROM users "
                 "WHERE id = ?")
        return self._execute(query, (user_id,), fetch="one")

    def add_user_xp(self, user_id: int, amount: int):
        query = ("UPDATE users "
                 "SET xp = xp + ? "
                 "WHERE id = ?")
        return self._execute(query, (amount, user_id))

    def get_user_xp(self, user_id: int):
        query = ("SELECT xp "
                 "FROM users "
                 "WHERE id = ?")
        res = self._execute(query, (user_id,), fetch="one")
        return res[0] if res and res != -1 else -1

    def add_user_level(self, user_id: int, level: int):
        query = ("UPDATE users "
                 "SET lvl = lvl + ? "
                 "WHERE id = ?")
        return self._execute(query, (level, user_id))

    def get_user_level(self, user_id: int):
        query = ("SELECT lvl F"
                 "ROM users "
                 "WHERE id = ?")
        res = self._execute(query, (user_id,), fetch="one")
        return res[0] if res and res != -1 else -1

    def get_top_ten_users(self):
        query = ("SELECT * "
                 "FROM users "
                 "ORDER BY xp DESC")
        return self._execute(query, fetch="many", size=10)

    def get_event(self, event_id: int):
        query = ("SELECT * "
                 "FROM events "
                 "WHERE id = ?")
        return self._execute(query, (event_id,), fetch="one")

    def get_event_by_msg_id(self, msg_id: int):
        query = ("SELECT * "
                 "FROM events "
                 "WHERE msg_id = ?")
        return self._execute(query, (msg_id,), fetch="one")

    def get_events_by_user(self, user_id: int):
        query = ("SELECT * "
                 "FROM event_participants "
                 "WHERE user_id = ?")
        return self._execute(query, (user_id,), fetch="all")

    def create_invite(self, invite_id: str, inviter_id: int):
        query = """INSERT INTO invites(id, inviter_id) 
                   VALUES (?, ?)"""
        return self._execute(query, (invite_id, inviter_id))

    def get_uses_per_invite(self):
        query = ("SELECT id "
                 "FROM invites")
        unique_invites = self._execute(query, fetch="all")
        uses = {}
        for invite in unique_invites:
            invite_id = invite[0]
            query = ("SELECT * "
                     "FROM invites_link "
                     "WHERE invite_id = ?")
            amount = len(self._execute(query, (invite_id,), fetch="all"))
            uses[invite_id] = amount
        return uses

    def add_invite_link(self, invite_id: str, invitee_id: int,):
        query = """SELECT * 
                   FROM invites_link 
                   WHERE invitee_id = ?"""
        user = self._execute(query, (invitee_id,), fetch="one")

        if user:
            query = """UPDATE invites_link 
                       SET status = ? 
                       WHERE invitee_id = ?"""
            return self._execute(query, ("joined", invitee_id), fetch="all")

        query = """INSERT INTO invites_link(invite_id, invitee_id, status) 
                   VALUES (?, ?, ?)"""
        return self._execute(query, (invite_id, invitee_id, "joined"))

    def remove_invite_link(self, invitee_id: int):
        query = """UPDATE invites_link 
                   SET status = ? 
                   WHERE invitee_id = ?"""
        return self._execute(query, ("left", invitee_id),)

    def get_invites_by_user(self, user_id: int):
        query = ("SELECT * "
                 "FROM invites_link "
                 "LEFT JOIN invites ON invites.id = invites_link.invite_id "
                 "WHERE inviter_id = ? AND status = ?")

        return self._execute(query, (user_id, "joined"), fetch="all")

    def get_top_inviters(self):
        query = ("SELECT invites.inviter_id, COUNT(invites.id) AS total_invites "
                 "FROM invites_link "
                 "LEFT JOIN invites ON invites.id = invites_link.invite_id "
                 "GROUP BY invites.inviter_id "
                 "ORDER BY total_invites DESC")

        return self._execute(query, fetch="many", size=10)
