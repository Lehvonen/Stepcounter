import numpy as np
import matplotlib.pyplot as plt

#Simple function to visualize 4 arrays that are given to it
def visualize_data(timestamps, x_arr,y_arr,z_arr,s_arr):
  #Plotting accelerometer readings
  plt.figure(1)
  plt.plot(timestamps, x_arr, color = "blue",linewidth=1.0)
  plt.plot(timestamps, y_arr, color = "red",linewidth=1.0)
  plt.plot(timestamps, z_arr, color = "green",linewidth=1.0)
  plt.show()
  #magnitude array calculation
  m_arr = []
  for i, x in enumerate(x_arr):
    m_arr.append(magnitude(x_arr[i],y_arr[i],z_arr[i]))
  plt.figure(2)
  #plotting magnitude and steps
  plt.plot(timestamps, s_arr, color = "black",linewidth=1.0)
  plt.plot(timestamps, m_arr, color = "red",linewidth=1.0)
  plt.show()

#Function to read the data from the log file

def read_data(filename):

  with open(filename) as f:
    rowCount = sum(1 for row in f)

  timestamps = [0] * rowCount
  x_array = [0] * rowCount
  y_array = [0] * rowCount
  z_array = [0] * rowCount

  with open(filename) as f:
    lines = f.readlines()

  for i in range(rowCount):
    values = lines[i].strip().split(",")
    timestamps[i] = 1 + i
    x_array[i] = float(values[1])
    y_array[i] = float(values[2])
    z_array[i] = float(values[3])

  return timestamps, x_array, y_array, z_array

#Function to count steps.
#Should return an array of timestamps from when steps were detected
#Each value in this arrray should represent the time that step was made.
#Basic algorithm (part 2): static threshold
def count_steps(timestamps, x_arr, y_arr, z_arr):
  rv = []
  threshold = 11
  above = False
  for i, time in enumerate(timestamps):
    m = magnitude(x_arr[i], y_arr[i], z_arr[i])
    if(m > threshold and not above):
      rv.append(time)
      above = True
    elif(m < threshold):
      above = False
  return rv

#Enhanced algorithm (part 3): dynamic threshold + time window
def count_steps_enhanced(timestamps, x_arr, y_arr, z_arr):
  rv = []
  sample_rate = 10      #Hz, MATLAB Mobile sampling rate
  block_size = 20       #samples used to calculate each threshold (2 s)
  min_step_time = 0.2   #seconds, steps closer than this are vibrations
  min_range = 1.0       #if the signal varies less than this, nobody is walking
  min_gap = int(min_step_time * sample_rate)

  #Smoothed magnitude: average of current and previous sample
  m_arr = []
  prev_m = magnitude(x_arr[0], y_arr[0], z_arr[0])
  for i in range(len(timestamps)):
    m = magnitude(x_arr[i], y_arr[i], z_arr[i])
    m_arr.append((m + prev_m) / 2)
    prev_m = m

  #First threshold is calculated from the first block itself
  block = m_arr[0:block_size]
  threshold = (max(block) + min(block)) / 2
  active = (max(block) - min(block)) > min_range

  above = False
  last_step = -min_gap
  for i, time in enumerate(timestamps):
    #Dynamic threshold: recalculate from the previous block, only the previous block affects the "new" block
    if(i > 0 and i % block_size == 0):
      block = m_arr[i-block_size:i]
      threshold = (max(block) + min(block)) / 2
      active = (max(block) - min(block)) > min_range
    if(m_arr[i] > threshold and not above):
      above = True
      #Time window: only count if enough time has passed since the last step so that random vibrations / noise doesnt muddy the results
      if(active and i - last_step >= min_gap):
        rv.append(time)
        last_step = i
    elif(m_arr[i] < threshold):
      above = False
  return rv


#Calculate the magnitude of the given vector
def magnitude(x,y,z):
  return np.linalg.norm((x,y,z))

#Function to convert array of times where steps happened into array to give into graph visualization
#Takes timestamp-array and array of times that step was detected as an input
#Returns an array where each entry is either zero if corresponding timestamp has no step detected or 50000 if the step was detected
def generate_step_array(timestamps, step_time):
  s_arr = []
  ctr = 0
  for i, time in enumerate(timestamps):
    if(ctr<len(step_time) and step_time[ctr]<=time):
      ctr += 1
      s_arr.append( 3 )
    else:
      s_arr.append( 0 )
  while(len(s_arr)<len(timestamps)):
    s_arr.append(0)
  return s_arr

#Check that the sizes of arrays match
def check_data(t,x,y,z):
  if( len(t)!=len(x) or len(y)!=len(z) or len(x)!=len(y) ):
    print("Arrays of incorrect length")
    return False
  print("The amount of data read from accelerometer is "+str(len(t))+" entries")
  return True

def main():
  #read data from a measurement file, change the inoput file name if needed
  timestamps, x_array, y_array, z_array = read_data("11_walk_noTurn.csv")
  #Chek that the data does not produce errors
  if(not check_data(timestamps, x_array,y_array,z_array)):
    return
  #Count the steps based on array of measurements from accelerometer
  st = count_steps(timestamps, x_array, y_array, z_array)
  st2 = count_steps_enhanced(timestamps, x_array, y_array, z_array)
  #Print the result
  print("This data contains "+str(len(st))+" steps according to basic algorithm")
  print("Enhanced algorithm: "+str(len(st2))+" steps")
  #convert array of step times into graph-compatible format
  s_array = generate_step_array(timestamps, st)
  #visualize data and steps
  visualize_data(timestamps, x_array,y_array,z_array,s_array)

main()

