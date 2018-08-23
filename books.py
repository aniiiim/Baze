# uvozimo ustrezne podatke za povezavo


import auth
auth.db = "sem2018_%s" % auth.user

##import auth
##auth.db = "sem2018_anamarijam" #% auth.user

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_books():
    cur.execute("""
        CREATE TABLE books (
            book_id SERIAL PRIMARY KEY,
            goodreads_book_id NUMERIC NOT NULL,
            best_book_id NUMERIC NOT NULL,
            work_id NUMERIC NOT NULL,
            books_count NUMERIC NOT NULL,
            isbn TEXT,
            isbn_13 TEXT,
            authors TEXT NOT NULL,
            original_publication_year NUMERIC,
            original_title TEXT,
            title TEXT NOT NULL,
            language_code TEXT,
            average_rating NUMERIC NOT NULL,
            ratings_count NUMERIC NOT NULL,
            work_ratings_count NUMERIC NOT NULL,
            work_text_reviews_count NUMERIC NOT NULL,
            ratings_1 NUMERIC,
            ratings_2 NUMERIC,
            ratings_3 NUMERIC,
            ratings_4 NUMERIC,
            ratings_5 NUMERIC,
            image_url TEXT,
            small_image_url TEXT
            );
            """)
    conn.commit()

def ustvari_wish():
    cur.execute("""
        CREATE TABLE wish(
        book_id INTEGER REFERENCES books(book_id),
        isbn TEXT,
        authors TEXT,
        original_publication_year NUMERIC,
        original_title TEXT,
        title TEXT,
        image_url TEXT ,
        user_id INTEGER 
        );
        """)
    conn.commit()
  
def ustvari_tabelo():
    cur.execute("""
            CREATE TABLE ratings (
            user_id NUMERIC,
            book_id INTEGER REFERENCES books(book_id),
            rating NUMERIC NOT NULL
            );

            CREATE TABLE to_read (
            user_id NUMERIC,
            book_id INTEGER REFERENCES books(book_id)
            );
            
            CREATE TABLE tags (
            tag_id SERIAL PRIMARY KEY,
            tag_name TEXT
            );

    """)
    conn.commit()

def ustvari_uporabnik():
    cur.execute ("""
       CREATE TABLE uporabnik (
            user_id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            ime TEXT NOT NULL,
            priimek TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL
            );
      """ )
    conn.commit()


def ustvari_book_tags():
    cur.execute ("""
       CREATE TABLE book_tags (
            goodreads_book_id NUMERIC,
            tag_id INTEGER NOT NULL REFERENCES tags(tag_id),
            count INTEGER
            );
      """ )
    conn.commit()
# ALTER TABLE book_tags
# ADD book_tags_id SERIAL PRIMARY KEY;
def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE IF EXISTS ratings CASCADE;
        DROP TABLE IF EXISTS to_read CASCADE;
        DROP TABLE IF EXISTS tags CASCADE;
    """)
    conn.commit()
def pobrisi_books():
    cur.execute ("""
       DROP TABLE IF EXISTS books CASCADE;
      """ )
    conn.commit()

def pobrisi_wish():
    cur.execute ("""
    DROP TABLE IF EXISTS wish CASCADE;
    """ )
    conn.commit()
    
def pobrisi_uporabnik():
    cur.execute ("""
       DROP TABLE IF EXISTS uporabnik CASCADE;
      """ )
    conn.commit()
def pobrisi_book_tags():
    cur.execute ("""
       DROP TABLE IF EXISTS book_tags CASCADE;
      """ )
    conn.commit()

def uvozi_podatke():
    with open("books.csv", encoding="UTF-8") as f:
        rd= csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            try:
                r = [None if x in ('', '-') else x for x in r]
                r= r[1:(len(r))]
                cur.execute("""
                    INSERT INTO books
                    (goodreads_book_id,best_book_id, work_id, books_count, isbn, isbn_13, authors, original_publication_year, original_title, title, language_code, average_rating,ratings_count,work_ratings_count,work_text_reviews_count, ratings_1, ratings_2, ratings_3, ratings_4, ratings_5, image_url, small_image_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s)
                    RETURNING book_id
                """, r)
                rid, = cur.fetchone()
            except Exception as ex:
                print('Napaka:',r)
                raise ex
    conn.commit()
def uvozi_knjige():
    with open("books.csv", encoding="UTF-8") as f:
        rd= csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            try:
                r = [None if x in ('', '-') else x for x in r]
                r= r[1:(len(r))]
                cur.execute("""
                    INSERT INTO knjige
                    (goodreads_book_id,best_book_id, work_id, books_count, isbn, isbn_13, authors, original_publication_year, original_title, title, language_code, average_rating,ratings_count,work_ratings_count,work_text_reviews_count, ratings_1, ratings_2, ratings_3, ratings_4, ratings_5, image_url, small_image_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s)
                    RETURNING book_id
                """, r)
                rid, = cur.fetchone()
            except Exception as ex:
                print('Napaka:',r)
                raise ex
    conn.commit()
def uvozi_ratings():
    with open("ratings.csv", encoding="UTF-8") as f:
        #rd = UnicodeReader(f)
        rd= csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            try:
                r = [None if x in ('', '-') else x for x in r]
                r= r[1:(len(r))]
                #print( r,len(r))
                cur.execute("""
                    INSERT INTO ratings
                    (book_id,rating)
                    VALUES (%s, %s)
                    RETURNING user_id
                """, r)
                rid, = cur.fetchone()
            except Exception as ex:
                print('Napaka:',r)
                raise ex
    conn.commit()

def uvozi_to_read():
    with open("to_read.csv", encoding="UTF-8") as f:
        #rd = UnicodeReader(f)
        rd= csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        i=0
        for r in rd:
            i=i+1
            try:
                r = [None if x in ('', '-') else x for x in r]
                r= r[1:(len(r))]
                #print( r,len(r))
                cur.execute("""
                    INSERT INTO to_read
                    (user_id)
                    VALUES (%s)
                    RETURNING book_id
                """, r)
                rid, = cur.fetchone()
            except Exception as ex:
                print('Napaka:',r,i)
                raise ex
    conn.commit()

def uvozi_book_tags():
    with open("book_tags.csv", encoding="UTF-8") as f:
        #rd = UnicodeReader(f)
        rd= csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        i=0
        for r in rd:
            i=i+1
            try:
                r = [ None if x in ('', '-') else x for x in r]
                r= r[1:(len(r))]
                #print( r,len(r))
                cur.execute("""
                    INSERT INTO book_tags
                    (tag_id, count)
                    VALUES (%s,%s)
                    RETURNING goodreads_book_id
                """, r)
                rid, = cur.fetchone()
            except Exception as ex:
                print('Napaka:',r,i)
                raise ex
    conn.commit()
    
def pravice():
    cur.execute("""
        GRANT ALL ON ALL TABLES IN SCHEMA public TO tejar WITH GRANT OPTION;
        GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO tejar WITH GRANT OPTION;
        GRANT CONNECT ON DATABASE sem2018_anamarijam TO tejar WITH GRANT OPTION;
        GRANT ALL ON ALL TABLES IN SCHEMA public TO katarinak WITH GRANT OPTION;
        GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO katarinak WITH GRANT OPTION;
        GRANT CONNECT ON DATABASE sem2018_anamarijam TO katarinak WITH GRANT OPTION;
        GRANT ALL ON SCHEMA public TO katarinak;
        GRANT ALL ON SCHEMA public TO tejar;
        GRANT CONNECT ON DATABASE sem2018_anamarijam TO javnost;
        GRANT ALL ON SCHEMA public TO javnost;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;
    """)
    conn.commit()

#od baze ze odvežeš conn.close()

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
