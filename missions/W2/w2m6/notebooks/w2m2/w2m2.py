'''
기능요구사항
대륙 이름을 포함한 문장을 출력하는 함수
다른 이름이 제공되지 않는 경우 함수는 기본 대륙으로 "Asia"를 사용
스크립트는 기본 대륙과 함께 기능을 한 번 실행하고, 다른 대륙 이름인 America, Europe,Africa 세 번 실행해야 합니다.
스크립트는 함수의 모든 인스턴스가 종료되기 전에 실행이 완료

프로그래밍 요구사항
파이썬의 다중 처리 모듈을 사용하세요.
주어진 대륙 이름을 출력하는 함수를 정의하세요.
여러 프로세스를 생성하여 이 함수를 호출합니다.
모든 프로세스가 제대로 시작되고 완료되었는지 확인하세요.
'''
import multiprocessing 

# "Asia"를 default 값으로 사용
def print_log(data="Asia"):

    print(f"The name of continent is : {data}")

if __name__ == "__main__":
    #Process를 활용하여 멀티 프로세스 생성
    p1 = multiprocessing.Process(target=print_log)
    p2 = multiprocessing.Process(target=print_log,args=("America",))
    p3 = multiprocessing.Process(target=print_log,args=("Europe",))
    p4 = multiprocessing.Process(target=print_log,args=("Africa",))

    processes = [p1,p2,p3,p4]

    for process in processes:
        process.start()

    for process in processes:
        process.join()


