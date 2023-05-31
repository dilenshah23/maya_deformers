#ifndef AUTOROLLNODE_H
#define AUTOROLLNODE_H

#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnPlugin.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MMatrix.h>
#include <maya/MVector.h>
#include <maya/MQuaternion.h>
#include <maya/MTransformationMatrix.h>

class AutoRollNode : public MPxNode {
public:
    AutoRollNode();
    virtual ~AutoRollNode();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
    static void* creator();
    static MStatus initialize();

public:
    static MTypeId id;
    static MObject inMatrix;
    static MObject distance;
    static MObject radius;
    static MObject speed;
    static MObject axis;
    static MObject direction;
    static MObject outMatrix;
    static MObject outRoll;
    static MObject outPitch;
    static MObject outYaw;
};

#endif // AUTOROLLNODE_H
