import threading
import inspect
import ctypes
import time

class thread_control:
    def __init__(self):
        pass

    class submit:
        """
        例   如:
            def print_():
                print(time.time())
            thread = pool(func=print_,name='print',*args,**kwargs)
        暂停线程:thread.pause()
        恢复线程:thread.resume()
        停止线程:thread.stop()
        线程内函数已经为循环，不要将死循环函数放入线程中，否则线程可能会死掉
        """

        def __init__(self, func, name, state=False, *args, **kwargs):
            self.func = func
            self.name = name
            self.args = args
            self.kwargs = kwargs
            self.result = None
            self.__flag = threading.Event()  # 用于暂停线程的标识
            self.__flag.set()  # 设置为True
            self.__running = threading.Event()  # 用于停止线程的标识
            self.__running.set()  # 将running设置为True
            self.thread = threading.Thread(target=self.run, name=self.name)
            self.thread.setDaemon(state)
            self.thread.start()

        def run(self):
            while self.__running.is_set():
                self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
                try:
                    ret = self.func(*self.args, **self.kwargs)
                    self.result = ret
                except Exception as e:
                    print(e)
                    self.result = None
                # if ret == 'end':
                #     self.stop()
                #     break

        def pause(self):
            self.__flag.clear()  # 设置为False, 让线程阻塞

        def resume(self):
            self.__flag.set()  # 设置为True, 让线程停止阻塞

        def stop(self):
            self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
            self.__running.clear()  # 设置为False
            self.shutdown(self.thread)

        def get_result(self):
            if self.result:
                return self.result
            elif self.result is None:
                return None
            else:
                return None

        def alive(self):
            alive = self.thread.is_alive()
            # print('{} is alive: {}'.format(self.name, alive))
            return alive

        def shutdown(self, thread):
            def _async_raise(tid, exctype):

                """raises the exception, performs cleanup if needed"""

                tid = ctypes.c_long(tid)
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))

                if not inspect.isclass(exctype):
                    exctype = type(exctype)

                    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))

                if res == 0:

                    raise ValueError("invalid thread id")

                elif res != 1:

                    # """if it returns a number greater than one, you're in trouble,

                    # and you should call it again with exc=NULL to revert the effect"""

                    ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)

                    raise SystemError("PyThreadState_SetAsyncExc failed")

            try:
                _async_raise(thread.ident, SystemExit)
            except:
                pass

    class once:
        def __init__(self, func, name, state=True, *args, **kwargs):
            self.func = func
            self.name = name
            self.args = args
            self.kwargs = kwargs
            self.result = None
            self.thread = threading.Thread(target=self.run, name=self.name)
            self.thread.setDaemon(state)
            self.thread.start()
        def run(self):
            self.result = self.func(*self.args, **self.kwargs)

        def stop(self):
            self.shutdown(self.thread)

        def get_result(self):
            if self.result:
                return self.result
            elif self.result is None:
                return None
            else:
                return None

        def shutdown(self, thread):
            def _async_raise(tid, exctype):

                """raises the exception, performs cleanup if needed"""

                tid = ctypes.c_long(tid)
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))

                if not inspect.isclass(exctype):
                    exctype = type(exctype)

                    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))

                if res == 0:

                    raise ValueError("invalid thread id")

                elif res != 1:

                    # """if it returns a number greater than one, you're in trouble,

                    # and you should call it again with exc=NULL to revert the effect"""

                    ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)

                    raise SystemError("PyThreadState_SetAsyncExc failed")

            try:
                _async_raise(thread.ident, SystemExit)
            except:
                pass

        def alive(self):
            alive = self.thread.is_alive()
            # print('{} is alive: {}'.format(self.name, alive))
            return alive


def attempt(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(e)
        pass

def get_time():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

if __name__ == '__main__':
    thread_control = thread_control()
    a = thread_control.once(get_time, 'get_time', True)