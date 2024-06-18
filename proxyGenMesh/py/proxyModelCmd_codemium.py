import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.cmds as cmds
import numpy as np
import heapq

class ProxyModelCmd(ompx.MPxCommand):
    kPluginCmdName = "generateProxyModel"

    def __init__(self):
        try:
            ompx.MPxCommand.__init__(self)
            self.reduction_percentage = 50  # Default reduction percentage
        except Exception as e:
            # Wrap the exception in a RuntimeError to preserve the original stack trace
            raise RuntimeError(str(e)).with_traceback(sys.exc_info()[2])

    def doIt(self, args):
        try:
            # Parse arguments
            argData = om.MArgDatabase(self.syntax(), args)
            if argData.isFlagSet("-r"):
                self.reduction_percentage = argData.flagArgumentDouble("-r", 0)
            
            sel = om.MSelectionList()
            om.MGlobal.getActiveSelectionList(sel)
            
            if sel.length() == 0:
                raise RuntimeError("No selection found")
            
            dagPath = om.MDagPath()
            sel.getDagPath(0, dagPath)
            
            fnMesh = om.MFnMesh(dagPath)
            
            vertices = om.MPointArray()
            fnMesh.getPoints(vertices, om.MSpace.kWorld)
            
            # Get the polygons
            polygons = []
            polyIter = om.MItMeshPolygon(dagPath)
            while not polyIter.isDone():
                polyVertices = om.MIntArray()
                polyIter.getVertices(polyVertices)
                polygons.append(list(polyVertices))
                polyIter.next()
            
            edges_to_keep = set()
            silhouette_edges = self.get_silhouette_edges(fnMesh, vertices)
            edges_to_keep.update(silhouette_edges)

            target_reduction = self.reduction_percentage / 100.0
            reduced_mesh = self.reduce_mesh(fnMesh, vertices, polygons, edges_to_keep, target_reduction)
            
            proxy_mesh = self.create_proxy_mesh(reduced_mesh)
            
            om.MGlobal.displayInfo("Proxy model created successfully")
        except Exception as e:
            # Wrap the exception in a RuntimeError to preserve the original stack trace
            raise RuntimeError(str(e)).with_traceback(sys.exc_info()[2])

    def get_silhouette_edges(self, fnMesh, vertices):
        try:
            silhouette_edges = set()
            view_direction = om.MVector(0, 0, 1)

            normals = fnMesh.getNormals(om.MSpace.kWorld)

            edgeIter = om.MItMeshEdge(fnMesh.object())
            while not edgeIter.isDone():
                faceIds = edgeIter.getConnectedFaces()

                if len(faceIds) == 2:
                    normal1 = om.MVector(*normals[faceIds[0]])
                    normal2 = om.MVector(*normals[faceIds[1]])

                    dot1 = normal1 * view_direction
                    dot2 = normal2 * view_direction

                    if (dot1 > 0 and dot2 < 0) or (dot1 < 0 and dot2 > 0):
                        silhouette_edges.add(edgeIter.index())

                edgeIter.next()

            return silhouette_edges
        except Exception as e:
            raise RuntimeError("Error in get_silhouette_edges: {}".format(str(e)))

    def reduce_mesh(self, fnMesh, vertices, polygons, edges_to_keep, target_reduction):
        initial_vertex_count = vertices.length()
        target_vertex_count = int(initial_vertex_count * (1.0 - target_reduction))

        quadrics = [np.zeros((4, 4)) for _ in range(vertices.length())]

        faceIter = om.MItMeshPolygon(fnMesh.object())
        while not faceIter.isDone():
            verts = om.MIntArray()
            faceIter.getVertices(verts)
            plane = self.calculate_plane(faceIter)

            for vert in verts:
                quadric = self.calculate_quadric(plane)
                quadrics[vert] += quadric

            faceIter.next()

        edge_heap = []
        edgeIter = om.MItMeshEdge(fnMesh.object())
        while not edgeIter.isDone():
            edge_index = edgeIter.index()
            if edge_index not in edges_to_keep:
                v1 = edgeIter.index(0)
                v2 = edgeIter.index(1)
                cost, new_pos = self.calculate_collapse_cost(v1, v2, quadrics[v1], quadrics[v2], vertices)
                heapq.heappush(edge_heap, (cost, edge_index, (new_pos.x, new_pos.y, new_pos.z)))

            edgeIter.next()

        collapsed_edges = set()
        while edge_heap and vertices.length() > target_vertex_count:
            cost, edge, new_pos_coords = heapq.heappop(edge_heap)
            new_pos = om.MPoint(new_pos_coords[0], new_pos_coords[1], new_pos_coords[2])
            if edge in collapsed_edges:
                continue

            index_ptr = om.MScriptUtil()
            index_ptr.createFromInt(0)
            index_ptr_ptr = index_ptr.asIntPtr()
            edgeIter.setIndex(edge, index_ptr_ptr)
            v1 = edgeIter.index(0)
            v2 = edgeIter.index(1)

            if not self.is_edge_valid(fnMesh, v1, v2):
                continue

            self.collapse_edge(fnMesh, v1, v2, new_pos)
            quadrics[v1] += quadrics[v2]
            quadrics[v2] = np.zeros((4, 4))
            collapsed_edges.add(edge)

            for edge in self.get_connected_edges(fnMesh, v1):
                if edge not in collapsed_edges:
                    edgeIter.setIndex(edge, index_ptr_ptr)
                    v1 = edgeIter.index(0)
                    v2 = edgeIter.index(1)
                    if v1 is None or v2 is None:
                        continue
                    cost, new_pos = self.calculate_collapse_cost(v1, v2, quadrics[v1], quadrics[v2], vertices)
                    heapq.heappush(edge_heap, (cost, edge, (new_pos.x, new_pos.y, new_pos.z)))

        reduced_vertices = om.MPointArray()
        fnMesh.getPoints(reduced_vertices, om.MSpace.kWorld)
        reduced_polygons = []
        polyIter = om.MItMeshPolygon(fnMesh.object())
        while not polyIter.isDone():
            polyVertices = om.MIntArray()
            polyIter.getVertices(polyVertices)
            reduced_polygons.append(list(polyVertices))
            polyIter.next()

        return reduced_vertices, reduced_polygons

    def calculate_plane(self, faceIter):
        points = faceIter.getPoints(om.MPointArray())
        if len(points) < 3:
            raise ValueError("Face has less than 3 vertices")

        p1, p2, p3 = points[:3]
        edge1 = p2 - p1
        edge2 = p3 - p1
        normal = edge1.cross(edge2)
        normal.normalize()

        d = - (normal.x * p1.x + normal.y * p1.y + normal.z * p1.z)
        return normal.x, normal.y, normal.z, d

    def calculate_quadric(self, plane):
        a, b, c, d = plane
        if any(map(lambda x: x is None, [a, b, c, d])):
            raise ValueError("Invalid plane parameters")
        
        q = np.array([
            [a ** 2, a * b, a * c, a * d],
            [a * b, b ** 2, b * c, b * d],
            [a * c, b * c, c ** 2, c * d],
            [a * d, b * d, c * d, d ** 2]
        ])
        return q

    def calculate_collapse_cost(self, v1, v2, q1, q2, vertices):
        # Check if vertices and q1, q2 are not None
        if vertices is None or q1 is None or q2 is None:
            raise ValueError("Invalid input parameters")

        # Check if indices are within the vertices array
        if v1 >= len(vertices) or v2 >= len(vertices):
            raise ValueError("Invalid vertex indices")

        q = q1 + q2

        # Calculate the position of the new vertex
        try:
            pos = np.linalg.solve(q[:3, :3], -q[:3, 3])
        except np.linalg.LinAlgError:
            pos = (np.array([vertices[v1].x, vertices[v1].y, vertices[v1].z]) +
                   np.array([vertices[v2].x, vertices[v2].y, vertices[v2].z])) * 0.5

        # Calculate the cost of collapsing the edge
        cost = np.dot(np.dot(pos, q[:3, :3]), pos) + 2 * np.dot(q[:3, 3], pos) + q[3, 3]

        # Create a new MPoint object
        new_pos = om.MPoint(pos[0], pos[1], pos[2])

        return cost, new_pos

    def is_edge_valid(self, fnMesh, v1, v2):
        """
        Check if the edge is valid for collapsing.
        Args:
            fnMesh (om.MFnMesh): The mesh object.
            v1 (int): The index of the first vertex.
            v2 (int): The index of the second vertex.
        Returns:
            bool: True if the edge is valid, False otherwise.
        """
        # Check if the edge indices are valid
        if v1 < 0 or v2 < 0 or v1 >= fnMesh.numVertices() or v2 >= fnMesh.numVertices():
            return False

        # Check if the edge is valid
        edgeIter = om.MItMeshEdge(fnMesh.object())
        while not edgeIter.isDone():
            if (edgeIter.index(0) == v1 and edgeIter.index(1) == v2) or (edgeIter.index(0) == v2 and edgeIter.index(1) == v1):
                break
            edgeIter.next()

        if edgeIter.isDone():
            return False  # Edge not found

        # Check for non-manifold edges
        connectedFaces = om.MIntArray()
        if not edgeIter.getConnectedFaces(connectedFaces) or connectedFaces.length() != 2:
            return False  # Non-manifold edge

        return True


    def collapse_edge(self, fnMesh, v1, v2, new_pos):
        if fnMesh is None:
            raise ValueError("Invalid fnMesh argument")
        if v1 < 0 or v2 < 0 or v1 >= fnMesh.numVertices() or v2 >= fnMesh.numVertices():
            raise ValueError("Invalid vertex indices")
        if new_pos is None:
            raise ValueError("Invalid new_pos argument")

        fnMesh.setPoint(v1, new_pos)
        fnMesh.setPoint(v2, new_pos)

    def get_connected_edges(self, fnMesh, vertex):
        if fnMesh is None:
            raise ValueError("Invalid fnMesh argument")
        if vertex < 0 or vertex >= fnMesh.numVertices():
            raise ValueError("Invalid vertex index")

        connected_edges = []
        vertexIter = om.MItMeshVertex(fnMesh.object())
        index_ptr = om.MScriptUtil()
        index_ptr.createFromInt(vertex)
        index_ptr_ptr = index_ptr.asIntPtr()
        vertexIter.setIndex(index_ptr_ptr)
        if not vertexIter.isDone() and vertexIter.index() == vertex:
            edges = om.MIntArray()
            vertexIter.getConnectedEdges(edges)
            for i in range(edges.length()):
                connected_edges.append(edges[i])
        return connected_edges

    def create_proxy_mesh(self, reduced_mesh):
        reduced_vertices, reduced_polygons = reduced_mesh

        if reduced_vertices is None or reduced_polygons is None:
            raise ValueError("Invalid reduced mesh")

        new_mesh_fn = om.MFnMesh()
        try:
            new_mesh_fn.create(reduced_vertices.length(), len(reduced_polygons), 
                               reduced_vertices, reduced_polygons, [], 
                               om.MObject())
        except RuntimeError as e:
            # Handle invalid arguments or creation failure
            raise ValueError("Failed to create mesh") from e

        new_mesh_name = new_mesh_fn.name()
        if new_mesh_name is None:
            raise ValueError("Failed to obtain mesh name")

        cmds.select(new_mesh_name)
        return new_mesh_name

def cmdCreator():
    try:
        return ompx.asMPxPtr(ProxyModelCmd())
    except Exception as e:
        # Wrap the exception in a RuntimeError to preserve the original stack trace
        raise RuntimeError(str(e)).with_traceback(sys.exc_info()[2])

def syntaxCreator():
    syntax = om.MSyntax()
    syntax.addArg(om.MSyntax.kDouble)
    syntax.addFlag("-r", "-reduction", syntax.lastArg())
    return syntax

def initializePlugin(mobject):
    if mobject is None:
        raise ValueError("Invalid mobject")

    mplugin = ompx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(ProxyModelCmd.kPluginCmdName, cmdCreator, syntaxCreator)
    except RuntimeError as e:
        # Handle registration failure
        raise ValueError("Failed to register command: %s" % ProxyModelCmd.kPluginCmdName) from e

def uninitializePlugin(mobject):
    if mobject is None:
        raise ValueError("Invalid mobject")

    mplugin = ompx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(ProxyModelCmd.kPluginCmdName)
    except RuntimeError as e:
        # Handle deregistration failure
        raise ValueError("Failed to deregister command: %s" % ProxyModelCmd.kPluginCmdName) from e

if __name__ == "__main__":
    cmds.loadPlugin(__file__)
    cmds.generateProxyModel(r=50)
