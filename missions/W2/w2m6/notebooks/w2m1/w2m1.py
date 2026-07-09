'''
기능요구사항
task의 이름(A,B..) 과 지속시간을 정의
Worker Pool (Worker수: 2개)을 사용 할 것
작업 실행
작업 목록의 각 작업에 대해 작업 이름과 기간을 나타내는 대기 메시지를 출력
time.sleep을 사용하여 지정된 시간 동안 time.sleep 하면서 시뮬레이션
작업을 완료한 후, 작업이 완료되었음을 나타내는 메시지를 출력
동시성: 작업자 풀을 사용하여 작업이 동시에 실행
'''

import multiprocessing
import time

#로그 출력 프로세스를 진행하는 함수
def print_log(task):
    process_name, process_time = task
    print("Process ",process_name," waiting ",process_time," seconds")

    time.sleep(process_time) 

    print(f"Process {process_name} Finished")

if __name__ == "__main__":
    num_processes = 2

    duration_time = [("A",5),("B",2),("C",1),("D",3)]
    # Pool을 활용하여 멀티프로세싱 진행
    with multiprocessing.Pool(processes=2) as pool:
        pool.map(print_log,duration_time)