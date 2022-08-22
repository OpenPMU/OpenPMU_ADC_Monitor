# OpenPMU_ADC_Monitor
Tool to check the output of the OpenPMU ADC.  Receives SVs in XML format, renders as a chart.

## Usage

Launch `OpenPMU_ADC_Monitor.py` using Python 3.

Assuming that a conventional OpenPMU ADC based on a Beaglebone Black (BBB) is in use, and that it is outputting a stream of SV data to the default IP / port, set the network interface to `192.168.7.1` and port to `48001`.  Otherwise, use the settings that have been manually configured.

The single phase version of the software assumes voltage input on Channel 0, current input on Channel 1, and will display the product of these (power).

![OpenPMU ADC Monitor Screenshot](https://github.com/OpenPMU/OpenPMU_ADC_Monitor/blob/main/images/OpenPMU_ADC_Monitor%20-%20image001.png)
