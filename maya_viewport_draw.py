import sys, json
import maya.cmds as cmds
import maya.mel as mel

import maya.OpenMaya as OpenMayav1
import maya.OpenMayaUI as OpenMayaUIv1
import maya.OpenMayaRender as OpenMayaRenderv1

import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.api.OpenMayaAnim as OpenMayaAnim
import maya.api.OpenMayaRender as OpenMayaRender

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass
IMAGEPATH = "file_path"
#############################################################################
##
## Node implementation with standard viewport draw
##
#############################################################################
class TestNode(OpenMayaUI.MPxLocatorNode):
    id = OpenMaya.MTypeId( 0x82307 )
    drawDbClassification = "drawdb/geometry/TestNode"
    drawRegistrantId = "TestNodePlugin"

    @staticmethod
    def creator():
        return TestNode()

    @staticmethod
    def initialize():
        pass

    def __init__(self):
        OpenMayaUI.MPxLocatorNode.__init__(self)
        # Getting all the Information

    def compute(self, plug, data):
        return None

    def draw(self, view, path, style, status):
    
        # Getting the OpenGL renderer
        glRenderer = OpenMayaRenderv1.MHardwareRenderer.theRenderer()
        # Getting all classes from the renderer
        glFT = glRenderer.glFunctionTable()
        
         # Pushed current state
        glFT.glPushAttrib( OpenMayaRenderv1.MGL_CURRENT_BIT )
        # Enabled Blend mode (to enable transparency)
        glFT.glEnable( OpenMayaRenderv1.MGL_BLEND )
        # Defined Blend function
        glFT.glBlendFunc( OpenMayaRenderv1.MGL_SRC_ALPHA, OpenMayaRenderv1.MGL_ONE_MINUS_SRC_ALPHA )
        # create x-ray view and will be seen always
        glFT.glDisable( OpenMayaRenderv1.MGL_DEPTH_TEST )
    
        # Starting the OpenGL drawing
        view.beginGL()
    
        # Getting the active viewport
        activeView = view.active3dView()
        
        # Setting a color for Viewport draw
        view.setDrawColor( OpenMaya.MColor( (1.0, 1.0, 1.0, 1.0) ) )
        
        # Writing text on 3D space
        view.drawText("3D SPACE TEXT", OpenMaya.MPoint(0,1,0), OpenMayaUIv1.M3dView.kCenter )
        
        # Getting the near and far plane for the viewport
        textPositionNearPlane = OpenMaya.MPoint()
        textPositionFarPlane = OpenMaya.MPoint()
        
        # Setting a color for Viewport draw
        view.setDrawColor( OpenMaya.MColor( (0.5, 0.3, 0.4, 1.0) ) )
        
        # Writing text in 2D space(drawing on the viewport plane)
        activeView.viewToWorld(500, 500, textPositionNearPlane, textPositionFarPlane )
        activeView.drawText("2D SPACE TEXT", textPositionNearPlane, OpenMayaUI.M3dView.kCenter )
            
        # Drawing Image on Viewport
        image = OpenMaya.MImage()
        # Import image from a path
        image.readFromFile(IMAGEPATH)
        # Writing the image on viewport with the given x, y coordinates
        view.writeColorBuffer(image, 100, 100)
        
        # Disable Blend mode
        glFT.glDisable( OpenMayaRenderv1.MGL_BLEND )
        glFT.glEnable( OpenMayaRenderv1.MGL_DEPTH_TEST )
        # Restore the state
        glFT.glPopAttrib()
        # Ending the OpenGL drawing
        view.endGL()
    

#############################################################################
##
## Viewport 2.0 override implementation
##
#############################################################################
class TestNodeData(OpenMaya.MUserData):
    def __init__(self):
        OpenMaya.MUserData.__init__(self, False) ## don't delete after draw


class TestNodeDrawOverride(OpenMayaRender.MPxDrawOverride):
    @staticmethod
    def creator(obj):
        return TestNodeDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return

    def __init__(self, obj):
        OpenMayaRender.MPxDrawOverride.__init__(self, obj, TestNodeDrawOverride.draw)
        
    def supportedDrawAPIs(self):
        ## this plugin supports both GL and DX
        return OpenMayaRender.MRenderer.kOpenGL | OpenMayaRender.MRenderer.kDirectX11 | OpenMayaRender.MRenderer.kOpenGLCoreProfile

    def prepareForDraw(self, objPath, cameraPath, frameContext, oldData):
        ## Retrieve data cache (create if does not exist)
        data = oldData
        if not isinstance(data, TestNodeData):
            data = TestNodeData()

        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, objPath, drawManager, frameContext, data):
        locatordata = data
        if not isinstance(locatordata, TestNodeData):
            return
        drawManager.beginDrawable()

        textColor = OpenMaya.MColor((1.0,1.0,1.0, 1.0))
        drawManager.setColor( textColor )

        drawManager.text( OpenMaya.MPoint(0, 1, 0), "3D SPACE TEXT", OpenMayaRender.MUIDrawManager.kCenter )

        textColor = OpenMaya.MColor((0.5, 0.3, 0.4, 1.0))
        drawManager.setColor( textColor )

        drawManager.text2d( OpenMaya.MPoint(500, 500), "2D SPACE TEXT", OpenMayaRender.MUIDrawManager.kCenter )

        drawManager.endDrawable()

        
def initializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj, "Name", "1.0", "Any")

    try:
        plugin.registerNode("TestNode", TestNode.id, TestNode.creator, TestNode.initialize, OpenMaya.MPxNode.kLocatorNode, TestNode.drawDbClassification)
    except:
        sys.stderr.write("Failed to register node\n")
        raise

    try:
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator(TestNode.drawDbClassification, TestNode.drawRegistrantId, TestNodeDrawOverride.creator)
    except:
        sys.stderr.write("Failed to register override\n")
        raise

def uninitializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj)

    try:
        plugin.deregisterNode(TestNode.id)
    except:
        sys.stderr.write("Failed to deregister node\n")
        pass

    try:
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator(TestNode.drawDbClassification, TestNode.drawRegistrantId)
    except:
        sys.stderr.write("Failed to deregister override\n")
        pass
