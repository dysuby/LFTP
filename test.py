import sys
from utils import Constant
import filecmp

if filecmp.cmp(Constant.SERVER_PATH + sys.argv[1], Constant.CLIENT_PATH + sys.argv[2], False):
    print('Same File')
else:
    print('Seem to not same')
