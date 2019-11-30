def dbInsertWord(con, w):
# возвращает индекс, вставленного слова
    cursor = con.cursor()
    cursor.execute('INSERT INTO word VALUES(DEFAULT,%s) RETURNING id;', (w,))
    con.commit()
    ind = cursor.fetchall()
    cursor.close()
    return [ind[0][0]]
    
def dbInsertMorph(con, m):
# возвращает индекс, вставленного морфа
    cursor = con.cursor()
    comand = 'INSERT INTO morph_constraints VALUES(DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;'
    params = (m.s_cl, m.animate,m.gender, m.number, \
        m.case_morph, m.reflection, m.perfective, m.transitive, \
        m.person, m.tense, m.voice, m.degree, m.static)
    cursor.execute(comand, params)
    con.commit()
    ind = cursor.fetchall()
    cursor.close()
    return [ind[0][0]]
    
def dbFindMorph(con, m):
# здесь ответ - одно индекс !! Морфы все должны быть различны!!
    cursor = con.cursor()
    comand = "SELECT id FROM morph_constraints WHERE " + \
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
        "static = %s;"
    params = (m.s_cl, m.animate,m.gender, m.number, \
        m.case_morph, m.reflection, m.perfective, m.transitive, \
        m.person, m.tense, m.voice, m.degree, m.static)
    cursor.execute(comand, params)
    ans = []
    for row in cursor:
        ans.append(row[0])
    cursor.close()
    if len(ans) == 0:
        return None # нет такого морфа
    if len(ans) > 1:
        print("ОШИБКА: в базе есть два одинаковых морфа")
        return None
    else:
        return [ans[0]]
    
def dbFindWord(con, w):
# здесь ответ - может быть несколько разных номеров у одного слова
# на всякий случай для семантики
    cursor = con.cursor()
    comand = "SELECT id FROM word WHERE " + \
        "name = %s;"
    params = (w,)
    cursor.execute(comand, params)
    ans = []
    for row in cursor:
        ans.append(row[0])
    cursor.close()
    if len(ans) == 0:
        return None # нет такого морфа
    return ans

def findOrInsertMorph(con, m):
    res = dbFindMorph(con, m)
    if res:
        return res
    res = dbInsertMorph(con, m)
    return res

def findOrInsertWord(con, m):
    res = dbFindWord(con, m)
    if res:
        return res
    res = dbInsertWord(con, m)
    return res