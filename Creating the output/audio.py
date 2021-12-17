#importing Libraries

import numpy as np
import cv2
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D
from keras.optimizers import Adam
from keras.layers import MaxPooling2D
from keras.preprocessing.image import ImageDataGenerator
from gtts import gTTS
import os
from moviepy.editor import *
import time


#Initializing the model

emotion_model = Sequential()

emotion_model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48,48,1)))
emotion_model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Dropout(0.25))

emotion_model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Dropout(0.25))

emotion_model.add(Flatten())
emotion_model.add(Dense(1024, activation='relu'))
emotion_model.add(Dropout(0.5))
emotion_model.add(Dense(7, activation='softmax'))
emotion_model.load_weights('../Training the model/emotion_model.h5')

cv2.ocl.setUseOpenCL(False)


emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

#Reading from video feed
TIMER = int(2)
cap = cv2.VideoCapture(0)
while True:
    # Find haar cascade to draw bounding box around face
    ret, frame = cap.read()
    if not ret:
        break
    bounding_box = cv2.CascadeClassifier("../haarcascade_frontalface_default.xml")
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    num_faces = bounding_box.detectMultiScale(gray_frame,scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in num_faces:
        cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
        roi_gray_frame = gray_frame[y:y + h, x:x + w]
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)
        emotion_prediction = emotion_model.predict(cropped_img)
        maxindex = int(np.argmax(emotion_prediction))
        cv2.putText(frame, emotion_dict[maxindex],(x+20, y-60),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),2,cv2.LINE_AA)

    cv2.imshow('Video', cv2.resize(frame,(600,600),interpolation = cv2.INTER_CUBIC))
    k = cv2.waitKey(125)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if k == 32: 
        prev = time.time() 
        while TIMER >= 0: 
            ret, img = cap.read()  
            font = cv2.FONT_HERSHEY_SIMPLEX 
            cv2.putText(img, str(TIMER), 
                        (50, 50), font, 
                        2, (0, 255, 0), 
                        3, cv2.LINE_AA) 
            cv2.imshow('a', img) 
            cv2.waitKey(125) 
            cur = time.time() 
            if cur-prev >= 1: 
                prev = cur 
                TIMER = TIMER-1
        ret, img = cap.read() 
        cv2.putText(img, emotion_dict[maxindex],(x+20, y-60),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),2,cv2.LINE_AA)
        cv2.imshow('a', img) 
        cv2.waitKey(2500)
        pic = emotion_dict[maxindex]
        break
cap.release()
cv2.destroyAllWindows()


#inputs
message = input("Enter word:")

#converting to sound
speech = gTTS(text = message,lang = 'en' , tld = 'co.in')
name = message + ".mp3"
if os.path.exists(name):
        os.remove(name)
speech.save(name)
pic = pic + '.png'
clip = ImageSequenceClip([pic], fps = 1)

# getting only first 1 seconds
clip = clip.subclip(0, 1)
# loading audio file
audioclip = AudioFileClip(name).subclip(0, 1)
  
# adding audio to the video clip
videoclip = clip.set_audio(audioclip)
videoclip.write_videofile("vid.mp4", fps = 1)
name = ''
pic = ''
os.remove(name)
