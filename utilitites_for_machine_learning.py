import os

# generate negative description file
def generate_negative_description_file():
    with open('neg.txt', 'w') as f:
        for filename in os.listdir('machinelearning/negative'):
            f.write('negative/' + filename + '\n')

generate_negative_description_file()

# open cv version 3.4.12 needed for this. Use the programs to train cascade.
# note: change working directory to this directory in cmd

# generate positive description file using:
# C:\Users\klaud\Downloads\opencv3412\opencv\build\x64\vc15\bin\opencv_annotation.exe --annotations=pos.txt --images=machinelearning/positive/

# generate positive samples from the annotations to get a vector file using:
# C:\Users\klaud\Downloads\opencv3412\opencv\build\x64\vc15\bin\opencv_createsamples.exe -info pos.txt -w 48 -h 48 -num 1000 -vec pos.vec

# classifier training arguments:
# C:\Users\klaud\Downloads\opencv3412\opencv\build\x64\vc15\bin\opencv_traincascade.exe -data machinelearning/ -vec pos.vec -bg neg.txt -precalcValBufSize 6000 -precalcIdxBufSize 6000 -numPos 360 -numNeg 180 -numStages 50 -w 24 -h 24 -maxFalseAlarmRate 0.25 -minHitRate 0.999