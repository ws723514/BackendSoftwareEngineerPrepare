.PHONY: proto

proto:
	python -m grpc_tools.protoc -I ./proto \
	  --python_out=./app --grpc_python_out=./app \
	  ./proto/*.proto
