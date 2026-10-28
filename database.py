import mysql.connector
from mysql.connector import pooling
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages MySQL connection pool and offers context wrapper services."""
    _pool = None

    @classmethod
    def initialize_pool(cls, host, user, password, database, pool_size=10, pool_name='hospital_pool'):
        """Initializes the MySQL connection pool."""
        if cls._pool is None:
            try:
                cls._pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name=pool_name,
                    pool_size=pool_size,
                    pool_reset_session=True,
                    host=host,
                    user=user,
                    password=password,
                    database=database
                )
                logger.info(f"MySQL Connection Pool initialized successfully. Size: {pool_size}")
            except mysql.connector.Error as err:
                logger.error(f"Error initializing MySQL Connection Pool: {err}")
                raise err

    @classmethod
    def get_connection(cls):
        """Retrieves an active database connection from the pool."""
        if cls._pool is None:
            raise RuntimeError("Database Connection Pool has not been initialized. Call initialize_pool first.")
        return cls._pool.get_connection()

class DBConnectionContext:
    """Context manager for managing connection extraction and checkout safety."""
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = DatabaseManager.get_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            try:
                while getattr(self.conn, 'unread_result', False):
                    self.conn.get_rows()
            except Exception:
                pass
            try:
                self.conn.close()  # Returns connection back to pool
            except Exception:
                pass

class DBTransactionContext:
    """Context manager wrapping block actions within transactional boundaries."""
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = DatabaseManager.get_connection()
        self.conn.start_transaction()
        self.cursor = self.conn.cursor(dictionary=True)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                if self.conn:
                    try:
                        self.conn.rollback()
                        logger.warning("Transaction rolled back due to error.")
                    except mysql.connector.Error as rollback_err:
                        logger.error(f"Error executing transaction rollback: {rollback_err}")
            else:
                if self.conn:
                    self.conn.commit()
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
