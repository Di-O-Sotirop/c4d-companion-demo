#############################################################################
# Copyright 2022 - University of Modena and Reggio Emilia                   #
#                                                                           #
# Author:                                                                   #
#    Dionysios Sotiropoulos, <dsotirop at unimore.it>                       #
#    Alessandro Capotondi, <a.capotondi at unimore.it>                      #
#                                                                           #
# Licensed under the Apache License, Version 2.0 (the "License");           #
# you may not use this file except in compliance with the License.          #
# You may obtain a copy of the License at                                   #
#                                                                           #
#    http://www.apache.org/licenses/LICENSE-2.0                             #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS,         #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
# See the License for the specific language governing permissions and       #
# limitations under the License.                                            #
#                                                                           #
# C4D Companion Computer Demo                                               #
#                                                                           #
# This software is developed under the ECSEL project Comp4drones(No 826610) #
#                                                                           #
#############################################################################

def formatNumeric(number, intlen, totallen):
    #get sign
    if number >= 0:
        sig = '+'
    else:
        sig = '-'
        number = -number
    #manipulate number part
    intpart = int(number)
    floatpart = str(number-intpart)
    intpart = str(intpart)
    intpart = intpart.zfill(intlen)
    floatpart = str(floatpart)
    floatpart = floatpart[2:]

    numstr = sig + intpart + '.' + floatpart

    clip = len(numstr) - totallen
    if clip > 0:
        outNum = numstr[:-clip]
    else:
        outNum = numstr.zfill(totallen)
    return outNum

def formatPlantCnt(number, total_length):
    if number > 10**total_length:
        outNum = 10**total_length-1
    else:
        outNum = str(number)
        outNum = outNum.zfill(total_length)
    return outNum
