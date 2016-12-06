import logging
import socket
import time
import network.config as config
import eventlet

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename="network/log/all.log",
                    filemode='a')


# def exit_on_conditions(func):
#     def inner(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except NeedExitException as e:
#             log_str = "\n\n%s ( %s, %s )\n%s" \
#                       % (func.__name__, args, kwargs, str(e))
#             logging.debug(log_str)
#             return


def exception_log(func):
    logger = logging.getLogger(__name__)

    def logged_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_str = "\n\n%s\n%s ( %s, %s )\n%s" \
                      % (__name__, func.__name__, args, kwargs, str(e))
            print(log_str)
            logger.exception(log_str)
    return logged_func


def exit_on_error(func, exception_type):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exception_type as e:
            error_str = "Exit on Exception " + str(exception_type) + "\n" + str(e)
            print(error_str)
            logging.error(error_str)
            eventlet.kill(eventlet.getcurrent())
            return None
    return inner


class NeedExitException(Exception):
    pass


@exception_log
def encode_timestamp():
    return int(time.time() * 1000).to_bytes(config.TIME_LEN, config.ENDIAN)


@exception_log
def decode_timestamp(bytes_msg):
    return int.from_bytes(bytes_msg, config.ENDIAN) / 1000.0


def dprint(*args):
    print(*args, flush=True)