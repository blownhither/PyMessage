import random
import time

from network.Client import Client

""" This is an example for Client
    .run            ->
    .get_groups:    -> [(group_id, name, n_members), ... ]
    .join_group:    group_id, in_group_alias -> confirmation
    .put_msg:       text_msg, target_group_id
    .read_msg       blocking -> [{msg=, groupId=, userId=, time=}, ...]
                        when blocking=False, returns False if no message

"""
if __name__ == "__main__":
    r = random.randint(0, 1000)
    client = Client(r)
    client.run()
    print("This is client " + str(r))

    client.start()
    print(client.get_groups())
    print(client.join_group(8848, "mzy1"))
    print(client.join_group(8848, "mzy2"))  # Rename

    # Note: Do NOT block me
    while True:
        msg = "Hello No." + str(random.randint(1000, 2000))
        client.put_msg(msg, 8848)
        ml = None
        while ml is None:
            ml = client.read_msg(blocking=False)
        for x in ml:
            print("server: " + str(x["msg"]))
        time.sleep(3)

    client.close()