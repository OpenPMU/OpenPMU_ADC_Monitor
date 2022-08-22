"""
OpenPMU - ADC Monitor
Copyright (C) 2022  www.OpenPMU.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


#!/usr/bin/python
# main ui file used to display data and information
# __author__ = 'xzhao'

# load packages
from __future__ import print_function

import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings, QSize, QPoint
from PyQt5 import uic

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal as Signal

import pyqtgraph as pg
import numpy as np
from datetime import datetime

sys.path.append('../..')
import PMU as PMU
import tools

APP_ID = 'belfast.university.queens.xiaodong.zhao.pmudataplotgui'  # arbitrary string
# ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

# the main ui
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
UI_FILE = os.path.join(SCRIPT_DIRECTORY, 'PMUDataPlotGUI.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(UI_FILE)

# DEBUG & DEVELOPMENT
import csv
import pandas as pd
import soundfile as sf
csvWrite = False
waveWrite = False


class MainWindow(TemplateBaseClass):
    def __init__(self, parent=None):
        TemplateBaseClass.__init__(self)

        # Define Colours
        
        RYBcolour = {0:(255,0,0),       # Red
                     1:(255,160,0),     # Yellow  (orange)
                     2:(0,0,255),       # Blue
                     3:(0,0,0),         # Black
                     4:(255,0,0),       # Red
                     5:(255,160,0),     # Yellow  (orange)
                     6:(0,0,255),       # Blue
                     7:(0,0,0) }        # Black

        # load ui from file
        self.ui = WindowTemplate()
        self.ui.setupUi(self)
        self.ui.ip.addItems(tools.getLocalIP())
        self.ui.ip.addItem('127.0.0.1')
        self.ui.startBtn.clicked.connect(self.start)
        self.isStarted = False

        # read windows size settings
        self.readSettings()

        self.plotTime = 100  # the time length to plot, in ms
        
        # create plots
        self.ui.plotArea.setBackground('w')
        self.plots = []
        self.plotTexts = []
        
        
        p1 = self.ui.plotArea.addPlot(row = 1, col = 1, title="Voltage (V)")
        p1.setLabels(left='V', bottom='Time (s)')
        p1.enableAutoRange('xy', True)
        self.plt0 = p1.plot()
        self.plt1 = p1.plot()
        self.plt2 = p1.plot()
        self.plt3 = p1.plot()
        self.plt0.setPen(color=RYBcolour[0], width=2)
        self.plt1.setPen(color=RYBcolour[1], width=2)
        self.plt2.setPen(color=RYBcolour[2], width=2)
        self.plt3.setPen(color=RYBcolour[3], width=2)
        p1.showGrid(x = True, y = True, alpha = 0.3) 
        
        
        p2 = self.ui.plotArea.addPlot(row = 2, col = 1, title="Current (I)")
        p2.setLabels(left='A', bottom='Time (s)')
        p2.enableAutoRange('xy', True)
        self.plt4 = p2.plot()
        self.plt5 = p2.plot()
        self.plt6 = p2.plot()
        self.plt7 = p2.plot()
        self.plt4.setPen(color=RYBcolour[0], width=2)
        self.plt5.setPen(color=RYBcolour[1], width=2)
        self.plt6.setPen(color=RYBcolour[2], width=2)
        self.plt7.setPen(color=RYBcolour[3], width=2)
        p2.showGrid(x = True, y = True, alpha = 0.3) 

        p3 = self.ui.plotArea.addPlot(row = 3, col = 1, title="Power (P)")
        p3.setLabels(left='W', bottom='Time (s)')
        p3.enableAutoRange('xy', True)
        self.pltWatts = p3.plot(fillLevel=0, brush=(50,50,200,50))
        self.pltWatts.setPen(color=RYBcolour[0], width=2)
        p3.showGrid(x = True, y = True, alpha = 0.3) 

        
        # Link X-axis
        p1.setXLink(p2)
        p2.setXLink(p3)
        
        # for i in range(0, PMU.Receiver.CH_NUMBER):
        #     # data plot area
        #     p = self.ui.plotArea.addPlot(row = (i%4) + 1, col = (i // 4) + 1, title="Ch %d" % (i + 1))
        #     p.setLabels(left='V %d' % (i + 1), bottom='Time (s)')
        #     p.enableAutoRange('xy', True)
        #     plt = p.plot()

        #     # plt.setPen(color=(255 - 32 * i, 128 * (i % 2), 32 * i), width=2)
        #     plt.setPen(color=RYBcolour[i], width=2)
        #     self.plots.append(plt)

        #     # text area used to display some information
        #     text = pg.TextItem("", anchor=(0, 0), border='w', fill=(178, 206, 207, 50), color=(255, 0, 0))  #
        #     p.addItem(text)
        #     text.setPos(0, 0)
        #     self.plotTexts.append(text)

        #     ### Code below replaced by row=, col= in addPlot
            
        #     # # arrange plots in 2 rows
        #     # if i % 2 == 1:
        #     #     self.ui.plotArea.nextRow()
        #     # if i % 2 == 0:
        #     #     self.ui.plotArea.nextColumn()
            
                


        # thread to receive data
        self.dataThread = dataThread(self.plotTime)
        self.dataThread.displayDataSig.connect(self.displayData)
        self.dataThread.updateTimeSig.connect(self.updateTime)
        self.dataThread.msgSig.connect(self.displayMsg)

    def start(self):
        if not self.isStarted:
            self.ui.startBtn.setText('Stop')
            self.dataThread.ip = self.ui.ip.lineEdit().text()
            self.dataThread.port = int(self.ui.port.text())
            self.dataThread.start()
            self.isStarted = True
        else:
            self.ui.startBtn.setText('Start')
            self.dataThread.stop()
            self.isStarted = False

    # when closing app, save settings
    def closeEvent(self, event):
        self.dataThread.stop()
        self.dataThread.wait(1000)
        self.writeSettings()
        event.accept()

    # save settings
    def writeSettings(self):
        settings = QSettings("xzhao", "PMUClient")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
        settings.setValue("ip", self.ui.ip.lineEdit().text())
        settings.setValue("port", self.ui.port.text())

    # read settings
    def readSettings(self):
        settings = QSettings("xzhao", "PMUClient")
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        if type(pos) is QVariant:
            pos = pos.toPoint()
        if type(size) is QVariant:
            size = size.toSize()
        self.resize(size)
        self.move(pos)
        self.ui.ip.lineEdit().setText(settings.value("ip", "127.0.0.1"))
        self.ui.port.setText(settings.value("port", "48001"))

    # sample time and display them on LCD
    def updateTime(self, gpsDateTime):

        self.ui.lcdYear.display(gpsDateTime.year)
        self.ui.lcdMonth.display(str(gpsDateTime.month).zfill(2))
        self.ui.lcdDay.display(str(gpsDateTime.day).zfill(2))
        self.ui.lcdHour.display(str(gpsDateTime.hour).zfill(2))
        self.ui.lcdMin.display(str(gpsDateTime.minute).zfill(2))
        self.ui.lcdSec.display(str(gpsDateTime.second).zfill(2))

    # plots data
    def displayData(self, data):
        # [tData, chData] = data
        # for i in range(0, PMU.Receiver.CH_NUMBER):
        #     rms = np.sqrt(np.mean(np.square(chData[i, :])))
        #     avg = np.average(chData[i, :])
        #     self.plots[i].setData(y=chData[i, :], x=tData[0:chData.shape[1]])
        #     self.plotTexts[i].setText("RMS: %0.2f\nMean: %0.2f" % (rms, avg))
        
        [tData, chData, powerData] = data
        self.plt0.setData(y=chData[0, :], x=tData[0:chData.shape[1]])
        #self.plt1.setData(y=chData[1, :], x=tData[0:chData.shape[1]])
        #self.plt2.setData(y=chData[2, :], x=tData[0:chData.shape[1]])
        #self.plt3.setData(y=chData[3, :], x=tData[0:chData.shape[1]])
        self.plt4.setData(y=chData[4, :], x=tData[0:chData.shape[1]])
        #self.plt5.setData(y=chData[5, :], x=tData[0:chData.shape[1]])
        #self.plt6.setData(y=chData[6, :], x=tData[0:chData.shape[1]])
        #self.plt7.setData(y=chData[7, :], x=tData[0:chData.shape[1]])

        self.pltWatts.setData(y=powerData[:], x=tData[0:chData.shape[1]])

    def displayMsg(self, msg):
        msgBox = QMessageBox(QMessageBox.Warning,
                             "Warning", msg,
                             QMessageBox.NoButton, self)
        msgBox.addButton("&Continue", QMessageBox.RejectRole)
        msgBox.exec_()


# data thread used to receive data
class dataThread(QThread):
    displayDataSig = Signal(list)
    updateTimeSig = Signal(datetime)
    msgSig = Signal(str)

    def __init__(self, plotTime):
        QThread.__init__(self)
        self.plotTime = plotTime
        self.ip = '127.0.0.1'
        self.port = 48001
        self.stopThread = False

    def stop(self):
        self.stopThread = True

    def run(self, ):
        try:
            pmu = PMU.Receiver(self.ip, self.port, forward=True, forwardIP='127.0.0.1', forwardPort=48011)
        except IOError as msg:
            self.msgSig.emit(str(msg))
            return
        
        # number of recs before display
        dataCnt = 0
        preFrame = 0
        frameCnt = 0

        self.stopThread = False
        while not self.stopThread:
            dataInfo = pmu.receive()
            if dataInfo is None:
                continue
            
            # update displayed time and print frame information to stdout
            dt = datetime.combine(datetime.strptime(dataInfo['Date'], "%Y-%m-%d").date(), datetime.strptime(dataInfo['Time'], "%H:%M:%S.%f").time())
            if dt:
                if dt.microsecond == 0:  # new second
                    # update displayed time
                    self.updateTimeSig.emit(dt)
                    # if frameCnt != 0:
                    print(preFrame, ':', frameCnt)
                    print(str(dt) + " frame: " + str(dataInfo['Frame']), end='')
                    frameCnt = 0
                elif dataInfo['Frame'] - preFrame == 1:
                    print(".", end='')
                else:
                    print("%d %d" % (preFrame, dataInfo['Frame']), end='')
                preFrame = dataInfo['Frame']
                frameCnt += 1

            # samples size each time
            n = dataInfo['n']
            Fs = dataInfo['Fs']
            interval = dataInfo['n'] * 1000.0 / dataInfo['Fs']
            recNo = int(self.plotTime / interval)
            # holds data sample each time
            if "dataBuffer" not in locals():
                dataBuffer = np.zeros([PMU.Receiver.CH_NUMBER, n])
            # hold data to plot
            if "payloadDataBuffer" not in locals():
                payloadDataBuffer = np.zeros([PMU.Receiver.CH_NUMBER, n * recNo])
                plotDataY = np.empty_like(payloadDataBuffer)

            # sample size n has changed
            if dataBuffer.shape != (PMU.Receiver.CH_NUMBER, n):
                dataBuffer = np.zeros([PMU.Receiver.CH_NUMBER, n])
                dataCnt = 0
                payloadDataBuffer = np.zeros([PMU.Receiver.CH_NUMBER, n * recNo])
                plotDataY = np.empty_like(payloadDataBuffer)

            # read sampled data
            for i in range(0, PMU.Receiver.CH_NUMBER):
                k = 'Channel_%d' % i
                if k in dataInfo.keys():
                    # print(len(dataInfo[k]['Payload']),k)
                    dataBuffer[i,] = (dataInfo[k]['Payload'])

            # buffer data and plot
            payloadDataBuffer[:, dataCnt * n:(dataCnt * n + n)] = dataBuffer[:, :]
            dataCnt += 1
            if dataCnt >= recNo:  # update data plot
                dataCnt = 0
                samples = dataInfo['Fs'] / 1000.0 * self.plotTime
                plotDataT = ( np.arange(samples) / samples ) * ( self.plotTime / 1000.0 )
                # make a copy of data, so it is not altered while being displayed
                plotDataY[:] = payloadDataBuffer
                
                Vscale = 167.5
                Iscale = 11.3
                
                plotDataY[0] = plotDataY[0] * Vscale
                plotDataY[4] = plotDataY[4] * Iscale
                
                powerData = plotDataY[0] * plotDataY[4]
                
                self.displayDataSig.emit([plotDataT, plotDataY, powerData])
                
                # if csvWrite == True:
                #     df = pd.DataFrame({"name1" : plotDataY[0], "name2" : plotDataY[4]})
                #     df.to_csv("SV Data.csv", mode='a', header=False, index=False)
                #     print("Write to CSV...")
                                 
                # if waveWrite == True:
                        
                #     waveFilePath = "TEST.wav"
                #     sampleRate = 12800
                #     channels = 2
                    
                #     chunk = [plotDataY[0],plotDataY[4]]
                #     samples = (np.array(chunk).astype(np.float32) * 32767/5.0 ).astype(np.int16).transpose()
                    
                #     try:
                #         with sf.SoundFile(waveFilePath, 'r+') as waveFile:
        
                #             waveFile.seek(0,sf.SEEK_END)
                #             waveFile.write(samples)
                #     except:
                #         with sf.SoundFile(waveFilePath, 'w+', sampleRate, channels) as waveFile:

                #             waveFile.write(samples)
                    
                #     print("Write to Wave...")               

        pmu.close()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    ico = QIcon('..\\Resources\\pmulogo.png')
    app.setWindowIcon(ico)
    window.setWindowIcon(ico)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
