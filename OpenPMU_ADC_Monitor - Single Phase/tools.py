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

import socket
import psutil

def getLocalIP():
    
    family = socket.AF_INET
    
    ips = []
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == family:
                if snic.address.startswith("169.254"):   # Ignore 169.254.x.x
                    continue
                else:
                    ips.append(snic.address)
                    
    ips.sort()
    
    return(ips)


"""
The approach below works well until Python 3.7, but after that no wheel
seems to be available for netifaces, so a new approach using standard
libraries is now used.  Tested in Python 3.9 on Windows.
"""

# import netifaces

# def getLocalIP():
#     """
#     get the current ip address of local machine

#     :return: IP addresses in a list
#     """
#     try:
#         ips=[]
#         for i in netifaces.interfaces():
#             j=netifaces.ifaddresses(i)
#             if  netifaces.AF_INET in j.keys():
#                 for k in j[netifaces.AF_INET]:
#                     ips.append(k["addr"])
#         #ips=socket.gethostbyname_ex(socket.gethostname())[-1]
#     except:
#         return []
#     ips.sort()
#     return ips
