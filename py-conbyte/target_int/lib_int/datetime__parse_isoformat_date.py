def datetime__parse_isoformat_date(dtstr):
    # It is assumed that this function will only be called with a
    # string of length exactly 10, and (though this is not used) ASCII-only
    if len(dtstr) != 10:
        return None

    year = int(dtstr[0:4])
    if year < 0:
        return None

    if dtstr[4] != '-':
        return None

    month = int(dtstr[5:7])
    if month <= 0 or month > 12:
        return None

    if dtstr[7] != '-':
        return None

    day = int(dtstr[8:10])
    if day <= 0 or day > 32:
        return None

    return [year, month, day]

print(datetime__parse_isoformat_date("2019-07-19"))   # pragma: no cover
