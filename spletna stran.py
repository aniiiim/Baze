#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

# uvozimo ustrezne podatke za povezavo
import   auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

# uvozimo hashlib
import hashlib

# odkomentiraj, če želiš sporočila o napakah
# debug(True)
static_dir = "./static"

# Skrivnost za kodiranje cookijev
secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"

##@route("/static/<filename:path>")
##def static(filename):
##    """Splošna funkcija, ki servira vse statične datoteke iz naslova
##       /static/..."""
##    return static_file(filename, root=static_dir)
##
##@get("/css/<filepath:re:.*\.css>")
##def css(filepath):
##    return static_file(filepath, root="./static/css")
##
##@get("/fonts/<filepath:re:.*\.(eot|otf|svg|ttf|woff|less|css|scss|woff2?)>")
##def font(filepath):
##    return static_file(filepath, root="static/fonts")
##
##@get("/img/<filepath:re:.*\.(jpg|png|PNG|gif|ico|svg)>")
##def img(filepath):
##    return static_file(filepath, root="static/img")
##
##@get("/js/<filepath:re:.*\.js>")
##def js(filepath):
##    return static_file(filepath, root="static/js")
##
##@get("/ico/<filepath:re:.*\.ico>")
##def ico(filepath):
##    return static_file(filepath, root="static/ico")

@route('/static/<filename:path>')
def static(filename):
    """Splošna funkcija, ki servira vse statične datoteke iz naslova
       /static/..."""
    return static_file(filename, root=static_dir)

@route("/")
def main():
    redirect("/books")
    
@get('/books')
def index():
    uporabnik = get_user()
    print(uporabnik)
##    """Vrni dano število knjig (privzeto 9). Rezultat je seznam, katerega
##       elementi so oblike [knjiga_id, avtor,naslov,slika]    """
##    cur.execute("""SELECT (book_id, authors, title, original_publication_year, average_rating,image_url) FROM books ORDER BY average_rating DESC LIMIT %s""", [9])
    seznam=top_9()
    if request.query.logged=="Logout":
        logout()
        redirect("/books")
    return template('index.html',
                    username = uporabnik[1],
                    ime = uporabnik[2],
                    najboljsi=seznam)

@get('/product_details.html')
def podrobnosti():
    uporabnik = get_user()
    if request.query.logged=="Logout":
        logout()
        redirect("/books")
    return template('product_details.html',
                    username = uporabnik[1],
                    ime = uporabnik[2])

@get("/item/<book_id>/")
def item_get(book_id):
    uporabnik = get_user()
    if request.query.logged=="Logout":
        logout()
        redirect("/books")
    cur.execute( ''' SELECT book_id, isbn,  authors, title, original_publication_year, original_title, average_rating,image_url FROM books
         where book_id = %s''',[book_id])
    vse=cur.fetchall()
    print(uporabnik)
  
    return template('product_details.html',
                    vse=vse,
                    username = uporabnik[1],
                    ime = uporabnik[2])

@post("/item/<book_id>/")
def item_post(book_id):
    uporabnik = get_user(auto_login = True)
    cur.execute( ''' SELECT book_id, isbn,  authors, title, original_publication_year, original_title, average_rating,image_url FROM books
         where book_id = %s''',[book_id])
    vse=cur.fetchall()

    cur.execute('''SELECT book_id,authors,title,
                    owner_id,original_publication_year,average_rating,image_url,
                    user_id,username,ime,priimek,email FROM kbooks
                    JOIN uporabnik ON uporabnik.user_id=books.owner_id
                    where book_id = %s''',[book_id])
    item=cur.fetchone()

    wish=request.forms.get("wish")
    if wish is not None:
        cur.execute('''INSERT INTO wish (book_id,isbn,authors,original_publication_year, original_title, title, image_url,user_id)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',[book_id,vse[0][1],vse[0][2],vse[0][4],vse[0][5],vse[0][3],vse[0][7],curuser[0]]) #zapiši transakcijo

    return template("product_details.html",
                    vse=vse,
                    username=None)

@route("/four-col.html")
def main():
    redirect("/all")
@get('/all')
def products():
    query = dict(request.query)
    qstring = str(request.query_string)
    qstring = re.sub('&?page=\d+','', qstring, flags=re.IGNORECASE)
    pagenr = request.query.page or 1
    
    ORstring='''SELECT  authors, title, average_rating, image_url, book_id FROM books
                WHERE 1=1\n'''
    parameters=[]
    try:
        krnekaj= query['search']
    except:
        query['search']=''
    
    if query['search'] != '': 
        ORstring += '''AND (LOWER(title) LIKE LOWER(%s) )'''
        parameters = parameters + ['%'+query['search']+'%']
        print('%'+query['search']+'%')

    ORstring += "ORDER BY title ASC" #po abecednem redu razvrščeni
    cur.execute(ORstring,parameters)
    predmeti=cur.fetchall()
    uporabnik = get_user()
    if request.query.logged=="Logout":
        logout()
        redirect("/books")
    #iz query stringov poberemo vse (filtri in št strani)
    #ta tabela je potrebna zaradi razlicnih koncnic (jpg, png, etc.)
##    cur.execute("SELECT book_id,image_url FROM books WHERE book_id IS NOT NULL ",[[i[0] for i in vse]])
##    slike = cur.fetchall()
##    slike = {i[0]:i[1] for i in slike}
##    %pic = slike[vse[i-1][0]] v templateju
    return template('four-col.html',
                    pagenr= int(pagenr),
                    qstring=qstring,
                    vse=predmeti,
                    username = uporabnik[1],
                    ime = uporabnik[2],
                    query=query)


##@route("/products.html")
##def main():
##    redirect("/zanri/<zanrid>")
    

@get('/zanri/<zanrid>')
def zanri_get(zanrid):
    uporabnik = get_user()
    if request.query.logged=="Logout":
        logout()
        redirect("/books")
    query = dict(request.query)
    qstring = str(request.query_string)
    qstring = re.sub('&?page=\d+','', qstring, flags=re.IGNORECASE)
    pagenr = request.query.page or 1
    cur.execute(''' SELECT s.book_id, s.goodreads_book_id,s.authors, s.title,
                    s.average_rating, s.image_url,
                    r.book_tags_id, r.tag_id,h.tag_name,
                    r.count FROM books AS s
                    INNER JOIN book_tags AS r
                    ON s.goodreads_book_id= r.goodreads_book_id
                    INNER JOIN tags AS h
                    ON r.tag_id=h.tag_id
                    WHERE h.tag_name = %s
                    ORDER BY title ASC''',[zanrid])
    zanri=cur.fetchall()
    ORstring='''SELECT  authors, title, average_rating, image_url, book_id FROM books
                WHERE 1=1\n''' 
    parameters=[]
    try:
        krnekaj= query['search']
    except:
        query['search']=''
    
    if query['search'] != '': 
        ORstring += '''AND (LOWER(title) LIKE LOWER(%s) )'''
        parameters = parameters + ['%'+query['search']+'%']
        print('%'+query['search']+'%')

    ORstring += "ORDER BY title ASC" #po abecednem redu razvrščeni
    cur.execute(ORstring,parameters)
    predmeti=cur.fetchall()
    
    return template('products.html',
                    pagenr= int(pagenr),
                    qstring=qstring,
                    vse=predmeti,
                    zanri=zanri,
                    query=query,
                    username = uporabnik[1],
                    ime = uporabnik[2],)

@route("/login.html")
def main():
    redirect("/login")
@get('/login')
def login():
    uporabnik=get_user()
    if request.query.logged=="Logout":
        logout()
        redirect("/books")
    return template('login.html',
                    username = uporabnik[1],
                    ime = uporabnik[2])

@route("/account.html")
def main():
    redirect("/account")  
@get('/account')
def profil():
    uporabnik=get_user()
    if request.query.logged=="Logout":
        logout()
        redirect("/books")
    return template('account.html',
                    username = uporabnik[1],
                    ime = uporabnik[2],
                    uporabnik = uporabnik)

@route("/contact.html")
def main():
    redirect("/contact")
@get('/contact')
def kontakt():
    return template('contact.html')

@route("/forget_password.html")
def main():
    redirect("/forget_password")
@get('/forget_password')
def geslo():
    return template('forget_password.html')





def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

# Funkcija, ki v cookie spravi sporocilo
def set_sporocilo(tip, vsebina):
    response.set_cookie('message', (tip, vsebina), path='/', secret=secret)

# Funkcija, ki iz cookija dobi sporočilo, če je
def get_sporocilo():
    sporocilo = request.get_cookie('message', default=None, secret=secret)
    response.delete_cookie('message')
    return sporocilo

def get_user(auto_login = False,auto_redir=False):
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Če ni prijavljen, presumeri
       na stran za prijavo ali vrni None (odvisno od auto_login).
    """
    # Dobimo username iz piškotka
    username = request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        cur.execute("SELECT user_id, username, ime, priimek, email FROM uporabnik WHERE username=%s",
                  [username])
        r = cur.fetchone()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return r
    # Če pridemo do sem, uporabnik ni prijavljen, naredimo redirect
    if auto_login:
        redirect('/login/')
    else:
        return [None,None, None, None, None]

def main():
        """Glavna stran."""
    # Iz cookieja dobimo uporabnika (ali ga preusmerimo na login, če
    # nima cookija)
        curuser = get_user()
    # Morebitno sporočilo za uporabnika
        sporocilo = get_sporocilo()
    # Vrnemo predlogo za glavno stran
        return template("index.html",
                        ime=ime,
                        username=username,
                        sporocilo=sporocilo
                        )
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
@get("/login/")
def login_get():
    """Serviraj formo za login."""
    uporabnik = get_user(auto_redir = True)
    return template("login.html", 
                           napaka=None,
                           username=None)

def logout():
    """Pobriši cookie in preusmeri na login."""
    response.delete_cookie('username')
    #redirect('/login/')

@post("/login/")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = request.forms.username
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(request.forms.password)
    # Preverimo, ali se je uporabnik pravilno prijavil
    #c = baza.cursor()
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s AND password=%s",
              [username, password])
    if cur.fetchone() is None:
        # Username in geslo se ne ujemata
        return template("login.html", #template za login
                               napaka="Nepravilna prijava",
                               username=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")

@post("/contact")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = request.forms.username
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(request.forms.password)
    # Preverimo, ali se je uporabnik pravilno prijavil
    #c = baza.cursor()
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s AND password=%s",
              [username, password])
    if cur.fetchone() is None:
        # Username in geslo se ne ujemata
        return template("contact.html", #template za login
                               napaka="Nepravilna prijava",
                               username=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")

@post("/books")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = request.forms.username
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(request.forms.password)
    # Preverimo, ali se je uporabnik pravilno prijavil
    #c = baza.cursor()
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s AND password=%s",
              [username, password])
    if cur.fetchone() is None:
        # Username in geslo se ne ujemata
        return template("index.html", #template za login
                               napaka="Nepravilna prijava",
                               username=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")

@route("/register.html")
def main():
    redirect("/register")

@get("/register")
def login_get():
    """Prikaži formo za registracijo."""
    uporabnik = get_user(auto_redir = True)
    if request.query.logged=="Logout":
        logout()
        redirect("/books")
    return template("register.html",
                    username = uporabnik[1],
                    ime = uporabnik[2],
                    napaka=None)

@get("/contact")
def login_get():
    """Prikaži formo za registracijo."""
    uporabnik = get_user(auto_redir = True)
    if request.query.logged=="Logout":
        logout()
        redirect("/books")
    return template("contact.html",
                    username = uporabnik[1],
                    ime = uporabnik[2],
                    napaka=None)


@post("/register")
def register_post():
    """Registriraj novega uporabnika."""
    username = request.forms.username
    ime = request.forms.ime
    priimek = request.forms.priimek
    email = request.forms.email
    password1 = request.forms.password1
    password2 = request.forms.password2
    uporabnik = get_user(auto_redir = True)
    # Ali uporabnik že obstaja?
    #c = baza.cursor()
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s", [username])
    if cur.fetchone():
        # Uporabnik že obstaja
        return template("register.html",
                               username=username,
                               ime=ime,
                               napaka='To uporabniško ime je že zavzeto.')
    elif not password1 == password2:
        # Gesli se ne ujemata
        return template("register.html",
                               username=username,
                               ime=ime,
                               napaka='Gesli se ne ujemata.')
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        password = password_md5(password1)
        cur.execute("INSERT INTO uporabnik (username, ime, priimek, password, email) VALUES (%s,%s,%s,%s,%s)", 
                  (username, ime, priimek, password, email))
        # Daj uporabniku cookie
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")

def user_change(username):
    """Obdelaj formo za spreminjanje podatkov o uporabniku."""
    # Kdo je prijavljen?
    (username, ime) = get_user()
    # Staro geslo (je obvezno)
    password1 = password_md5(request.forms.password1)
    # Preverimo staro geslo
    cur.execute ("SELECT 1 FROM uporabnik WHERE username=%s AND password=%s",
               [username, password1])
    # Pokazali bomo eno ali več sporočil, ki jih naberemo v seznam
    sporocila = []
    if cur.fetchone():
        # Geslo je ok
        # Ali je treba spremeniti geslo?
        password2 =request.forms.password2
        password3 = request.forms.password3
        if password2 or password3:
            # Preverimo, ali se gesli ujemata
            if password2 == password3:
                # Vstavimo v bazo novo geslo
                password2 = password_md5(password2)
                cur.execute ("UPDATE uporabnik SET password=%s WHERE username =%s", [password2, username])
                sporocila.append(("alert-success", "Spremenili ste geslo."))
            else:
                sporocila.append(("alert-danger", "Gesli se ne ujemata."))
    else:
        # Geslo ni ok
        sporocila.append(("alert-danger", "Napačno staro geslo."))
    cur.close ()
    # Prikažemo stran z uporabnikom, z danimi sporočili. Kot vidimo,
    # lahko kar pokličemo funkcijo, ki servira tako stran
    #return user_wall(username, sporocila=sporocila)

def top_9(limit=21):
    """Vrni dano število knjig (privzeto 9). Rezultat je seznam, katerega
       elementi so oblike [knjiga_id, avtor,naslov,slika]    """
    cur.execute(
    """SELECT book_id, authors, title, original_publication_year, average_rating,image_url
       FROM books 
       ORDER BY average_rating DESC
       LIMIT %s
    """, [limit])
    najboljsi = cur.fetchall()
##    # Rezultat predelamo v nabor.
####    top_10 = tuple(cur)
####    # Nabor id-jev knjig, ki jih bomo vrnili
####    tids = (top[0] for top in top_10)
####    # Sedaj prenesemo rezultate poizvedbe v slovar
####    for (tid, username, ime, vsebina) in c:
####        komentar[tid].append((username, ime, vsebina))
####    c.close()
##    # Vrnemo nabor, kot je opisano v dokumentaciji funkcije:
    return(najboljsi)

######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080)
