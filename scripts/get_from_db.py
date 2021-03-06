#!/usr/bin/env python2
from base64 import b64decode
import pymysql.cursors
import pymysql
import sys

connection = pymysql.connect(host='localhost', user='root', db='its-ques', password='')
assert(len(sys.argv) >= 3)
labNo = sys.argv[1] # 'LAB-8'
queNo = 2
probId = sys.argv[2] # '2143'

try:
    with connection.cursor() as cursor:
        sql2 = """
        SELECT code_id, user_id, contents FROM code as C JOIN
          (SELECT code_id, verdict FROM evaluation as E JOIN
            (SELECT id, score FROM assignment as A)
           WHERE assignment_id IN
             (SELECT id FROM assignment
              WHERE event_name = "{0}"
              AND question = {1})
           GROUP BY code_id
           HAVING count(distinct verdict)=1 AND verdict="ACCEPTED") as A
        ON A.code_id = C.id;
       """.format(labNo, queNo)
        sql1 = """
            select c.id, c.user_id, c.contents, a.score, e.verdict
            from code c, evaluation e, assignment a
            where ((c.id = e.code_id) and (e.assignment_id = a.id) and
                   (a.event_name = "{0}" and a.question = "{1}")   and
                   (a.score is not NULL));
        """.format(labNo, queNo)
        sql = """
             ( select c.id, c.user_id, c.contents, a.score
            from code c, assignment a
            where ((c.id = a.submission) and
                   (a.event_name = "{0}" and a.problem_id = {1}) and
                   (a.score is not NULL))
            group by c.id );
        """.format(labNo, probId)
        cursor.execute(sql)
        result = cursor.fetchall()
        with open('output-{}-{}.csv'.format(labNo, probId), 'w') as f:
            cnt = 0
            for r in result:
                cnt+=1
                f.write(','.join([str(a) for a in r]))
                f.write('\n')
            print("Result: " + str(cnt) + " rows.")
except Exception as e:
    print(str(e))
finally:
    connection.close()
