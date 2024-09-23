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
    def schedule_task(cls, key, callback, *args, delay=0, **kwargs):
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


    TaskScheduler.schedule_task("task1", my_function, "Hello after 5 seconds", delay=5)
    TaskScheduler.schedule_task("task1", my_function, "Hello after 2 seconds", delay=2)
    TaskScheduler.schedule_task("task2", my_function, "Hello after 3 seconds", delay=3)
    TaskScheduler.schedule_task("task3", my_function, "Immediate execution", delay=0)

    import time

    time.sleep(10)
