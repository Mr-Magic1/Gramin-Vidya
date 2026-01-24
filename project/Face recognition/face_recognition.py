import cv2 as cv
import numpy as np
import os
from sklearn.neighbors import KNeighborsClassifier # <--- IMPORT SKLEARN


cap = cv.VideoCapture(0, cv.CAP_DSHOW)
face_cascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")

dataset_path = "./face_dataset/"
face_data = [] 
labels = []
class_id = 0 
names = {} 

#Check if dataset exists
if not os.path.exists(dataset_path):
    print("Error: Dataset folder not found!")
    exit()

#loading data
print("Loading data...")
for fx in os.listdir(dataset_path):
    if fx.endswith('.npy'):
        names[class_id] = fx[:-4] # Map 0 -> "Abhay"
        
        data_item = np.load(dataset_path + fx)
        face_data.append(data_item)

        # Create labels (Class ID) for this file
        target = class_id * np.ones((data_item.shape[0],))
        labels.append(target)
        
        class_id += 1

#changing into array to apply KNN
X = np.concatenate(face_data, axis=0)
Y = np.concatenate(labels, axis=0)

print(f"Data Loaded. Classes: {names}")

model = KNeighborsClassifier(n_neighbors=5) 

# Train the model (X=Images, Y=Labels)
model.fit(X, Y)
print("Model Trained Successfully!")



#face_recognition
while True:
    ret, frame = cap.read()
    if not ret: continue

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for face in faces:
        x, y, w, h = face

        # Extract Face
        offset = 5
        face_section = frame[y-offset:y+h+offset,x-offset:x+w+offset]
        
        if face_section.size == 0: continue

        # Resize and Flatten to match Training Data
        face_section = cv.resize(face_section, (100, 100))
        out = face_section.flatten()

        #prediction
        pred_label = model.predict([out])
        
        # Get the name
        pred_name = names[int(pred_label[0])]

        #show 
        cv.putText(frame, pred_name, (x, y-10), cv.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2, cv.LINE_AA)
        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv.imshow("Face Recognition", frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()