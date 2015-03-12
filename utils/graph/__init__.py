import matplotlib.pyplot

def graph_ohlc_pivots(dates, opens, highs, lows, closes, high_pivots, low_pivots):
    high_minus_low = list(h-l for h,l in zip(highs, lows))

    axes = matplotlib.pyplot.axes()
    bars = axes.bar(dates, high_minus_low, 0, bottom=lows, color="k")

    for (o, c, bar) in zip(opens, closes, bars):
        x = bar.get_x()
        axes.plot((x-0.4, x), (o, o), color="k")
        axes.plot((x, x+0.4), (c, c), color="k")

    axes.plot(list(high_pivots.keys()), list(high_pivots.values()), "g^")
    axes.plot(list(low_pivots.keys()), list(low_pivots.values()), "rv")

    matplotlib.pyplot.grid(True)
    matplotlib.pyplot.show()

def find_alternating_pivot(dates, highs, lows):
    length = len(dates)

    highest_high_idx = 0
    highest_high = highs[highest_high_idx]

    lowest_high_idx = 0
    lowest_high = highs[lowest_high_idx]

    highest_low_idx = 0
    highest_low = lows[highest_low_idx]

    lowest_low_idx = 0
    lowest_low = lows[lowest_low_idx]

    i=1
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
   

def alternating_pivots(dates, highs, lows):
    (idx, high_or_low, next_pivot_starting_idx) = find_alternating_pivot(dates, highs, lows)

    if idx is not None:
        (high_pivots, low_pivots) = alternating_pivots(dates[next_pivot_starting_idx:], highs[next_pivot_starting_idx:], lows[next_pivot_starting_idx:])
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


