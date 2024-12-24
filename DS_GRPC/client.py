import grpc
from distributed_system_pb2 import Empty, ReadRequest, WriteRequest
from distributed_system_pb2_grpc import SuperNodeStub, DataNodeStub
import random
import time

SUPER_NODE_IP = "127.0.0.1"
SUPER_NODE_PORT = 5000
NODE_COUNT = 3  # Set the number of nodes to interact with (for quorum)

def get_random_node():
    with grpc.insecure_channel(f"{SUPER_NODE_IP}:{SUPER_NODE_PORT}") as channel:
        stub = SuperNodeStub(channel)
        return stub.GiveRandomNode(Empty())

def perform_read(file_name, node_count):
    print(f"Performing READ on {file_name} at {node_count} nodes")
    read_responses = []
    start_time = time.time()  

    # Fetch responses from multiple nodes
    for _ in range(node_count):
        node = get_random_node()  
        with grpc.insecure_channel(f"{node.ip}:{node.port}") as channel:
            stub = DataNodeStub(channel)
            response = stub.RequestRead(ReadRequest(file_name=file_name, node_id=node.id))
            read_responses.append((node, response))

    # implementation of quorum protocol for read operation
    successful_reads = [r for r in read_responses if r[1].status == 1]
    if len(successful_reads) >= (node_count // 2) + 1:  
        print(f"Read Success: Data is consistent across nodes")
    else:
        print(f"Read Failed: Quorum not reached")

    end_time = time.time()  
    read_time = end_time - start_time
    print(f"Read completed in {read_time:.4f} seconds")

    # Log which node and file were read from
    for node, response in read_responses:
        print(f"Read from Node {node.id} ({node.ip}:{node.port}), File: {file_name}, Status: {response.status}")

    return read_time  

def perform_write(file_name, content, node_count):
    print(f"Performing WRITE on {file_name} at {node_count} nodes with content '{content}'")
    write_responses = []
    start_time = time.time()  

    # Write to multiple nodes
    for _ in range(node_count):
        node = get_random_node()  
        with grpc.insecure_channel(f"{node.ip}:{node.port}") as channel:
            stub = DataNodeStub(channel)
            response = stub.RequestWrite(WriteRequest(file_name=file_name, content=content, node_id=node.id))
            write_responses.append((node, response))

    # quorum protocol implementation for write operation
    successful_writes = [r for r in write_responses if r[1].status == 1]
    if len(successful_writes) >= (node_count // 2) + 1:  # Quorum reached
        print(f"Write Success: Data written successfully to nodes")
    else:
        print(f"Write Failed: Quorum not reached")

    end_time = time.time()  
    write_time = end_time - start_time
    print(f"Write completed in {write_time:.4f} seconds")

    # Log which node and while file were written to
    for node, response in write_responses:
        print(f"Write to Node {node.id} ({node.ip}:{node.port}), File: {file_name}, Status: {response.status}")

    return write_time  

def fetch_file_system_state():
    with grpc.insecure_channel(f"{SUPER_NODE_IP}:{SUPER_NODE_PORT}") as channel:
        stub = SuperNodeStub(channel)
        state = stub.GetFileSystemState(Empty())
        for node_id, files in state.node_files.items():
            print(f"Node {node_id}: {files.files}")

def main(op, number_of_ops):
    total_read_time = 0  
    total_write_time = 0  

    if op == 3:
        fetch_file_system_state()
        return

    for i in range(number_of_ops):
        node = get_random_node()
        if op == 0 and random.random() < 0.9:  # Read-heavy
            total_read_time += perform_read(f"file{i % 3}", NODE_COUNT)
        elif op == 1 and random.random() < 0.9:  # Write-heavy
            total_write_time += perform_write(f"file{i % 3}", f"Content-{i}", NODE_COUNT)
        else:  # Balanced or secondary op
            if random.random() < 0.5:
                total_read_time += perform_read(f"file{i % 3}", NODE_COUNT)
            else:
                total_write_time += perform_write(f"file{i % 3}", f"Content-{i}", NODE_COUNT)

    # Print total time for all operations
    print(f"\nTotal Time for Reads: {total_read_time:.4f} seconds")
    print(f"Total Time for Writes: {total_write_time:.4f} seconds")
    print(f"Total Time for All Operations: {total_read_time + total_write_time:.4f} seconds")

if __name__ == "__main__":
    import sys
    op = int(sys.argv[1])  # 0: Read-heavy, 1: Write-heavy, 2: Balanced, 3: Fetch state
    number_of_ops = int(sys.argv[2])
    main(op, number_of_ops)






