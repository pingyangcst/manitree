# This file is part of Androguard.
#
# Copyright (C) 2010, Anthony Desnos <desnos at t0t0.fr>
# All rights reserved.
#
# Androguard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Androguard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Androguard.  If not, see <http://www.gnu.org/licenses/>.

import bytecode

from bytecode import SV

import StringIO
from struct import pack, unpack
from xml.dom import minidom


######################################################## AXML FORMAT ########################################################
# Translated from http://code.google.com/p/android4me/source/browse/src/android/content/res/AXmlResourceParser.java
class StringBlock :

	
    ATTRIBUTE_IX_NAMESPACE_URI  = 0
    ATTRIBUTE_IX_NAME           = 1
    ATTRIBUTE_IX_VALUE_STRING   = 2
    ATTRIBUTE_IX_VALUE_TYPE     = 3
    ATTRIBUTE_IX_VALUE_DATA     = 4
    ATTRIBUTE_LENGTH            = 5

    CHUNK_AXML_FILE             = 0x00080003
    CHUNK_RESOURCEIDS           = 0x00080180
    CHUNK_XML_FIRST             = 0x00100100
    CHUNK_XML_START_NAMESPACE   = 0x00100100
    CHUNK_XML_END_NAMESPACE     = 0x00100101
    CHUNK_XML_START_TAG         = 0x00100102
    CHUNK_XML_END_TAG           = 0x00100103
    CHUNK_XML_TEXT              = 0x00100104
    CHUNK_XML_LAST              = 0x00100104

    START_DOCUMENT              = 0
    END_DOCUMENT                = 1
    START_TAG                   = 2
    END_TAG                     = 3
    TEXT                        = 4

    def __init__(self, buff) :
        buff.read( 4 )

        self.chunkSize = SV( '<L', buff.read( 4 ) )
        self.stringCount = SV( '<L', buff.read( 4 ) )
        self.styleOffsetCount = SV( '<L', buff.read( 4 ) )
        
        # unused value ?
        buff.read(4) # ?
        
        self.stringsOffset = SV( '<L', buff.read( 4 ) )
        self.stylesOffset = SV( '<L', buff.read( 4 ) )

        self.m_stringOffsets = []
        self.m_styleOffsets = []
        self.m_strings = []
        self.m_styles = []

        for i in range(0, self.stringCount.get_value()) :
            self.m_stringOffsets.append( SV( '<L', buff.read( 4 ) ) )

        for i in range(0, self.styleOffsetCount.get_value()) :
            self.m_stylesOffsets.append( SV( '<L', buff.read( 4 ) ) )

        size = self.chunkSize.get_value() - self.stringsOffset.get_value()
        if self.stylesOffset.get_value() != 0 :
            size = self.stylesOffset.get_value() - self.stringsOffset.get_value()

        # FIXME
        if (size%4) != 0 :
            pass

        for i in range(0, size / 4) :
            self.m_strings.append( SV( '=L', buff.read( 4 ) ) )

        if self.stylesOffset.get_value() != 0 :
            size = self.chunkSize.get_value() - self.stringsOffset.get_value()
            
            # FIXME
            if (size%4) != 0 :
                pass

            for i in range(0, size / 4) :
                self.m_styles.append( SV( '=L', buff.read( 4 ) ) )

    def getRaw(self, idx) :
        if idx < 0 or self.m_stringOffsets == [] or idx >= len(self.m_stringOffsets) :
            return None

        offset = self.m_stringOffsets[ idx ].get_value()
        length = self.getShort(self.m_strings, offset)

        data = ""

        while length > 0 :
            offset += 2
            # Unicode character
            data += unichr( self.getShort(self.m_strings, offset) )
            
            # FIXME
            if data[-1] == "&" :
                data = data[:-1]

            length -= 1

        return data

    def getShort(self, array, offset) :

        value = array[offset/4].get_value()
        if ((offset%4)/2) == 0 :
            return value & 0xFFFF
        else :
            return value >> 16

