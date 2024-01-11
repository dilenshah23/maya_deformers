#include "WrinkleDeformer.h"
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnPlugin.h>
#include <maya/MItGeometry.h>
#include <maya/MPointArray.h>
#include <maya/MFnMesh.h>

// Define the static members
MTypeId     WrinkleDeformer::id(0x0011E182); // Unique ID for the node
MObject     WrinkleDeformer::intensityAttr;  // Attribute for intensity
MObject     WrinkleDeformer::paintMapAttr;   // Attribute for paint map

WrinkleDeformer::WrinkleDeformer() {}

WrinkleDeformer::~WrinkleDeformer() {}

void* WrinkleDeformer::creator()
{
    return new WrinkleDeformer();
}

MStatus WrinkleDeformer::initialize()
{
    MFnNumericAttribute nAttr;

    // Create the intensity attribute
    intensityAttr = nAttr.create("intensity", "int", MFnNumericData::kFloat, 0.0);
    nAttr.setKeyable(true);
    nAttr.setStorable(true);
    nAttr.setWritable(true);
    nAttr.setReadable(true);
    nAttr.setMin(0.0);
    nAttr.setMax(1.0);
    addAttribute(intensityAttr);

    // Create the paint map attribute
    paintMapAttr = nAttr.create("paintMap", "pm", MFnNumericData::kFloat, 0.0);
    nAttr.setArray(true);
    nAttr.setUsesArrayDataBuilder(true);
    addAttribute(paintMapAttr);

    // Define the effect of the attributes on the deformer
    attributeAffects(intensityAttr, outputGeom);
    attributeAffects(paintMapAttr, outputGeom);

    return MS::kSuccess;
}

MStatus WrinkleDeformer::deform(MDataBlock& dataBlock, MItGeometry& iter, const MMatrix& mat, unsigned int multiIndex)
{
    // Get the intensity attribute value
    MDataHandle intensityHandle = dataBlock.inputValue(intensityAttr);
    float intensity = intensityHandle.asFloat();

    // Iterate over each point in the geometry
    for (; !iter.isDone(); iter.next()) 
    {
        // Get the original position of the current point
        MPoint point = iter.position();

        // Calculate compression for the current point
        float compression = calculateCompression(iter);

        // Apply the wrinkle effect based on intensity and compression
        point.y += intensity * compression; // Placeholder modification

        // Set the new position of the point
        iter.setPosition(point);
    }

    return MS::kSuccess;
}

float WrinkleDeformer::calculateCompression(MItGeometry& geomIter)
{
    MStatus status;

    // Get the thisMObject (the MObject representing this node)
    MObject thisNode = thisMObject();

    // Access the original mesh (rest state)
    MPlug inputPlug(thisNode, input);
    inputPlug = inputPlug.elementByLogicalIndex(geomIter.index());
    MDataHandle inputDataHandle = inputPlug.asMDataHandle();
    MObject inputDataObject = inputDataHandle.asMesh();
    
    // Original positions of vertices
    MFnMesh inputMeshFn(inputDataObject, &status);
    CHECK_MSTATUS_AND_RETURN(status, 0.0f);
    MPointArray origPoints;
    inputMeshFn.getPoints(origPoints, MSpace::kWorld);

    // Current position
    MPoint currentPoint = geomIter.position(MSpace::kWorld);

    // Initialize variables for distance calculation
    double totalDistChange = 0.0;
    int numAdjacentVerts = 0;

    // Get the list of connected vertices
    MIntArray connectedVertices;
    geomIter.getConnectedVertices(connectedVertices);

    for (unsigned int i = 0; i < connectedVertices.length(); ++i) {
        // Original and current position of the connected vertex
        MPoint origPosConnected = origPoints[connectedVertices[i]];
        geomIter.setPosition(connectedVertices[i]);
        MPoint currentPosConnected = geomIter.position(MSpace::kWorld);

        // Calculate distance change
        double origDist = (origPosConnected - origPoints[geomIter.index()]).length();
        double currentDist = (currentPosConnected - currentPoint).length();

        // Accumulate the change in distance
        double distChange = origDist - currentDist;
        if (distChange > 0) { // Consider only compression, not expansion
            totalDistChange += distChange;
            numAdjacentVerts++;
        }

        // Reset the iterator's position
        geomIter.setPosition(currentPoint, MSpace::kWorld);
    }

    // Calculate average compression factor
    float compressionFactor = 0.0f;
    if (numAdjacentVerts > 0) {
        double avgDistChange = totalDistChange / numAdjacentVerts;
        compressionFactor = static_cast<float>(std::min(avgDistChange, 1.0));
    }

    return compressionFactor;
}


// Plug-in initialization and uninitialization routines
MStatus initializePlugin(MObject obj)
{
    MFnPlugin plugin(obj, "Your Name", "1.0", "Any");
    plugin.registerNode("WrinkleDeformer", WrinkleDeformer::id, 
                        WrinkleDeformer::creator, 
                        WrinkleDeformer::initialize, 
                        MPxNode::kDeformerNode);

    return MS::kSuccess;
}

MStatus uninitializePlugin(MObject obj)
{
    MFnPlugin plugin(obj);
    plugin.deregisterNode(WrinkleDeformer::id);

    return MS::kSuccess;
}
