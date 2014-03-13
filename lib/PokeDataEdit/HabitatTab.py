#!/usr/lib/python
# -*- coding: utf-8 -*- 

import wx, sys
from GLOBALS import *
from lib.Tools.rom_insertion_operations import *
from lib.OverLoad.Button import *

class HABITAT(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.HabitatNames = ["Grassland","Forest","Water's-edge","Sea","Cave","Mountain","Rough-terrain","Urban","Rare"]
        self.CurrentHabitat = None
        self.CurrentPage = None
        self.GenerateHabitatUI()
    
    def GenerateHabitatUI(self):
        self.Sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.HabitatTypeList = wx.ListCtrl(self, -1, style=wx.LC_REPORT, size=(140,400))
        self.HabitatTypeList.InsertColumn(0, 'Habitat', width=140)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectHabitat,  self.HabitatTypeList)
        
        self.PageList = wx.ListCtrl(self, -1, style=wx.LC_REPORT, size=(60,400))
        self.PageList.InsertColumn(0, 'Page', width=50)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectPage,  self.PageList)
        
        name = encode_per_platform('POK\xe9MON')
        self.PokeList = wx.ListCtrl(self, -1, style=wx.LC_REPORT, size=(140,400))
        self.PokeList.InsertColumn(0, name, width=140)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectPoke,  self.PokeList)
        
        butons_vbox = wx.BoxSizer(wx.VERTICAL)
        self.POKE_NAME = ComboBox(self, -1, choices=Globals.PokeNames,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        butons_vbox.Add(self.POKE_NAME, 0, wx.EXPAND | wx.ALL, 5)
        
        ADD_POKE =  Button(self, 3, u"Add "+name)
        self.Bind(wx.EVT_BUTTON, self.OnAddPoke, id=3)
        butons_vbox.Add(ADD_POKE, 0, wx.EXPAND | wx.ALL, 5)

        DELETE_POKE =  Button(self, 4, u"Remove "+name)
        self.Bind(wx.EVT_BUTTON, self.OnDeletePoke, id=4)
        butons_vbox.Add(DELETE_POKE, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_UP = Button(self, 5, "Move Up")
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, id=5)
        butons_vbox.Add(MOVE_UP, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_DOWN = Button(self, 6, "Move Down")
        self.Bind(wx.EVT_BUTTON, self.OnMoveDown, id=6)
        butons_vbox.Add(MOVE_DOWN, 0, wx.EXPAND | wx.ALL, 5)
        
        PAGE_MOVE_UP = Button(self, 7, "Move Page Up")
        self.Bind(wx.EVT_BUTTON, self.OnMovePageUp, id=7)
        butons_vbox.Add(PAGE_MOVE_UP, 0, wx.EXPAND | wx.ALL, 5)
        
        PAGE_MOVE_DOWN = Button(self,8, "Move Page Down")
        self.Bind(wx.EVT_BUTTON, self.OnMovePageDown, id=8)
        butons_vbox.Add(PAGE_MOVE_DOWN, 0, wx.EXPAND | wx.ALL, 5)
        
        self.NotInPokeList = wx.ListCtrl(self, -1, style=wx.LC_REPORT, size=(140,400))
        self.NotInPokeList.InsertColumn(0, 'Not Used', width=140)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectPoke,  self.NotInPokeList)
        
        self.Sizer.Add(self.HabitatTypeList, 0, wx.ALL, 5)
        self.Sizer.Add(self.PageList, 0, wx.ALL, 5)
        self.Sizer.Add(self.PokeList, 0, wx.ALL, 5)
        self.Sizer.Add(butons_vbox, 0, wx.ALL, 5)
        self.Sizer.Add(self.NotInPokeList, 0, wx.ALL, 5)
        
        self.SetSizer(self.Sizer)
        self.Layout()
        
        self.LoadHabitatData()
        
    def LoadHabitatData(self):
        self.TableOffset = int(Globals.INI.get(Globals.OpenRomID, "habitats"), 0)
        self.Habitats = {"Grassland":[],"Forest":[],"Water's-edge":[],"Sea":[],"Cave":[],"Mountain":[],"Rough-terrain":[],"Urban":[],"Rare":[]}
        with open(Globals.OpenRomName, "rb") as rom:
            LogOffset = self.TableOffset
            for habitat in self.HabitatNames:
                rom.seek(LogOffset)
                PagesOffset = read_pointer(rom.read(4))
                PagesNum = read_number(rom.read(4))
                LogOffset += 8
                for n in range(PagesNum):
                    rom.seek(PagesOffset)
                    PokesOffset = read_pointer(rom.read(4))
                    PokesNum = read_number(rom.read(4))
                    PagesOffset += 8
                    PokesList = []
                    for p in range(PokesNum):
                        rom.seek(PokesOffset)
                        PokesList.append(read_number(rom.read(2)))
                        PokesOffset += 2
                    self.Habitats[habitat].append(PokesList)
        for habitat in self.HabitatNames:
            index = self.HabitatTypeList.InsertStringItem(sys.maxint, habitat)
        self.FindNonUsedPokes()
        
    def OnSelectHabitat(self, event):
        self.PageList.DeleteAllItems()
        self.PokeList.DeleteAllItems()
        selection = self.HabitatTypeList.GetFocusedItem()
        if selection != -1:
            selection = self.HabitatTypeList.GetItem(selection, 0)
            selection = selection.GetText()
            
            for num, page in enumerate(self.Habitats[selection]):
                index = self.PageList.InsertStringItem(sys.maxint, str(num))
            self.CurrentHabitat = selection
            
    def OnSelectPage(self, event):
        self.PokeList.DeleteAllItems()
        selection = self.PageList.GetFocusedItem()
        if selection != -1:
            selection = self.PageList.GetItem(selection, 0)
            selection = int(selection.GetText())
            self.CurrentPage = selection
            self.ReloadPokesList()
            
    def OnSelectPoke(self, event):
        event = event.GetEventObject()
        poke = event.GetFocusedItem()
        if poke != -1:
            poke = event.GetItem(poke, 0)
            poke = poke.GetText()
            poke = Globals.PokeNames.index(poke)
            self.POKE_NAME.SetSelection(poke)
            
    def SearchAndRemovePoke(self, POKE):
        for habitat in self.Habitats:
            for PageNum, page in enumerate(self.Habitats[habitat]):
                for poke in self.Habitats[habitat][PageNum]:
                    if poke == POKE:
                        index = self.Habitats[habitat][PageNum].index(poke)
                        del self.Habitats[habitat][PageNum][index]
    
    def OnAddPoke(self, event):
        POKE = self.POKE_NAME.GetSelection()
        if POKE != -1:
            self.SearchAndRemovePoke(POKE)
            self.Habitats[self.CurrentHabitat][self.CurrentPage].append(POKE)
            self.ReloadPokesList()
            index = len(self.Habitats[self.CurrentHabitat][self.CurrentPage])
            self.PokeList.Select(index-1)
            self.PokeList.Focus(index-1)
            
    def OnDeletePoke(self, event):
        selection = self.PokeList.GetFocusedItem()
        if selection != -1:
            del self.Habitats[self.CurrentHabitat][self.CurrentPage][selection]
            self.ReloadPokesList()
            length = len(self.Habitats[self.CurrentHabitat][self.CurrentPage])
            if selection == length:
                index = selection-1
            else: index = selection
            self.PokeList.Select(index)
            self.PokeList.Focus(index)
            
    def OnMoveUp(self, *args):
        poke = self.PokeList.GetFocusedItem()
        if poke != -1:
            poke = self.PokeList.GetItem(poke, 0)
            poke = poke.GetText()
            poke = Globals.PokeNames.index(poke)
            
            index = self.Habitats[self.CurrentHabitat][self.CurrentPage].index(poke)
            if index > 0:
                self.Habitats[self.CurrentHabitat][self.CurrentPage][index], self.Habitats[self.CurrentHabitat][self.CurrentPage][index-1] = self.Habitats[self.CurrentHabitat][self.CurrentPage][index-1], self.Habitats[self.CurrentHabitat][self.CurrentPage][index]
                self.ReloadPokesList()
                self.PokeList.Select(index-1)
                self.PokeList.Focus(index-1)
                
    def OnMoveDown(self, *args):
        poke = self.PokeList.GetFocusedItem()
        if poke != -1:
            poke = self.PokeList.GetItem(poke, 0)
            poke = poke.GetText()
            poke = Globals.PokeNames.index(poke)
            
            index = self.Habitats[self.CurrentHabitat][self.CurrentPage].index(poke)
            if index < len(self.Habitats[self.CurrentHabitat][self.CurrentPage])-1:
                self.Habitats[self.CurrentHabitat][self.CurrentPage][index], self.Habitats[self.CurrentHabitat][self.CurrentPage][index+1] = self.Habitats[self.CurrentHabitat][self.CurrentPage][index+1], self.Habitats[self.CurrentHabitat][self.CurrentPage][index]
                self.ReloadPokesList()
                self.PokeList.Select(index+1)
                self.PokeList.Focus(index+1)
    
    def OnMovePageUp(self, *args):
        
        if self.CurrentPage 
                
    def OnMovePageDown(self, *args):
        length = len(self.Habitats[self.CurrentHabitat])-1
        if self.CurrentPage == length: return
    
    
    def ReloadPokesList(self):
        self.PokeList.DeleteAllItems()
        for poke in self.Habitats[self.CurrentHabitat][self.CurrentPage]:
            index = self.PokeList.InsertStringItem(sys.maxint, Globals.PokeNames[poke])
        self.FindNonUsedPokes()
    
    def FindNonUsedPokes(self):
        AllPokesInHabitats = []
        PokesNotInHabitats = []
        self.NotInPokeList.DeleteAllItems()
        for habitat in self.Habitats:
            for PageNum, page in enumerate(self.Habitats[habitat]):
                for poke in self.Habitats[habitat][PageNum]:
                    AllPokesInHabitats.append(Globals.PokeNames[poke])
        for POKE in Globals.PokeNames:
            if POKE not in AllPokesInHabitats:
                PokesNotInHabitats.append(POKE)
        for poke in PokesNotInHabitats:
            if poke[0] != "?":
                index = self.NotInPokeList.InsertStringItem(sys.maxint, poke)
    
"""In a Fire Red ROM, there is a table of data located at the address '0x452c4c'. 
Each entry in this table contains two pieces of information. One is a pointer and 
the other is a 32-bit number (I assume this is to keep the alignment consistent). 
The pointer points to another table and the number specifies the size of that table. 
In one of these secondary tables, there are a number of entries (the exact number is 
specified by the number mentioned earlier), each of which are also composed of a 
pointer and a 32-bit number. These pointers point instead to a list of pokémon and 
the number dictates the length of that list.

After a bit of research, I determined that the first table of pointers controls the 
classification of pokémon habitats (e.g., Grassland, Mountain, Rough-Terrain, etc.) 
as displayed in the PokéDex. The secondary tables specify which pokémon are in each 
Habitat and which pokémon appear on each "page" of the PokéDex (see the screenshots 
if you don't know what I mean). Let's look at an example. The first pointer at 
'0x452c4c' points to '0x4527d4' and is followed by the number '0x1b'. Thus, if you 
have a complete PokéDex, then there will be 27 ('0x1b' in decimal) pages of pokémon 
in the Grassland Habitat (the pointers are arranged in the order that they appear 
in-game, so Grassland comes first). The first pointer at '0x4527d4' points to 
'0x4524d0' and is followed by the number '0x4'. This means that the first four 
pokémon at that address are grouped onto one "PokéDex page". In this case, the 
numbers at that address (after reversing them) are '0x0013', '0x0014', '0x00a1', 
and '0x00a2', which correspond to Rattata, Raticate, Sentret, and Furret. """

