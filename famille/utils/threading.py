import multiprocessing


def async(func):
    """
    A decorator to make a function asynchronous,
    using the multiprocessing python lib.

    :param func:     the function to decorate
    """
    def wrapped(*args, **kwargs):
        process = multiprocessing.Process(target=func, args=args, kwargs=kwargs)
        process.start()

    return wrapped
