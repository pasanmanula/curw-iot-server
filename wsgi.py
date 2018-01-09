
######################## debug ####################################################
import pydevd
import sys
sys.path.append("pycharm-debug-py3k.egg")

pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)
###################################################################################

from app import app

if __name__ == "__main__":
    app.run(debug=True)

