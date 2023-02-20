#include <maya/MPxNode.h>
#include <maya/MTypeId.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MMatrix.h>
#include <maya/MGlobal.h>

class AutoRollNode : public MPxNode
{
public:
    static void* creator();
    static MStatus initialize();

    virtual MStatus compute(const MPlug& plug, MDataBlock& data);

    static MObject aDistance;
    static MObject aDirection;
    static MObject aInputMatrix;
    static MObject aOutputMatrix;

    static MTypeId id;
};

MObject AutoRollNode::aDistance;
MObject AutoRollNode::aDirection;
MObject AutoRollNode::aInputMatrix;
MObject AutoRollNode::aOutputMatrix;

MTypeId AutoRollNode::id(0x00000001);

void* AutoRollNode::creator()
{
    return new AutoRollNode();
}

MStatus AutoRollNode::initialize()
{
    MFnUnitAttribute uAttr;
    MFnNumericAttribute nAttr;
    MFnTypedAttribute tAttr;

    aDistance = uAttr.create("distance", "d", MFnUnitAttribute::kDistance);
    uAttr.setKeyable(true);
    uAttr.setStorable(true);
    uAttr.setWritable(true);
    uAttr.setReadable(true);
    uAttr.setDefault(0.0);

    aDirection = nAttr.createPoint("direction", "dir");
    nAttr.setKeyable(true);
    nAttr.setStorable(true);
    nAttr.setWritable(true);
    nAttr.setReadable(true);
    nAttr.setDefault(1.0, 0.0, 0.0);

    aInputMatrix = tAttr.create("inputMatrix", "imat", MFnData::kMatrix);
    tAttr.setStorable(false);
    tAttr.setKeyable(false);
    tAttr.setReadable(true);

    aOutputMatrix = tAttr.create("outputMatrix", "omat", MFnData::kMatrix);
    tAttr.setStorable(false);
    tAttr.setKeyable(false);
    tAttr.setWritable(false);
    tAttr.setReadable(true);

    addAttribute(aDistance);
    addAttribute(aDirection);
    addAttribute(aInputMatrix);
    addAttribute(aOutputMatrix);

    attributeAffects(aDistance, aOutputMatrix);
    attributeAffects(aDirection, aOutputMatrix);
    attributeAffects(aInputMatrix, aOutputMatrix);

    return MS::kSuccess;
}

MStatus AutoRollNode::compute(const MPlug& plug, MDataBlock& data)
{
    if (plug != m_outputRotation)
    {
        return MS::kUnknownParameter;
    }

    MStatus status;
    double deltaTime = data.inputValue(m_deltaTime).asDouble();
    double distance = data.inputValue(m_distance).asDouble();
    double wheelRadius = data.inputValue(m_wheelRadius).asDouble();

    // calculate wheel rotation
    double wheelCircumference = 2 * M_PI * wheelRadius;
    double rotation = (distance / wheelCircumference) * 360.0;

    // calculate roll based on velocity
    double roll = 0.0;
    MVector velocity = data.inputValue(m_velocity).asVector();
    if (!velocity.isZero())
    {
        velocity.normalize();
        MVector upVector(0.0, 1.0, 0.0);
        roll = -MVector::angle(velocity, upVector) * 180.0 / M_PI;
    }

    // set output rotation
    MFnMatrixAttribute matrixAttr;
    MMatrix inputMatrix = data.inputValue(m_inputMatrix).asMatrix();
    MQuaternion rotationQuaternion(MVector(0.0, 1.0, 0.0), rotation);
    MQuaternion rollQuaternion(MVector(1.0, 0.0, 0.0), roll);
    MMatrix rotationMatrix = rotationQuaternion.asMatrix();
    MMatrix rollMatrix = rollQuaternion.asMatrix();
    MMatrix outputMatrix = inputMatrix * rollMatrix * rotationMatrix;
    MDataHandle outputHandle = data.outputValue(m_outputRotation);
    outputHandle.setMMatrix(outputMatrix);
    data.setClean(plug);

    return MS::kSuccess;
}

