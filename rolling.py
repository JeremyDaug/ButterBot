import dice
import re


def roll(arr):
    ret = ''
    # split our roll into the rolls and the ops
    # ret = dice.roll(arr, verbose=True)
    res = list(filter(None, re.split("[+\-*/ ()]+", arr)))
    ops = re.findall("[+\-*/()]", arr)
    rollsults = []
    calc = ''
    for i in range(len(res)): # go through the rolls and ops and put them back together
        if i-1 >= 0:
            ret += ' ' + ops[i-1] + ' '
            calc += ' ' + ops[i-1] + ' '
        rollsults.append(dice.roll(str(res[i]), verbose=False))

        ret += str(rollsults[i])
        if isinstance(rollsults[i], list):
            calc += str(sum(rollsults[i]))
        else:
            calc += str(rollsults[i])

    # throw the summed equation in to get a final result.
    ret += ' = ' + str(dice.roll(calc))
    return ret
