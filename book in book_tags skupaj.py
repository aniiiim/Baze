CREATE TABLE poskus(
    bookid SERIAL PRIMARY KEY,
    goodreadsbook NUMERIC NOT NULL)

INSERT INTO poskus VALUES (1,2)
INSERT INTO poskus VALUES (2,3)
INSERT INTO poskus VALUES (3,4)
INSERT INTO poskus VALUES (4,1)


CREATE TABLE poskus2(
    booktags SERIAL PRIMARY KEY,
    goodreadsbook NUMERIC NOT NULL,
    tagid INTEGER NOT NULL,
    count INTEGER)

INSERT INTO poskus2 VALUES (1,1,30574,167697)
INSERT INTO poskus2 VALUES (2,1,11305,37174)
INSERT INTO poskus2 VALUES (3,2,11557,34173)
INSERT INTO poskus2 VALUES (4,2,8717,12986)
INSERT INTO poskus2 VALUES (5,3,33114,12716)
INSERT INTO poskus2 VALUES (6,4,11743,9954)
INSERT INTO poskus2 VALUES (7,4,14017,7169)

CREATE VIEW skupaj AS
SELECT poskus.bookid, poskus.goodreadsbook,
poskus2.booktags, poskus2.tagid, poskus2.count
FROM poskus
INNER JOIN poskus2
ON poskus.goodreadsbook = poskus2.goodreadsbook
ORDER BY booktags ASC


DROP TABLE IF EXISTS poskus CASCADE
DROP TABLE IF EXISTS poskus2 CASCADE
DROP VIEW IF EXISTS skupaj CASCADE

