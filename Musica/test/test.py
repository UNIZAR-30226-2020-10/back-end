from flaskr.db import DB
import unittest

DB.drop_all()
DB.create_all()

loader = unittest.TestLoader()
tests = loader.discover('.', "test_server.py")
testRunner = unittest.runner.TextTestRunner()
testRunner.run(tests)

DB.drop_all()
DB.create_all()
