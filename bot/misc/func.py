import time
from loguru import logger

logger.add("./logs/log.json", format="{time} | {level} | {message}",
           level="INFO", serialize=True, rotation="1 day", compression="zip")


def progressBar(iter, total, *, prefix='', suffix='', decimals=2, length=25, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iter / float(total)))
    filledLength = int(length * iter // total)
    bar_ = fill * filledLength + '_' * (length - filledLength)
    print(f'\r{prefix} |{bar_}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iter == total:
        print()


def waitBar(wait_time):  # wait_time in seconds
    for sec in range(wait_time + 1):
        progressBar(sec, wait_time, prefix=f'Пауза {wait_time} секунд(ы)')
        time.sleep(1)
