import threading,time,random
def client_model():
    print("Go into the client thread!")
    while True:
        Wtime = random.randint(0, 4)
        # print("Wait time:%d" % Wtime)
        time.sleep(Wtime)
    return