'''
기능요구사항
Task 분배. 10개의 태스크(0~9)를 task_to_accomplish 큐를 활용하여 수행
4개의 프로세스를 가지고 task to accomplish 큐에 있는 작업을 수행
각각의 프로세스는 현재 수행하고 있는 task를 출력하고 이후 수행 결과를 task_that_are_done 큐에 저장
time.sleep(0.5)를 활용하여 작업 수행 시간을 시뮬레이션 해보기
Process.join()을 통해 모든 프로세스들이 그들의 작업을 완료하도록 하기
모든 프로세스가 종료되면 tasks_that_are_done에 저장된 완료 메세지를 출력하기
'''

from multiprocessing import Process,Queue
from queue import Empty
import time 

# 작업 수행 함수를 정의
def execute_task(id,task_queue,done_queue):
    while True:
        # 예외 처리를 통해 여러 개의 프로세스에서 task를 가져가도록 함
        try:
            task = task_queue.get_nowait()
        except Empty:
            break
        
        # 할당 받은 task를 출력하고 0.5초 수행
        print(f"Task no {task}")
        time.sleep(0.5)

        # 완료 메세지를 done_queue에 put
        done_queue.put(f"Task {task} is done by Process-{id}")

if __name__ == "__main__":
    # 프로세스의 개수는 4개
    num_processes = 4

    task_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    # 10개의 작업을 task_to_accomplish 큐에 put
    for i in range(0,10):
        task_to_accomplish.put(i)

    processes = []

    # Process 정의 (프로세스 번호, 작업해야 할 큐, 작업 완료 큐)를 execute_task 함수에 전달
    for process_id in range(num_processes):
        p = Process(target=execute_task, args=(process_id+1,task_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # process.join()을 통해 모든 프로세스가 작업이 완료될 때 까지 기다림
    for process in processes:
        process.join()

    # 모든 프로세스가 종료되면 결과 출력물을 출력
    while not tasks_that_are_done.empty():
        print(tasks_that_are_done.get())

    
    

