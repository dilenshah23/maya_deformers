#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMesh.h>
#include <maya/MItGeometry.h>
#include <maya/MPxDeformerNode.h>

class CollisionDeformer : public MPxDeformerNode
{
public:
    CollisionDeformer();
    virtual ~CollisionDeformer();

    static void* creator();
    static MStatus initialize();

    virtual MStatus deform(MDataBlock& data, MItGeometry& itGeo, const MMatrix& localToWorldMatrix, unsigned int geomIndex);

    static MTypeId id;
    static MObject aBounciness;
    static MObject aFriction;
};

MTypeId CollisionDeformer::id(0x100000);
MObject CollisionDeformer::aBounciness;
MObject CollisionDeformer::aFriction;

CollisionDeformer::CollisionDeformer() {}
CollisionDeformer::~CollisionDeformer() {}

void* CollisionDeformer::creator()
{
    return new CollisionDeformer();
}

MStatus CollisionDeformer::initialize()
{
    MFnNumericAttribute nAttr;
    aBounciness = nAttr.create("bounciness", "b", MFnNumericData::kFloat, 1.0);
    nAttr.setKeyable(true);
    addAttribute(aBounciness);
    attributeAffects(aBounciness, outputGeom);

    aFriction = nAttr.create("friction", "f", MFnNumericData::kFloat, 0.5);
    nAttr.setKeyable(true);
    addAttribute(aFriction);
    attributeAffects(aFriction, outputGeom);

    return MS::kSuccess;
}

MStatus CollisionDeformer::deform(MDataBlock& data, MItGeometry& itGeo, const MMatrix& localToWorldMatrix, unsigned int geomIndex)
{
    MStatus status;

    float bounciness = data.inputValue(aBounciness).asFloat();
    float friction = data.inputValue(aFriction).asFloat();

    MFnMesh fnMesh(inputGeom, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    for (; !itGeo.isDone(); itGeo.next()) {
        MPoint point = it
        // perform collision calculations here
        // use bounciness and friction attributes to control the behavior
        // of the collision

        fnMesh.setPoint(itGeo.index(), point, MSpace::kObject);
    }

    return MS::kSuccess;
}
