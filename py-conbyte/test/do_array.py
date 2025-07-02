
def do_array(a, b):
    array = [1, 2, 3, 4]

    sliced = array[2:]
    c = sliced[0]

    d = array[1:3]

    array[0] = 6
    return array[0]
