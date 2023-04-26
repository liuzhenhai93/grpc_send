#coding:utf-8
import random
import time
import numpy as np
import serialize_helper
import grpc
import rpc_weights_syn_pb2 as pb2
import rpc_weights_syn_pb2_grpc as pb2_grpc

global_random = np.random.rand(*[16*1024,1024]).astype("float32")
def generate_state_dict(num):
    dict = {}
    for i in range(num):
        dict[f"{i}"] = global_random
    return dict

# TODO(liuzhenhai): split according to size
def split_state_dict(dict, segment_size):
    keys = list(dict.keys())
    num = (len(keys) + segment_size - 1) // segment_size
    for i in range(num):
        seg_keys = keys[i*segment_size: min((i+1)*segment_size, len(keys))]
        yield pb2.SynchronizeWeightsRequest(weights={k :serialize_helper.numpy_to_proto(dict[k]) for k in seg_keys})

def run():
    options= [('grpc.max_receive_message_length',1024*1024*1024)]
    conn = grpc.insecure_channel('localhost:5001', options=options)
    client = pb2_grpc.WeightSyncStub(channel=conn)
    dict = generate_state_dict(1000)
    begin_time = time.time()
    response = client.SynchronizeWeights(split_state_dict(dict, 3))
    print(response.result)
    end_time = time.time()
    print(f"it takes {(end_time - begin_time)} s")

if __name__ == '__main__':
    run()



