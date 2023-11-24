import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import floor
from math import ceil
from PIL import Image

#Reads in CSV. CSV should have a header row. Crap at the top may need to be deleted.
df = pd.read_csv('saticon.csv', sep=',')

#truncates data to single full frame. Do this manually.
result    = df.loc[950000:5000000] 

#Normalizes amplitudes to the range of [0,255]
result    = (result - result.min()) / (result.max() - result.min())*255

#Adds column for the detected start of a new line.
result["line"] = 0

#Manually sets X resolution and automatically detects y resolution.
oversampling=2
x_dim=640*oversampling
y_dim=0

triggered = 0 #State variable
line_width= 0 
line_widths=[] #Array of measured line widths.
for ind in result.index:
    #Sets triggered state variable when sync goes high and stays there until it goes low.
    if(result['sync'][ind]>127):
        triggered = 1
        if(line_width>0): #Ignores starting condition with zero length
            line_widths.append(line_width)
        line_width=0
    #Detects the start of a new line and records the position.
    elif(result['sync'][ind]<=127):
        if(triggered):
            triggered=0
            result.at[ind, 'line'] = 255
            y_dim=y_dim+1
        line_width=line_width+1

#Median line width used to determine on what interval to sample the image.
line_width = np.median(line_widths)
pixel_spacing = floor(line_width/x_dim)
x_dim=ceil(line_width/pixel_spacing)+1

print("Height = ", y_dim, " pixels")
print("Width set to ", x_dim, " pixels")
print("Samples per x Pixel = ",pixel_spacing)

# Create a new black image of the approprate size.
img = Image.new( 'RGB', (x_dim,y_dim+1), "black") 
pixels = img.load() # Create the pixel map

#Same loop as before, but now it populates the image based on previously determined sampling interval.
triggered= 0
yposition=0
xposition = 0
for ind in result.index:
    if(result['sync'][ind]>127):
        triggered = 1
    elif(result['sync'][ind]<=127):
        if(triggered):
            triggered = 0
            xposition  = 0
            result.at[ind, 'line'] = 255
            yposition=yposition+1
        if(xposition%pixel_spacing==0 and int(xposition/pixel_spacing)<x_dim-1):
            #print(x_dim-2,",",int(xposition/pixel_spacing),",",y_dim,",",yposition)
            pixels[int(xposition/pixel_spacing),yposition] = (int(result['amplitude'][ind]), int(result['amplitude'][ind]), int(result['amplitude'][ind]))
        xposition=xposition+1
print(result)

#Resizes image to compensate for interlacing.
img = img.resize((x_dim,y_dim*2*oversampling))
img.show()

#Saves image
img.save(r'saticon.png')

#Plots raw data
plt.plot(result['time'],result['amplitude'], label="Brightness Signal")
plt.plot(result['time'], result['sync'], label="Sync Signal")
plt.plot(result['time'], result['line'], label="Start of Line")
plt.xlabel("Time")
plt.ylabel("Normalized Amplitude")
plt.title("Saticon Waveforms")
plt.legend()
plt.show()