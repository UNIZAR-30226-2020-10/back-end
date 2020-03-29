import os

from flaskr.app_content import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ['PORT'])
