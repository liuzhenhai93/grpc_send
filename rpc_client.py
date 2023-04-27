#coding:utf-8
import random
import time
import numpy as np
import serialize_helper
import grpc
import rpc_weights_syn_pb2 as pb2
import rpc_weights_syn_pb2_grpc as pb2_grpc
from multiprocessing import Process
from collections import OrderedDict

global_random = np.random.rand(*[8*1024,1024]).astype("float32")
def generate_state_dict(num):
    dict = OrderedDict()
    for i in range(num):
        dict[f"{1000-i}"] = global_random
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
            seg_dict = OrderedDict()
            for k in seg_keys:
                seg_dict[k] = dict[k]
            yield seg_dict

def split_state_dict_by_size(dict, segment_size):
    keys = list(dict.keys())
    num = (len(keys) + segment_size - 1) // segment_size
    for i in range(num):
        seg_keys = keys[i*segment_size: min((i+1)*segment_size, len(keys))]
        if seg_keys:
            seg_dict = OrderedDict()
            for k in seg_keys:
                seg_dict[k] = dict[k]
            yield seg_dict

def split_state_dict_by_data_size(dict, segment_size=256*1024*1024):
    cur_size = 0
    seg_dict = OrderedDict()
    for (k, v) in dict.items():
        cur_size = cur_size + v.itemsize * v.size
        seg_dict[k] = v
        if cur_size >= segment_size:
            yield seg_dict
            cur_size = 0
            seg_dict = OrderedDict()
    if seg_dict:
        yield seg_dict


def stream_send(dict, size):
    for d in split_state_dict_by_data_size(dict, size):
        keys = [k for (k, _) in d.items()]
        values = [serialize_helper.numpy_to_proto(v) for (_, v) in d.items()]
        yield pb2.SynchronizeWeightsRequest(keys=keys, weights=values)

def send_weights(state_dict, ip_port = "localhost:5001", segment_size = 256*1024*1024):
    begin_time = time.time()
    options=[
        ('grpc.max_send_message_length', -1),
        ('grpc.max_receive_message_length', -1),
    ]
    conn = grpc.insecure_channel(ip_port, options=options)
    client = pb2_grpc.WeightSyncStub(channel=conn)
    response = client.SynchronizeWeights(stream_send(state_dict, segment_size))
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
    dict = generate_state_dict(1000)
    send_weights(dict, 'localhost:5001', 256*1024*1024)

def run_with_multiprocess():
    dict = generate_state_dict(1000)
    begin_time = time.time()
    send_weight_with_multiprocess(dict, "localhost:5001", 8)
    end_time = time.time()
    print(f"it takes {(end_time - begin_time)} s")


if __name__ == '__main__':
    run()
    #run_with_multiprocess()



