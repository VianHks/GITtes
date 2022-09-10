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
frmtdtenow=dt_string = frmtdtenow.strftime("%d-%m-%Y %H:%M:%S")

class user(db.Model):
    usrid=db.Column(db.Integer, primary_key=True, index=True)
    usrname=db.Column(db.String(50), nullable=False,unique=True)
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

class lkspostby(db.Model):
    idlksby=db.Column(db.Integer, primary_key=True, index=True)
    idposting=db.Column(db.Integer, db.ForeignKey('posting.idposting'), nullable=False)
    likeby=db.Column(db.Integer, nullable=True)

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
    isipost = data['isipost']
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
#LIKE POSTING
@app.route('/lks/', methods=['POST'])
def likes_posting():
    data = request.get_json()
    lksby = lkspostby(
    idposting=data['idposting'],
    likeby=data['usrid']
    )
    
    try:
        db.session.add(lksby)
        db.session.commit()
    except:
        return {
            "Message": "Gagal Menyukai Postingan"
        }, 400
    return {
        "Message": "Menyukai Postingan Berhasil"
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
#DELETE USER
@app.route('/usrdlte/<id>', methods=['DELETE'])
def dlte_usr(id):
    parsed = BasicAuth()
    username = parsed[0]
    password= parsed[1]
    
    cek=user.query.filter_by(usrname=username).first()
    
    if str(cek.usrid)==id:


        try:
            b=db.engine.execute('SELECT * FROM public.follower WHERE usrid='+str(id)+'AND apprvl=1')
            for z in b:
                flwr = follower.query.filter_by(idfollower=z[0]).first()
                db.session.delete(flwr)
                db.session.commit()

            c=db.engine.execute('SELECT * FROM public.follower WHERE followerid='+str(id)+'AND apprvl=1')
            for i in c:
                flwing= follower.query.filter_by(idfollower=i[0]).first()
                db.session.delete(flwing)
                db.session.commit()

        #dlte likesby dan posting per user    
            a=db.engine.execute('SELECT a.idposting,a.usrid,b.idlksby FROM public.posting as a,public.lkspostby as b WHERE b.idposting=a.idposting AND a.usrid='+str(id)+'')
            for j in a:
        
                ceklksby=lkspostby.query.filter_by(idlksby=j[2]).first()
                db.session.delete(ceklksby)
                db.session.commit()

            e=db.engine.execute('SELECT * FROM public.lkspostby WHERE likeby='+str(id)+'')
            for l in e:
            # return str(i[0])
            
                lkbydel=lkspostby.query.filter_by(idlksby=l[0]).first()
                db.session.delete(lkbydel)
                db.session.commit()

            d=db.engine.execute('SELECT * FROM public.posting WHERE usrid='+id+'')
            for k in d:
                psting = posting.query.filter_by(idposting=k[0]).first()
                db.session.delete(psting)
                db.session.commit()

            usr = user.query.filter_by(usrid=id).first()
            db.session.delete(usr)
            db.session.commit()
    
        except:
    
            return {
                "Message": "Hapus User Belum Berhasil"
            }, 500
        return {
            "Message": "Hapus User Berhasil"
        }, 201
    else:
        return {
            "Message": "User ID tidak sesuai Request Delete"
        }, 401
#UNLIKE POSTING
@app.route('/unlkepost/<idpost>/<id>', methods=['DELETE'])
def unlike_psting(idpost,id):
    
    try:
        lksby = lkspostby.query.filter_by(idposting=idpost).filter_by(likeby=id).first()
        db.session.delete(lksby)
        db.session.commit()
    except:
    
        return {
            "Message": "Gagal Unlike Post"
        }, 500
    return {
        "Message": "Unlike Post Berhasil"
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

#DELETE POSTING
@app.route('/postdel/<idpost>', methods=['DELETE'])
def dlte_psting(idpost):
    parsed = BasicAuth()
    username = parsed[0]
    password= parsed[1]
    
    cek=user.query.filter_by(usrname=username).first()
    cekusrpost = posting.query.filter_by(idposting=idpost).first()
    if str(cek.usrid)==str(cekusrpost.usrid):
        
        try:
        
            lkby = lkspostby.query.filter_by(idposting=idpost).all()

            for i in lkby:
                dlte=lkspostby.query.filter_by(idlksby=i.idlksby).first()
                db.session.delete(dlte)
                db.session.commit()
    
            psting = posting.query.filter_by(idposting=idpost).first()
            db.session.delete(psting)
            db.session.commit()
        except:
    
            return {
                "Message": "Gagal Hapus Postingan"
            }, 500
        return {
            "Message": "Hapus Postingan Berhasil"
        }, 201
    else:
        return {
            "Message": "Silahkan Cek Username & Pass (User Tidak Sesuai)!!"
        }
#UPDATE DATA USER
@app.route('/usr/<id>', methods=['PUT'])
def update_usr(id):
    parsed = BasicAuth()
    username = parsed[0]
    password= parsed[1]
    
    cek=user.query.filter_by(usrname=username).first()
    
    if str(cek.usrid)==id:
        data  = request.get_json()
        usr = user.query.filter_by(usrid=id).first()
        usr.password = data['password']
        usr.nickname = data['nickname']

        try:
            db.session.commit()
        except:
            return {
            "Message": "Update data failed"
            }, 400
        return {
            "Message": "Update data success"
        }, 201
    else:
         return {
            "Message": "Update Gagal,Silahkan Cek Username / Password"
            },401

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
@app.route('/getlksby/<id>', methods=['GET'])
def get_likesby(id):
    a=db.engine.execute('SELECT * FROM public.lkspostby WHERE idposting='+id+'')
    arr=[]
    for i in a:
        usrnick = user.query.filter_by(usrid=i[2]).first()
        arr.append({'usrid':i[2],'NickName':usrnick.nickname})
    
    return jsonify(arr)

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

#GET POPULAR USER
@app.route('/popusr/', methods=['GET'])
def get_mostpopusr():
    a=db.engine.execute('SELECT * FROM(SELECT usrid as id,COUNT(usrid) as id_count FROM public.follower GROUP BY usrid)t ORDER BY id_count desc limit 1')
    arr=[]
    for i in a:
        ncknme = user.query.filter_by(usrid=i[0]).first()
        
        arr.append({'usrid':i[0],'Nickname':str(ncknme.nickname),'Followers':i[1]})
    return jsonify(arr)

#GET POPULAR TWEET
@app.route('/poptweet/', methods=['GET'])
def get_mostpoptweet():
    a=db.engine.execute('SELECT * FROM(SELECT idposting as id,COUNT(idposting) as post_count FROM public.lkspostby GROUP BY idposting)t ORDER BY post_count desc limit 1')
    arr=[]
    for i in a:
        postnme = posting.query.filter_by(idposting=i[0]).first()
        
        arr.append({'idposting':i[0],'IsiPost':str(postnme.isipost),'LikesCount':i[1]})
    return jsonify(arr)

#GET POPULAR TWEET
@app.route('/ppstwit/', methods=['GET'])
def get_mstpoptwit():
    a=db.engine.execute('SELECT * FROM(SELECT idposting as id,COUNT(idposting) as post_count FROM public.lkspostby GROUP BY idposting)t ORDER BY post_count desc limit 1')
    arr=[]
    for i in a:
        postnme = posting.query.filter_by(idposting=i[0]).first()
        
        arr.append({'idposting':i[0],'IsiPost':str(postnme.isipost),'LikesCount':i[1]})
    return jsonify(arr)

#GET INACTIVE USER
@app.route('/inctveuser/', methods=['GET'])
def get_invctveusr():
    cekdte=db.engine.execute('SELECT * FROM public.user')
    arr=[]
    for i in cekdte:
        day_off=datetime.now()-i[4]
        if day_off.days>60:
            arr.append({'usrid':i[0],'LastLogin':i[4],'LamaHari':day_off.days})
    
    return jsonify(arr)

    
