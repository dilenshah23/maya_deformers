import maya.api.OpenMaya as om

class FeatherSlider(om.MPxDeformerNode):
    def __init__(self):
        om.MPxDeformerNode.__init__(self)

    def deform(self, data, itGeo, localToWorldMatrix, geomIndex):
        # Get the feather position matrix
        featherMatrix = self.getFeatherMatrix(data)

        # Iterate through the mesh vertices
        while not itGeo.isDone():
            # Get the vertex position
            position = itGeo.position()

            # Transform the position by the feather matrix
            newPosition = position * featherMatrix

            # Set the new position of the vertex
            itGeo.setPosition(newPosition)

            # Move to the next vertex
            itGeo.next()

    def getFeatherMatrix(self, data):
        # Get the feather matrix attribute
        featherMatrixAttr = data.inputValue(self.featherMatrixAttr)

        # Get the feather matrix value
        featherMatrix = featherMatrixAttr.asMatrix()

        return featherMatrix

    def nodeInitializer(self):
        # Create the feather matrix attribute
        mAttr = om.MFnMatrixAttribute()
        self.featherMatrixAttr = mAttr.create("featherMatrix", "fmat")
        mAttr.setStorable(True)

        # Add the attribute to the node
        self.addAttribute(self.featherMatrixAttr)

        # Set the attribute as affect
        self.attributeAffects(self.featherMatrixAttr, self.outputGeom)

# Initialize the plugin
def initializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    plugin.registerNode("featherSlider", FeatherSlider.kPluginNodeId, FeatherSlider.nodeInitializer, FeatherSlider.deform)

# Uninitialize the plugin
def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    plugin.deregisterNode(FeatherSlider.kPluginNodeId)
