###From a file, creates new linux users and passwords with administrator permissions

import os

__author__ = "Caleb Whitman"
__version__ = "1.0.0"
__email__ = "calebrwhitman@gmail.com"


""" Creates new users based off of the given user list
    Args:
        users (string): file containing a list of usernames and passwords. Created by createUsersList.py
        """
def createUsers(users):
    with open(users) as f:
        for line in f.readlines(0):
            namePass = line.split(';')
            user = namePass[0].strip('\n')
            password = namePass[1].strip('\n')
            print(user)

if __name__ == '__main__':
    createUsers("users.txt")