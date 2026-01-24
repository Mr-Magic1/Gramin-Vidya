import cv2 as cv
cap = cv.VideoCapture(0, cv.CAP_DSHOW)

while True:
    ret,frame = cap.read()

    if ret == False:
        break

    cv.imshow("video frame",frame)

    key_pressed = cv.waitKey(1) & 0xFF

    if key_pressed == ord('q'):
        break

cap.release()
cv.destroyAllWindows()