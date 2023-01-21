#ifndef __WRINKLEDEFORMER_H__
#define __WRINKLEDEFORMER_H__

#include <maya/MPxDeformerNode.h>
#include <maya/MDataBlock.h>
#include <maya/MItGeometry.h>
#include <maya/MTypeId.h>
#include <maya/MFnNumericAttribute.h>

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

#endif // __WRINKLEDEFORMER_H__
