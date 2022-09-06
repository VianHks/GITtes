from itertools import count
from select import select
from sqlite3 import Date
from turtle import pos
from flask import Flask, jsonify,request
from flask_sqlalchemy import SQLAlchemy
import base64
from datetime import datetime


app = Flask(__name__)
db = SQLAlchemy(app)

# app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:jaberwar@localhost:5432/SocMed?sslmode=disable'

frmtdtenow=datetime.now()
frmtdtenow=dt_string = frmtdtenow.strftime("%d/%m/%Y %H:%M:%S")

class user(db.Model):
    usrid=db.Column(db.Integer, primary_key=True, index=True)
    usrname=db.Column(db.String(50), nullable=False)
    password=db.Column(db.String(50), nullable=False)
    nickname=db.Column(db.String(50), nullable=False)
    lastlogin=db.Column(db.DateTime,nullable=False)
    crtdate=db.Column(db.DateTime,nullable=False)
    stsusr=db.Column(db.String(50), nullable=False)

class follower(db.Model):
    idfollower=db.Column(db.Integer, primary_key=True, index=True)
    usrid=db.Column(db.Integer, db.ForeignKey('user.usrid'), nullable=False)
    followerid=db.Column(db.Integer, db.ForeignKey('user.usrid'), nullable=False)
    apprvl=db.Column(db.Integer, nullable=False)

class posting(db.Model):
    idposting=db.Column(db.Integer, primary_key=True, index=True)
    usrid=db.Column(db.Integer, db.ForeignKey('user.usrid'), nullable=False)
    postdate=db.Column(db.DateTime,nullable=False)
    isipost=db.Column(db.String(280), nullable=False)
    likeby=db.Column(db.String(1000), nullable=True)


db.create_all()
db.session.commit()

def BasicAuth() :
    pass_str = request.headers.get('Authorization')     #untuk mengambil authorization di postman
    pass_bersih = pass_str.replace('Basic ',"")         #untuk memotong "basic" (pada value authorization)
    hasil_decode = base64.b64decode(pass_bersih)        #untuk merubah password (decode) "dGVzbWlrOnRlczEyMw==" menjadi "tes123" (base64.b64code merupakan package fungsi dari python)
    hasil_decode_bersih = hasil_decode.decode('utf-8')  #untuk membuang "b" pada hasil_decode (.decode('utf-8))
    username_aja = hasil_decode_bersih.split(":")[0]    #untuk slicing apabila ingin menampilkan username saja (username:)
    pass_aja = hasil_decode_bersih.split(":")[1]        #untuk slicing apabila ingin menampilkan pass saja (:password)
    return[username_aja,pass_aja]


#CREATE USER
@app.route('/usr/', methods=['POST'])
def create_usr():
    
    data = request.get_json()
    usr = user(
    usrname=data['usrname'],
    password=data['password'],
    nickname = data['nickname'],
    lastlogin=frmtdtenow,
    crtdate=frmtdtenow,
    stsusr="Aktif"
    )
    try:
        db.session.add(usr)
        db.session.commit()
    except:
        return {
            "Message": "Simpan Belum Berhasil"
        }, 400
    return {
        "Message": "Simpan Data User Berhasil"
    }, 201

#POSTING
@app.route('/post/', methods=['POST'])
def create_posting():
    
    data = request.get_json()
    post = posting(
    usrid=data['usrid'],
    postdate=frmtdtenow,
    isipost = data['isipost'],
    likeby=0
    )
    try:
        db.session.add(post)
        db.session.commit()
    except:
        return {
            "Message": "Posting Belum Berhasil"
        }, 400
    return {
        "Message": "Posting Berhasil"
    }, 201

#FOLLOW A USER
@app.route('/flwr/', methods=['POST'])
def create_flwr():
    
    data = request.get_json()
    flwr = follower(
    usrid=data['usrid'],
    followerid=data['followerid'],
    apprvl = 0
    )
    try:
        db.session.add(flwr)
        db.session.commit()
    except:
        return {
            "Message": "Gagal Mengikuti"
        }, 400
    return {
        "Message": "Mengikuti"
    }, 201

#UNFOLLOW USER
@app.route('/fldlte/<id>/<fl>', methods=['DELETE'])
def dlte_flwr(id,fl):
    try:
        flwr = follower.query.filter_by(usrid=id).filter_by(followerid=fl).first()
        db.session.delete(flwr)
        db.session.commit()
    except:
    
        return {
            "Message": "Gagal Unfollow"
        }, 500
    return {
        "Message": "Unfollow Berhasil"
    }, 201


#UPDATE DATA USER
@app.route('/usr/<id>', methods=['PUT'])
def update_usr(id):
    data  = request.get_json()
    usr = user.query.filter_by(usrid=id).first()
    usr.password = data['password']
    usr.nickname = data['nickname']

    try:
        db.session.commit()
    except:
        return {
            "Message": "update data failed"
        }, 400
    return {
        "Message": "update data success"
    }, 201

#LIKE POSTING
@app.route('/lks/<id>', methods=['PUT'])
def update_like(id):
    data  = request.get_json()
    post = posting.query.filter_by(idposting=id).first()
    
    if post.likeby==0:
        post.likeby = data['usrid']
    else:
        post.likeby = post.likeby + ',' + data['usrid']

    try:
        db.session.commit()
    except:
    
        return {
            "Message": "Like Posting Gagal"
        }, 400
    return {
        "Message": "Like Posting Sukses"
    }, 201

#GET FOLLOWER FROM USER
@app.route('/getflwr/<id>', methods=['GET'])
def get_flwr(id):
    flwr = follower.query.filter_by(usrid=id).filter_by(apprvl=1).all()
    arr=[]
    listname=[]
    for i in flwr:
        # arr.append(i['followerid'])
        arr.append(i.followerid)
    # return arr
    for j in arr:
        ceknme = user.query.filter_by(usrid=j).first()
        listname.append(ceknme.nickname)
    
    return listname

#GET USER FOLLOWING
@app.route('/getflwing/<id>', methods=['GET'])
def get_flwing(id):
    a=db.engine.execute('SELECT a.usrid,a.usrname,a.nickname,b.followerid,b.apprvl FROM public.user as a,public.follower as b WHERE a.usrid=b.usrid AND followerid='+str(id)+' AND apprvl=1')
    arr=[]
    for i in a:
        
        arr.append({'usrid':i[0],'Nickname':i[2]})
    return jsonify(arr)

#GET USER PROFILE
@app.route('/getusr', methods=['GET'])
def get_usr():
    a=db.engine.execute('SELECT usrid,usrname,nickname,lastlogin FROM public.user')
    
    arr=[]
    for i in a:
        flwr = follower.query.filter_by(usrid=i[0]).filter_by(apprvl=1).count()
        flwing=follower.query.filter_by(followerid=i[0]).filter_by(apprvl=1).count()
        arr.append({'usrid':i[0],'Nickname':i[2],'LastLogin':i[3],'Follower':flwr,'Following':flwing})

    return jsonify(arr)

#GET POSTING LIKE BY    
@app.route('/lksby/<id>', methods=['GET'])
def get_likesby(id):
    post = posting.query.filter_by(idposting=id).first()
    arr=[]
    arr=post.likeby
    likeby=[]
    # # return arr
    for i in range(len(arr)):
        if arr[i]!=',':
            nicknme = user.query.filter_by(usrid=arr[i]).first()
            likeby.append(nicknme.nickname)
    return likeby

#SEARCH TWEET
@app.route('/tweetsearch', methods=['POST'])
def search_tweet():
	
    data = request.get_json()
    p = posting.query.filter(posting.isipost.ilike('%' + data['Posting'] + '%')).all()
    arr=[]
    for i in p:
        arr.append({'idposting':i.idposting,'usrid':i.usrid,'IsiTweet':i.isipost})


    return jsonify(arr)

#GET LIST TWEET
@app.route('/gettweet/<id>', methods=['GET'])
def list_tweet(id):
    post = posting.query.filter_by(usrid=id).all()
    arr=[]
    for i in post:
        arr.append({'idposting':i.idposting,'Tweet':i.isipost})


    return jsonify(arr)