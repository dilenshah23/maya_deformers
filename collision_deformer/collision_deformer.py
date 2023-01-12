import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx

class CollisionDeformer(ommpx.MPxDeformerNode):
    kNodeName = "collisionDeformer"
    kNodeClassify = "deformer"
    kNodeID = om.MTypeId(0x100000) # You should use a unique id for your node

    aBounciness = om.MObject()
    aFriction = om.MObject()

    def __init__(self):
        ommpx.MPxDeformerNode.__init__(self)

    def deform(self, data, itGeo, localToWorldMatrix, geomIndex):
        input = ommpx.cvar.MPxDeformerNode_input
        env = ommpx.cvar.MPxDeformerNode_envelope
        bounciness = data.inputValue(CollisionDeformer.aBounciness).asFloat()
        friction = data.inputValue(CollisionDeformer.aFriction).asFloat()

        while not itGeo.isDone():
            index = itGeo.index()
            inputGeom = ommpx.MFnMesh(input)
            point = inputGeom.getPoint(index, om.MSpace.kObject)
            
            # perform collision calculations here
            # use bounciness and friction attributes to control the behavior
            # of the collision

            inputGeom.setPoint(index, point, om.MSpace.kObject)

            itGeo.next()
            
    def accessoryNodeSetup(self, dagMod):
        pass

    def accessoryNodeConnections(self):
        pass

def nodeCreator():
    return ommpx.asMPxPtr(CollisionDeformer())

def nodeInitializer():
    nAttr = om.MFnNumericAttribute()

    CollisionDeformer.aBounciness = nAttr.create("bounciness", "b", om.MFnNumericData.kFloat, 1.0)
    nAttr.setKeyable(True)
    CollisionDeformer.addAttribute(CollisionDeformer.aBounciness)
    CollisionDeformer.attributeAffects(CollisionDeformer.aBounciness, ommpx.cvar.MPxDeformerNode_outputGeom)

    CollisionDeformer.aFriction = nAttr.create("friction", "f", om.MFnNumericData.kFloat, 0.5)
    nAttr.setKeyable(True)
    CollisionDeformer.addAttribute(CollisionDeformer.aFriction)
    CollisionDeformer.attributeAffects(CollisionDeformer.aFriction, ommpx.cvar.MPxDeformerNode_outputGeom)
    
def initializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.registerNode(CollisionDeformer.kNodeName, CollisionDeformer.kNodeID, nodeCreator, nodeInitializer, ommpx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write("Failed to register node: %s" % CollisionDeformer.kNodeName)
        raise
