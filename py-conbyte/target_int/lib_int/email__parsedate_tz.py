
def email__parsedate_tz(data):
    """Convert date to extended time tuple.

    The last (additional) element is the time zone offset in seconds, except if
    the timezone was specified as -0000.  In that case the last element is
    None.  This indicates a UTC timestamp that explicitly declaims knowledge of
    the source timezone, as opposed to a +0000 timestamp that indicates the
    source timezone really was UTC.

    """

    _daynames = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    _monthnames = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
                   'aug', 'sep', 'oct', 'nov', 'dec',
                   'january', 'february', 'march', 'april', 'may', 'june', 'july',
                   'august', 'september', 'october', 'november', 'december']

    if len(data) == 0:
        return None
    data = data.split()

    # The FWS after the comma after the day-of-week is optional, so search and
    # adjust for this.
    if data[0].endswith(',') or data[0].lower() in _daynames:
        # There's a dayname here. Skip it
        del(data[0])
    else:
        # i = data[0].rfind(',')
        i = data[0].find(',')
        if i >= 0:
            data[0] = data[0][i+1:]
    if len(data) == 3: # RFC 850 date, deprecated
        stuff = data[0].split('-')
        if len(stuff) == 3:
            data = stuff + data[1:]
    if len(data) == 4:
        s = data[3]
        i = s.find('+')
        if i == -1:
            i = s.find('-')
        if i > 0:
            data[3:] = [s[:i], s[i:]]
        else:
            data.append('') # Dummy tz
    if len(data) < 5:
        return None
    data = data[:5]
    [dd, mm, yy, tm, tz] = data
    mm = mm.lower()
    if mm not in _monthnames:
        dd, mm = mm, dd.lower()
        if mm not in _monthnames:
            return None
    mm = _monthnames.index(mm) + 1
    if mm > 12:
        mm -= 12
    if dd[-1] == ',':
        dd = dd[:-1]
    i = yy.find(':')
    if i > 0:
        yy, tm = tm, yy
    if yy[-1] == ',':
        yy = yy[:-1]
    if not yy[0].isdigit():
        yy, tz = tz, yy
    if tm[-1] == ',':
        tm = tm[:-1]
    tm = tm.split(':')
    if len(tm) == 2:
        [thh, tmm] = tm
        tss = '0'
    elif len(tm) == 3:
        [thh, tmm, tss] = tm
    elif len(tm) == 1 and '.' in tm[0]:
        # Some non-compliant MUAs use '.' to separate time elements.
        tm = tm[0].split('.')
        if len(tm) == 2:
            [thh, tmm] = tm
            tss = 0
        elif len(tm) == 3:
            [thh, tmm, tss] = tm
    else:
        return None

    # Try
    if not (yy.isdigit() and dd.isdigit() and thh.isdigit() and tmm.isdigit() and tss.isdigit()):
        return None
    yy = int(yy)
    dd = int(dd)
    thh = int(thh)
    tmm = int(tmm)
    tss = int(tss)

    # Check for a yy specified in two-digit format, then convert it to the
    # appropriate four-digit format, according to the POSIX standard. RFC 822
    # calls for a two-digit yy, but RFC 2822 (which obsoletes RFC 822)
    # mandates a 4-digit yy. For more information, see the documentation for
    # the time module.
    if yy < 100:
        # The year is between 1969 and 1999 (inclusive).
        if yy > 68:
            yy += 1900
        # The year is between 2000 and 2068 (inclusive).
        else:
            yy += 2000

    return [yy, mm, dd, thh, tmm, tss, 0, 1, -1]

print(email__parsedate_tz("Mon, 16 Nov 2009 13:32:02 +0100"))   # pragma: no cover
