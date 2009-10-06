'''
Created on Apr 30, 2009

@author: Nathan
'''

import Image

Vmax = 64
Umax = 64
Ymax = 16


# The function adds less to a given color point if 
# This is an attempt to reduce the effect of a large area so it won't
# overwhelm small areas that you want to be separate colors.
# Also attempts to fill in gaps by adding a lesser effect to all
# surrounding color space


def generate_color_space(colors, imgdir):
    '''
        Generates the .tm file.
        The file has a few lines of header followed by a 16*64*64 data block.
        Each position of [Y][U][V] has a byte representing which color that 
        point falls under.
        
        This function generates that file.
        
        Each pixel of a color adds a weighted amount to that YUV position
        and the surrounding ones. After all the colors have their say,
        the one with the highest amount on a particular YUV point is the
        winner ( or undefined if no color claims that spot )
        
        colors comes in as:
            [ [ { picture_index_int : Area } , average_color_tuple , colorname], (repeat that for all colors) ]
        with Area being the list of list of adjacent points in a picture.
    '''
    colfile = open("easiertrain.col", 'w')
    
    colfile.write("0 (128 128 128) \"unclassified\" 8 1.00")
    colfile.write(chr(10))
    
    colornum = 1
    
    for color in colors:
        colfile.write(str(colornum))
        colfile.write(" (")
        colfile.write(str(color[1][0]))
        colfile.write(" ")
        colfile.write(str(color[1][1]))
        colfile.write(" ")
        colfile.write(str(color[1][2]))
        colfile.write(") ")
        colfile.write(" \"")
        colfile.write(color[2])
        colfile.write("\" 8 0.75")
        colfile.write(chr(10))
        
        colornum += 1
    
    
    
    # Make the list of colors for each YUV point
    
    colorspace = [ [ [[0 for w in xrange(0,len(colors)+1)] \
                         for x in xrange(0,Vmax)]          \
                         for y in xrange(0,Umax)]          \
                         for z in xrange(0,Ymax)]
    
    tmfile = open("easiertrain.tm", 'w')
    
    #Header information for the tm file.
    tmfile.write("TMAP")
    tmfile.write(chr(10))
    tmfile.write("YUV8")
    tmfile.write(chr(10))
    tmfile.write(str(Ymax)+" "+str(Umax)+" "+str(Vmax))
    tmfile.write(chr(10))
    
    colorindex = 0
    
    for color in colors:
        colorindex += 1
        totalarea = 0
        for picture in color[0]:
            for area in color[0][picture]:
                totalarea += len(area)
                
        for picture in color[0]:
            img = Image.open( imgdir[picture] ).convert("YCbCr")
            
            pixels = list( img.getdata() )
            width, height = img.size
            for area in color[0][picture]:
                for(x,y) in area:
                    
                    #Python Image Library actually has it in YCrCb order. 
                    
                    colorspace \
                    [pixels[x + y * width][0]>>4] \
                    [pixels[x + y * width][2]>>2] \
                    [pixels[x + y * width][1]>>2] \
                    [colorindex] += 1000/totalarea
                    
                        
                    #for Y in xrange(-1,2):
                    #    for U in xrange(-3,4):
                    #        for V in xrange(-3,4):
                    #            try:
                                    
                    #                colorspace                        \
                    #                [(pixels[x + y * width][0]>>4)+Y] \
                    #                [(pixels[x + y * width][1]>>2)+U] \
                    #                [(pixels[x + y * width][2]>>2)+V] \
                    #                [colorindex] += 1/totalarea
                                    
                    #            except IndexError:
                    #                pass
                                        
                                    
        
    for Y in xrange(0,Ymax):
        for U in xrange(0,Umax):
            for V in xrange(0,Vmax):

                    
#For each point in YUV space, pick the best candidate print it as a char
                tmfile.write(\
                             chr(\
                             str(list_int_max(colorspace[Y][U][V])\
                             )\
                             ) )

def list_int_max(list):
    '''
        finds the position on a list with the highest value 
    '''
    
    maxentry = 0
    for i in xrange(0, len(list)):
        if list[i] > list[maxentry]:
            maxentry = i
    
    return maxentry