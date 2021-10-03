from flask import Flask, render_template, request
app = Flask(__name__, template_folder='templates')
import pymongo
import shortuuid
import smtplib
from email.message import EmailMessage
import qrcode
import base64
import requests
import os

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/info')
def info():
   return render_template('info.html')


@app.route('/maketestform')
def student():
   return render_template('index.html')

@app.route('/maketest',methods = ['POST', 'GET'])
def submission():
   client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
   if request.method == 'POST':
      result = request.form
      db = client['myFirstDatabase']
      collection = db["Teacher_Test_Papers"]
      #print(result)
      teacherEntrysDict = {} 
      for i in result:
        teacherEntrysDict[i]=result[i]
      teacherEntrysDict["unique_id"] = shortuuid.uuid()
      #print(teacherEntrysDict["unique_id"])
      collection.insert_one(teacherEntrysDict)
      s = smtplib.SMTP('smtp.gmail.com', 587)
      s.starttls()
      s.login("letsproctor@gmail.com", "letsproctor@123")
      #message = f"Hi Your unique id for test {teacherEntrysDict['title']} is {teacherEntrysDict['unique_id']}"
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
      message['To'] = teacherEntrysDict["emailid"]
      s.send_message(message)
        
      return render_template("submission.html",result = teacherEntrysDict)
      
@app.route('/resultform')
def getProcResult():
   return render_template('resultsforms.html')

@app.route('/results',methods = ['POST', 'GET'])
def results():
   client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
   if request.method == 'POST':
      result = request.form
      db = client['myFirstDatabase']
      collection = db["Results_Proctoring"]
      studentResultDict = {} 
      for i in result:
        studentResultDict[i]=result[i]
      print(studentResultDict)
      
      responseFromDatabase = collection.find({'email id' : studentResultDict['email id'], "unique_id":studentResultDict['uniqueid']})
      
      completeStudentResultDict = {} 
      for i in responseFromDatabase:
        print(i,">>>")
        for j in i:
            completeStudentResultDict[j]=i[j]
      
      return render_template("results.html",result = completeStudentResultDict)
      
@app.route('/studentexamform')
def examform():
   return render_template('examform.html')

@app.route('/exam',methods = ['POST', 'GET'])
def exam():
   client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
   if request.method == 'POST':
      result = request.form
      examDict = {}
      for i in result:
        examDict[i]=result[i]
      #print(examDict["email id"],examDict["uuid"])
      qrimg = qrcode.make(examDict["email id"]+" "+examDict["uuid"])
      qrimg.save("image.jpg")
      
      with open("image.jpg", "rb") as file:
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": "c4b63af118f97f88cdeea980cdb4d6c9",
            "image": base64.b64encode(file.read()),
        }
        res = requests.post(url, payload)
        uploaded_url = dict(res.json())["data"]["display_url"]
        examDict["uploaded_url"] = uploaded_url
      os.remove("image.jpg")
      
      db = client['myFirstDatabase']
      collection = db["Teacher_Test_Papers"]
      responseFromDatabase = collection.find({"unique_id":examDict["uuid"]})
      for i in responseFromDatabase:
        for j in i: 
            #print(j,i[j])
            if j=="gformlink":
                g_form = i[j]
      examDict["g_form"] = g_form
      
      
      
      
      return render_template("exam_main.html",result = examDict)
      #pyinstaller proctor.py --onefile --paths=D:\React_apps\Resonate\env\Lib\site-packages --add-data=D:\React_apps\Resonate\env\Lib\site-packages\mediapipe\modules;mediapipe\modules
      
if __name__ == '__main__':
   client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
   app.run(debug = True)
   
