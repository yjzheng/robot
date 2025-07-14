begin = int(input('Begin from angle:'))
end = int(input('End angle:'))
for index in range(5):
    print(int((end-begin) * index / 5) + begin)