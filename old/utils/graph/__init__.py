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


    #closes_voladj = [c*(math.exp(0.7*v/100)-(math.exp(0.7*0.12)-1)) for (c,v) in zip(closes, vcloses)]
    closes_voladj = [c*math.exp(0.7*v/100) for (c,v) in zip(closes, vcloses)]
    closes_voladj = [x - (closes[0]*(math.exp(0.7*0.13)-1)) for x in closes_voladj]
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

def graph_ohlc_darenger_bands(dates, opens, highs, lows, closes, high_band, low_band):
    high_minus_low = list(h-l for h,l in zip(highs, lows))

    axes = matplotlib.pyplot.axes()
    bars = axes.bar(dates, high_minus_low, 0, bottom=lows, color="k")

    for (o, c, bar) in zip(opens, closes, bars):
        x = bar.get_x()
        axes.plot((x-0.4, x), (o, o), color="k")
        axes.plot((x, x+0.4), (c, c), color="k")

    axes.plot(dates, high_band)
    axes.plot(dates, low_band)

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

def darenger_bands(highs, lows, vhighs):
    band_exp = -0.7
    high_band = [highs[0]]#+high[0]*vhighs[0]/100/math.sqrt(252)]
    low_band = [lows[0]]#-low[0]*vhighs[0]/100/math.sqrt(252)]

    i=1
    while i<len(highs):
        high_band.append(high_band[i-1]*math.exp(band_exp)+highs[i])
        low_band.append(low_band[i-1]*math.exp(band_exp)+lows[i])
        i+=1

    band = highs[0]*vhighs[0]/100/math.sqrt(252)
    high_band[0] += band
    low_band[0] -= band

    for i in range(1,len(highs)):
        exp_sum = (math.exp(band_exp*(i+1))-1)/(math.exp(band_exp)-1)
        band = highs[i]*vhighs[i]/100/math.sqrt(252)
        high_band[i] = high_band[i]/exp_sum + band
        low_band[i] = low_band[i]/exp_sum - band

    return (high_band, low_band)
