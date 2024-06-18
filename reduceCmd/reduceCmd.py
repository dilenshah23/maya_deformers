import maya.api.OpenMaya as om
import maya.cmds as cmds

class ReduceCmd(om.MPxCommand):
    def __init__(self):
        om.MPxCommand.__init__(self)
        self.mMesh = cmds.ls(selection=True)[0]
        self.mLeastCost = []
        self.mCollapseVert = []
        self.mEdgeFaces = []
        self.m_percentage = 0
        self.m_count = 0
        self.m_basePath = None

    @staticmethod
    def creator():
        return ReduceCmd()

    @staticmethod
    def newSyntax():
        syntax = om.MSyntax()
        syntax.addFlag("-p", "-percentage", om.MSyntax.kUnsigned)
        syntax.setObjectType(om.MSyntax.kSelectionList, 1, 1)
        syntax.useSelectionAsDefault(True)
        syntax.enableEdit(False)
        syntax.enableQuery(False)
        return syntax

    def isUndoable(self):
        return False

    def getShapeNode(self, path):
        if path.apiType() == om.MFn.kMesh:
            return om.MStatus.kSuccess

        numShapes = path.numberOfShapesDirectlyBelow()
        for i in range(numShapes):
            path.extendToShapeDirectlyBelow(i)
            if not path.hasFn(om.MFn.kMesh):
                path.pop()
                continue

            fnNode = om.MFnDagNode(path)
            if not fnNode.isIntermediateObject():
                return om.MStatus.kSuccess
            path.pop()
        return om.MStatus.kFailure

    def doIt(self, argList):
        argData = om.MArgDatabase(self.syntax(), argList)
        selectedObj = argData.getObjects()
        selectedObj.getDagPath(0, self.m_basePath)
        if self.getShapeNode(self.m_basePath) != om.MStatus.kSuccess:
            om.MGlobal.displayError("Please select a polygon mesh")
            return om.MStatus.kFailure

        self.m_percentage = argData.flagArgumentInt("-p", 0)

        fnMesh = om.MFnMesh(self.m_basePath)
        vertices = fnMesh.getPoints(om.MSpace.kWorld)
        edges = fnMesh.getEdgeVertices()
        faces = fnMesh.getVertices()

        self.computeAllEdgeCosts()

        target_count = int(len(vertices) * (1 - self.m_percentage / 100.0))
        while len(vertices) > target_count:
            minCostIndex = self.findMinCostVert()
            u, v = edges[minCostIndex]
            self.collapse(u, v)
            vertices = fnMesh.getPoints(om.MSpace.kWorld)
            edges = fnMesh.getEdgeVertices()
            self.computeAllEdgeCosts()

        return om.MStatus.kSuccess

    def computeAllEdgeCosts(self):
        self.mLeastCost = []
        fnMesh = om.MFnMesh(self.m_basePath)
        edges = fnMesh.getEdgeVertices()
        for u, v in edges:
            cost = self.computeEdgeCost(u, v)
            self.mLeastCost.append(cost)

    def computeEdgeCost(self, u, v):
        fnMesh = om.MFnMesh(self.m_basePath)
        pointU = fnMesh.getPoint(u, om.MSpace.kWorld)
        pointV = fnMesh.getPoint(v, om.MSpace.kWorld)
        edgeLength = (pointU - pointV).length()
        return edgeLength

    def collapse(self, u, v):
        fnMesh = om.MFnMesh(self.m_basePath)
        points = fnMesh.getPoints(om.MSpace.kWorld)
        midpoint = (points[u] + points[v]) / 2
        points[u] = midpoint
        points[v] = midpoint
        fnMesh.setPoints(points, om.MSpace.kWorld)

    def findMinCostVert(self):
        leastIndex = 0
        for i in range(len(self.mLeastCost)):
            if self.mLeastCost[i] < self.mLeastCost[leastIndex]:
                leastIndex = i
        return leastIndex

def initializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject, "dilens", "0.1", "2024")
    try:
        mplugin.registerCommand("reduceCmd", ReduceCmd.creator, ReduceCmd.newSyntax)
    except:
        om.MGlobal.displayError("Failed to register command: reduceCmd")

def uninitializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand("reduceCmd")
    except:
        om.MGlobal.displayError("Failed to deregister command: reduceCmd")