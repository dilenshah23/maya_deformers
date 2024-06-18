from maya.api import OpenMaya as om2

def maya_useNewAPI():
    pass

class FrameRotationInterpolatorNode(om2.MPxNode):
    kNodeName = "frameRotationInterpolatorNode"
    kNodeID = om2.MTypeId(0x00122C)

    inputRotate = None
    inputTime = None
    outputRotate = None

    def __init__(self):
        om2.MPxNode.__init__(self)

    @staticmethod
    def creator():
        return FrameRotationInterpolatorNode()

    @staticmethod
    def initialize():
        nAttr = om2.MFnNumericAttribute()
        uAttr = om2.MFnUnitAttribute()

        # Input Rotation
        FrameRotationInterpolatorNode.inputRotate = nAttr.createPoint("inputRotate", "inR")
        FrameRotationInterpolatorNode.addAttribute(FrameRotationInterpolatorNode.inputRotate)

        # Input Time
        FrameRotationInterpolatorNode.inputTime = uAttr.create("inputTime", "inT", om2.MFnUnitAttribute.kTime, 0.0)
        FrameRotationInterpolatorNode.addAttribute(FrameRotationInterpolatorNode.inputTime)

        # Output Rotation
        FrameRotationInterpolatorNode.outputRotate = nAttr.createPoint("outputRotate", "outR")
        nAttr.writable = False
        nAttr.storable = False
        FrameRotationInterpolatorNode.addAttribute(FrameRotationInterpolatorNode.outputRotate)

        # Attribute affects
        FrameRotationInterpolatorNode.attributeAffects(FrameRotationInterpolatorNode.inputRotate, FrameRotationInterpolatorNode.outputRotate)
        FrameRotationInterpolatorNode.attributeAffects(FrameRotationInterpolatorNode.inputTime, FrameRotationInterpolatorNode.outputRotate)

    def compute(self, plug, dataBlock):
        if plug == FrameRotationInterpolatorNode.outputRotate:
            currentTime = dataBlock.inputValue(FrameRotationInterpolatorNode.inputTime).asTime().value
            inputRotateData = dataBlock.inputValue(FrameRotationInterpolatorNode.inputRotate).asVector()
            
            # Convert input Euler angles (degrees) to Quaternions for stable interpolation
            eulerCurrent = om2.MEulerRotation([om2.MAngle(angle, om2.MAngle.kDegrees).asRadians() for angle in inputRotateData])
            quatCurrent = eulerCurrent.asQuaternion()

            # Example: Estimate or calculate the next frame's rotation
            # In practice, this might come from another data source or estimation logic
            # Placeholder for next frame's rotation - this should be replaced with actual logic
            nextFrameRotateData = om2.MVector(inputRotateData.x + 1, inputRotateData.y + 1, inputRotateData.z + 1)  # Simplified example
            eulerNext = om2.MEulerRotation([om2.MAngle(angle, om2.MAngle.kDegrees).asRadians() for angle in nextFrameRotateData])
            quatNext = eulerNext.asQuaternion()

            # Interpolate between current and next quaternion based on a factor or logic defining the interpolation amount
            # For simplicity, using a fixed blend factor; in practice, this might be dynamic or based on specific conditions
            blendFactor = 0.5  # Example blend factor
            quatInterpolated = om2.MQuaternion.slerp(quatCurrent, quatNext, blendFactor)

            # Convert the interpolated quaternion back to Euler angles
            eulerInterpolated = quatInterpolated.asEulerRotation()
            outputRotate = om2.MVector(eulerInterpolated.x * om2.MAngle.kDegreesPerRadian, 
                                    eulerInterpolated.y * om2.MAngle.kDegreesPerRadian, 
                                    eulerInterpolated.z * om2.MAngle.kDegreesPerRadian)

            # Set the output value
            outputRotateData = dataBlock.outputValue(FrameRotationInterpolatorNode.outputRotate)
            outputRotateData.setMVector(outputRotate)
            dataBlock.setClean(plug)
        else:
            return om2.kUnknownParameter


# Plugin registration
def initializePlugin(plugin):
    pluginFn = om2.MFnPlugin(plugin)
    try:
        pluginFn.registerNode(SlerpRotationNode.kNodeName, SlerpRotationNode.kNodeID, SlerpRotationNode.creator, SlerpRotationNode.initialize)
    except:
        om2.MGlobal.displayError(f"Failed to register node: {SlerpRotationNode.kNodeName}")

def uninitializePlugin(plugin):
    pluginFn = om2.MFnPlugin(plugin)
