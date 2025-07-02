

def smtpd_parseargs(arg1, arg2):
    if len(arg1) == 0:
        localspec = 'localhost:8025'
    else:
        localspec = arg1

    if len(arg2) == 0:
        remotespec = 'localhost:8025'
    else:
        remotespec = 'localhost:25'

    # split into host/port pairs
    i = localspec.find(':')
    if i < 0:
        return 0
    else:
        localhost = localspec[:i]

    if localspec[i+1:].isdigit():
        localport = int(localspec[i+1:])
    else:
        return 0

    i = remotespec.find(':')
    if i < 0:
        return 0
    else:
        remotehost = remotespec[:i]

    if remotespec[i+1:].isdigit():
        remoteport = int(remotespec[i+1:])
    else:
        return 0

    if localport >= 0 and remoteport >= 0:
        return 1
    else:
        return 2



print(smtpd_parseargs("localhost:8025", "localhost:25"))   # pragma: no cover
