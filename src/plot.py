import pandas as pd
import matplotlib.pyplot as plt
import os

# Пути к файлам (проверь, что они существуют в папке outputs_csv)
# Мы используем файлы сценария Uneven_Win
file_std = "outputs_csv/Uneven_Win_STD_tripinfo.csv"
file_rl = "outputs_csv/Uneven_Win_RL_tripinfo.csv"

if not os.path.exists(file_std) or not os.path.exists(file_rl):
    print("Ошибка: Сначала запусти compare_final_v8.py, чтобы создать CSV файлы!")
    exit()

# Читаем данные (разделитель точка с запятой)
df_std = pd.read_csv(file_std, sep=';')
df_rl = pd.read_csv(file_rl, sep=';')

plt.figure(figsize=(12, 6))

# Строим гистограммы времени ожидания
plt.hist(df_std['waitingTime'], bins=50, alpha=0.6, label='Standard', color='red', edgecolor='black')
plt.hist(df_rl['waitingTime'], bins=50, alpha=0.6, label='AI (RL)', color='green', edgecolor='black')

plt.xlabel('Время ожидания (секунды)')
plt.ylabel('Количество машин')
plt.title('Гистограмма времени ожидания: Кто ждал дольше?')
plt.legend()
plt.grid(True, alpha=0.3)

plt.savefig('waiting_time_histogram.png', dpi=300)
print("Гистограмма сохранена как waiting_time_histogram.png")
plt.show()