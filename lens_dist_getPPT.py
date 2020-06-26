"""
Undistorts, reprojects and crops specific areas of a picture from a camera in
order to extract slideshow and chalkboard images
"""

import cv2, time, sys, glob
import numpy as np



width = 1920
height = 1080
# Compensating parm. (Lens distortion)
K = np.array([[857.48296979, 0, 968.06224829], [0, 876.71824265, 556.37145899-50], [0, 0, 1]])
zoomOutM = np.array([[857.48296979-350, 0, 968.06224829], [0, 876.71824265-200, 556.37145899], [0, 0, 1]])
d = np.array([-0.257614020, 0.0877086999, 0, 0, -0.0157194091*5/6])
#Projection parm.
orig_pts = np.float32([[370-10, 366-10], [1554, 454], [32, 1076], [1790, 990]])
dest_pts = np.float32([[0, 0], [width, 0], [0, int(height*0.75)], [width, int(height*0.75)]])
blank_frame = np.zeros((height,width,3),np.uint8)
mapx, mapy = cv2.initUndistortRectifyMap(K,d,None,zoomOutM,(width,height),5)
perMat = cv2.getPerspectiveTransform(orig_pts, dest_pts)

def diffImg(t1,t2,t3):
	d1 = simpleFilter(255-t1)
	d2 = simpleFilter(255-t2)
	d3 = simpleFilter(255-t3)
	
	ave1 = cv2.bitwise_and(d1,d2)
	ave2 = cv2.bitwise_and(d2,d3)
	ave3 = cv2.bitwise_and(ave1,ave2)
	diff13 = cv2.absdiff(d1,d3)
	diff23 = cv2.absdiff(d2,d3)
	diff = cv2.bitwise_and(diff13,diff23)
	#kernel = np.ones((5,5),np.uint8)
	#kernel1 = np.ones((100,100),np.uint8)
	#opening = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)	
	#closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel1)
	#kernel = np.ones((7,7),np.uint8)	
	#forel_im = diff13 + diff23
	#opening = cv2.morphologyEx(forel_im, cv2.MORPH_OPEN, kernel)
	#kernel = np.ones((7,7),np.uint8)
	#dilation = cv2.dilate(opening,kernel,iterations = 12)
	#dstim = ave3 - dst
	#return 255-ave3
	return 255 - ave3 + diff
def simpleFilter(o_frame):
	fil_im = cv2.adaptiveThreshold(o_frame,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,17,3)
	inv_im = fil_im
	return 255 - inv_im

def lensFilter(o_frame,h,w):
	newframe = cv2.remap(o_frame, mapx, mapy,cv2.INTER_LINEAR)
	pro_frame = cv2.warpPerspective(newframe, perMat, (w,int(h*0.75)))
	return pro_frame

def getPPT(o_frame):
	#PPT Projection parm.
	PPTorig_pts = np.float32([[590, 132], [916, 166], [486, 370],
                       [910, 396]])
	PPTdest_pts = np.float32([[0, 0], [800, 0], [0, 600], [800, 600]])
	Op1_frame = cv2.remap(o_frame, mapx, mapy,cv2.INTER_LINEAR)
	PPTproj = cv2.getPerspectiveTransform(PPTorig_pts, PPTdest_pts)
	pro_frame = cv2.warpPerspective(Op1_frame,PPTproj,(800,600))
	return d

def compareIm(frame1,frame2):
	diffim = cv2.absdiff(frame1,frame2)
	diffPx = cv2.countNonZero(diffim)
	if diffPx > 100:
		return True
	else:
		return False

def Automat(vid_name):
	#For feed fra webcam: cv2.VideoCapture(0)
	#For feed fra fil: cv2.VideoCapture('filnavn')
	cap = cv2.VideoCapture(vid_name)
	#cap2 = cv2.VideoCapture(vid_name)
	cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,10000)
	winMOT = "Video feed"
	cv2.namedWindow(winMOT,cv2.CV_WINDOW_AUTOSIZE)
	#winMOT2 = "Video feed"
	#cv2.namedWindow(winMOT2,cv2.CV_WINDOW_AUTOSIZE)

	width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
	size = (width, height)
	FPS = cap.get(cv2.cv.CV_CAP_PROP_FPS)
	total_frames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
	frame_lapse = (1/FPS)*1000
	current_frame = 0
	blank_frame = np.zeros((height*2,width/2),np.uint8)

	if (cap.read()[0]):
		t_1 = cv2.cvtColor(cap.read()[1],cv2.COLOR_RGB2GRAY)
		t_2 = cv2.cvtColor(cap.read()[1],cv2.COLOR_RGB2GRAY)
		t_3 = cv2.cvtColor(cap.read()[1],cv2.COLOR_RGB2GRAY)
	else:
		t_1 = cv2.cvtColor(np.zeros((height,width,3),np.uint8),cv2.COLOR_RGB2GRAY)
		t_2 = cv2.cvtColor(np.zeros((height,width,3),np.uint8),cv2.COLOR_RGB2GRAY)
		t_3 = cv2.cvtColor(np.zeros((height,width,3),np.uint8),cv2.COLOR_RGB2GRAY)
	oldF = t_2
	oldF_dos = t_1
	count = 0
	count_dos = 0 
	count_tres = 0
	while(cap.isOpened()):
		while current_frame < total_frames:
			ret, frame = cap.read()
			current_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
			if(ret):
					t_1 = t_2
					t_2 = t_3
					if (cap.read()[0]):
						count = count + 1
						count_dos = count_dos + 1
						count_tres = count_tres + 1
						t_3 = cv2.cvtColor(cap.read()[1],cv2.COLOR_RGB2GRAY)
					else:
						t_3 = cv2.cvtColor(np.zeros((height,width,3),np.uint8),cv2.COLOR_RGB2GRAY)
					if (count > 30) and (cap.read()[0]):
						count = 0
						oldF = cv2.cvtColor(cap.read()[1],cv2.COLOR_RGB2GRAY)
					if (count_dos > 50) and (cap.read()[0]):
						count_dos = 0
						oldF_dos = cv2.cvtColor(cap.read()[1],cv2.COLOR_RGB2GRAY)
					print "Frame: " + str(current_frame)
					#**********************NOTER OG PPT
					if count_tres > 80:
						count_tres = 0
						print "Frame: " + str(current_frame)  
						Mframe = diffImg(oldF_dos,oldF,t_3)
						da1 = lensFilter(Mframe,height,width)
						x_off2 = 0
						y_off = 5
 						tavl1 = da1[10:height*2/3+30,20:int(width/2)-45]
						tavl2 = da1[height*1/3+50:height*2/3,35:int(width/2)-45]
						tavl3 = da1[height*1/3+50:height*2/3,int(width/2)+45:int(width)]
						print str(tavl1.shape[0]) + " X " + str(tavl1.shape[1])
						blank_frame[y_off:y_off+tavl1.shape[0], x_off2:x_off2+tavl1.shape[1]] = tavl1
						y_off2 = tavl1.shape[0]

						blank_frame[y_off2:y_off2+tavl2.shape[0], x_off2:x_off2+tavl2.shape[1]] = tavl2
						y_off3 = tavl1.shape[0]+tavl2.shape[0]

						blank_frame[y_off3:y_off3+tavl3.shape[0], x_off2:x_off2+tavl3.shape[1]] = tavl3

						y_off4 = tavl1.shape[0]+ tavl2.shape[0] + tavl3.shape[0]
						vis = blank_frame[0:y_off4,0:int(width/2)-85]
						Out_PPT = getPPT(frame)
						#fgmask = bgs.apply(t_3)
						#cv2.imwrite('NOTE/'+'Proj_'+str(int(current_frame/30.0))+'sec.png',Out_NOTE)
						#cv2.imwrite('PPT/'+'Proj_'+str(int(current_frame/30.0))+'sec.png',Out_PPT)
						res = cv2.resize(Mframe,None,fx=0.75,fy=0.6,interpolation = cv2.INTER_CUBIC)
						#cv2.flip(frame,1) for at spejlvende
						cv2.imshow(winMOT,tavl1)
						#cv2.imshow(winMOT2,Out_PPT)
					if cv2.waitKey(1) & 0xFF == ord('q'):
						break
		print "Another Great Success!"
		cv2.waitKey(0)			
		cap.release()
		cv2.destroyAllWindows()
		return;

Automat('GOPR0202.MP4')
sys.exit()
