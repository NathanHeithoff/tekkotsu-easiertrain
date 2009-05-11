#!/usr/bin/env python
'''
    Uses hashes of tuples to simulate 2-d arrays for the masks.   

    Prewitt algorithms adapted for color edge detection by Nathan Heithoff
    for Introduction to Cognitive Robotics @ Rensselaer Polytechnic Institute
    
    Original algorithm (c) David Reynolds
    http://alwaysmovefast.com/2007/12/05/basic-edge-detection-in-python/
'''

import Image
import sys

def get_prewitt_masks():
    xmask = {}
    ymask = {}
  
    xmask[(0,0)] = -1
    xmask[(0,1)] = 0
    xmask[(0,2)] = 1
    xmask[(1,0)] = -1
    xmask[(1,1)] = 0
    xmask[(1,2)] = 1
    xmask[(2,0)] = -1
    xmask[(2,1)] = 0
    xmask[(2,2)] = 1
  
    ymask[(0,0)] = 1
    ymask[(0,1)] = 1
    ymask[(0,2)] = 1
    ymask[(1,0)] = 0
    ymask[(1,1)] = 0
    ymask[(1,2)] = 0
    ymask[(2,0)] = -1
    ymask[(2,1)] = -1
    ymask[(2,2)] = -1
    return (xmask, ymask)
  
   
  
def prewitt(pixels, width, height, threshold):
    '''
        This function creates the edges.
        Pixels are the original image pixels.
        Width and height are those stats for the image.
        Theshold is what determines how much color change creates an edge.
            Lower threshold means more edges will be detected.
    '''

    xmask, ymask = get_prewitt_masks()
  
    # create a new greyscale image for the output
    outimg = Image.new('RGB', (width, height))
    outpixels = list(outimg.getdata())
  
    for y in xrange(height):
        for x in xrange(width):
            sumX, sumY, magnitude = 0, 0, 0

            if y == 0 or y == height-1: magnitude = 10000 #magic number
            elif x == 0 or x == width-1: magnitude = 10000 #magic number
            else:
                for k in xrange(0, 3):
                    for i in xrange(-1, 2):
                        for j in xrange(-1, 2):
                            # convolve the image pixels with the Prewitt mask
                            sumX += (pixels[x+i+(y+j)*width][k])\
                                    * xmask[i+1, j+1]

                            sumY += (pixels[x+i+(y+j)*width][k])\
                                    * ymask[i+1, j+1]
  
                    # approximate the magnitude of the gradient
                    magnitude += abs(sumX) + abs(sumY)
                    if magnitude > 0:
                        magnitude = magnitude
  
            if magnitude >= threshold: magnitude = 255
            elif magnitude < threshold: magnitude = 0
  
            outpixels[x+y*width] = 255 - magnitude,\
                                   255 - magnitude,\
                                   255 - magnitude

    outimg.putdata(outpixels)
    return outimg 


def getarea(pixels,width, height, xco, yco):
    '''
        Takes the image of the edges, its width and height,
            and the coordinates of the mouseclick.
                
        It returns the area enclosed by the edges.
    '''
    if pixels[xco + yco * width] != (255, 255, 255):
        return ();
    
    area        = [(xco,yco)]
    alreadyseen = {(xco,yco):pixels[xco + yco * width] }
    
    print pixels[xco + yco * width]
    
    for (xco,yco) in area:
        
        for i in xrange(-1,2):
            for j in xrange(-1,2):
                if pixels[xco+i + (yco+j) * width] == (255,255,255):
                    if (xco+i,yco+j) not in alreadyseen:
                        alreadyseen[(xco+i,yco+j)]=pixels[xco+i +\
                                                          (yco+j) *\
                                                          width]
                        area.append((xco+i,yco+j))

    return alreadyseen.keys()

def highlight(pixels, width, height, area, color):
    '''
        Pixels are from the edge image.
        The area is the list of lists containing the points that are going to be
            highlighted.
    '''
    outpixels = pixels
    
    for i in area:
        for (x,y) in i:
            outpixels[x + y * width] = color
        
    outimg = Image.new('RGB', (width, height))
    outimg.putdata(outpixels)
    return outimg

def average_color(pixels, width, height, area):
    '''
        Calculates the average color in an area of pixels.
        This is called before the highlight function.
    '''
    r,g,b = 0, 0, 0
    size = 0
    for i in area:
        for(x,y) in i:
            r += pixels[x + y * width][0]
            g += pixels[x + y * width][1]
            b += pixels[x + y * width][2]
        size += len(i)

    if size == 0:
        return

    r = r / size
    g = g / size
    b = b / size

    return (r,g,b)
