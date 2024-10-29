import unittest
from app import db, app
from app import Author, Publisher, Inventory, Books

class TestModels(unittest.TestCase):

    def setUp(self):
        self.app = app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_author_creation(self):
        author = Author(name="Author two")
        db.session.add(author)
        db.session.commit()
        self.assertIsNotNone(author.id)
        self.assertEqual(author.name, "Author Two")

    def test_publisher_creation(self):
        publisher = Publisher(name="Publiser Two")
        db.session.add(publisher)
        db.session.commit()
        self.assertIsNotNone(publisher.id)
        self.assertEqual(publisher.name, "Publiser Two")

if __name__ == '__main__':
    unittest.main()
