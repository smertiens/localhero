import time, sys
print("Starting process")
while True:
    try:
        print('.')
        
        time.sleep(1)
    except KeyboardInterrupt:
        break

print('End process')