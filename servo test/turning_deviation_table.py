import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--deviation_file', '-d', type=str, default="<no data>", required=True, help='The deviation file to turning.')
parser.add_argument('--turning_value', '-v', type=int, default="<no data>", required=True, help='The value for turning.')

args = parser.parse_args()

filename = args.deviation_file
try:
    f = open(filename, "r")
    data = f.read()
    f.close()
    #print(data)
    array = data.split(',')
    print("length=", len(array))
    if len(array) == 36+1:  #180/5 + 1, count by every 5 degree
        print("before:",array)
        array = [ int(array[i]) + args.turning_value for i in range(len(array))]  
        print("after:",array)
        os.rename( filename, filename+".backup")
        f = open(filename, "w")
        for i in range(len(array)):
            f.write(str(array[i]))
            if (i % 2) == 0:
                if( i != len(array) - 1): 
                    f.write(",")
            else: 
                f.write(",\n")
        f.close()
except:
    print( "Open file", args.deviation_file, "error.")

print("value", args.turning_value)
