#!/usr/bin/env python

"""
Simple adaptive threshold app in order convert an RGB picture of a chalkboard
with notes to a BW image with notes ready to be be compiled into a pdf
"""

import cv2
import numpy as np
import glob
import datetime
import os

now = datetime.datetime.now()
folderIMG = now.strftime("IMG_%Y_%m_%d")
folderNOTE = now.strftime("NOTE_%Y_%m_%d")
if not os.path.exists(folderNOTE):
    os.makedirs(folderNOTE)

def simpleFilter(o_frame):
	fil_im = cv2.adaptiveThreshold(o_frame,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,25,-10)
	return 255-fil_im

for filename in sorted(glob.iglob(folderIMG+'/*.jpg')):
    imgName = filename.split('/',1)[1]
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    outNote = simpleFilter(gray)
    cv2.imwrite(folderNOTE+"/"+imgName,outNote)

if cv2.waitKey(0) == 27:
	cv2.destroyAllWindows()
