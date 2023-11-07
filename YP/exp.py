import time
start = time.time()
time.sleep(3)
end = time.time()
execution_time_seconds = end - start
print(execution_time_seconds)

with open("YP/Total Time.csv", 'w') as file:
    # Write each result to the file
    file.write(str(execution_time_seconds))