

def formatNumeric(number, intlen, totallen):
    #get sign
    if number >= 0:
        sig = '+'
    else:
        sig = '-'
        number = -number
    #manipulate number part
    intpart = int(number)
    floatpart = str(number-intpart)
    intpart = str(intpart)
    intpart = intpart.zfill(intlen)
    floatpart = str(floatpart)
    floatpart = floatpart[2:]

    numstr = sig + intpart + '.' + floatpart

    clip = len(numstr) - totallen
    if clip > 0:
        outNum = numstr[:-clip]
    else:
        outNum = numstr.zfill(totallen)
    return outNum

def formatPlantCnt(number, total_length):
    if number > 10**total_length:
        outNum = 10**total_length-1
    else:
        outNum = str(number)
        outNum = outNum.zfill(total_length)
    return outNum


