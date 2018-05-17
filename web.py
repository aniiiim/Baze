#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

# odkomentiraj, če želiš sporočila o napakah
# debug(True)
static_dir = "./static"

##@route("/static/<filename:path>")
##def static(filename):
##    """Splošna funkcija, ki servira vse statične datoteke iz naslova
##       /static/..."""
##    return static_file(filename, root=static_dir)

@get("/css/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="./static/css")

@get("/fonts/<filepath:re:.*\.(eot|otf|svg|ttf|woff|woff2?)>")
def font(filepath):
    return static_file(filepath, root="static/fonts")

@get("/images/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    return static_file(filepath, root="static/images")

@get("/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="static/js")

@get("/sass/<filepath:re:.*\.scss>")
def sass(filepath):
    return static_file(filepath, root="static/sass")

@get('/books')
def index():
    return template('index.html')

@get('/books/<bookid>/')
def single(bookid):
    return template('single.html')
##
##@get('/transakcije/:x/')
##def transakcije(x):
##    cur.execute("SELECT * FROM transakcija WHERE znesek > %s ORDER BY znesek, id", [int(x)])
##    return template('transakcije.html', x=x, transakcije=cur)
##
##@get('/dodaj_transakcijo')
##def dodaj_transakcijo():
##    return template('dodaj_transakcijo.html', znesek='', racun='', opis='', napaka=None)
##
##@post('/dodaj_transakcijo')
##def dodaj_transakcijo_post():
##    znesek = request.forms.znesek
##    racun = request.forms.racun
##    opis = request.forms.opis
##    try:
##        cur.execute("INSERT INTO transakcija (znesek, racun, opis) VALUES (%s, %s, %s)",
##                    (znesek, racun, opis))
##    except Exception as ex:
##        return template('dodaj_transakcijo.html', znesek=znesek, racun=racun, opis=opis,
##                        napaka = 'Zgodila se je napaka: %s' % ex)
##    redirect("/")

######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080)
