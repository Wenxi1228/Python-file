import threading

# 定义一个共享变量
shared_variable = 0

# 定义一个线程锁用于同步访问共享变量
lock = threading.Lock()

# 定义一个线程任务
def thread_task():
    global shared_variable

    # 获取线程锁
    lock.acquire()

    try:
        # 修改共享变量
        shared_variable += 1
        print(f"Thread {threading.current_thread().name}: Shared variable = {shared_variable}")
    finally:
        # 释放线程锁
        lock.release()

# 创建多个线程
threads = []
for i in range(5):
    thread = threading.Thread(target=thread_task)
    threads.append(thread)

# 启动所有线程
for thread in threads:
    thread.start()

# 等待所有线程结束
for thread in threads:
    thread.join()

# 所有线程执行完毕后打印最终的共享变量值
print(f"Final shared variable value: {shared_variable}")