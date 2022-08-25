import sys
from Summary.analyze.util import add_tasks_to_db

'''
This script cannot be in the "TaskExtractor" package because then Django cannot migrate
'''
if __name__ == '__main__':
    add_tasks_to_db(sys.argv[1])
