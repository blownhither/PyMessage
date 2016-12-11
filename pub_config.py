# PMDatagram Type num
CREATE_GROUP = 0
GET_GROUPS = 1
RETURN_GROUPS = 2
CLIENT_SEND_MSG = 3
SERVER_SEND_MSG = 4
GET_GROUP_MEMBERS = 5
RETURN_GROUP_MEMBERS = 6
HISTORY = 7
JOIN_GROUP = 8
CONFIRM_JOIN_GROUP = 9
REQUEST_ID = 10
RETURN_ID = 11
CONFIRM_CREATE_GROUP = 12
REQUEST_QUIT_GROUP = 13
CONFIRM_QUIT_GROUP = 14
SEND_FILE = 15
REQUEST_HISTORY = 16
RETURN_HISTORY = 17


# PMDatagram Fields
FIELDS = {
    "Type": "T", "T": "T", 0: "T",          # necessary
    "GroupId": "g", "g": "g", 1: "g",       # necessary
    "MsgId": "m", "m": "m", 2: "m",         # necessary
    "Time": "t", "t": "t", 3: "t",
    "Text": "x", "x": "x", 4: "x",
    "FileName": "f", "f": "f",
    "FileText": "ft", "ft": "ft",   # seg
    "List": "l", "l": "l",          # or append length
    "UserId": "u", "u": "u",
    "UserName": "n", "n": "n",
    # set to -1 when invalid but necessary
}

"""
    2. In RETURN_GROUPS mode, List field will be [(group_id, name, n_members), ]

"""