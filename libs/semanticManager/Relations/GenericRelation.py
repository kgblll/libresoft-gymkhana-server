#!/usr/bin/env python

#  Copyright (C) 2009 GSyC/LibreSoft
# 
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#
#  Author : Jose Gato Luis <jgato@libresoft.es>
#
#


class GenericRelation:

    def __init__ (self, typRelation):
        self.type = typRelation
    
    def setLema (self, lema):
        self.lema = lema
        
    def start (self):
        pass
        
    
