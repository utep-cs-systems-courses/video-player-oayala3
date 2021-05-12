import threading
import cv2
import queue
import os

lock = threading.Lock()

class vQueue():
        def __init__(self):
                self.queue=[]
                self.full  = threading.Semaphore(0)
                self.empty = threading.Semaphore(10)
                
        def set(self, frame):
                self.empty.acquire()
                self.queue.append(frame)
                self.full.release()
                
        def get(self):
                self.full.acquire()
                frame = self.queue.pop(0)
                self.empty.release()
                return frame

def convertToGray(producer, consumer):
        count = 0
        current = producer.get()
        while current is not None:
                grayFrame = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
                consumer.set(grayFrame)
                count += 1                        
                consumer.set(None)

def extractFrames(producer, fileName, maxFrames):

                count = 0
                vidcap = cv2.VideoCapture(fileName)
                status, image = vidcap.read()
                while status and count < maxFrames:

                        status, jpgImage = cv2.imencode('.jpg',image)
                        producer.set(image)
                        status, image = vidcap.read()
                        count += 1
                producer.put(None)

def displayFrames(consumer):
        count = 0
        current=consumer.get()
        while current is not None:

                cv2.imshow('Video', current)
                if cv2.waitKey(42) and 0xFF == ord('q'):
                        break
                count += 1
                current=consumer.get()
                
        cv2.destroyAllWindows()               



pQueue = vQueue()                            
cQueue = vQueue()
fileName = 'clip.mp4'
maxFrames = 700     
extract = threading.Thread(target = extractFrames, args = (pQueue,fileName,maxFrames))
convert = threading.Thread(target = convertToGray, args = (pQueue, cQueue))
display = threading.Thread(target = displayFrames, args = {cQueue})                
extract.start()
convert.start()
display.start()
