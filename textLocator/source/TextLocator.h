#ifndef __TEXT_LOCATOR_H__
#define __TEXT_LOCATOR_H__

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

#endif // __TEXT_LOCATOR_H__
