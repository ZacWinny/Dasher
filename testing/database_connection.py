import unittest
from main import create_app
from flask_sqlalchemy import SQLAlchemy


class DatabaseConnectionTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.db = SQLAlchemy(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_database_connection(self):
        result = self.db.engine.execute('select id from restaurants')
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
