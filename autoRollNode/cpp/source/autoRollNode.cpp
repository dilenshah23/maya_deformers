#include <maya/MFnNumericAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MTypeId.h>
#include <maya/MMatrix.h>
#include <maya/MVector.h>
#include <maya/MPxNode.h>
#include <maya/MGlobal.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MTime.h>
#include <math.h>

class AutoRollNode : public MPxNode {
public:
    AutoRollNode() {}
    virtual ~AutoRollNode() {}
    static void* creator() { return new AutoRollNode(); }
    static MStatus initialize();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);

    static MTypeId typeId;
    static MObject distance;
    static MObject radius;
    static MObject speed;
    static MObject axis;
    static MObject direction;
    static MObject inMatrix;
    static MObject outMatrix;
    static MObject outRoll;
    static MObject outPitch;
    static MObject outYaw;
};

MTypeId AutoRollNode::typeId(0x80005);
MObject AutoRollNode::distance;
MObject AutoRollNode::radius;
MObject AutoRollNode::speed;
MObject AutoRollNode::axis;
MObject AutoRollNode::direction;
MObject AutoRollNode::inMatrix;
MObject AutoRollNode::outMatrix;
MObject AutoRollNode::outRoll;
MObject AutoRollNode::outPitch;
MObject AutoRollNode::outYaw;

MStatus AutoRollNode::initialize() {
    MFnNumericAttribute nAttr;
    MFnEnumAttribute eAttr;
    MFnMatrixAttribute mAttr;
    MFnCompoundAttribute cAttr;
    MFnUnitAttribute uAttr;

    // Create the input attributes
    distance = nAttr.create("distance", "dist", MFnNumericData::kDouble, 0.0);
    nAttr.setKeyable(true);
    nAttr.setMin(0.0);
    nAttr.setSoftMax(100.0);
    radius = nAttr.create("radius", "rad", MFnNumericData::kDouble, 1.0);
    nAttr.setKeyable(true);
    nAttr.setMin(0.0);
    speed = nAttr.create("speed", "spd", MFnNumericData::kDouble, 1.0);
    nAttr.setKeyable(true);
    nAttr.setMin(0.0);
    axis = eAttr.create("axis", "axs", 0);
    eAttr.addField("X", 0);
    eAttr.addField("Y", 1);
    eAttr.addField("Z", 2);
    direction = eAttr.create("direction", "dir", 0);
    eAttr.addField("Forward", 0);
    eAttr.addField("Backward", 1);

    // Create the output attributes
    outMatrix = mAttr.create("outMatrix", "omat");
    outRoll = uAttr.create("outRoll", "orol", MFnUnitAttribute::kAngle, 0.0);
    outPitch = uAttr.create("outPitch", "opit", MFnUnitAttribute::kAngle, 0.0);
    ("outYaw", "oyaw", MFnUnitAttribute::kAngle, 0.0);

    // Create the compound attribute for the rotation values
    MFnDependencyNode depFn;
    MObject rotCompound = depFn.create("rotation", "rot");
    depFn.addAttribute(outRoll);
    depFn.addAttribute(outPitch);
    depFn.addAttribute(outYaw);

    // Create the input and output matrix attributes
    inMatrix = mAttr.create("inMatrix", "imat");
    mAttr.setStorable(true);
    mAttr.setConnectable(true);
    mAttr.setKeyable(false);
    mAttr.setHidden(true);
    addAttribute(inMatrix);
    attributeAffects(inMatrix, outMatrix);

    // Create the attribute dependencies
    addAttribute(distance);
    addAttribute(radius);
    addAttribute(speed);
    addAttribute(axis);
    addAttribute(direction);
    addAttribute(outMatrix);
    attributeAffects(distance, outMatrix);
    attributeAffects(radius, outMatrix);
    attributeAffects(speed, outMatrix);
    attributeAffects(axis, outMatrix);
    attributeAffects(direction, outMatrix);

    // Add the output attributes to the node
    addAttribute(outMatrix);
    addAttribute(rotCompound);

    return MS::kSuccess;
}

MStatus AutoRollNode::compute(const MPlug& plug, MDataBlock& data) {
    if (plug != outMatrix && plug.parent() != outMatrix && plug != outRoll && plug != outPitch && plug != outYaw) {
        return MS::kUnknownParameter;
    }
    // Get the input data
    MMatrix matrix = data.inputValue(inMatrix).asMatrix();
    double dist = data.inputValue(distance).asDouble();
    double rad = data.inputValue(radius).asDouble();
    double spd = data.inputValue(speed).asDouble();
    int axs = data.inputValue(axis).asShort();
    int dir = data.inputValue(direction).asShort();

    // Get the position and direction from the matrix
    MVector pos = MVector(matrix[3][0], matrix[3][1], matrix[3][2]);
    MVector dirVec = MVector(matrix(axs, 0), matrix(axs, 1), matrix(axs, 2));
    if (dir == 1) {
        dirVec *= -1.0;
    }

    // Calculate the rotation angle based on the distance travelled
    double angle = (dist / (2 * M_PI * rad)) * 360.0;
    angle *= dirVec * MVector(1.0, 0.0, 0.0);
    angle *= spd;
    angle = fmod(angle, 360.0);

    // Calculate the new matrix with the rotation applied
    MMatrix rotMatrix = MMatrix::rotation(angle * M_PI / 180.0, dirVec) * matrix;
    MDataHandle outMatrixHandle = data.outputValue(outMatrix);
    outMatrixHandle.setMMatrix(rotMatrix);

    // Calculate the roll, pitch, and yaw values from the matrix
    double roll, pitch, yaw;
    MTransformationMatrix transMatrix(rotMatrix);
    transMatrix.getRotation().getValues(roll, pitch, yaw);
    roll *= 180.0 / M_PI;
    pitch *= 180.0 / M_PI;
    yaw *= 180.0 / M_PI;
    MDataHandle outRollHandle = data.outputValue(outRoll);
    outRollHandle.setDouble(roll);
    MDataHandle outPitchHandle = data.outputValue(outPitch);
    outPitchHandle.setDouble(pitch);
    MDataHandle outYawHandle = data.outputValue(outYaw);
    outYawHandle.setDouble(yaw);
    
    // Set the output data
    data.setClean(plug);
    
    return MS::kSuccess;
}

void* AutoRollNode::creator() {
    return new AutoRollNode();
}

MStatus initializePlugin(MObject obj) {
    MFnPlugin plugin(obj, "AutoRollNode", "1.0", "Any");
    MStatus status = plugin.registerNode("autoRoll", AutoRollNode::id, AutoRollNode::creator, AutoRollNode::initialize);
    if (!status) {
        status.perror("registerNode");
        return status;
    }

    return MS::kSuccess;
}

MStatus uninitializePlugin(MObject obj) {
    MFnPlugin plugin(obj);
    MStatus status = plugin.deregisterNode(AutoRollNode::id);
    if (!status) {
        status.perror("deregisterNode");
        return status;
    }

    return MS::kSuccess;
}



