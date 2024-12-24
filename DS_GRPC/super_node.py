import grpc
from concurrent import futures
import random
from distributed_system_pb2 import Node, FileSystemState, Empty
from distributed_system_pb2_grpc import SuperNodeServicer, add_SuperNodeServicer_to_server

class SuperNodeService(SuperNodeServicer):
    def __init__(self):
        self.active_nodes = [
            Node(ip="127.0.0.1", port=5001, id=1),
            Node(ip="127.0.0.1", port=5002, id=2),
            Node(ip="127.0.0.1", port=5003, id=3),
        ]
    
    def GiveRandomNode(self, request, context):
        return random.choice(self.active_nodes)
    
    def GetFileSystemState(self, request, context):
        # Simulated file system state for demonstration
        return FileSystemState(node_files={
            1: {"files": ["file1", "file2"]},
            2: {"files": ["file3"]},
            3: {"files": ["file4", "file5"]},
        })

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_SuperNodeServicer_to_server(SuperNodeService(), server)
    server.add_insecure_port("[::]:5000")
    server.start()
    print("Super Node running on port 5000")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
