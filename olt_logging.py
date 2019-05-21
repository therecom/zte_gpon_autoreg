import logging

def send_log(MODULE_NAME):

    logger = logging.getLogger(MODULE_NAME)
    logger.setLevel(logging.INFO)

#    console = logging.StreamHandler()
#    console.setLevel(logging.DEBUG)
    logfile = logging.FileHandler('logfile_test1.log')
    logfile.setLevel(logging.INFO)

#    formatter_console = logging.Formatter('{asctime} - {name} - {levelname} - {message}',
#                                  datefmt='%H:%M:%S', style='{')
    message = "\n{} - {}:\n{}\n{}".format('{asctime}',
                '{levelname}','{message}','-'*80)

    formatter_logfile = logging.Formatter(message, datefmt='%H:%M:%S', style='{')

#    console.setFormatter(formatter_console)
#    logger.addHandler(console)

    logfile.setFormatter(formatter_logfile)
    logger.addHandler(logfile)

    return logger
