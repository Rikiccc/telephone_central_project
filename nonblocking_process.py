import threading
import time
class KeyboardThread(threading.Thread):
    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()
    def run(self):
        while True:
            user_input = input()
            self.input_cbk(user_input)
            global stop
            stop = True
            break
def my_callback(inp):
    print('You Entered:', inp)
def count():
    while True:
        global current_time
        current_time = time.time()
        print('It has passed %.3f s' % (current_time-start_time))
        time.sleep(2)
        if stop:
            return
if __name__ == '__main__':
    start_time = time.time()
    current_time = None
    stop = False
    kthread = KeyboardThread(my_callback)
    count()
