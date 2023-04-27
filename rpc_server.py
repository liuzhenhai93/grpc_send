#coding:utf-8
import grpc
import rpc_weights_syn_pb2 as pb2
import rpc_weights_syn_pb2_grpc as pb2_grpc
import time
from concurrent import futures
import serialize_helper
from collections import OrderedDict

class WeightSync(pb2_grpc.WeightSyncServicer):
    def SynchronizeWeights(self, request_iterator, context):
        dict = OrderedDict()
        for request in request_iterator:
            for (k, v) in zip(request.keys,request.weights):
                v = serialize_helper.proto_to_numpy(v)
                dict[k] = v
                print(f"{k}:{v.size}")
        return pb2.SynchronizeWeightsResponse(result ='ok')


global_grpc_server = None
def start_server(ip_port="0.0.0.0:5001"):
    global global_grpc_server
    assert global_grpc_server is None
    options=[
        ('grpc.max_send_message_length', -1),
        ('grpc.max_receive_message_length', -1),
    ]
    global_grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=8), options = options)
    pb2_grpc.add_WeightSyncServicer_to_server(WeightSync(), global_grpc_server)
    global_grpc_server.add_insecure_port(ip_port)
    print(f"server will start at {ip_port}")
    global_grpc_server.start()

def stop_server():
    global global_grpc_server
    global_grpc_server.stop(0)
    global_grpc_server = None

def run():
    start_server('0.0.0.0:5001')
    try:
        while 1:
            time.sleep(3600)
    except KeyboardInterrupt:
        stop_server()


if __name__ == '__main__':
    run()
