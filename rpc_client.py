#coding:utf-8
import random
import time
import numpy as np
import serialize_helper
import grpc
import rpc_weights_syn_pb2 as pb2
import rpc_weights_syn_pb2_grpc as pb2_grpc
from multiprocessing import Process

global_random = np.random.rand(*[8*1024,1024]).astype("float32")
def generate_state_dict(num):
    dict = {}
    for i in range(num):
        dict[f"{i}"] = global_random
    return dict

def split_state_dict_by_num(dict, segment_num):
    keys = list(dict.keys())
    size = len(keys) // segment_num
    index = 0
    for i in range(segment_num):
        segment_size = size
        if len(keys) % segment_num > i:
            segment_size = segment_size + 1
        seg_keys = keys[index:(index+segment_size)]
        index = index + segment_size
        if seg_keys:
            yield {k :dict[k] for k in seg_keys}

def split_state_dict_by_size(dict, segment_size):
    keys = list(dict.keys())
    num = (len(keys) + segment_size - 1) // segment_size
    for i in range(num):
        seg_keys = keys[i*segment_size: min((i+1)*segment_size, len(keys))]
        if seg_keys:
            yield {k :dict[k] for k in seg_keys}

def stream_send(dict, size):
    for d in split_state_dict_by_size(dict, size):
        yield pb2.SynchronizeWeightsRequest(weights = {k: serialize_helper.numpy_to_proto(v) for (k, v) in d.items()})

def send_weights(state_dict, ip_port = "localhost:5001"):
    begin_time = time.time()
    options= [('grpc.max_receive_message_length',1024*1024*1024)]
    conn = grpc.insecure_channel('localhost:5001', options=options)
    client = pb2_grpc.WeightSyncStub(channel=conn)
    response = client.SynchronizeWeights(stream_send(state_dict, 3))
    print(response.result)
    end_time = time.time()
    print(f"send_weights takes {(end_time - begin_time)} s")


def send_weight_with_multiprocess(state_dict, ip_port, num_process):
    processes = []
    for d in split_state_dict_by_num(state_dict, num_process):
        processes.append(Process(target=send_weights, args=(d, ip_port)))
    for p in processes:
        p.start()
    for p in processes:
        p.join()

def run():
    options= [('grpc.max_receive_message_length',1024*1024*1024)]
    conn = grpc.insecure_channel('localhost:5001', options=options)
    client = pb2_grpc.WeightSyncStub(channel=conn)
    dict = generate_state_dict(1000)
    begin_time = time.time()
    for seg_dict in split_state_dict_by_num(dict, 10):
        response = client.SynchronizeWeights(stream_send(seg_dict, 3))
        print(response.result)
    end_time = time.time()
    print(f"it takes {(end_time - begin_time)} s")


def run_with_multiprocess():
    dict = generate_state_dict(1000)
    begin_time = time.time()
    send_weight_with_multiprocess(dict, "localhost:5001", 8)
    end_time = time.time()
    print(f"it takes {(end_time - begin_time)} s")


if __name__ == '__main__':
    run_with_multiprocess()



