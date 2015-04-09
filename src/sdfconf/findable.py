#!/usr/bin/env python
# -*- coding: latin-1 -*-

#from sdfconf import sdf, mol2
try:
    import sdf, mol2
except ImportError:
    from sdfconf import sdf, mol2
from collections import OrderedDict as OrDi
import bisect as bi
import numpy

class Findable(object):
    
    def __init__(self, iterable=None, **kwargs):
        self._maindict = None #ordered dict jonka alkiot sis�lt�v�t koordinaatit listana, indeksi avaimena
        self._orders = [] #Lista joka tulee sis�lt�m�� dimensioiden m��r�n listapareja (tuplessa), jotka sis�lt�v�t kunkin koordinaattipisteen indeksin ja yhden dimension koordinaatin. Listat j�rjestetty kunkin dimension mukaan kasvavaan j�rjestykseen.
        self._thelen = 0 #Dimensioiden lukum��r�
        if iterable:
            self.set_iterable(iterable, kwargs.get('ignores', ['H'])) #Luodaan datarakenne
                
        else:
            self.set_iterable([]) #Tyhj� rakenne
            
    def set_iterable(self, iterable, ignores=[]):
        if type(iterable) in (list, tuple):
            pass
        elif type(iterable) in (sdf.Sdfmole,mol2.Mol2Mol):
            iterable = [list(atom[1]) for atom in iterable.atomsGenerator(ignores=ignores)]
        else:
            raise TypeError('Input must be of type list, tuple, Sdfmole, Mol2Mol.')
        
        if type(iterable[0]) not in (list, tuple):
            iterable = (iterable,) 
            
        self._thelen = len(iterable[0]) #ks init
        self._maindict = OrDi(enumerate(iterable)) #ks init
        self._orders = [] #ks init
        for i in range(self._thelen): #joka dimensiolle
            self._orders.append(([],[])) #lis�t��n listapari
            for key in sorted(self._maindict, key=lambda x: self._maindict[x][i]): #jokaiselle pisteelle (koordinaattien lukuj�rjestyksess�)
                self._orders[i][0].append(  key  ) #listaan 0 lis�t��n indeksi
                self._orders[i][1].append(  self._maindict[key][i]  ) #listaan 0 lis�t��n koordinaatti
        
    def findinrange(self, coord, radius, indexes=None , level = 0): #kutsuttaessa anna hakukoordinaatti ja s�de, muut auttavat rekursiivisessa dimensioiden k�sittelyss�
        '''
        tehd��n ensin haut joilla haetaan s�teen sis�ll� olevat pisteen yksitt�isten dimensioiden mukaan ja vasta siten l�ytyneille pisteille tehd��n todellinen et�isyyshaku.
        Eli ensin etsit��n s�teen mukainen kuutio ja vasta sen sis�lt� pallo :P (kun kolme ulottuvuutta)
        '''
        
        if not indexes:
            indexes = self._maindict.keys() #haetaan alkuper�iset indeksit
        
        ind_left  = bi.bisect_right( self._orders[level][1] , coord[level]-radius ) #puolitushaku piste - radius
        ind_right =  bi.bisect_left( self._orders[level][1] , coord[level]+radius ) #puolitushaku piste + radius
        
        if indexes is not self._maindict.keys(): #mik�li ei ensimm�inen taso
            new_indexes = list( set(indexes) & set(self._orders[level][0][ind_left:ind_right]) ) #ulosmenevist� indekseist� poistetaan ne joita ei ollut edellisess� haussa
        else:
            new_indexes = self._orders[level][0][ind_left:ind_right] #indeksit puolitushakujen v�list� l�ytyv�t
        
        if len(new_indexes)==0: #mik�li ei l�ytynyt mit��n, palaa
            return new_indexes
        elif level<self._thelen-1: #mik�li ei olla viimeisessa dimensiossa
            return self.findinrange(coord, radius, new_indexes, level +1) #haetaan my�s seuraavasta dimensiosta, annetaan my�s t��ll� l�ytyneet
        else: #mik�li ollaan viimeisess� dimensiossa
            final = []
            co1 = numpy.array(coord)
            for i in new_indexes: #k�yd��n l�pi l�ydetyt pisteet
                if  (sum((co1-numpy.array(self._maindict[i]))**2))**0.5 <= radius: #et�isyystesti
                    final.append(i)
            return final

