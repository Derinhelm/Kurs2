def dbInsertWord(con, w, cursor):
    # возвращает индекс, вставленного слова
    cursor.execute('INSERT INTO word VALUES(DEFAULT,%s) RETURNING id;', (w,))
    con.commit()
    ind = cursor.fetchall()
    return ind[0][0]


def dbInsertMorph(con, m, cursor):
    # возвращает индекс, вставленного морфа
    command = 'INSERT INTO morph_constraints' \
              ' VALUES(DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;'
    params = (m.s_cl, m.animate, m.gender, m.number,
              m.case_morph, m.reflection, m.perfective, m.transitive,
              m.person, m.tense, m.voice, m.degree, m.static, m.prep_type)
    cursor.execute(command, params)
    con.commit()
    ind = cursor.fetchall()
    return ind[0][0]


def dbFindMorph(con, m, cursor):
    # здесь ответ - одно индекс !! Морфы все должны быть различны!!
    command = "SELECT id FROM morph_constraints WHERE " + \
              "s_cl = %s AND " + \
              "animate = %s AND " + \
              "gender = %s AND " + \
              "number = %s AND " + \
              "case_morph = %s AND " + \
              "reflection = %s AND " + \
              "perfective = %s AND " + \
              "transitive = %s AND " + \
              "person = %s AND " + \
              "tense = %s AND " + \
              "voice = %s AND " + \
              "degree = %s AND " + \
              "static = %s AND " \
              "prep_type = %s;"
    params = (m.s_cl, m.animate, m.gender, m.number,
              m.case_morph, m.reflection, m.perfective, m.transitive,
              m.person, m.tense, m.voice, m.degree, m.static, m.prep_type)
    cursor.execute(command, params)
    ans = []
    for row in cursor:
        ans.append(row[0])
    if len(ans) == 0:
        return None  # нет такого морфа
    if len(ans) > 1:
        print("ОШИБКА: в базе есть два одинаковых морфа")
        return None
    else:
        return ans[0]


def dbFindWord(con, w, cursor):
    command = "SELECT id FROM word WHERE " + \
              "name = %s;"
    params = (w,)
    cursor.execute(command, params)
    ans = []
    for row in cursor:
        ans.append(row[0])
    if len(ans) == 0:
        return None  # нет такого морфа
    return ans[0]


def findOrInsertMorph(con, m, cursor):
    res = dbFindMorph(con, m, cursor)
    if res:
        return res
    res = dbInsertMorph(con, m, cursor)
    return res


def findOrInsertWord(con, m, cursor):
    res = dbFindWord(con, m, cursor)
    if res:
        return res
    res = dbInsertWord(con, m, cursor)
    return res
