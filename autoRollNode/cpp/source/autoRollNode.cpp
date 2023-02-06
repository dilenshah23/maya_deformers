#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MVector.h>
#include <maya/MMatrix.h>
#include <maya/MEulerRotation.h>
#include <maya/MQuaternion.h>
#include <maya/MFnDependencyNode.h>

class AutoRollNode : public MPxNode
{
public:
    AutoRollNode();
    virtual ~AutoRollNode();
    static void* creator();
    static MStatus initialize();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);

private:
    static MObject m_inputMatrix;
    static MObject m_forwardVector;
    static MObject m_outputRotation;
};

MTypeId AutoRollNode::id(0x0011AEF0);
MObject AutoRollNode::m_inputMatrix;
MObject AutoRollNode::m_forwardVector;
MObject AutoRollNode::m_outputRotation;

AutoRollNode::AutoRollNode() {}
AutoRollNode::~AutoRollNode() {}

void* AutoRollNode::creator()
{
    return new AutoRollNode();
}

MStatus AutoRollNode::initialize()
{
    MStatus status;
    MFnMatrixAttribute mAttr;
    MFnNumericAttribute nAttr;
    MFnUnitAttribute uAttr;

    m_inputMatrix = mAttr.create("inputMatrix", "im", MFnMatrixAttribute::Type, &status);
    mAttr.setStorable(true);
    addAttribute(m_inputMatrix);

    m_forwardVector = nAttr.createPoint("forwardVector", "fv", &status);
    nAttr.setStorable(true);
    addAttribute(m_forwardVector);

    m_outputRotation = uAttr.create("outputRotation", "or", MFnUnitAttribute::kAngle, 0.0, &status);
    uAttr.setStorable(false);
    uAttr.setWritable(false);
    addAttribute(m_outputRotation);

    attributeAffects(m_inputMatrix, m_outputRotation);
    attributeAffects(m_forwardVector, m_outputRotation);

    return MS::kSuccess;
}

MStatus AutoRollNode::compute(const MPlug& plug, MDataBlock& data)
{
    MStatus status;
    if (plug != m_outputRotation)
    {
        return MS::kUnknownParameter;
    }

    MMatrix inputMatrix = data.inputValue(m_inputMatrix).asMatrix();
    MVector forwardVector = data.inputValue(m_forwardVector).asVector;
    
    MVector forwardProjection = forwardVector * inputMatrix;
    forwardProjection.normalize();
    
    MVector upVector = MVector::up;
    MVector upProjection = upVector * inputMatrix;
    upProjection.normalize();

    MVector rightVector = forwardProjection ^ upProjection;
    rightVector.normalize();

    MVector upRoll = upVector * (rightVector * upVector);
    upRoll.normalize();

    MQuaternion targetRotation = MQuaternion(upVector, upRoll);

    MDataHandle outputRotationHandle = data.outputValue(m_outputRotation);
    outputRotationHandle.set(targetRotation.asEulerRotation());
    outputRotationHandle.setClean();

    return MS::kSuccess;
}


void* AutoRollNode::creator()
{
return new AutoRollNode();
}
