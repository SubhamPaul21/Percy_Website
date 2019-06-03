from flask import Flask,render_template,flash,request,url_for,redirect, abort, Response
import os
#from gtts import gTTS
from PIL import Image
import requests
from random import sample
import face_recognition
import cv2
import glob
import sqlite3
#import random
import numpy as np
import wikipedia



app = Flask(__name__, template_folder='templates')
conn = sqlite3.connect('loginDetails.db')

@app.route('/index/')
def index():
    return render_template('index.html')

@app.route('/login/',methods=["GET","POST"])
def login_page():
    if request.method == 'POST':
        try:
            login_username = request.form['name'].lower()
            login_password = request.form['passwrd'].lower()
            print(login_username)
            print(login_password)
            con = sqlite3.connect('loginDetails.db')
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("select * from users")

            rows = cur.fetchall()
            usernames = set()
            passwords = set()
            for row in rows:
                usernames.add(row["username"])
                passwords.add(row["password"])
            #print(usernames)
            if login_username in usernames and login_password in passwords:
                return redirect(url_for('facelogin'))
            else:
                msg = 'Incorrect Username or Password. Please try again or Create Account'
                return render_template('invalid.html', msg = msg)
        except:
            return render_template('404.html')
    return render_template('existinglogin.html')

@app.route('/addnew/', methods = ['POST', 'GET'])
def addnew():
    if request.method == 'POST':
        try:
            new_username = request.form['username'].lower()
            new_firstname = request.form['firstname'].lower()
            new_lastname = request.form['lastname'].lower()
            new_password = request.form['password'].lower()
            print(new_firstname)
            print(new_lastname)
            print(new_username)
            print(new_password)
            with sqlite3.connect("loginDetails.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (firstname,lastname,username,password) VALUES (?,?,?,?)", (new_firstname,new_lastname,new_username,new_password))

                con.commit()
                msg = "Record successfully added"

        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("newaccountresult.html", mesg = msg)
            con.close()
    return render_template('newlogin.html')

@app.route('/list/')
def list():
    con = sqlite3.connect('loginDetails.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from users")

    rows = cur.fetchall()
    #for row in rows:
    #print(row["firstname"])
    return render_template('list.html', rows=rows)

@app.route('/login/home/')
def home():
    return render_template('home.html')

@app.route('/logout/')
def logout():
    return render_template('logout.html')

@app.route('/home/tdlist/')
def tdlist():
    return render_template('td_list.html')

@app.route('/home/jokes/')
def dad_jokes():
    return render_template('jokes.html')

@app.route('/home/wiki/', methods=['GET','POST'])
def wiki():
    if request.method == 'POST':
        terms = request.form['term']
        term = terms.lower()
        data = wikipedia.summary(term)
        return render_template('upload.html', result = data)
    return render_template('wiki.html')

@app.route('/home/jokes/random/')
def random():
    base_url = 'https://icanhazdadjoke.com/'
    response = requests.get(base_url,headers={'Accept':'application/json'}).json()
    jokee = response['joke']
    print(jokee)
    # count = str(random.randint(1,100))
    # print(count)
    # myObj = gTTS(text=jokee, lang='en', slow=False)
    # myObj.save('./static/songs/random_joke'+count+'.mp3')
    # time.sleep(3)
    # file = 'random_joke'+count+'.mp3'
    return render_template('random.html',result = jokee)

@app.route('/home/jokes/specific/', methods=["GET","POST"])
def specific():
    if request.method == "POST":
        attempt_term = request.form['textme']

        user_input = attempt_term.lower()
        base_url = 'https://icanhazdadjoke.com/'
        # get the response object and make json syntax out of it.
        response = requests.get(base_url + 'search',headers={'Accept':'application/json'},params={'term':user_input}).json()
        num_jokes = response['total_jokes']
        list_jokes = []
        if num_jokes > 1:
            for i in enumerate(response['results']):
                id = i[0]
                #print(id)
                if id < num_jokes:
                    joke = i[1]['joke']
                    list_jokes.append(joke)
                    id = id + 1

            two_random_joke = sample(list_jokes,2)
            #print(two_random_joke)
            return render_template('specific.html', result=two_random_joke)
        else:
            error = 'There are no jokes with this search term. Go back and try something else'
            return render_template('specific.html',error=error)

@app.route('/home/weather/')
def weather():
    return render_template('weather.html')

@app.route('/home/movie/')
def fresh_tomatoes():
    return render_template('fresh_tomatoes.html')

@app.route('/home/news/')
def news():
    news_content = []
    url = ('https://newsapi.org/v2/top-headlines?'
       'country=in&'
       'apiKey=41868dec8ba44b31b7b9f1be2489192b')
    response = requests.get(url)
    data = response.json()
    for content in data['articles'][:5]:
        desc = content['description']
        news_content.append(desc)
    #[0]['source']['name'])
    return render_template('news.html', context = news_content)

@app.route('/home/weather/weather_details/', methods=["GET","POST"])
def weather_details():
    if request.method == "POST":
        attempt_cityname = request.form['cityname']
        print(attempt_cityname)
        key = '58e4c54415194bb7b8d191443191903'
        base_url = 'http://api.apixu.com/v1/current.json'
        final_url = base_url + '?key=' + key + '&q=' + attempt_cityname
        request_from_url = requests.get(final_url)
        data = request_from_url.json()
        weather_info = data['current']['condition']['text']
        print(weather_info)
        details = {'location' : data['location']['name'],
	               'region' : data['location']['region'],
	               'weather' : data['current']['condition']['text'],
                   'lat' : data['location']['lat'],
                   'lon' : data['location']['lon'],
	               'temp_c' : data['current']['temp_c'],
                   'temp_f' : data['current']['temp_f'],
                   'is_day' : 'Night' if data['current']['is_day'] == 0 else 'Day',
                   'wind_kph' : data['current']['wind_kph'],
                   'humidity' : data['current']['humidity'],
                   'feelslike_c' : data['current']['feelslike_c'],
                   'feelslike_f' : data['current']['feelslike_f']}

        if 'sunny' in weather_info.lower():
            file = 'sunny.mp3'
            return render_template('weather_details.html', info=details, result=file)
        elif 'rain' in weather_info.lower():
            file = 'rain.mp3'
            return render_template('weather_details.html', info=details, result=file)
        elif 'clear' in weather_info.lower():
            file = 'clear.mp3'
            return render_template('weather_details.htm4l', info=details, result=file)
        elif 'snowy' in weather_info.lower():
            file = 'snowy.mp3'
            return render_template('weather_details.html', info=details, result=file)
        elif 'overcast' in weather_info.lower():
            file = 'overcast.mp3'
            return render_template('weather_details.html', info=details, result=file)
        elif 'thunderstorm' in weather_info.lower():
            file = 'thunderstorm.mp3'
            return render_template('weather_details.html', info=details, result=file)
        elif 'mist' in weather_info.lower():
            file = 'mist.mp3'
            return render_template('weather_details.html', info=details, result=file)
        elif 'haze' in weather_info.lower():
            file = 'haze.mp3'
            return render_template('weather_details.html', info=details, result=file)
        elif 'cloudy' in weather_info.lower():
            file = 'cloudy.mp3'
            return render_template('weather_details.html', info=details, result=file)

        return render_template('weather_details.html', info=details)

@app.route('/index/about/')
def about():
    return render_template('about.html')


@app.route('/facelogin/', methods=["GET", "POST"])
def facelogin():
    if request.method == "POST":
        information = ''
        try:
            print('Hey')
            #page_name = 'index'

            # Load faces
            faces = './dataset/*.jpg'
            face = glob.glob(faces)
            for fn in face:
                try_image = face_recognition.load_image_file(f'{fn}')
                print(f'{fn}')
                try_face_encoding = face_recognition.face_encodings(try_image)

                if not try_face_encoding: 
                    print("No face found on the image")
                #return render_template(url_for('index'))

            try_face_encoding = try_face_encoding[0]

            # Array of faces
            known_face_encodings = [
                try_face_encoding,
            ]
            #print(len(known_face_encodings))
            face_locations = []
            face_encodings = []
            process_this_frame = True

            img = request.files.get('image')
            print(type(img))
            imge = img.read()
            nparr = np.frombuffer(imge, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if process_this_frame:
                face_locations = face_recognition.face_locations(img_np)
                face_encodings = face_recognition.face_encodings(
                img_np, face_locations)
                if len(face_encodings) == 0:
                    information = 'No faces found... Please Face Infront of the Camera'
                    return render_template('result.html', message = information)

                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(
                        known_face_encodings, face_encoding)
                    print(matches)
                    if True in matches:
                        first_match_index = matches.index(True)
                        information = 'You were successfully logged in'
                        return render_template('faceloginsuccess.html', name = information)
                        #flash('You were successfully logged in')
                        #return render_template('result.html', message = mesg)
                        #return redirect(url_for('result'))
                    else:
                        information = 'Wrong User Face ID. Please Register'
                        return render_template('result.html', message = information)
                        #return render_template('result.html', message = mesg)
        except:
            return render_template('404.html')
    return render_template('cvlogin.html')

def getImagesAndLabels(path):
    face_detector = cv2.CascadeClassifier('./lbpcascade_frontalface.xml')
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    ids = []

    for imagePath in imagePaths:

        PIL_img = Image.open(imagePath).convert('L')  # convert it to grayscale
        print(type(PIL_img))
        img_numpy = np.array(PIL_img, 'uint8')
        print(type(img_numpy))

        id = os.path.split(imagePath)[-1].split(".")[1]
        print(type(id))
        faces = face_detector.detectMultiScale(img_numpy)

        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y+h, x:x+w])
            ids.append(id)

    return faceSamples, ids

@app.route('/faceregister/', methods=["GET","POST"])
def flogin():
    # function to get the images and label data
    if request.method == "POST":
        face_username = request.form.get('name').lower()
        print(face_username)
        con = sqlite3.connect('loginDetails.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from users")
        rows = cur.fetchall()
        usernames = set()
        for row in rows:
            usernames.add(row["username"])
            #print(usernames)
        if face_username in usernames:
            count = 0
            #print('Hello YO YO')
            img = request.files.get('image')
            print(type(img))
            imge = img.read()
            nparr = np.frombuffer(imge, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            face_detector = cv2.CascadeClassifier('./lbpcascade_frontalface.xml')
            gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
            #print('Gray', type(gray))
            faces = face_detector.detectMultiScale(gray, 1.3, 5)
            if len(faces) == 0:
                msg = 'No faces found... Please Face Infront of the Camera'
                return render_template('result.html', mesg = msg)
            for (x, y, w, h) in faces:
                while count < 5:
                    count += 1
                        # Save the captured image into the dataset folder
                    cv2.imwrite("dataset/User." + face_username + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
                print(count)
                if count == 5:
                    msg = "Photo Dataset Created... Please Press Home Button"
                    return render_template("result.html", mesg = msg)
                else:
                    msg = "Couldn't get Data.Please Capture Again"
                    return render_template("result.html", mesg = msg)
        else:
            return redirect(url_for('index'))
            #return render_template('index.html')

    return render_template('download.html')


@app.route('/result/')
def result():
    return render_template('result.html')

@app.errorhandler(404)
def page_not_found(e):
    #flash(404)
    return render_template('404.html')


if __name__ == "__main__":
    #port = int(os.getenv('PORT', 5000))
    app.secret_key = 'super123'
    app.config['SESSION_TYPE'] = 'filesystem'

    #sess.init_app(app)

    #print ("Starting app on port %d" %(port))

    app.run(debug=True)
    #port=port, host='0.0.0.0')
