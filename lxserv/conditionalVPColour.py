#python
import lx
import lxifc
import lxu

import time
import modo

com_listener = None
selected_morph = False

class selectionListen(lxifc.SelectionListener):
    def __init__(self):
        self.selSrv = lx.service.Selection()
        self.vmapType = lxu.utils.lxID4("VMAP")
        self.morfType = lxu.utils.lxID4("MORF")
        self.itemType = lxu.utils.lxID4("ITEM")
        self.meshType = lxu.utils.lxID4("MESH")
        self.defaultColour = [0.2632736, 0.2632736, 0.2632735]

    def selevent_Add(self, type, subtType):
        # Don't do anything in listeners if undo is invalid. Bad things will happen.
        if lx.service.Undo().State() == lx.symbol.iUNDO_INVALID:
            return

        global selected_morph

        # Easy case - we've selected a vmap
        if (type == self.vmapType):
            # if it's a morph, grab our colour and set the pref. Else, set to default.
            if (subtType == self.morfType):
                selected_morph = True
                lx.eval("pref.value color.deformers {{{} {} {}}}".format(*(lx.eval("user.value noirq.conditionalVPColour.morphColour ?").split(" "))))
            else:
                lx.eval("pref.value color.deformers {{{} {} {}}}".format(*self.defaultColour))

        # What if we've selected a mesh that doe snot have the vmap?
        sceneSrv = lx.service.Scene()
        meshItemType = sceneSrv.ItemTypeLookup("mesh")
        meshSrv = lx.service.Mesh()

        if (type == self.itemType):
            # There's probably a nicer way than this, but it works.
            # Basically loop through the selected meshes, then loop through the selected vmaps, then see if the mesh has that vmap
            for modoItem in modo.Scene().selectedByType("mesh"):
                asMesh = modo.Mesh(modoItem)                
                srvSel = lx.service.Selection()
                vmapType = srvSel.LookupType(lx.symbol.sSELTYP_VERTEXMAP)
                for k in range(srvSel.Count(vmapType)):
                    mPkt = srvSel.ByIndex(vmapType, k)
                    pt = lx.object.VMapPacketTranslation(srvSel.Allocate(lx.symbol.sSELTYP_VERTEXMAP))
                    if pt.Type(mPkt) == lx.symbol.i_VMAP_MORPH:
                        vmapName = pt.Name(mPkt)
                        for m in asMesh.geometry.vmaps.morphMaps:
                            if (m.name == pt.Name(mPkt)):
                                lx.eval("pref.value color.deformers {{{} {} {}}}".format(*(lx.eval("user.value noirq.conditionalVPColour.morphColour ?").split(" "))))
                                selected_morph = True
                                return
            # Bit dirty, but use a global to track that we have a morph selected. If we think we did, we can reset, else don't bother.
            if selected_morph:
                lx.eval("pref.value color.deformers {{{} {} {}}}".format(*self.defaultColour))


    def selevent_Remove(self, type, subtType):
        # Remove is basically the same
        if lx.service.Undo().State() == lx.symbol.iUNDO_INVALID:
            return
        global selected_morph

        if (type == self.vmapType and subtType == self.morfType):
            selected_morph = False
            lx.eval("pref.value color.deformers {{{} {} {}}}".format(*self.defaultColour))

        if (type == self.itemType):
            for modoItem in modo.Scene().selectedByType("mesh"):
                asMesh = modo.Mesh(modoItem)                
                srvSel = lx.service.Selection()
                vmapType = srvSel.LookupType(lx.symbol.sSELTYP_VERTEXMAP)
                for k in range(srvSel.Count(vmapType)):
                    mPkt = srvSel.ByIndex(vmapType, k)
                    pt = lx.object.VMapPacketTranslation(srvSel.Allocate(lx.symbol.sSELTYP_VERTEXMAP))
                    if pt.Type(mPkt) == lx.symbol.i_VMAP_MORPH:
                        vmapName = pt.Name(mPkt)
                        for m in asMesh.geometry.vmaps.morphMaps:
                            if (m.name == pt.Name(mPkt)):
                                selected_morph = True
                                lx.eval("pref.value color.deformers {{{} {} {}}}".format(*(lx.eval("user.value noirq.conditionalVPColour.morphColour ?").split(" "))))
                                return
            if selected_morph:
                lx.eval("pref.value color.deformers {{{} {} {}}}".format(*self.defaultColour))


# We fire this command on startup to start the listeners. We also reset the value
class enableViewportConditionalCMD(lxu.command.BasicCommand):
    def __init__ (self):
        lxu.command.BasicCommand.__init__ (self)

    def cmd_Flags (self):
        return lx.symbol.fCMD_UNDO

    def basic_Enable (self, msg):
        return True

    
    def basic_Execute (self, msg, flags):
        listenerService = lx.service.Listener()
        MyListen = selectionListen()
        global com_listener
        if com_listener is None:
            com_listener = lx.object.Unknown(MyListen)
            listenerService.AddListener(com_listener)

        selSrv = lx.service.Selection()
        defaultColour = [0.2632736, 0.2632736, 0.2632735]
        srvSel = lx.service.Selection()
        vmapType = srvSel.LookupType(lx.symbol.sSELTYP_VERTEXMAP)
        
        for k in range(srvSel.Count(vmapType)):
            mPkt = srvSel.ByIndex(vmapType, k)
            pt = lx.object.VMapPacketTranslation(srvSel.Allocate(lx.symbol.sSELTYP_VERTEXMAP))
            if pt.Type(mPkt) == lx.symbol.i_VMAP_MORPH:
                lx.eval("pref.value color.deformers {{{} {} {}}}".format(*(lx.eval("user.value noirq.conditionalVPColour.morphColour ?").split(" "))))
                return

        lx.eval("pref.value color.deformers {{{} {} {}}}".format(*defaultColour))

# User values can be assocaited with an action. (See the user values cfg). This is that action, which is bascially set the vp colour.
class setViewportDeformerColourCMD(lxu.command.BasicCommand):
    def __init__ (self):
        lxu.command.BasicCommand.__init__ (self)

    def cmd_Flags (self):
        return lx.symbol.fCMD_UNDO

    def basic_Enable (self, msg):
        return True

    
    def basic_Execute (self, msg, flags):
        srvSel = lx.service.Selection()
        vmapType = srvSel.LookupType(lx.symbol.sSELTYP_VERTEXMAP)
        for k in range(srvSel.Count(vmapType)):
            mPkt = srvSel.ByIndex(vmapType, k)
            pt = lx.object.VMapPacketTranslation(srvSel.Allocate(lx.symbol.sSELTYP_VERTEXMAP))
            if pt.Type(mPkt) == lx.symbol.i_VMAP_MORPH:
                lx.eval("pref.value color.deformers {{{} {} {}}}".format(*(lx.eval("user.value noirq.conditionalVPColour.morphColour ?").split(" "))))
                return


lx.bless(enableViewportConditionalCMD, "noirq.conditionalVPColour.startup")
lx.bless(setViewportDeformerColourCMD, "noirq.conditionalVPColour.set")