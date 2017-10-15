import dice


def roll(arr):
    val = arr[0]
    try:
        ret = dice.roll(val)
    except:
        ret = "I'm sorry, I can't roll that. Please try again."
    if isinstance(ret, list):
        val += 't'
        ret = dice.roll(val)
    return ret