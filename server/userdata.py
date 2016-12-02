#-*-coding:utf-8-*- 
__author__ = 'kanchan'
import network

class Group():
    __group_count__ = 0

    def __init__(self, creator):
        self.creator = creator
        self.groupID = 'Group%d#%s' % (self.__group_count__, creator)
        self.__group_count__ += 1
        # [user, login_status]
        self.members = {creator: False}

groups = {}


def get_groups(user):
    res = []
    for groupID, group in groups:
        if user in group.members:
            res.append(groupID)
    return res


def join_group(user, groupID):
    if groupID not in groups:
        return
    group = groups[groupID]
    group.members[user] = True


# should be a callback function
def check_user_online():
    for groupID, group in groups:
        for user in group.members:
            if not test_user_online(groupID, user):
                group[user] = False
            else:
                group[user] = True


def test_user_online(groupID, user):
    pass


