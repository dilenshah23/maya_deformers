#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMesh.h>
#include <maya/MItGeometry.h>
#include <maya/MPxDeformerNode.h>

class WrinkleDeformer : public MPxDeformerNode
{
public:
    WrinkleDeformer();
    virtual ~WrinkleDeformer();

    static void* creator();
    static MStatus initialize();

    virtual MStatus deform(MDataBlock& data, MItGeometry& itGeo, const MMatrix& localToWorldMatrix, unsigned int geomIndex);

    static MTypeId id;
    static MObject aAmount;
    static MObject aDirection;
};

MTypeId WrinkleDeformer::id(0x100000);
MObject WrinkleDeformer::aAmount;
MObject WrinkleDeformer::aDirection;

WrinkleDeformer::WrinkleDeformer() {}
WrinkleDeformer::~WrinkleDeformer() {}

void* WrinkleDeformer::creator()
{
    return new WrinkleDeformer();
}

MStatus WrinkleDeformer::initialize()
{
    MFnNumericAttribute nAttr;
    aAmount = nAttr.create("amount", "amt", MFnNumericData::kFloat, 1.0);
    nAttr.
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMesh.h>
#include <maya/MItGeometry.h>
#include <maya/MPxDeformerNode.h>

class WrinkleDeformer : public MPxDeformerNode
{
public:
    WrinkleDeformer();
    virtual ~WrinkleDeformer();

    static void* creator();
    static MStatus initialize();

    virtual MStatus deform(MDataBlock& data, MItGeometry& itGeo, const MMatrix& localToWorldMatrix, unsigned int geomIndex);

    static MTypeId id;
    static MObject aAmount;
    static MObject aDirection;
};

MTypeId WrinkleDeformer::id(0x100000);
MObject WrinkleDeformer::aAmount;
MObject WrinkleDeformer::aDirection;

WrinkleDeformer::WrinkleDeformer() {}
WrinkleDeformer::~WrinkleDeformer() {}

void* WrinkleDeformer::creator()
{
    return new WrinkleDeformer();
}

MStatus WrinkleDeformer::initialize()
{
    MFnNumericAttribute nAttr;
    aAmount = nAttr.create("amount", "amt", MFnNumericData::kFloat, 1.0);
    nAttr.setKeyable(true);
    addAttribute(aAmount);
    attributeAffects(aAmount, outputGeom);

    aDirection = nAttr.create("direction", "dir", MFnNumericData::kFloat, 1.0);
    nAttr.setKeyable(true);
    addattribute(aDirection);
    attributeAffects(aDirection, outputGeom);

    return MS::kSuccess;
}

MStatus WrinkleDeformer::deform(MDataBlock& data, MItGeometry& itGeo, const MMatrix& localToWorldMatrix, unsigned int geomIndex)
{
    MStatus status;

    float amount = data.inputValue(aAmount).asFloat();
    float direction = data.inputValue(aDirection).asFloat();

    MFnMesh fnMesh(inputGeom, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    for (; !itGeo.isDone(); itGeo.next()) {
        MPoint point = itGeo.position();
        float wrinkle = amount * (1 - direction * point.y);
        point.x += wrinkle;
        fnMesh.setPoint(itGeo.index(), point, MSpace::kObject);
    }

    return MS::kSuccess;
}
