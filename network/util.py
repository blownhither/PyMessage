import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename="network/log/all.log",
                    filemode='a')


def exception_log(func):
    logger = logging.getLogger(__name__)

    def logged_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_str = "\n\n%s ( %s, %s )\n%s" \
                      % (func.__name__, args, kwargs, str(e))
            logger.exception(log_str)
    return logged_func
