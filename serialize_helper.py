from io import BytesIO
import numpy as np
import time
import rpc_weights_syn_pb2 as pb2

def numpy_to_proto(array, allow_pickle=False):
    bytes = BytesIO()
    np.save(bytes, array, allow_pickle=allow_pickle)
    return pb2.NpArray(array=bytes.getvalue())
def proto_to_numpy(proto, allow_pickle=False):
    nda_bytes = BytesIO(proto.array)
    return np.load(nda_bytes, allow_pickle=allow_pickle)


if __name__ == "__main__":
    allow_pickle = False
    a = np.random.rand(*[64*1024,1024]).astype("float64")
    begin_time = time.time()
    b = numpy_to_proto(a, allow_pickle=allow_pickle)
    end_time = time.time()
    print(f"serialize takes {(end_time - begin_time)} s")
    begin_time = time.time()
    c = proto_to_numpy(b, allow_pickle=allow_pickle)
    end_time = time.time()
    print(f"de serialize takes {(end_time - begin_time)} s")

