#System Tester.py - programmed by George Pruitt
#Feel free to distribute and improve upon
#Version 2.0
#/////////////////////////////////////////////////////////////////////////////////
#--------------------------------------------------------------------------------
#Import Section - inlcude functions, classes, variables
#from external modules
#--------------------------------------------------------------------------------
#import csv
#import numpy as np

import tkinter as tk
import os.path
from marketDataClass import marketDataClass
from dataMasterLists import commName, bigPtVal, minMove
from tkinter.filedialog import askopenfilenames
from equityDataClass import equityClass
from trade import trade
from tradeClass import tradeInfo
from systemMarket import systemMarketClass
from indicators import highest,lowest,rsiClass,stochClass,sAverage,bollingerBands

class portManagerClass(object):
    def __init__(self):
        self.portDate = list()
        self.marketSymbols= list()
        self.individEquity = list()
        self.combinedEquity = list()
        self.numConts = list()

class systemMarkTrackerClass(object):
    def __init__(self):
        self.marketData = marketDataClass
        self.entryPrice = list()
        self.entryQuant = list()
        self.exitQuant = list()
        self.entryName =list()
        self.mp = list()
        self.curShares = 0
        self.tradesList = list()
        self.equity = equityClass
        self.totProfit = 0
        self.barsSinceEntry = 0
        self.cumuProfit = 0
        self.equItm = 0

    def setSysMarkTrackingData(self,marketData):
        self.marketData = marketData

    def setSysMarkTrackingInfo(self,entryPrice,entryQuant,entryName,totProfit,mp,barsSinceEntry,curShares):
        self.entryPrice.append(entryPrice)
        self.entryQuant.append(entryQuant)
        self.entryName.append(entryName)
        self.mp.append(mp)
        self.totProfit = totProfit
        self.curShares = curShares

    def setSysMarkTrackingEquity(self,equity):
        self.equity = equity

def getDataAtribs(dClass):
   return(dClass.bigPtVal,dClass.symbol,dClass.minMove)
def getDataLists(dClass):
   return(dClass.date,dClass.open,dClass.high,dClass.low,dClass.close)
def roundToNearestTick(price,upOrDown,tickValue):
    temp1 = price - int(price)
    temp2 = int(temp1 / tickValue)
    temp3 = temp1 -(tickValue*temp2)
    if upOrDown == 1:
        temp4 = tickValue - temp3
        temp5 = temp1 + temp4
    if upOrDown == -1:
        temp4 = temp1 - temp3
        temp5 = temp4
    return(int(price) + temp5)

def calcTodaysOTE(mp,myClose,entryPrice,entryQuant,myBPV):
    todaysOTE = 0
    for entries in range(0,len(entryPrice)):
        if mp >= 1:
            todaysOTE += (myClose - entryPrice[entries])*myBPV*entryQuant[entries]
        if mp <= -1:
           todaysOTE += (entryPrice[entries] - myClose)*myBPV*entryQuant[entries]
    return(todaysOTE)

def exitPos(myExitPrice,myExitDate,tempName,myCurShares):
    global tradeName,entryPrice,entryQuant,exitPrice,numShares,myBPV,cumuProfit
    global cumuProfit
    if mp < 0:
        trades = tradeInfo('liqShort',myExitDate,tempName,myExitPrice,myCurShares,0)
        profit = trades.calcTradeProfit('liqShort',mp,entryPrice,myExitPrice,entryQuant,myCurShares) * myBPV
        profit = profit - myCurShares *commission
        trades.tradeProfit = profit
        cumuProfit += profit
        trades.cumuProfit = cumuProfit
    if mp > 0:
        trades = tradeInfo('liqLong',myExitDate,tempName,myExitPrice,myCurShares,0)
        profit = trades.calcTradeProfit('liqLong',mp,entryPrice,myExitPrice,entryQuant,myCurShares) * myBPV
        profit = profit - myCurShares * commission
        trades.tradeProfit = profit
        cumuProfit += profit
        trades.cumuProfit = cumuProfit
    curShares = 0
    for remShares in range(0,len(entryQuant)):
       curShares += entryQuant[remShares]
    return (profit,trades,curShares)
    
def bookTrade(entryOrExit,lOrS,price,date,tradeName,shares):
    global mp,commission,totProfit,curShares,barsSinceEntry,listOfTrades
    global entryPrice,entryQuant,exitPrice,numShares,myBPV,cumuProfit
    if entryOrExit == -1:
        profit,trades,curShares = exitPos(price,date,tradeName,shares)
        listOfTrades.append(trades)
        mp = 0
    else:
        profit = 0
        curShares = curShares + shares
        barsSinceEntry = 1
        entryPrice.append(price)
        entryQuant.append(shares)
        if lOrS == 1:
            mp += 1
            marketPosition[i] = mp
            trades = tradeInfo('buy',date,tradeName,entryPrice[-1],shares,1)
        if lOrS ==-1:
            mp -= 1
            marketPosition[i] = mp
            trades = tradeInfo('sell',date,tradeName,entryPrice[-1],shares,1)
        listOfTrades.append(trades)
    return(profit,curShares)

dataClassList = list()

fileName = "c:\PythonBackTester\dataMaster.csv"
fileName = "dataMaster.csv"
def parseDate(dateString):
    whereIsAslash = dateString.find('/')
    if whereIsAslash != -1:
        firstSlashLoc = whereIsAslash
        x = dateString[0:whereIsAslash]
        tempStr = dateString[whereIsAslash+1:len(dateString)]
        whereIsAslash = tempStr.find('/')
        y = tempStr[0:whereIsAslash]
        z = tempStr[whereIsAslash+1:len(tempStr)]
        if firstSlashLoc < 4:
            tempDate = int(z)*10000 + int(x)*100 + int(y)
        else:
            tempStr = dateString.replace('/','')
            tempDate = int(tempStr)
        return(tempDate)
    whereIsAdash = dateString.find('-')
    if whereIsAdash != -1:
        firstDashLoc = whereIsAdash
        x = dateString[0:whereIsAslash]
        tempStr = dateString[whereIsAslash+1:len(dateString)]
        whereIsAslash = tempStr.find('/')
        y = tempStr[0:whereIsAslash]
        z = tempStr[whereIsAslash+1:len(tempStr)]
        if firstSlashLoc < 4:
            tempDate = int(z)*10000 + int(x)*100 + int(y)
        else:
            tempStr = dateString.replace('-','')
            tempDate = int(tempStr)
        return(tempDate)
    return(int(dateString))



def getData():
    tempFileList = list()
    portfolioFileNames = list()
    totComms = 0
    with open(fileName) as f:
       f_csv = csv.reader(f)
       for row in f_csv:
          commName.append(row[0])
          bigPtVal.append(float(row[1]))
          minMove.append(float(row[2]))
          totComms = totComms + 1
    f.close
    root = tk.Tk()
    root.withdraw()
    cnt = 0
    files = askopenfilenames(filetypes=(('CSV files', '*.csv'),
                                       ('TXT files', '*.txt'),('POR files', '*.por')),
                                       title='Select Markets or Ports. To Test- CSV format only!')
    fileList = root.tk.splitlist(files)
    fileListLen = len(fileList)
    for marketCnt in range(0,fileListLen):
        head,tail = os.path.split(fileList[marketCnt])
        tempStr = tail
        isThisAport = tempStr.find('.por')
        if isThisAport != -1:
            portMarketCnt = 0
            with open(fileList[marketCnt], "r") as f:
                for line in f:
                    portfolioFileNames.append(line.rstrip('\n'))
                    portMarketCnt += 1
            if portMarketCnt == 0:
                print("Portfolio File Empty -- Reselect market or portfolio ")
                quit()
            del fileList
            fileList = list()
            head = head +"/"
            for x in range(0,portMarketCnt):
                fileList += (head+portfolioFileNames[x],)
            fileListLen = len(fileList)
            break


    for marketCnt in range(0,fileListLen):
        head,tail = os.path.split(fileList[marketCnt])
        tempStr = tail[0:2]
        commIndex = 0
        foundInDataMaster = 0
        for i in range(totComms):
            if tempStr == commName[i]:
                commIndex = i
                foundInDataMaster = 1
        newDataClass = marketDataClass()
        if foundInDataMaster != 0:
            newDataClass.setDataAttributes(commName[commIndex],bigPtVal[commIndex],minMove[commIndex])
        else:
            newDataClass.setDataAttributes(tail,100,0.01)
        with open(fileList[marketCnt]) as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                numCols = len(row)
                for col in range(0,numCols):
                    row[col] = row[col].replace(' ','')
                tempStr = row[0]
                isThereAslash = tempStr.find('/')
                isThereAdash = tempStr.find('-')
                if isThereAslash != -1:
                    tempStr = tempStr.replace('/','')
                if isThereAdash != -1:
                    tempStr = tempStr.replace('-','')
                isThereAdigit = tempStr.isdigit()
                if (isThereAdigit):
                    if numCols == 5:
                        newDataClass.readData(parseDate(row[0]),float(row[1]),float(row[2]),float(row[3]),float(row[4]),0.0,0.0)
                    if numCols == 7:
                        newDataClass.readData(parseDate(row[0]),float(row[1]),float(row[2]),float(row[3]),float(row[4]),float(row[5]),float(row[6]))
                    cnt = cnt + 1
        dataClassList.append(newDataClass)
        f.close
    return(dataClassList)

def removeDuplicates(li):
    my_set = set()
    res = []
    for e in li:
        if e not in my_set:
            res.append(e)
            my_set.add(e)
    return res

def main():
    pass

if __name__ == '__main__':
    smtl = list()
    masterDateList = list()
    masterDateGlob = list()
    masterDateGlob[:] = []
    masterDateList[:] = []
    marketDataInc= list()
    myBPVList = list()
    myComNameList = list()
    myMinMoveList= list()
    portManager = portManagerClass()
    marketList = getData()
    marketDataInc.append(0)
    curShares = 0
    commission = 50
    cumuProfit = 25
    systemMarketList = list()

    numMarkets = len(marketList)
    for i in range(0,numMarkets):
        systemMarkTracker = systemMarkTrackerClass()
        equity = equityClass()
        systemMarkTracker.setSysMarkTrackingData(marketList[i])
        systemMarkTracker.setSysMarkTrackingEquity(equity)
        smtl.append(systemMarkTracker)
        marketDataInc.append(0)
        myBPV,myComName,myMinMove= getDataAtribs(smtl[i].marketData)
        myBPVList.append(myBPV)
        myComNameList.append(myComName)
        myMinMoveList.append(myMinMove)
        systemMarket = systemMarketClass()
        systemMarket.systemName = "CrossTest1"
        systemMarket.symbol = myComName
        systemMarketList.append(systemMarket)

    masterDateGlob = list()
    for i in range(0,numMarkets):
        numDaysInData = len(smtl[i].marketData.date)
        masterDateGlob += smtl[i].marketData.date
    masterDateList = removeDuplicates(masterDateGlob)
    masterDateList = sorted(masterDateList)
    x= 1
    jCnt = 0
    k=5
    barsSinceEntry = 0
    portEquItm = 0
    for i in range(len(masterDateList)-600,len(masterDateList)):
        portManager.portDate.append(masterDateList[i])
        kCnt = 0
        dailyPortCombEqu = 0
        for j in range(0,numMarkets):
            if j == 0 : dailyPortCombEqu = 0
            equItm = smtl[j].equItm
            equItm += 1
            myBPV = myBPVList[j]
            myComName = myComNameList[j]
            myMinMove = myMinMoveList[j]
            if myComName not in portManager.marketSymbols:
                portManager.marketSymbols.append(myComName)
                portManager.numConts.append(1)
##                portManager.individEquity.append(0)
            curShares = 0
            todaysCTE = todaysOTE = 0
            mktsToday = 0
            if masterDateList[i] in smtl[j].marketData.date:
                k = smtl[j].marketData.date.index(masterDateList[i])
                if len(smtl[j].mp) !=0:
                    mp = smtl[j].mp[-1]
                    entryPrice = smtl[j].entryPrice
                    entryQuant= smtl[j].entryQuant
                    numShares = entryQuant
                    curShares = smtl[j].curShares
                    cumuProfit = smtl[j].cumuProfit
                    cumuProfit = 50
                    barsSinceEntry = smtl[j].barsSinceEntry
                else:
                    mp = 0
                totProfit = smtl[j].totProfit
                if k > 5:
                    if marketList[j].high[k] >= highest(marketList[j].high,40,k,1) and mp !=1:
                        price = max(marketList[j].open[k],marketList[j].high[k-1])
                        if mp <= -1:
                            profit,trades,curShares = exitPos(price,marketList[j].date[k],"RevShrtLiq",curShares)
                            smtl[j].tradesList.append(trades)
                            mp = 0
                            todaysCTE = profit
                            totProfit += profit
                        tradeName = "Test B"
                        mp += 1
                        numShares = 1
                        curShares = curShares + numShares
                        barsSinceEntry = 1
                        smtl[j].setSysMarkTrackingInfo(price,numShares,tradeName,totProfit,mp,barsSinceEntry,curShares)
                        trades = tradeInfo('buy',marketList[j].date[k],tradeName,smtl[j].entryPrice[-1],numShares,1)
                        smtl[j].tradesList.append(trades)
                    if marketList[j].low[k] <= lowest(marketList[j].low,40,k,1) and barsSinceEntry > 1 and mp !=-1:
                        price = min(marketList[j].open[k],marketList[j].low[k-1])
                        if mp >= 1:
                            profit,trades,curShares = exitPos(price,marketList[j].date[k],"RevLongLiq",curShares)
                            smtl[j].tradesList.append(trades)
                            mp = 0
                            todaysCTE = profit
                            totProfit += profit
                        mp -= 1
                        tradeName = "Test S"
                        numShares = 1
                        curShares = curShares + numShares
                        barsSinceEntry = 1
                        smtl[j].setSysMarkTrackingInfo(price,numShares,tradeName,totProfit,mp,barsSinceEntry,curShares)
                        trades = tradeInfo('sell',marketList[j].date[k],tradeName,smtl[j].entryPrice[-1],numShares,1)
                        smtl[j].tradesList.append(trades)
                    if mp != 0 :
                        barsSinceEntry += 1
                        todaysOTE = calcTodaysOTE(mp,marketList[j].close[k],smtl[j].entryPrice,smtl[j].entryQuant,myBPV)
                    smtl[j].barsSinceEntry = barsSinceEntry
                    smtl[j].curShares = curShares
                    smtl[j].equItm = equItm
                    smtl[j].equity.setEquityInfo(marketList[j].date[k],equItm,todaysCTE,todaysOTE)
                    portManager.individEquity.append((j,smtl[j].equity.dailyEquityVal[-1]))
                    dailyPortCombEqu += portManager.individEquity[portEquItm][1]
                    portEquItm += 1
            else:
                print("Missing Date", masterDateList[i] )
                portManager.individEquity.append((j,smtl[j].equity.dailyEquityVal[-1]))
                dailyPortCombEqu += portManager.individEquity[portEquItm][1]
                portEquItm += 1
        portManager.combinedEquity.append(dailyPortCombEqu)


    for j in range(0,numMarkets):
        myCumuProfit = 0
        numsmtlTrades = len(smtl[j].tradesList)
        systemMarketList[j].
        for i in range(0,len(smtl[j].tradesList)):
            myCumuProfit += smtl[j].tradesList[i].tradeProfit
##            print(i," ",numsmtlTrades," ",smtl[j].tradesList[i].tradeDate,",",smtl[j].tradesList[i].tradeName,",",smtl[j].tradesList[i].tradePrice,",",smtl[j].tradesList[i].tradeProfit," ",myCumuProfit)
##            print(smtl[j].tradesList[i].tradeName)
##            print(smtl[j].tradesList[i].tradePrice)
##            print(smtl[j].tradesList[i].tradeProfit)
        for i in range(0,len(smtl[j].equity.equityItm)):
            print(i," ",smtl[j].equity.equityItm[i]," ",smtl[j].equity.equityDate[i]," ",smtl[j].equity.dailyEquityVal[i])

    for j in range(0,len(portManager.combinedEquity)):
        print(portManager.portDate[j],' ',portManager.combinedEquity[j])
