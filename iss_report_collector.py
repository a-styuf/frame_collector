import re
import os
import time

# настройки программы :todo вынеcти настройки в текстовый интерфейс
start_frame_time = "2015 12 06"  # время запуска - необходимо для сортировки кадров с синхронизацией и без
additional_frame_process = True
old_frame_process = True

time_start = time.perf_counter()
# паттерн для поиска стандартных кадров ОАИ НГУ
frame_pattern = re.compile(r"[0-9-]{2,3}0F[0F][F1][ 0-9-]{0,3}0[A-F][0-9A-F]{1,2}(?:[ 0-9]{1,3}-[0-9A-F]{4}){30}")
# паттерн для дополнительных кадров
additional_data_pattern = re.compile(r"0F[0F][F1] 0C[0-1]0 [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4}")  # ЗУ БДД

try:
    os.mkdir("Data")
except OSError as error:
    print(error)


def list_files_in_dir_and_subdir(work_path):
    file_list = []
    all_list = os.listdir(work_path)
    all_list = [os.path.normpath(os.path.join(work_path, var)) for var in all_list]
    tmp_list = []
    while all_list:
        for path in all_list:
            if os.path.isfile(path):
                file_list.append(os.path.normpath(path))
                # print(len(file_list))
                pass
            else:
                subdir_list = os.listdir(path)
                subdir_list = [os.path.normpath(os.path.join(path, var)) for var in subdir_list]
                tmp_list.extend(subdir_list)
                pass
        all_list = tmp_list
        tmp_list = []
    return file_list


list_dir_and_file = list_files_in_dir_and_subdir("Data")
print("Найдено файлов: ", list_dir_and_file)



new_file_frames = []
old_file_frames = []
bdd_file_frames = []


def calc_frame_time(frame, bound_time=""):
    time_pattern = re.compile(r"0F[0F][F1] 0C[0-1][0-9A-F] [0-9A-F]{4} ([0-9A-F]{4} [0-9A-F]{4})")
    bound_time_s = time.mktime(time.strptime(bound_time, "%Y %m %d")) - time.mktime(time.strptime("2000 01 01 00:00:00", "%Y %m %d %H:%M:%S"))

    time_list = time_pattern.findall(frame)
    time_frame_s = 0
    if time_list:
        time_str = time_list[0]
        time_frame_s = (int(time_str.split(" ")[0], 16) << 16) + int(time_str.split(" ")[1], 16)
        #print(bound_time_s, time_frame_s)
    if time_frame_s >= bound_time_s:
        return 1
    else:
        return 0


def additional_data_find(frame):
    result = additional_data_pattern.search(frame)
    # print(result)
    if additional_data_pattern.search(frame):
        return 1
    else:
        return 0


file_num = 0


for num, file_path in enumerate(list_dir_and_file):
    if ".txt" in file_path:  # os.path.isfile(file_path):
        print("Обработка файла: ", file_path)

        file = open(file_path, "r")
        file_lines_str = "".join(file.readlines())
        print("Всего строк в файле:", len(file_lines_str.split("\n")))

        frames_result = frame_pattern.findall(file_lines_str)
        print(num, file_path, len(frames_result))
        if frames_result:
            new_file_frames.append('\n' + file_path + '\n')
            new_file_frames.extend(frames_result)
        file_num += 1
    else:
        # print("Обработка файла: ", file_path)
        # print("Файл - не файл!", "\n")
        pass

# проверка на уникальность кадров
print("Количество кадров: %d" % len(new_file_frames))
new_list = []
copy = 0
number_of_repeated_frames = 0
percentage = 0
for num, frame in enumerate(new_file_frames):
    copy = 1
    for var in new_file_frames[num+1:]:
        if var == frame:
            copy = 0
            number_of_repeated_frames += 1
            if (100 * num / len(new_file_frames) - percentage) >= 10:
                percentage = 100 * num / len(new_file_frames)
                print("Number of repeat: %d" % number_of_repeated_frames, " Total progress: %d%%" % (100*num/len(new_file_frames)))
            break
    if copy:
        new_list.append(frame)
new_file_frames = new_list
print("Количество повторя кадров: %d" % number_of_repeated_frames)

# сортировка кадров по типам: актуальные, старые, из архива БДД
new_list = []
old_list = []
bdd_list = []
number_of_normal_frames = 0
number_of_old_frames = 0
number_of_bdd_frames = 0
for frame in new_file_frames:
    if additional_data_find(frame) and additional_frame_process:
        bdd_list.append(frame)
        number_of_bdd_frames += 1
    elif calc_frame_time(frame, bound_time=start_frame_time) == 0 and old_frame_process:
        old_list.append(frame)
        number_of_old_frames += 1
    else:
        new_list.append(frame)
        number_of_normal_frames += 1
print("\nКоличество обработанных файлов: %d" % file_num)

new_file_frames = new_list

print("Количество нормальных кадров: %d" % number_of_normal_frames)
new_file_str = "\n".join(new_file_frames)

os.chdir("Data")
with open("normal_data.txt", "w") as new_file:
    new_file.write(new_file_str)

if old_frame_process:
    print("Количество старых кадров: %d" % number_of_old_frames)
    old_file_str = "\n".join(old_list)
    with open("old_data.txt", "w") as new_file:
        new_file.write(old_file_str)

if additional_frame_process:
    print("Количество дополнительных кадров: %d" % number_of_bdd_frames)
    bdd_file_str = "\n".join(bdd_list)
    with open("additional_data.txt", "w") as new_file:
        new_file.write(bdd_file_str)

print("Конец. Выполненно за %.3f" % (time.perf_counter() - time_start))
input('Нажмите Enter для выхода\n')

