#ifndef __COLLISIONDEFORMER_H__
#define __COLLISIONDEFORMER_H__

#include <maya/MPxDeformerNode.h>
#include <maya/MDataBlock.h>
#include <maya/MItGeometry.h>
#include <maya/MTypeId.h>
#include <maya/MFnNumericAttribute.h>

class CollisionDeformer : public MPxDeformerNode
{
public:
    CollisionDeformer();
    virtual ~CollisionDeformer();

    static void* creator();
    static MStatus initialize();
    virtual MStatus deform(MDataBlock& data, MItGeometry& itGeo, const MMatrix& localToWorldMatrix, unsigned int geomIndex);

    static MTypeId id;
    static MObject aCollisionNode;
    static MObject aBounce;
    static MObject aFriction;
};

#endif // __COLLISIONDEFORMER_H__
