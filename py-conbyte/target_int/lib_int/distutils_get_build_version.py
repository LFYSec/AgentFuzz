def distutils_get_build_version(version):
    prefix = "MSC v."
    i = version.find(prefix)
    if i == -1:
        return None
    i = i + len(prefix)
    s, rest = version[i:].split(" ", 1)
    if not (s[:-2].isdigit() and s[2:3].isdigit()):
        return None
    majorVersion = int(s[:-2]) - 6
    if majorVersion >= 13:
        # v13 was skipped and should be v14
        majorVersion += 1
    # minorVersion = int(s[2:3]) / 10.0
    minorVersion = int(s[2:3])
    # I don't think paths are affected by minor version in version 6
    if majorVersion == 6:
        minorVersion = 0
    if majorVersion < 6:
        return None

    if majorVersion > 7:
        if majorVersion >= 8 and minorVersion >= 0:
            return "Import something"
        else:
            return "Import something else"
    else:
        return "Do something else"
    # else we don't know what version of the compiler this is
    return None


print(distutils_get_build_version("MSC v.1212 abc"))   # pragma: no cover
