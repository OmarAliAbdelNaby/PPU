import numpy as np
import cv2
from PIL import Image

def sort_contours(cnts, method="left-to-right"):
    # initialize the reverse flag and sort index
    reverse = False
    i = 0

    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True

    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1

    # construct the list of bounding boxes and sort them from top to
    # bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))

    # return the list of sorted contours and bounding boxes
    return (cnts, boundingBoxes)


#-------------------------- Reading the Image --------------------
img = cv2.imread('normal.jpg', 0)
#cv2.imshow('grayScale', img)
#cv2.waitKey(0)
thresh = 127
img_bin = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)[1]
#cv2.imshow('binary', img_bin)
#cv2.waitKey(0)
#------------------------------------------------------------------


#------------------------------- Kernel Processing ----------------
# Defining a kernel length
kernel_length = np.array(img).shape[1] // 80
# A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
# A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
# A kernel of (3 X 3) ones.
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
#------------------------------------------------------------------


#----------------------------- Detecting Digits ---------------------------
# Find contours for image, which will detect all the boxes
contours, hierarchy = cv2.findContours(img_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# Sort all the contours by top to bottom.
(contours, boundingBoxes) = sort_contours(contours, method="top-to-bottom")
idx = 0
for c in contours:
    # Returns the location and width,height for every contour
    x, y, w, h = cv2.boundingRect(c)
    if (w > 80 and h > 20) and w > 3*h:
        idx += 1
        new_img = img_bin[y:y+h, x:x+w]
        cv2.imwrite( str(idx)+'.png', new_img)
# If the box height is greater then 20, widht is >80, then only save it as a box in "cropped/" folder.
    if (w > 80 and h > 20) and w > 3*h:
        idx += 1
        new_img = img_bin[y:y+h, x:x+w]
        cv2.imwrite(str(idx) + '.png', new_img)
#---------------------------------------------------------------------------


output = cv2.imread('1.png')
#cv2.imshow('Output', output)
#cv2.waitKey(0)


#------------------ Resizing ------------------
scale_percent = 150 # percent of original size
width = int(output.shape[1] * scale_percent / 100)
height = int(output.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
resized = cv2.resize(output, dim, interpolation = cv2.INTER_AREA)
#------------------------------------------------
#cv2.imshow('resizedOutput', resized)
#cv2.waitKey(0)


#--------------------------- Denoising the output ----------------
#cv2.imwrite('LCD.png', resized)
kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
opening = cv2.morphologyEx(resized, cv2.MORPH_OPEN, kernel2)
#cv2.imshow('Opening', opening)
#cv2.waitKey(0)
closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel2)
#cv2.imshow('Closing', closing)
#cv2.waitKey(0)
closingNOT = cv2.bitwise_not(closing)
cv2.imwrite('closingNOT.png', closingNOT)
#------------------------------------------------------------------


#------------------------------- Cropping -------------------
im = Image.open('closingNOT.png')
#im.show()
width, height = im.size   # Get dimensions
new_height = height/2
left = (width - width)/2
top = (height - new_height)/2 -14
right = ((width + width)/2) -10
bottom = (height + new_height)/2 +14
cropped = im.crop((left, top, right, bottom))
#cropped.show()
cropped.save('mainOutput.jpg')
#-----------------------------------------------------------
