import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya

class WrinkleDeformer(OpenMayaMPx.MPxDeformerNode):
    kPluginNodeId = OpenMaya.MTypeId(0x0011E182)  # Unique ID for the plugin
    kPluginNodeName = "WrinkleDeformer"

    # Attribute handles
    intensityAttr = OpenMaya.MObject()
    paintMapAttr = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geomIter, matrix, multiIndex):
        # Get intensity attribute
        intensityHandle = dataBlock.inputValue(self.intensityAttr)
        intensity = intensityHandle.asFloat()

        # Get paint map attribute
        paintMapHandle = dataBlock.inputArrayValue(self.paintMapAttr)

        while geomIter.isDone() is False:
            point = geomIter.position()
            weight = self.weightValue(dataBlock, multiIndex, geomIter.index())

            # Analyze local geometry to detect compression
            compressionFactor = self.calculateCompression(geomIter)

            # Modify 'point' based on intensity, paintMap, and compression
            if compressionFactor > 0:
                # Only apply wrinkles in compressed areas
                wrinkleEffect = compressionFactor * intensity * weight
                # Wrinkle logic - This should be replaced with actual wrinkle creation logic
                point.y += wrinkleEffect

            geomIter.setPosition(point)
            geomIter.next()

    def calculateCompression(self, geomIter):
        """
        Calculate the compression factor for the current vertex.
        This method analyzes the local geometry to determine compression.
        """
        # Access the original mesh (rest state)
        thisNode = self.thisMObject()
        plug = OpenMaya.MPlug(thisNode, self.input)
        plug = plug.elementByLogicalIndex(geomIter.index())
        dataHandle = plug.asMDataHandle()
        inputGeom = dataHandle.asMesh()

        # Original positions of vertices
        origPoints = OpenMaya.MPointArray()
        inputGeom.getPoints(origPoints)

        # Current position
        currentPoint = geomIter.position()

        # Calculate average change in distance to adjacent vertices
        # Initialize variables for distance calculation
        totalDistChange = 0.0
        numAdjacentVerts = 0

        # Get the list of connected vertices
        connectedVertices = OpenMaya.MIntArray()
        geomIter.getConnectedVertices(connectedVertices)

        for i in range(connectedVertices.length()):
            # Original and current position of the connected vertex
            origPosConnected = origPoints[connectedVertices[i]]
            currentPosConnected = geomIter.setPosition(connectedVertices[i])

            # Calculate distance change
            origDist = (origPosConnected - origPoints[geomIter.index()]).length()
            currentDist = (currentPosConnected - currentPoint).length()

            # Accumulate the change in distance
            distChange = origDist - currentDist
            if distChange > 0:  # Consider only compression, not expansion
                totalDistChange += distChange
                numAdjacentVerts += 1

            # Reset the iterator's position
            geomIter.setPosition(currentPoint)

        # Calculate average compression factor
        if numAdjacentVerts > 0:
            avgDistChange = totalDistChange / numAdjacentVerts
            compressionFactor = min(avgDistChange, 1.0)  # Normalize to a maximum of 1
        else:
            compressionFactor = 0.0

        return compressionFactor
    
    @staticmethod
    def creator():
        return OpenMayaMPx.asMPxPtr(WrinkleDeformer())

    @staticmethod
    def initialize():
        nAttr = OpenMaya.MFnNumericAttribute()

        # Create intensity attribute
        WrinkleDeformer.intensityAttr = nAttr.create("intensity", "int", OpenMaya.MFnNumericData.kFloat, 0.0)
        nAttr.setKeyable(True)
        nAttr.setStorable(True)
        nAttr.setWritable(True)
        nAttr.setReadable(True)
        nAttr.setMin(0.0)
        nAttr.setMax(1.0)
        WrinkleDeformer.addAttribute(WrinkleDeformer.intensityAttr)

        # Create paint map attribute
        WrinkleDeformer.paintMapAttr = nAttr.create("paintMap", "pm", OpenMaya.MFnNumericData.kFloat, 0.0)
        nAttr.setArray(True)
        nAttr.setUsesArrayDataBuilder(True)
        WrinkleDeformer.addAttribute(WrinkleDeformer.paintMapAttr)

        # Set affects
        outputGeom = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom
        WrinkleDeformer.attributeAffects(WrinkleDeformer.intensityAttr, outputGeom)
        WrinkleDeformer.attributeAffects(WrinkleDeformer.paintMapAttr, outputGeom)

# Initialize the plugin when Maya loads it
def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, "Your Name", "1.0", "Any")
    plugin.registerNode(WrinkleDeformer.kPluginNodeName, WrinkleDeformer.kPluginNodeId, 
                        WrinkleDeformer.creator, WrinkleDeformer.initialize, OpenMayaMPx.MPxNode.kDeformerNode)

# Uninitialize the plugin when Maya unloads it
def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    plugin.deregisterNode(WrinkleDeformer.kPluginNodeId)
