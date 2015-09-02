from datetime import timedelta
import math
import matplotlib.pyplot

def graph_ohlc_voladj(dates, opens, highs, lows, closes, vcloses):
    high_minus_low = list(h-l for h,l in zip(highs, lows))

    axes = matplotlib.pyplot.axes()
    bars = axes.bar(dates, high_minus_low, 0, bottom=lows, color="k")

    for (o, c, bar) in zip(opens, closes, bars):
        x = bar.get_x()
        axes.plot((x-0.4, x), (o, o), color="k")
        axes.plot((x, x+0.4), (c, c), color="k")


    closes_voladj = [c*math.exp(0.7*v/100) for (c,v) in zip(closes, vcloses)]
    closes_voladj = [x - (closes_voladj[0]-closes[0]) for x in closes_voladj]
    #print(closes_voladj)
    axes.plot(dates, closes_voladj)
    #axes.plot(list(high_pivots.keys()), list(high_pivots.values()), "gv")
    #axes.plot(list(low_pivots.keys()), list(low_pivots.values()), "r^")


    matplotlib.pyplot.xlim(dates[0]-timedelta(days=5), dates[-1]+timedelta(days=5))
    matplotlib.pyplot.grid(True)
    matplotlib.pyplot.show()

def graph_ohlc_pivots(dates, opens, highs, lows, closes, high_pivots, low_pivots):
    high_minus_low = list(h-l for h,l in zip(highs, lows))

    axes = matplotlib.pyplot.axes()
    bars = axes.bar(dates, high_minus_low, 0, bottom=lows, color="k")

    for (o, c, bar) in zip(opens, closes, bars):
        x = bar.get_x()
        axes.plot((x-0.4, x), (o, o), color="k")
        axes.plot((x, x+0.4), (c, c), color="k")

    axes.plot(list(high_pivots.keys()), list(high_pivots.values()), "gv")
    axes.plot(list(low_pivots.keys()), list(low_pivots.values()), "r^")


    matplotlib.pyplot.xlim(dates[0]-timedelta(days=5), dates[-1]+timedelta(days=5))
    matplotlib.pyplot.grid(True)
    matplotlib.pyplot.show()

def find_alternating_pivot(dates, highs, lows, skip):
    length = len(dates)

    highest_high_idx = 0
    highest_high = highs[highest_high_idx]

    lowest_high_idx = 0
    lowest_high = highs[lowest_high_idx]

    highest_low_idx = 0
    highest_low = lows[highest_low_idx]

    lowest_low_idx = 0
    lowest_low = lows[lowest_low_idx]

    i=1+skip
    while i<length:
        if highest_low > highs[i] and highest_low > highs[0]:
            return (highest_high_idx, "high", highest_low_idx)
        if lowest_high < lows[i] and lowest_high < lows[0]:
            return (lowest_low_idx, "low", lowest_high_idx)

        if highest_high < highs[i]:
            highest_high = highs[i]
            highest_high_idx = i
        if lowest_high > highs[i]:
            lowest_high = highs[i]
            lowest_high_idx = i
        if highest_low < lows[i]:
            highest_low = lows[i]
            highest_low_idx = i
        if lowest_low > lows[i]:
            lowest_low = lows[i]
            lowest_low_idx = i

        i += 1

    return (None, None, None)
   

def alternating_pivots(dates, highs, lows, skip):
    (idx, high_or_low, next_pivot_starting_idx) = find_alternating_pivot(dates, highs, lows, skip)

    if idx is not None:
        (high_pivots, low_pivots) = alternating_pivots(dates[next_pivot_starting_idx:], highs[next_pivot_starting_idx:], lows[next_pivot_starting_idx:], max(idx-next_pivot_starting_idx,0))
        if high_or_low is "high":
            high_pivots[dates[idx]] = highs[idx]
        else:
            low_pivots[dates[idx]] = lows[idx]
        return (high_pivots, low_pivots)
    else:
        return ({}, {})

def fuzzy_pivots(dates, highs, lows):
    (idx, high_or_low, next_pivot_starting_idx) = find_alternating_pivot(dates, highs, lows)

    if idx is not None:
        (high_pivots, low_pivots) = fuzzy_pivots(dates[idx:], highs[idx:], lows[idx:])
        if high_or_low is "high":
            high_pivots[dates[idx]] = highs[idx]
        else:
            low_pivots[dates[idx]] = lows[idx]
        return (high_pivots, low_pivots)
    else:
        return ({}, {})

def upside_down_pivots(dates, highs, lows):
    (idx, high_or_low) = next_pivot(dates, highs, lows)

    if idx is not None:
        (high_pivots, low_pivots) = upside_down_pivots(dates[idx:], highs[idx:], lows[idx:])
        if high_or_low is "high":
            high_pivots[dates[idx]] = lows[idx]
        else:
            low_pivots[dates[idx]] = highs[idx]
        return (high_pivots, low_pivots)
    else:
        return ({}, {})

def next_pivot(dates, highs, lows):
    length = len(dates)

    #highest_high_iidx = 0
    #highest_high = highs[highest_high_idx]

    lowest_high_idx = 0
    lowest_high = highs[lowest_high_idx]

    highest_low_idx = 0
    highest_low = lows[highest_low_idx]

    #lowest_low_idx = 0
    #lowest_low = lows[lowest_low_idx]

    i=1
    while i<length:
        if highest_low > highs[i] and highest_low > highs[0]:
            return (highest_low_idx, "high")
        if lowest_high < lows[i] and lowest_high < lows[0]:
            return (lowest_high_idx, "low")

        #if highest_high < highs[i]:
            #highest_high = highs[i]
            #highest_high_idx = i
        if lowest_high > highs[i]:
            lowest_high = highs[i]
            lowest_high_idx = i
        if highest_low < lows[i]:
            highest_low = lows[i]
            highest_low_idx = i
        #if lowest_low > lows[i]:
            #lowest_low = lows[i]
            #lowest_low_idx = i

        i += 1

    return (None, None)

