import time

start_frame_time = "2040 1 1"  # время запуска - необходимо для сортировки кадров с синхронизацией и без

time_s = time.mktime(time.strptime(start_frame_time, "%Y %m %d")) - time.mktime(time.strptime("2000 01 01 00:00:00", "%Y %m %d %H:%M:%S"))

print("%d" % time_s)

for a_p in range(1, 128):
    for s_p in range(1, 2**15):
        if a_p*s_p == 1000000:
            print(a_p, s_p)
        else:
            pass