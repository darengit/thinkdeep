#!/usr/bin/env Rscript

# options(echo=FALSE)

library(zoo)

expSmoothing = function (vec, alpha) {
	retVec = vector()
	retVec = c(vec[1])

	for (i in 2:length(vec)) {
		retVec = c(retVec, alpha * retVec[i-1] + (1-alpha) * vec[i])
	}

	return(retVec)
}

addStdDev = function (vec, smoothVec, dateVec, vixVec, vixDateVec, factor) {
	bandVec = vector()
	for(i in 1:length(dateVec)) {
		vix = approx(vixDateVec, vixVec, dateVec[i], method="constant", rule=2, f=0)
		stdDev = vix$y / 100 / sqrt(252) * vec[i]
		bandVec = c(bandVec, smoothVec[i] + stdDev * factor)
	}

	return(bandVec)
}

spFrame = read.csv("/Users/dzou/R/data/sp.csv")
vixFrame = read.csv("/Users/dzou/R/data/vix.csv")

spDateVector = rev(as.Date(spFrame[,1]))
spHighVector = rev(spFrame[,3])
spLowVector = rev(spFrame[,4])

intraday = TRUE

if (intraday) {
	spDateVector = c(spDateVector, as.Date("2015-02-05"))
	spHighVector = c(spHighVector, 2060)
	spLowVector = c(spLowVector, 2043.45)
}

vixDateVector = rev(as.Date(vixFrame[,1]))
vixHighVector = rev(vixFrame[,3])

print("Begin smoothing")
alpha = 0.7
spHighSmoothVector = expSmoothing(spHighVector, alpha)
spLowSmoothVector = expSmoothing(spLowVector, alpha)

print("Expanding upper band 1 std dev")
spHighBandVector = addStdDev(spHighVector, spHighSmoothVector, spDateVector, vixHighVector, vixDateVector, 1);
print("Expanding lower band 1 std dev")
spLowBandVector = addStdDev(spLowVector, spLowSmoothVector, spDateVector, vixHighVector, vixDateVector, -1);

print("Plotting")
spHighZoo = zoo(spHighVector, spDateVector)
spLowZoo = zoo(spLowVector, spDateVector)
spHighBandZoo = zoo(spHighBandVector, spDateVector)
spLowBandZoo = zoo(spLowBandVector, spDateVector)

start = as.Date("2014-12-01")
end = as.Date("2015-03-01")

spHighZooWindow = window(spHighZoo, start=start, end=end)
spHighBandZooWindow = window(spHighBandZoo, start=start, end=end)
spLowZooWindow = window(spLowZoo, start=start, end=end)
spLowBandZooWindow = window(spLowBandZoo, start=start, end=end)

plot(c(start,end), c(min(min(spLowZooWindow), min(spLowBandZooWindow)), max(max(spHighZooWindow), max(spHighBandZooWindow))), col="white", xlab="", ylab="")
lines(spHighBandZooWindow, type="l", col="blue")
lines(spHighZooWindow, type="l", col="green")
lines(spLowBandZooWindow, type="l", col="black")
lines(spLowZooWindow, type="l", col="red")
grid(NULL,NULL,col="grey")
