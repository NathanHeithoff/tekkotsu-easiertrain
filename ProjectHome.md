EasierTrain is a tool for configuring Tekkotsu's color segmentation system. It is meant to replace EasyTrain, the current tool providing this functionality.

Tekkotsu: an open source, high-level robotics API developed out of CMU's CS department -- http://tekkotsu.no-ip.org

EasyTrain and color segmentation: http://www.cs.cmu.edu/~dst/Tekkotsu/Tutorial/colorsegment.shtml

11/03/09 - Install instructions (recommended platforms are Windows and Linux):

1) Install Python on your computer (http://www.python.org/)

2) Install Python Image Library (http://effbot.org/zone/pil-index.htm)

3) (recommended) Install psyco (http://sourceforge.net/projects/psyco/files/)

4) Download our source files: Get the featured download of EasierTrain-YYYYMMDD.zip on the right, or visit our downloads section.

NOTE: We recommend having a separate folder and separate copies of EasierTrain.py, edge.py, and generator.py for each color segmentation project you are working on.

5) view README.txt

EasierTrain outputs to files default.tm, default.col, and default.et. default.tm and default.col are used by Tekkotsu--you need to transfer these files over to the directory tekkotsu is running from. default.et is a serialization of all of your working data--retain this file if you want to change your segmentation later! Remember to update the xml file in that directory to only check for default.tm and default.col.


-- Michael and Nathan