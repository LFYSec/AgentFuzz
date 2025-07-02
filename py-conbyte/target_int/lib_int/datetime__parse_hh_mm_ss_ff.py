
def datetime__parse_hh_mm_ss_ff(tstr):
    # Parses things of the form HH[:MM[:SS[.fff[fff]]]]
    len_str = len(tstr)

    time_comps = [0, 0, 0, 0]
    pos = 0
    for comp in range(0, 3):
        if (len_str - pos) < 2:
            return None

        time_comps[comp] = int(tstr[pos:pos+2])

        pos += 2
        next_char = tstr[pos:pos+1]

        if pos + 1 >= len(tstr) or comp >= 2:
            break

        if tstr[pos:pos+1] != ':':
            return None

        pos += 1

    if pos < len_str:
        if tstr[pos] != '.':
            return None
        else:
            pos += 1

            len_remainder = len_str - pos
            tlist = [3, 6]
            if len_remainder not in tlist:
                return None

            time_comps[3] = int(tstr[pos:])
            if len_remainder == 3:
                time_comps[3] *= 1000

    if time_comps[0] > 12:
        return None
    if time_comps[0] < 0:
        return None

    if time_comps[1] > 60:
        return None
    if time_comps[1] < 0:
        return None

    if time_comps[2] > 60:
        return None
    if time_comps[2] < 0:
        return None

    return time_comps

print(datetime__parse_hh_mm_ss_ff("12:01:23.123456"))   # pragma: no cover
