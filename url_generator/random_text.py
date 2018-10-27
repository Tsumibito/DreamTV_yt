import re, random

'''
скрипт рендомизации текста. Два вида аргументов:
{комнатные|к.|ком.|Комн.} - один из перечисленных
[уютно,|тихо,] - мешаем порядок
'''

def give_me_rand_text_set(text, set_len):
    res = set()
    counter = 0
    while len(res) <= set_len:
        counter += 1
        res.add(rand_text(text))
        if counter > set_len*10:
            break
    return res

def rand_text(text):
    rgx = re.compile('\{([^{}]*)\}')
    cb = lambda m: random.choice(m.group(1).split('|'))
    while 1:
        r = rgx.sub(cb, text)
        if len(r) == len(text):
            return suffle_text(r)
        text = r

def suffle_text(text):
    aa = []
    for i in range(text.count('[')):
        aa.append(text[text.find('[')+1:text.find(']')])
        text = text.replace(text[text.find('['):text.find(']')+1], '{'+str(i)+'}')
    for i, j in enumerate(aa):
        d = j.split('|')
        random.shuffle(d)
        text = text.replace('{'+str(i)+'}', ' '.join(d))

    return text


