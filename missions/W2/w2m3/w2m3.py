'''
[Push 연산]
큐에 items를 추가하기 시작할때 출력문을 내야 함
정해진 리스트에서 주어진 색상을 큐에 더해야 함
아이템의 수와 아이템 그자체를 큐에 더할 때 출력되어야 함

[Pop 연산]
큐로부터 아이템이 제거될 때 출력문을 내야 함
큐가 빌 때까지 큐로부터 하나씩 아이템을 제거해야 함. 
큐로부터 아이템이 제거될 때 아이템의 수와 아이템 그 자체가 출력되어야 함
'''

import multiprocessing
from queue import Empty


# push 연산
def push_op(queue, items):
    print("pushing items to queue:")

    # push 연산 진행
    for idx, color in enumerate(items, start=1):
        queue.put(color)
        print(f"item no: {idx} {color}")

# pop 연산
def pop_op(queue):
    print("popping items from queue:")

    idx = 0
    while True:
        try:
            color = queue.get_nowait()
        except Empty:
            break

        print(f"item no: {idx} {color}")
        idx += 1


if __name__ == "__main__":
    # 멀티프로세싱 큐 생성
    q = multiprocessing.Queue()
    items = ["red", "green", "blue", "black"]

    # push 프로세스 생성 및 실행
    push_process = multiprocessing.Process(target=push_op, args=(q, items))
    push_process.start()
    push_process.join()

    # pop 프로세스 생성 및 실행
    pop_process = multiprocessing.Process(target=pop_op, args=(q,))
    pop_process.start()
    pop_process.join()
    

