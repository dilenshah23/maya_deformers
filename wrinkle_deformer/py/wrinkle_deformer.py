import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx

class WrinkleDeformer(ommpx.MPxDeformerNode):
    kNodeName = "wrinkleDeformer"
    kNodeClassify = "deformer"
    kNodeID = om.MTypeId(0x100fff)

    aAmount = om.MObject()
    aDirection = om.MObject()

    def __init__(self):
        ommpx.MPxDeformerNode.__init__(self)

    def deform(self, data, itGeo, localToWorldMatrix, geomIndex):
        input = ommpx.cvar.MPxDeformerNode_input
        env = ommpx.cvar.MPxDeformerNode_envelope
        amount = data.inputValue(WrinkleDeformer.aAmount).asFloat()
        direction = data.inputValue(WrinkleDeformer.aDirection).asFloat()

        while not itGeo.isDone():
            index = itGeo.index()
            inputGeom = ommpx.MFnMesh(input)
            point = inputGeom.getPoint(index, om.MSpace.kObject)
            
            wrinkle = amount*(1-direction*point.y)
            point.x += wrinkle
            inputGeom.setPoint(index, point, om.MSpace.kObject)

            itGeo.next()
    
    def accessoryNodeSetup(self, dagMod):
        pass

    def accessoryNodeConnections(self):
        pass

def nodeCreator():
    return ommpx.asMPxPtr(WrinkleDeformer())

def nodeInitializer():
    nAttr = om.MFnNumericAttribute()

    WrinkleDeformer.aAmount = nAttr.create("amount", "amt", om.MFnNumericData.kFloat, 1.0)
    nAttr.setKeyable(True)
    WrinkleDeformer.addAttribute(WrinkleDeformer.aAmount)
    WrinkleDeformer.attributeAffects(WrinkleDeformer.aAmount, ommpx.cvar.MPxDeformerNode_outputGeom)

    WrinkleDeformer.aDirection = nAttr.create("direction", "dir", om.MFnNumericData.kFloat, 1.0)
    nAttr.setKeyable(True)
    WrinkleDeformer.addAttribute(WrinkleDeformer.aDirection)
    WrinkleDeformer.attributeAffects(WrinkleDeformer.aDirection, ommpx.cvar.MPxDeformerNode_outputGeom)

def initializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.registerNode(WrinkleDeformer.kNodeName, WrinkleDeformer.kNodeID, nodeCreator, nodeInitializer, ommpx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write("Failed to register node: %s" % WrinkleDeformer.kNodeName)
        raise
