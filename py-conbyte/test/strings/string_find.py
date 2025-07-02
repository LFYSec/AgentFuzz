
# Test find
def string_find(a, b):
    search = a.find('ggg')
    ret = 0
    if search < 5:
        ret = 1
    else:
        ret = 2

    return ret
