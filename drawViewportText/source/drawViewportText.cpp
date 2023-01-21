#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/M3dView.h>
#include <maya/MDrawContext.h>
#include <maya/MGlobal.h>

class TextLocator : public MPxLocatorNode
{
public:
    TextLocator();
    virtual ~TextLocator();

    virtual void draw(M3dView& view, const MDagPath& path, M3dView::DisplayStyle style, M3dView::DisplayStatus status);

    static void* creator();
    static MStatus initialize();

    static MTypeId id;
    static MObject aText;
};

void TextLocator::draw(M3dView& view, const MDagPath& path, M3dView::DisplayStyle style, M3dView::DisplayStatus status)
{
    MObject thisNode = thisMObject();
    MString text;
    MGlobal::executeCommand("getAttr " + MString(thisNode.partialPathName()) + ".text", text);

    if (status == M3dView::kActive || status == M3dView::kLead)
    {
        view.beginGL();
        glPushAttrib(GL_CURRENT_BIT);

        // Get the camera's position and view direction
        MPoint cameraPos;
        MVector cameraDirection;
        view.getCamera(cameraPos, cameraDirection);
        cameraDirection = -cameraDirection;

        // Get the position of the locator
        MPoint locatorPos = path.inclusiveMatrix() * MPoint::origin;

        // Calculate the text's position
        MPoint textPos = locatorPos + (cameraDirection * 0.1);

        // Draw text
        glColor3f(1.0, 0.0, 0.0);
        view.drawText(text, textPos, M3dView::kLeft);

        glPopAttrib();
        view.endGL();
    }
    else
    {
        // Draw locator shape
        MPxLocatorNode::draw(view, path, style, status);
    }
}

MStatus TextLocator::initialize()
{
    MFnNumericAttribute nAttr;
    aText = nAttr.create("text", "txt", MFnNumericData::kString);
    nAttr.setStorable(true);
    addAttribute(aText);
    attributeAffects(aText, outputGeom);

    return MS::kSuccess;
}

void* TextLocator::creator()
{
    return new TextLocator();
}

MStatus initializePlugin(MObject obj)
{
    MFnPlugin plugin(obj, "MyPlugin", "1.0", "Any");
    plugin.registerNode("textLocator", TextLocator::id, TextLocator::creator, TextLocator::initialize);

    return MS::kSuccess;
}
