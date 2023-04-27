## 环境
pip3 install grpcio
pip3 install grpcio-tools  
pip3 install protobuf

## 代码生成
python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. rpc_weights_syn.proto

## demo 启动
启动 server:
python3 rpc_server.py
启动 client:
python3 rpc_client.py

## 用法

### 启动 server,主要逻辑 rpc_server.py，整合代码的时候只需要考虑 start_server 方法
### client 测试，逻辑 在 rpc_client.py，整合代码的时候只需要考虑 send_weights 方法