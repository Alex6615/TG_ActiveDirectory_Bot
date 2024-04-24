def timeisformatted(time:str) -> bool:
    time_digits = [str(i) for i in range(0,10)]
    time_length = [4, 6, 8, 12]
    if len(time) not in time_length :
        return False
    for num in range(0, len(time)) :
        if time[num] not in time_digits :
            return False
        else :
            return True
    

if __name__ == "__main__" :
    x = timeisformatted('0291200')
    print(x)
