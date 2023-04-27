#coding:utf-8
import grpc
import rpc_weights_syn_pb2 as pb2
import rpc_weights_syn_pb2_grpc as pb2_grpc
import time
from concurrent import futures
import serialize_helper

class WeightSync(pb2_grpc.WeightSyncServicer):
    def HelloGrpc(self, request, context):
        name = request.name
        age = request.age

        result = f'my name is {name}, i am {age} years old'
        return pb2.HelloGrpcReply(result = result)

    def SynchronizeWeights(self, request_iterator, context):
        dict = {}
        for request in request_iterator:
            for (k, v) in request.weights.items():
                v = serialize_helper.proto_to_numpy(v)
                dict[k] = v
                #print(f"{k}:{v.size}")
        return pb2.SynchronizeWeightsResponse(result ='ok')


def run():
    options=[
        ('grpc.max_send_message_length', -1),
        ('grpc.max_receive_message_length', -1),
    ]
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=8), options = options)
    pb2_grpc.add_WeightSyncServicer_to_server(WeightSync(), grpc_server)
    grpc_server.add_insecure_port('0.0.0.0:5001')
    print('server will start at 0.0.0.0:5001')
    grpc_server.start()
    try:
        while 1:
            time.sleep(3600)
    except KeyboardInterrupt:
        grpc_server.stop(0)

if __name__ == '__main__':
    run()
