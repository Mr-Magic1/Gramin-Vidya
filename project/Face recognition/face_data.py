import cv2 as cv
import numpy as np

cap= cv.VideoCapture( 0 ,cv.CAP_DSHOW )
face_cascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")

skip = 0
face_data = []
dataset_path= "./face_dataset/"

file_name = input("Enter the name of the student")

while True:
    ret,frame = cap.read()
    
    # converts the image into gray sacle so that easy to asses it 
    gray_frame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)

    if ret==False:
        break

    #Will return the coordinate of my face
    faces = face_cascade.detectMultiScale(gray_frame,1.1,6)
    
    if len(faces) == 0:
        continue

    k=1
    

    #sorting in the descending order using lambda function
    faces = sorted(faces, key = lambda x:x[2]*x[3],reverse = True)

    

    for face in faces[:1]:
        x,y,w,h = face
        

        #providing the padding of 5
        offset = 5
        face_offset = frame[y-offset:y+h+offset,x-offset:x+w+offset]
        
        if face_offset.size > 0:
            face_selection = cv.resize(face_offset, (100, 100))
            skip += 1
        
        if skip % 10 == 0:
            face_data.append(face_selection)
            print(len(face_data))

        cv.imshow(str(k), face_selection)
        k +=1
        
        #creating a rect frame around my face
        cv.rectangle(frame ,(x,y),(x+w,y+h),(0,255,0),2)
    
    #video read
    cv.imshow("faces",frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

#changing the data into numpy in order to apply it in KNN
face_data = np.array(face_data)
face_data = face_data.reshape((face_data.shape[0],-1))
print(face_data.shape)

np.save(dataset_path + file_name , face_data)
print("Data saved at:{}".format(dataset_path+file_name + '.npy'))

cap.release()
cv.destroyAllWindows