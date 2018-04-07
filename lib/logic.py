def to_ascii_simple(s):
    return s.decode('utf-8').encode('ascii', 'ignore')

def to_ascii(form):
    result = {}
    for k in form:
        result[k] = str(form[k].decode('utf-8').encode('ascii'))
    return result

def ids_to_csv(ids):
    return ','.join([str(_id) for _id in ids])

def csv_to_ids(csv):
    return [int(_id) for _id in csv.split(',')]
