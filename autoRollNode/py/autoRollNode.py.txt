import math
import maya.api.OpenMaya as om

# Define the autoRoll MPxNode class
class AutoRollNode(om.MPxNode):
    # Node ID
    kNodeId = om.MTypeId(0x00000123)

    # Node attributes
    inTime = None
    inSpeed = None
    inRadius = None
    outRotation = None

    def __init__(self):
        super(AutoRollNode, self).__init__()

    # Compute function for evaluating the node
    def compute(self, plug, dataBlock):
        if plug == AutoRollNode.outRotation:
            timeData = dataBlock.inputValue(AutoRollNode.inTime)
            speedData = dataBlock.inputValue(AutoRollNode.inSpeed)
            radiusData = dataBlock.inputValue(AutoRollNode.inRadius)
            rotationData = dataBlock.outputValue(AutoRollNode.outRotation)

            # Get the input values
            time = timeData.asTime().value()
            speed = speedData.asDouble()
            radius = radiusData.asDouble()

            # Calculate the rotation
            rotation = (speed * time) / radius
            rotation = math.degrees(rotation)

            # Set the output value
            rotationData.setDouble(rotation)

            # Mark the output plug as clean
            rotationData.setClean()

            return om.kSuccess

        return om.kUnknownParameter

# Creator function to create an instance of the node
def nodeCreator():
    return AutoRollNode()

# Initialize function to register the node
def initialize():
    nAttr = om.MFnNumericAttribute()

    AutoRollNode.inTime = om.MTime()
    AutoRollNode.inSpeed = nAttr.create("speed", "spd", om.MFnNumericData.kDouble, 0.0)
    AutoRollNode.inRadius = nAttr.create("radius", "rad", om.MFnNumericData.kDouble, 1.0)

    nAttr.setKeyable(True)
    nAttr.setStorable(True)

    AutoRollNode.outRotation = nAttr.create("rotation", "rot", om.MFnNumericData.kDouble, 0.0)
    nAttr.setWritable(False)
    nAttr.setStorable(False)

    # Add attributes to the node
    AutoRollNode.addAttribute(AutoRollNode.inTime)
    AutoRollNode.addAttribute(AutoRollNode.inSpeed)
    AutoRollNode.addAttribute(AutoRollNode.inRadius)
    AutoRollNode.addAttribute(AutoRollNode.outRotation)

    # Attribute affects relationships
    AutoRollNode.attributeAffects(AutoRollNode.inTime, AutoRollNode.outRotation)
    AutoRollNode.attributeAffects(AutoRollNode.inSpeed, AutoRollNode.outRotation)
    AutoRollNode.attributeAffects(AutoRollNode.inRadius, AutoRollNode.outRotation)

# Initialize the plugin
def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.registerNode("autoRoll", AutoRollNode.kNodeId, nodeCreator, initialize)
    except:
        om.MGlobal.displayError("Failed to register 'autoRoll' node")

# Uninitialize the plugin
def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterNode(AutoRollNode.kNodeId)
    except:
        om.MGlobal.displayError("Failed to deregister 'autoRoll' node")
