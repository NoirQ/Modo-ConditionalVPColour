#python
import lx
import lxifc
import lxu

import time

com_listener = None

class selectionListen(lxifc.SelectionListener):
    def __init__(self):
        self.selSrv = lx.service.Selection()
        self.vmapType = lxu.utils.lxID4("VMAP")
        self.morfType = lxu.utils.lxID4("MORF")
        self.defaultColour = [0.2632736, 0.2632736, 0.2632735]

    def selevent_Add(self, type, subtType):
        if lx.service.Undo().State() == lx.symbol.iUNDO_INVALID:
            return

        if (type == self.vmapType):
            if (subtType == self.morfType):
                lx.eval("pref.value color.deformers {{{} {} {}}}".format(*(lx.eval("user.value noirq.conditionalVPColour.morphColour ?").split(" "))))
            else:
                lx.eval("pref.value color.deformers {{{} {} {}}}".format(*self.defaultColour))

    def selevent_Remove(self, type, subtType):
        if lx.service.Undo().State() == lx.symbol.iUNDO_INVALID:
            return

        if (type == self.vmapType and subtType == self.morfType):
            lx.eval("pref.value color.deformers {{{} {} {}}}".format(*self.defaultColour))


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