import threading


class TaskScheduler:
    _tasks = {}

    @classmethod
    def _execute_task(cls, key, callback, *args, **kwargs):
        try:
            callback(*args, **kwargs)
        finally:
            del cls._tasks[key]

    @classmethod
    def schedule_task(cls, key, callback, delay=0, *args, **kwargs):
        if key not in cls._tasks:
            if delay:
                cls._tasks[key] = threading.Timer(delay, cls._execute_task, args=(key, callback) + args, kwargs=kwargs)
            else:
                cls._tasks[key] = threading.Thread(target=cls._execute_task, args=(key, callback) + args, kwargs=kwargs)

            cls._tasks[key].start()

    @classmethod
    def check_task(cls, key) -> bool:
        return key in cls._tasks


if __name__ == '__main__':
    def my_function(message):
        print(f"Function executed with message: {message}")


    TaskScheduler.schedule_task("task1", my_function, 5, "Hello after 5 seconds")
    TaskScheduler.schedule_task("task1", my_function, 2, "Hello after 2 seconds")
    TaskScheduler.schedule_task("task2", my_function, 3, "Hello after 3 seconds")
    TaskScheduler.schedule_task("task3", my_function, 0, "Immediate execution")

    import time

    time.sleep(10)
