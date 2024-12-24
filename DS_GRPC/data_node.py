import grpc
from concurrent import futures
from distributed_system_pb2 import ReadResponse, WriteResponse, NodeFiles, Empty
from distributed_system_pb2_grpc import DataNodeServicer, add_DataNodeServicer_to_server

class DataNodeService(DataNodeServicer):
    def __init__(self, node_id):
        self.node_id = node_id
        self.files = {}

    def RequestRead(self, request, context):
        if request.file_name in self.files:
            return ReadResponse(status=1, contents=self.files[request.file_name])
        return ReadResponse(status=0)

    def RequestWrite(self, request, context):
        self.files[request.file_name] = request.content
        print(f"Node {self.node_id}: Written {request.file_name} with content '{request.content}'")
        return WriteResponse(status=1, contents=f"File '{request.file_name}' written successfully")

    def GetFilesOnNode(self, request, context):
        return NodeFiles(files=list(self.files.keys()))

def serve(node_id, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DataNodeServicer_to_server(DataNodeService(node_id), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Data Node {node_id} running on port {port}")
    server.wait_for_termination()

if __name__ == "__main__":
    import sys
    node_id = int(sys.argv[1])
    port = int(sys.argv[2])
    serve(node_id=node_id, port=port)
