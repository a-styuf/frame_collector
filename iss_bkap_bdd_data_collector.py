import re
import os
import time

# настройки программы :todo вынеcти настройки в текстовый интерфейс
start_frame_time = "2018 12 06"  # время запуска - необходимо для сортировки кадров с синхронизацией и без
additional_frame_process = True
old_frame_process = True

time_start = time.perf_counter()
# паттерн для поиска стандартных кадров ОАИ НГУ
frame_pattern = re.compile(r"0F[0F][F1] 0C[0-1][0-9A-F] [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} "
                           r"[0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} "
                           r"[0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} "
                           r"[0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} "
                           r"[0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4}")
# паттерн для дополнительных кадров
additional_data_pattern = re.compile(r"0F[0F][F1] 0C[0-1]0 [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4}")  # ЗУ БДД
# бдд дата паттерн
bdd_data_pattern = re.compile(r"(0F[0F][F1] 0C11 [0-9A-F]{4} [0-9A-F]{4} [0-9A-F]{4}) ([0-9A-F]{4} ){25}([0-9A-F]{4}) [0-9A-F]{4}")

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


def collect_bdd_frame(frame):
    row_data = bdd_data_pattern.findall(frame)
    bdd_data = ""
    if row_data:
        bdd_data = row_data[0][0] + " " + row_data[0][2] + "\n"
    return bdd_data


file_num = 0


for num, file_path in enumerate(list_dir_and_file):
    if ".txt" in file_path:  # os.path.isfile(file_path):
        print("Обработка файла: ", file_path)

        file = open(file_path, "r")
        file_lines_str = "".join(file.readlines())
        print("Всего строк в файле:", len(file_lines_str.split("\n")))

        frames_result = frame_pattern.findall(file_lines_str)
        # print(num, file_path, len(frames_result))
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
bdd_list = []
for frame in new_file_frames:
    bdd_list.append(collect_bdd_frame(frame))
print("\nКоличество обработанных файлов: %d" % file_num)

os.chdir("Data")

with open("bdd_data.txt", "w") as new_file:
    new_file.write("".join(bdd_list))

print("Конец. Выполненно за %.3f" % (time.perf_counter() - time_start))
input('Нажмите Enter для выхода\n')

