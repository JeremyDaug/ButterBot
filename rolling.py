import dice


def roll(arr):
    val = arr[0]
    try:
        ret = dice.roll(val)
    except:
        ret = "I'm sorry, I can't roll that. Please try again."
    return ret
