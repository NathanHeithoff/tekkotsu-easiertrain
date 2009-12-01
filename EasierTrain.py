#!/usr/bin/env python
'''
    EasierTrain
    Generates color segmentation files (.col, .tm)
    for the Tekkotsu color segmentation system
    
    The idea that started EasierTrain is that the current Tekkotsu
    color selection tool, EasyTrain, is anything but. EasyTrain requires
    the user to make difficult 3D color selections in order to get any sort of
    useful colors. Getting more than a few colors working at once is very
    frustrating and probably limits the kinds of vision problems that people
    attempt to solve in Tekkotsu.
    
    EasierTrain abstracts away from the difficult color selection of EasyTrain
    by running an edge detection algorithm on the source images, simply allowing
    the user to click on the interesting region(s) of color across multiple
    pictures and add them to a color palette.
    For a how-to, see the acompanying README.

    We have (hopefully) documented EasierTrain well enough that other
    Tekkotsu users can continue its development and ultimately
    create a tool that is parity to or completely replaces EasyTrain.

    v1.0 developed with Python 2.6.2 on Windows XP
    by Michael Gram (michael dot i dot gram at gmail dot com)
    and Nathan Heithoff (nathanheithoff at gmail dot com)
    This program started as a final project for Introduction to Cognitive
    Robotics @ Rensselaer Polytechnic Institute, Spring 2009.
    Special thanks to:
        Bram van Heuveln for being a great professor, advisor, director of
        the Minds & Machines program, and pioneering cognitive robotics at RPI!
        And to Dave Touretzky for championing the Tekkotsu platform and helping
        cognitive robotics get off the ground.
'''
import sys
import edge
import Image # PIL
import os
import Tkinter as tk
import ImageTk
import generator
import pickle # serialization

class EasierTrain(tk.Tk):
    '''
        Base class containing the EasierTrain application.
    '''
    def __init__( self, master, imgdir ):
        tk.Tk.__init__( self, master )
        self.master = master

        self.imgpaths = [] # Paths to images in the folder

        # Color palette widgets
        self.colorNameInputs = [] # name entries
        self.colorFrames = [] # average color of the selection
        self.colorChkbtn = [] # checkbox for bulk operation i.e. delete

        self.thresholds = dict() # stores previous threshold associated with image

        self.img = None # stores the current image
        self.w, self.h = None, None # width and height of the current image
        self.edge_img = None # edge detection output
        self.pic = None # printed to self.canvas
        self.edge_pic = None # printed to self.canvas

        self.img_index = 0 # stores the place of the current image in imgpaths
        self.img_path = '' # stores the path of the current image
        self.highlight_area = dict() # stores the active area selection
        self.master_color_list = [] # stores all the data for added colors

        self.highlight_img = None # image data for current selection
        self.highlight_pic = None # printed to self.canvas
        self.canvas = None

        #Populates self.imgpaths with full paths to images in the directory
        for item in os.listdir(imgdir):
            relpath = os.path.join(imgdir,item)

            #Omit directories
            if os.path.isdir( relpath ):
                print "Omitting directory", relpath
                continue

            #Weed out files that are not compatible with PIL
            try:
                tmpImg = Image.open( relpath )
            except(IOError):
                print "Not a compatible image file", relpath
                continue

            print "Loading file", relpath
            self.imgpaths.append( relpath )
            self.thresholds[relpath] = 250

        if len(self.imgpaths) != 0:
            self.img_path = self.imgpaths[0]

#TODO why was there a separate initialize function?
#        self.initialize()
#
#    def initialize(self):
        '''
            Set up the GUI elements and events.
                Toolbox:
                    Navigation (previous/next picture)
                    Add color to palette
                    Save/load .col/.tm files
                Color palette:
                    List of color selections
                        checkbox (for bulk operation i.e. delete)
                        text entry for name
                        frame with the 'average color' of selection
                    Delete button
                Edge threshold:
                    Scale for quick adjustment of edges
                        (high threshold = fewer edges)
                    Number entry for precision threshold adjustment
                Canvas:
                    Displays current image and prewitt edges
        '''

        self.grid()

        #TODO Prevent Toplevel() windows from being closed?
        #TODO combine toolbox and scalebox?
        #TODO image thumbnails window
        self.toolbox = tk.Toplevel()
        self.toolbox.title( "Toolbox" )

        self.palette = tk.Toplevel()
        self.palette.title( "Color Palette" )

        self.scalebox = tk.Toplevel()
        self.scalebox.title( "Edge Threshold" )

        self.scale = tk.Scale( self.scalebox,\
                               from_=0, to=2500,\
                               sliderlength=10,\
                               length=250 )
        self.scale.set( 250 ) # Scale value referenced in drawImg()

        # Draw the picture to the canvas
        self.drawImg()

        self.scale.grid( column=0, row=0, columnspan=2 )

        # Event for adjusting the scale slider
        self.scale.bind( "<ButtonRelease-1>", self.OnScaleRelease )

        # Text entry and button for manual threshold input
        self.manualThresholdEntry = tk.Entry( self.scalebox, width=4 )
        self.manualThresholdEntry.grid( column=0, row=1 )
        self.manualThresholdButton = tk.Button( self.scalebox,\
                                       text='Set',\
                                       command=self.OnManualThresholdClick )
        self.manualThresholdButton.grid( column=1, row=1 ) 
        
        # Prev/Next picture navigation buttons
        self.prev = tk.Button( self.toolbox, text='Prev',\
                                            command=self.OnPrevClick )
        self.prev.grid( column=1, row=0, padx=2, pady=3 )
        self.next = tk.Button( self.toolbox, text='Next',\
                                            command=self.OnNextClick )
        self.next.grid( column=2, row=0, padx=2, pady=3 )
        
        # Add color to palette button
        self.add = tk.Button( self.toolbox, text='Add',\
                                           command=self.OnAddClick )
        self.add.grid( column=3, row=0, padx=10, sticky='E' )

        #Save and load(TODO) buttons for .col/.tm files
        self.save = tk.Button( self.toolbox, text='Save',\
                                             command=self.OnSaveClick )
        self.save.grid( column=1, row=1, padx=2, pady=3 )
        self.load = tk.Button( self.toolbox, text='Load',\
                                             command=self.OnLoadClick )
        self.load.grid( column=2, row=1, padx=2, pady=3 )

        # Delete button for color palette
        self.deleteBtn = tk.Button( self.palette, text='Delete',\
                                               command=self.OnDeleteClick )
        self.deleteBtn.grid( column=0, row=0 )

    def drawImg(self):
        '''
            Draws the current image to the screen.
        '''
        
        self.img = Image.open( self.img_path )
        self.pixels = list( self.img.getdata() )
        self.w, self.h = self.img.size
        self.edge_img = edge.prewitt( self.pixels,\
                                      self.w, self.h,\
                                      self.scale.get() )

        # Just make a new canvas each time the current image is changed
        if self.canvas != None:
            self.canvas.grid_remove()
        self.canvas = tk.Canvas( self.master, width=self.w*2, height=self.h )
        self.canvas.grid( column=0, row=0,\
                          columnspan=self.w/10,rowspan=self.h/10, sticky='NW' )

        # Rebind events to the new canvas
        self.canvas.bind( "<Button-1>", self.OnCanvasClick )
        self.canvas.bind( "<Shift-Button-1>", self.OnCanvasShiftClick )
        self.canvas.bind( "<Control-Button-1>", self.OnCanvasControlClick )

        # Draw the picture
        self.pic = ImageTk.PhotoImage(self.img)
        self.canvas.create_image( 0, 0, image=self.pic, anchor='nw' )

        # Draw the edge picture
        self.edge_pic = ImageTk.PhotoImage(self.edge_img)
        self.canvas.create_image( self.w, 0, image=self.edge_pic, anchor='nw' )
        
        self.edge_pixels = list( self.edge_img.getdata() )

    def drawPalette(self):
        '''
            Populates the color palette.
        '''
        for obj in self.colorNameInputs:
            obj.grid_remove()
        for obj in self.colorFrames:
            obj.grid_remove()
        for obj in self.colorChkbtn:
            obj.grid_remove()
        
        j=1
        for i in range( 0, len( self.colorNameInputs ) ):
            if i%10==0:
                j+=1
            self.colorChkbtn[i].grid( column=j*3, row=i%10 )
            self.colorNameInputs[i].grid( column=j*3+1, row=i%10 )
            self.colorFrames[i].grid( column=j*3+2, row=i%10 )

    def OnCanvasClick(self,event):
        '''
            Clears whatever previous area there was and gets this area.
        '''
    
        self.edge_pixels = list( self.edge_img.getdata() )

        # Clear whatever area was already on this picture
        self.highlight_area[self.img_path] = []
        
        
        #Grab the area around the event
        self.highlight_area[self.img_path].append(\
                                edge.getarea(self.edge_pixels, self.w, self.h,\
                                int(self.canvas.canvasx(event.x) % self.w),\
                                int(self.canvas.canvasx(event.y) ) ) )
        
        #Get the color
        color = edge.average_color(self.pixels,\
                                   self.w, self.h,\
                                   self.highlight_area[self.img_path])
        
        #Color in the area
        self.highlight_img = edge.highlight(self.edge_pixels,\
                                            self.w, self.h,\
                                            self.highlight_area[\
                                                self.img_path], color)
        
        self.highlight_pic = ImageTk.PhotoImage(self.highlight_img)

        self.canvas.create_image( self.w, 0,\
                                  image=self.highlight_pic,\
                                  anchor = 'nw' )

    def OnCanvasShiftClick(self,event):
        '''
            Adds any new area to whatever you already have.
            If you click on an already added area, nothing happens.
        '''
        event.widget.find_closest(event.x, event.y)
        
        #Checks if the area is already added. If so, it will be removed from the list
        #n is the position in the list of an area of adjacent pixels
        #i is the actual list of adjacent pixels
        #If the event is within i, then there's no need to add to area
        for i in self.highlight_area[self.img_path]:
                try:
                    dummy = i.index( (self.canvas.canvasx(event.x)%self.w,\
                                    self.canvas.canvasx(event.y)) )
                    return
                except(ValueError,AttributeError):
                    continue
                
        self.edge_pixels = list( self.edge_img.getdata() )
        self.highlight_area[self.img_path].append(\
            edge.getarea( self.edge_pixels, self.w, self.h, \
                          int(self.canvas.canvasx(event.x)%self.w),\
                          int(self.canvas.canvasx(event.y)) ) )
            
        color = edge.average_color( self.pixels,\
                                    self.w, self.h,\
                                    self.highlight_area[self.img_path] )
            
        self.highlight_img = edge.highlight(self.edge_pixels,\
                                            self.w, self.h,\
                                            self.highlight_area[self.img_path], color)
            
        self.highlight_pic = ImageTk.PhotoImage(self.highlight_img)
        self.canvas.create_image( self.w, 0,\
                                  image = self.highlight_pic, anchor = 'nw')
            
    def OnCanvasControlClick(self,event):
        '''
            Adds any new area to whatever you already have.
            If you click on an already added area, it will be removed.
        '''
        event.widget.find_closest(event.x, event.y)
        
        delete = -1
                
        #Checks if the area is already added. If so, it will be removed from the list
        #n is the position in the list of an area of adjacent pixels
        #i is the actual list of adjacent pixels
        #If the event is within i, index will succeed and delete will be the area number
        #Otherwise, index will raise an error and delete won't change.
        for n,i in enumerate(self.highlight_area[self.img_path]):
                try:
                    dummy = i.index( (self.canvas.canvasx(event.x)%self.w,\
                                     self.canvas.canvasx(event.y)) )
                    delete = n
                except(ValueError,AttributeError):
                    continue
        
        self.edge_pixels = list( self.edge_img.getdata() )
        
        if delete != -1:
            self.highlight_area[self.img_path].pop(delete)
            
        else:
            
            self.highlight_area[self.img_path].append(\
                edge.getarea( self.edge_pixels, self.w, self.h,\
                              int(self.canvas.canvasx(event.x)%self.w),\
                              int(self.canvas.canvasx(event.y)) ) )
            
        color = edge.average_color( self.pixels,\
                                    self.w, self.h,\
                                    self.highlight_area[self.img_path] )
            
        self.highlight_img = edge.highlight( self.edge_pixels,\
                                             self.w, self.h,\
                                             self.highlight_area[self.img_path], color )
            
        self.highlight_pic = ImageTk.PhotoImage(self.highlight_img)
        self.canvas.create_image( self.w, 0,\
                                  image = self.highlight_pic, anchor = 'nw' )

    def OnScaleRelease(self, event):
        '''
            Adjusts the threshold based on the value of the scale widget.
            Redraws edge_img and edge_pic, deletes any highlighting
            for the current picture.
        '''
        self.canvas.delete( self.edge_pic )
        self.canvas.delete( self.highlight_pic )
        
        # Redo the edge detection image with the new threshold
        self.edge_img = edge.prewitt( self.pixels,\
                                      self.w, self.h,\
                                      self.scale.get() )
        self.highlight_area[self.img_path] = []

        # draw the new image
        self.edge_pic = ImageTk.PhotoImage(self.edge_img)
        self.canvas.create_image( self.w, 0, image=self.edge_pic, anchor='nw' )

        self.thresholds[self.img_path] = self.scale.get()

    def OnManualThresholdClick(self):
        '''
            Manually adjusts the threshold based on input from
            entry box, if the input is an integer.
        '''
        i = self.manualThresholdEntry.get()
        self.manualThresholdEntry.delete(0,len(i))
        if i != str(int(i)):
            return
        self.scale.set(int(i)) # change the value of the scale
        self.OnScaleRelease(None)

    def PrevNextHandler(self, goToNext=True):
        '''
            Handles request for previous or next image.
            Assumes next image was requested unless otherwise indicated.
            Preserves selection of the previous pictures.
        ''' 
        
        target = 1
        if goToNext==False:
            target = -1 

        # store the current threshold for later reference
        self.thresholds[self.img_path] = self.scale.get()

        # increment to the next image
        self.img_index = (self.img_index+target) % len(self.imgpaths)

        self.img_path = self.imgpaths[self.img_index]

        # restore the threshold of the new image
        self.scale.set( self.thresholds[self.img_path] )
        self.drawImg()
        
        if self.img_index not in self.highlight_area:
            self.highlight_area[self.img_index] = []
        
        else:
            # draw the previous highlighting of the new image, if any
            color = edge.average_color(self.pixels,\
                                   self.w, self.h,\
                                   self.highlight_area[self.img_index])
        
            self.highlight_img = edge.highlight(
                self.edge_pixels, self.w, self.h,\
                self.highlight_area[self.img_path], color )
        
            self.highlight_pic = ImageTk.PhotoImage(self.highlight_img)

            self.canvas.create_image( self.w, 0,\
                                  image=self.highlight_pic,\
                                  anchor = 'nw' )

    def OnNextClick(self):
        '''
            Loads the next picture.
        '''
        self.PrevNextHandler()
        

    def OnPrevClick(self):
        '''
            Loads the previous picture.
        '''
        self.PrevNextHandler(False)
        
    def OnAddClick(self):
        '''
            Attempts to add the current selection to the color palette.
            Checks that <20 colors are in the palette and that the average
            color is not (0,0,0) i.e. no selection.
        '''
        if len( self.colorNameInputs ) == 20:
            print "ERROR: Tekkotsu is currently limited to 20 colors."
            print "       Delete some colors first."
            return
        
        R, G, B = (-1,-1,-1)
        total_area = 0
        
        for highlighted_img_path in self.highlight_area.keys():
            add_img = Image.open( highlighted_img_path )
            add_pixels = list( add_img.getdata() )
            add_w, add_h = add_img.size
            
            this_area = 0
            for area in self.highlight_area[highlighted_img_path]:
                this_area += len(area)
                
                    
            color = edge.average_color( add_pixels,\
                                    add_w, add_h,\
                                    self.highlight_area[highlighted_img_path] )
            
            try:
                
                R = (total_area * R + this_area * color[0])/(total_area+this_area)
                G = (total_area * G + this_area * color[1])/(total_area+this_area)
                B = (total_area * B + this_area * color[2])/(total_area+this_area)
                
                total_area += this_area
            
            except(TypeError):
                continue
               
            
        color = (R,G,B)
        
        if color == (-1,-1,-1):
            return
        
        # Bind checkbutton variable to the widget instance
        # because Tkinter is silly
        v = tk.IntVar()
        newChkbtn = tk.Checkbutton( self.palette, variable=v )
        newChkbtn.var = v

        # Convert decimal RGB color tuple to hex
        # Python makes me do things that makes my inner C programmer cry
        color = (str(hex(color[0])),str(hex(color[1])),str(hex(color[2])))
        hexcol='#'
        if ( len(color[0]) == 4 ):
            hexcol+=color[0][2]+color[0][3]
        else:
            hexcol+='0'+color[0][2]
        if ( len(color[1]) == 4 ):
            hexcol+=color[1][2]+color[1][3]
        else:
            hexcol+='0'+color[1][2]
        if ( len(color[2]) == 4 ):
            hexcol+=color[2][2]+color[2][3]
        else:
            hexcol+='0'+color[2][2]

        # Get a default name for the new color
        i=0
        colorNum = 1
        while i < len(self.colorNameInputs):
            if self.colorNameInputs[i].get() == "New color "+str(colorNum):
                colorNum+=1
                i=0
            else:
                i+=1
                
        self.master_color_list.append( [self.highlight_area , color, "New color"+str(colorNum)] )
        self.highlight_area = dict()

        # make a text entry field
        newEntry = tk.Entry( self.palette, width=10 )
        newEntry.insert( 0, "New color "+str(colorNum) )

        # make a new color frame
        # TODO make the mouse curor change on mouse-over to reflect
        #      clickable status
        newFrame = tk.Frame( self.palette,\
                             height=25, width=40,\
                             relief='raised',\
                             borderwidth=5,\
                             background=hexcol )
        newFrame.bind( "<Button-1>", self.OnColorClick )

        self.colorChkbtn.append(newChkbtn)
        self.colorNameInputs.append(newEntry)
        self.colorFrames.append(newFrame)

        self.drawPalette()

    def OnSaveClick(self):
        
        # Update the names of the colors from the Entry widgets
        for i in xrange( 0, len( self.master_color_list ) ):
            self.master_color_list[i][2] = self.colorNameInputs[i].get()
        
        generator.generate_color_space(self.master_color_list, self.imgpaths)

        toSerialize = (self.master_color_list,
                       self.thresholds)

        try:
            pickle.dump(toSerialize, open("default.et", "w"))

        except(pickle.PicklingError):
            print "Failed to write default.et"

    def OnLoadClick(self):
        '''TODO'''
        print "OnLoadClick not implemented! Unable to resore previous sessions."
        pass

    def OnDeleteClick(self):
        '''
            Deletes all colors in the palette with marked checkbuttons.
            The range is reversed so the master color list can effectively remove within the loop
        '''
        toRemove = []
        for i in reversed(range( 0, len( self.colorChkbtn ) )):
            if self.colorChkbtn[i].var.get() == 1:
                toRemove.append( ( self.colorChkbtn[i],\
                                   self.colorNameInputs[i],\
                                   self.colorFrames[i] ) )
                self.master_color_list.pop( i )

        for x in toRemove:
            x[0].grid_remove()
            self.colorChkbtn.remove(x[0])
            x[1].grid_remove()
            self.colorNameInputs.remove(x[1])
            x[2].grid_remove()
            self.colorFrames.remove(x[2])
        
        self.drawPalette()

    def OnColorClick(self, event):
        print "TODO"
        pass

if __name__ == "__main__":
    app = None
    #if len( sys.argv ) == 1:
    #    app = EasierTrain( None, '.' )
    #else:
    
    #OPTIONAL uncomment these lines if psyco is available on your platform
    import psyco
    psyco.full()
    
    app = EasierTrain( None, sys.argv[1] )
    app.title( 'EasierTrain' )
    app.mainloop()
