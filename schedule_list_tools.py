import os
import json
import time
import datetime



pwd = os.getcwd()
target_file = f"{pwd}/schedule_list.txt"

def Time_Check(time):
    now = datetime.datetime.now()
    if int(time[:4]) != now.year :
        return False
    elif int(time[4:6]) != now.month :
        return False
    elif int(time[6:8]) != now.day :
        return False
    else :
        if (now.hour - int(time[8:10])) == 1 :
            print('1')
            # interval is less than 1 miunte
            if abs(now.minute - int(time[10:12])) <= 1 :
                return True
            else :
                return False
        elif (int(time[8:10]) - now.hour) == 0 :
            if (int(time[10:12]) - now.minute) == 0 :
                return True 
            elif (int(time[10:12]) - now.minute) <= 1 :
                return True 
            else :
                return False
        else :
            return False
    
def Write_task(task:str):
    with open(target_file, 'a') as f:
        f.write(task)
        f.write('\n')

def Cleanup_tasks():
    now = datetime.datetime.now()
    tasks = []
    with open(target_file, mode='r') as f:
        tasks = f.readlines()
    if len(tasks) == 0 :
        return
    with open(target_file, mode='w') as f:
        for number, line in enumerate(tasks):
            task = json.loads(line[:-1])['Time']
            task_year = int(task[:4])
            task_month = int(task[4:6])
            task_day = int(task[6:8])
            task_hour = int(task[8:10])
            task_minute = int(task[10:12])
            if task_year > now.year :
                f.write(line)
            elif task_year == now.year :
                if task_month > now.month :
                    f.write(line)
                elif task_month == now.month :
                    if task_day > now.day :
                        f.write(line)
                    elif task_day == now.day :
                        if task_hour > now.hour :
                            f.write(line)
                        elif task_hour == now.hour :
                            if task_minute >= now.minute :
                                f.write(line)
                            else :
                                continue
                        else :
                            continue
                    else :
                        continue
                else :
                    continue
            else :
                continue

def Change_Index(tasks, min, number):
    temp = tasks[min]
    tasks[min] = tasks[number]
    tasks[number] = temp

def Sort_tasks():
    tasks = []
    with open(target_file, mode='r') as f:
        tasks = f.readlines()
    for index in range(len(tasks)-1):
        for next_index in range(index + 1, len(tasks)) :
            #if json.loads(tasks[next])['Time'] < json.loads(tasks[number])['Time'].split(' ')[0] :
            now = json.loads(tasks[index])['Time']
            next = json.loads(tasks[next_index])['Time']
            if int(next) < int(now) :
                Change_Index(tasks, index, next_index)
    with open(target_file, mode='w') as f:
        for task in tasks :
            f.write(task)
    
def Get_First_task():
    tasks = []
    with open(target_file, mode='r') as f:
        tasks = f.readlines()
    if len(tasks) == 0 :
        return
    task_time = json.loads(tasks[0][:-1])['Time']
    good_to_Execute = Time_Check(task_time)
    if good_to_Execute :
        return tasks[0]
    else :
        return 
                
def Delete_First_task():
    with open(target_file, mode='r') as f:
        tasks = f.readlines()
    with open(target_file, mode='w') as f:
        for line in range(1, len(tasks)) :
            f.write(tasks[line])

if __name__ == "__main__" :
    x = Get_First_task()
    #print(x)