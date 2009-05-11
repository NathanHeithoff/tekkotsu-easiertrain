HOW DOES I EASIERTRAIN?

Running EasierTrain requires the Python Imaging library (PIL) 1.1.6 or higher.
    http://www.pythonware.com/products/pil
EasierTrain developed on Python 2.6.2.

The EasierTrain user experience goes something like this:
    0. Run the script
        $ python EasierTrain.py <img-dir>
        <img-dir> is a direcory containing image files
        behavior when non-images are present in this folder is undefined

  0.5. Load #TODO implement me

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
                Use the big slider or the text entry and "set" button
            Multiple images
                Use prev/next buttons to cycle between images in <img-dir>
                Selection is PRESERVED when you click away from an image
                    #FIXME the program doesn't make this obvious
                    #TODO implement clear/clearall buttons?
            Happy with your selection? Click the "Add" button!

    2. Save #TODO work out the bugs in the .tm file
        Generates "easiertrain.tm" and "easiertrain.col" in cwd
            #TODO Save as... dialog

    3. Edit tekkotsu.xml to use new files
    
    4. Go use tekkotsu with superior color segmentation! Hopefully.
