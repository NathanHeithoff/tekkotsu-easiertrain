HOW DOES I EASIERTRAIN?

Running EasierTrain requires the Python Imaging library (PIL) 1.1.6 or higher.
    http://www.pythonware.com/products/pil
EasierTrain developed on Python 2.6.2.

Installing Psyco is also highly recommended.
http://psyco.sourceforge.net/

The EasierTrain user experience goes something like this:
    0. Setup
        a) Copy EasierTrain.py, edge.py, and generator.py into a new directory
           (we recommend each segmentation file have its own directory so
           you don't lose your work)
        b) cd to your new directory and run the script
            $ python EasierTrain.py <img-dir>
            <img-dir> is a direcory containing image files

  0.5. (optional) Load previous session data with the "Load" button

    1. Populate color palette
        a) Select colors
            Mouse controls
                Click to start a new selection on the image
                Shift-click to add new areas
                Ctrl-click to add new areas or to remove selected areas
            Threshold
                Lower threshold = more edges
                Threshold is stored on a per-image basis
                Adjusting threshold clears any selection in the current image
                To adjust, use the big slider or the text entry and "set" button
            Multiple images
                Use prev/next buttons to cycle between images in <img-dir>
                Selection is PRESERVED when you click away from an image
                    #FIXME the program doesn't make this obvious
                    #TODO implement clear/clearall buttons?
            Happy with your selection? Click the "Add" button!

    2. Save your work with the "save" button
        Generates three files:
            "default.tm" and "default.col"
                Used by tekkotsu
            "default.et"
                Your session data
                Retreive this color palette with "Load" button
            #TODO Save as... dialog

    3. Edit tekkotsu.xml to use new files
    
    4. Go use tekkotsu with superior color segmentation! Hopefully.
