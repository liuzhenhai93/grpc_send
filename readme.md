## 环境
pip3 install grpcio
pip3 install grpcio-tools  
pip3 install protobuf

## 代码生成
python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. rpc_weights_syn.proto