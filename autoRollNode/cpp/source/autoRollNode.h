#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MEulerRotation.h>

class AutoRoll : public MPxNode
{
public:
    AutoRoll();
    virtual ~AutoRoll();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);
    static void * creator();
    static MStatus initialize();

    static MTypeId id;

    static MObject inputTranslate;
    static MObject inputRotate;
    static MObject outputRotate;
};
