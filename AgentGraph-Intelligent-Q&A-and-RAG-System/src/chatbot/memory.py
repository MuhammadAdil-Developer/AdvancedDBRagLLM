import os
import pandas as pd
from typing import List,Dict
from datetime import datetime, date


import os
import pandas as pd
from typing import List
from datetime import datetime, date
import mysql.connector

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'myadmin',
    'password': 'admin123',
    'database': 'MyDB'
}

class Memory:
    @staticmethod
    def load_chat_history_from_db(thread_id: str) -> Dict[str, List[str]]:
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT user_query, ai_response
                FROM history
                WHERE thread_id = %s
            """
            cursor.execute(query, (thread_id,))
            result = cursor.fetchall()

            if not result:
                return {'human_message': [], 'Ai_response': []}

            chatbot_history = {
                'human_message': [row['user_query'] for row in result],
                'Ai_response': [row['ai_response'] for row in result]
            }

            return chatbot_history
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return {'human_message': [], 'Ai_response': []}
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def write_chat_history_to_db(chatbot_history: dict, thread_id: str, heading: str):
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            for user_query, ai_response in zip(chatbot_history['human_message'], chatbot_history['Ai_response']):
                query = """
                    INSERT INTO history (thread_id, user_query, ai_response, heading)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (thread_id, user_query, ai_response, heading))

            connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    @staticmethod
    def load_all_thread_ids_from_db() -> List[Dict[str, str]]:
        """
        Loads all distinct thread IDs and their headings from the database.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing a thread_id and heading.
        """
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)

            # Query to fetch all distinct thread IDs and headings
            query = "SELECT DISTINCT thread_id, heading FROM history"
            cursor.execute(query)
            result = cursor.fetchall()

            # Format the result as a list of dictionaries
            return result

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

