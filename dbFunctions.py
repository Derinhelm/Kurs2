from word_module import Morph
def dbInsertWord(con, w, cursor):
    # возвращает индекс, вставленного слова
    cursor.execute('INSERT INTO word VALUES(DEFAULT,%s) RETURNING id;', (w,))
    con.commit()
    ind = cursor.fetchall()
    return ind[0][0]


def dbInsertMorph(con, m, cursor):
    # возвращает индекс, вставленного морфа
    command = "INSERT INTO morph_constraints("
    param_list = []
    for (attr, val) in m:
        command += attr + ", "
        param_list.append(val)
    command = command[:-2] + ") VALUES(" + ("%s, " * len(param_list))[:-2] + ") RETURNING id;"
    params = tuple(param_list)
    cursor.execute(command, params)
    con.commit()
    ind = cursor.fetchall()
    return ind[0][0]


def dbFindMorph(con, m, cursor):
    # здесь ответ - одно индекс !! Морфы все должны быть различны!!
    command = "SELECT id FROM morph_constraints WHERE "
    param_list = []
    imp_attr = []
    for (attr, val) in m:
        command += attr + " = %s AND "
        param_list.append(val)
        imp_attr.append(attr)
    for attr in set(Morph.names) - set(imp_attr):
        command += attr + " = 'not_imp' AND "
    command = command[:-5] + ";"
    params = tuple(param_list)
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


def findOrInsertMorphConstraints(m, con, cursor):
    res = dbFindMorph(con, m, cursor)
    if res:
        return res
    res = dbInsertMorph(con, m, cursor)
    return res


def findOrInsertWord(m, con, cursor):
    res = dbFindWord(con, m, cursor)
    if res:
        return res
    res = dbInsertWord(con, m, cursor)
    return res
