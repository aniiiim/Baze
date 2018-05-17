# uvozimo ustrezne podatke za povezavo

import auth
auth.db = "sem2018_anamarijam" #% auth.user

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

def ustvari_tabelo():
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
            original_publication_year NUMERIC NOT NULL,
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

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE IF EXISTS books CASCADE;
    """)
    conn.commit()

def uvozi_podatke():
    with open("books.csv") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            r = [None if x in ('', '-') else x for x in r]
            cur.execute("""
                INSERT INTO books
                (goodreads_book_id,best_book_id, work_id, books_count, isbn, isbn_13, authors, original_publication_year, original_title, title, language_code, average_rating,ratings_count,work_ratings_count,work_text_reviews_count, ratings_1, ratings_2, ratings_3, ratings_4, ratings_5, image_url, small_image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s)
                RETURNING books_id
            """, r)
            rid, = cur.fetchone()
            print("Uvožena books %s z ID-jem %d" % (r[0], rid))
    conn.commit()
    
def pravice():
    cur.execute("""
        GRANT ALL ON ALL TABLES IN SCHEMA public TO tejar;
        GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO tejar;
        GRANT CONNECT ON DATABASE sem2018_anamarijam TO tejar;
        GRANT ALL ON ALL TABLES IN SCHEMA public TO katarinak;
        GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO katarinak;
        GRANT CONNECT ON DATABASE sem2018_anamarijam TO katarinak;
        GRANT ALL ON SCHEMA public TO katarinak;
        GRANT ALL ON SCHEMA public TO tejar;
        GRANT ALL ON SCHEMA public TO javnost;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;
    """)
    conn.commit()


##def prebivalci(stevilo):
##    cur.execute("""
##        SELECT * FROM obcina
##        WHERE prebivalstvo >= %s
##    """,[stevilo])
##    return cur.fetchall()
##    for r in cur:
##        print(r["ime"])
        #namesto returna lahko tud z for zanko

#od baze ze odvežeš conn.close()

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
