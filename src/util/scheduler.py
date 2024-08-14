import threading


class TaskScheduler:
    def __init__(self):
        self.tasks = {}

    def _execute_task(self, key, callback, *args, **kwargs):
        try:
            callback(*args, **kwargs)
        finally:
            del self.tasks[key]

    def schedule_task(self, key, callback, delay=0, *args, **kwargs):
        if key not in self.tasks:
            self.tasks[key] = threading.Timer(delay, self._execute_task, args=(key, callback) + args, kwargs=kwargs)
            self.tasks[key].start()


if __name__ == '__main__':
    def my_function(message):
        print(f"Function executed with message: {message}")


    scheduler = TaskScheduler()

    scheduler.schedule_task("task1", my_function, 5, "Hello after 5 seconds")
    scheduler.schedule_task("task1", my_function, 2, "Hello after 2 seconds")
    scheduler.schedule_task("task2", my_function, 3, "Hello after 3 seconds")
    scheduler.schedule_task("task3", my_function, 0, "Immediate execution")

    import time

    time.sleep(10)
