from flask import Flask, render_template, request, jsonify
app = Flask(__name__, template_folder='templates')
import pymongo
import shortuuid
import smtplib
from email.message import EmailMessage
import qrcode
import base64
import requests
import os
import cv2
import mediapipe as mp
import os
import time
import shortuuid
import base64
import requests

@app.route('/api/maketest',methods = ['POST', 'GET'])
def maketest():
   
   if request.method == "POST":
      result = request.json["formDetails"]
      print(result)
      client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
      db = client['myFirstDatabase']
      collection = db["Teacher_Test_Papers"]
      teacherEntrysDict = {} 
      for i in result:
        teacherEntrysDict[i]=result[i]
      teacherEntrysDict["unique_id"] = shortuuid.uuid()
      collection.insert_one(teacherEntrysDict)
      s = smtplib.SMTP('smtp.gmail.com', 587)
      s.starttls()
      s.login("letsproctor@gmail.com", "letsproctor@123")
      message = EmailMessage()
      message.set_content('''\
        <!DOCTYPE html>
        <html>
            <body>
                <div style="background-color:#CBC3E3;padding:10px 20px;">
                    <h2 style="font-family:Georgia, serif;color#454349;">Your Unique ID is here for <u><b>''' +str(teacherEntrysDict["title"]) + '''</u></b> test</h2>
                </div>
                <div style="padding:0px 0px;">
                    <div style="height: 400px;">
                        <div style="height: 70px ; background-color:#171c1a; font-size: 40px; color:white;">
                        <p style = "padding: 1px">
                        ''' +str(teacherEntrysDict["unique_id"]) + '''
                        </p>
                        </div>
                        <div style="text-align:center;">
                            <h3>'''+str(teacherEntrysDict["title"])+str(" test")+'''</h3>
                            <p>Please send the students the unique id that you have received in this Email. For more information click link below</p>
                            <a href="#">Read more</a>
                            
                        </div>
                    </div>
                </div>
            </body>
        </html>
        ''', subtype='html')
      message['Subject'] = f'Your Proctoring Code is here {teacherEntrysDict["unique_id"]}'
      message['From'] = "letsproctor@gmail.com" 
      message['To'] = teacherEntrysDict["email"]
      s.send_message(message)
      teacherEntrysDict.pop("_id")
      return jsonify(teacherEntrysDict)
   return "Success"

@app.route('/api/results',methods = ['POST', 'GET'])
def results():
    
    if request.method == "POST":
          client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
          result = request.json["formDetails"]
          db = client['myFirstDatabase']
          collection = db["Results_Proctoring"]
          studentResultDict = {} 
          for i in result:
            studentResultDict[i]=result[i]
          print(studentResultDict)
          
          responseFromDatabase = collection.find({'email id' : studentResultDict['email'], "unique_id":studentResultDict['uniqueID']})
          print(responseFromDatabase,"RESPONSE FORM DATABASE")
          completeStudentResultDict = {} 
          for i in responseFromDatabase:
            #print(i,"i")
            for j in i:
                completeStudentResultDict[j]=i[j]
          #print(completeStudentResultDict,"DATABASE")
          completeStudentResultDict.pop("_id")
          return jsonify(completeStudentResultDict)
    

@app.route('/api/video',methods = ['POST', 'GET'])
def video():
    if request.method == "POST":
        
        totalFrames = 0
        face_detected = 0
        face_tilt_detected = 0
        imagesurls = []
        #print(request.files)
        
        video = request.files.to_dict()["image"]
        #print(dir(video))
        unique_video = shortuuid.uuid()
        
        
        
        video.save(dst=f"{unique_video}.mp4")
        print("sleeping...")
        time.sleep(10)
        print("awake....")
        ### Operations on video ###
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_face_mesh = mp.solutions.face_mesh
        mp_face_detection = mp.solutions.face_detection # Face Track
        drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        cap = cv2.VideoCapture(f"{unique_video}.mp4")
        
        face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) #Mesh
        face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.7) # Track
        while cap.isOpened():
            success, image = cap.read()
            
            if success == True:
                totalFrames = totalFrames + 1
                half = cv2.resize(image, (0, 0), fx = 0.3, fy = 0.3)
                height,width,_=image.shape
                
                imagebb = image.copy()
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results2 = face_detection.process(image)
                image.flags.writeable = True
                
                if results2.detections:
                  if len(results2.detections)>1:
                    #print("multiple people detected")
                    face_detected = face_detected + 1
                    if face_detected % 10 == 0:
                        imagebb = cv2.putText(image, 'Person Detection', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
                        cv2.imwrite("fileupload2.jpg",imagebb)
                        with open("fileupload2.jpg", "rb") as file:
                            url = "https://api.imgbb.com/1/upload"
                            payload = {
                                "key": "c4b63af118f97f88cdeea980cdb4d6c9",
                                "image": base64.b64encode(file.read()),
                            }
                            res = requests.post(url, payload)
                            uploaded_url = dict(res.json())["data"]["display_url"]
                            imagesurls.append([uploaded_url,"People Detection"])
                            try:
                                os.remove("fileupload2.jpg")
                            except:
                                pass
                    
                  if len(results2.detections)==1:
                    print("Correct",end="")
                    
                else:
                  if face_detected % 10 == 0:
                        imagebb = cv2.putText(image, 'Person Detection', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
                        cv2.imwrite("fileupload3.jpg",imagebb)
                        with open("fileupload3.jpg", "rb") as file:
                            url = "https://api.imgbb.com/1/upload"
                            payload = {
                                "key": "c4b63af118f97f88cdeea980cdb4d6c9",
                                "image": base64.b64encode(file.read()),
                            }
                            res = requests.post(url, payload)
                            uploaded_url = dict(res.json())["data"]["display_url"]
                            imagesurls.append([uploaded_url,"People Detection"])
                            try:
                                os.remove("fileupload3.jpg")
                            except:
                                pass
                  face_detected = face_detected+1
                  
                
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
                    
                
                ######## Face Tilt #########
                if results2.detections:
                    for detection in results2.detections:
                        for ids,landmrk in enumerate(detection.location_data.relative_keypoints):
                            
                            if ids == 2:
                                nose = landmrk.x*width
                            if ids == 4:
                                leftCheekx = landmrk.x*width
                                leftCheeky = landmrk.y*height
                            if ids == 5:
                                rightCheekx = landmrk.x*width
                                rightCheeky = landmrk.y*height
                            if ids == 0:
                                FrightEyey = landmrk.y*height
                            if ids == 1:
                                FleftEyey = landmrk.y*height
                            if ids == 3:
                                mouth = landmrk.y * height
                            
                            try:
                                if leftCheekx > nose or rightCheekx < nose or (leftCheeky-FleftEyey)< -40 or (rightCheeky-FrightEyey) < -40 or abs(leftCheeky-mouth)<10 or abs(rightCheeky-mouth)<8:
                                    face_tilt_detected = face_tilt_detected + 1
                                    if face_tilt_detected % 5 == 0:
                                        imagebb = cv2.putText(image, 'Tilt Detection', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
                                        cv2.imwrite("fileupload.jpg",imagebb)
                                        with open("fileupload.jpg", "rb") as file:
                                            url = "https://api.imgbb.com/1/upload"
                                            payload = {
                                                "key": "c4b63af118f97f88cdeea980cdb4d6c9",
                                                "image": base64.b64encode(file.read()),
                                            }
                                            res = requests.post(url, payload)
                                            uploaded_url = dict(res.json())["data"]["display_url"]
                                            imagesurls.append([uploaded_url,"Tilt Detection"])
                                            try:
                                                os.remove("fileupload.jpg")
                                            except:
                                                pass

                            except:
                                pass
            else:
                print("false")
                break
        print(face_tilt_detected,"face tilt", totalFrames, "total Frame")        
        headtilt = int((face_tilt_detected/(totalFrames*3))*100)
        people = int((face_detected/totalFrames)*100)
        
        
        response = {"headtilt":headtilt, "people":people, "imagesurls":imagesurls, "totalFrames":totalFrames}
        
        return(jsonify(response))
         
            
          
    
    return "Success"

@app.route('/api/exam',methods = ['POST', 'GET', 'OPTIONS'])
def exam():
    
    if request.method == "POST":
          client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
          result = request.json["formDetails"]
          db = client['myFirstDatabase']
          collection = db["Teacher_Test_Papers"]
          result = request.json["formDetails"]
          print(result,"result")
          examDict = {}
          for i in result:
            examDict[i]=result[i]
            
          responseFromDatabase = collection.find({"unique_id":examDict["uniqueID"]})
          
          for i in responseFromDatabase:
            for j in i: 
                print(j,i[j])
                if j=="gform":
                    g_form = i[j]
          examDict["g_form"] = g_form
          return jsonify(examDict)
    if request.method == "OPTIONS":
        print("options")
        return "Success"
    return "Success"

@app.route('/api/submittest',methods=['POST','GET'])    
def submittest():
    if request.method=="POST":
        
        totaltabChange = request.json["alldata"][0]
        totalSize = request.json["alldata"][1]
        videoresponse = request.json["alldata"][2]
        propdata = request.json["alldata"][3]
        
        
        result_dict = {"name":propdata["name"],"roll no":propdata["roll"],"email id":propdata["email"],"unique_id":propdata["uniqueID"],"frames":videoresponse["totalFrames"],"headtilt":videoresponse["headtilt"], "people":videoresponse["people"],"tabchange":totaltabChange,"browsersize":totalSize,"imageurls":videoresponse["imagesurls"]}
        
        
        
        
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
        db = client['myFirstDatabase']
        collection = db["Results_Proctoring"]
        collection.insert_one(result_dict)
        
        print(result_dict)
        
        
        print(totaltabChange,"\n\n", totalSize,"\n\n", videoresponse,"\n\n", propdata,"\n\n",)
    return "Success"

if __name__ == '__main__':
   mp_drawing = mp.solutions.drawing_utils
   mp_drawing_styles = mp.solutions.drawing_styles
   mp_face_mesh = mp.solutions.face_mesh
   mp_face_detection = mp.solutions.face_detection # Face Track
   drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
   client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
   app.run(debug = True)
   
