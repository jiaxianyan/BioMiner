export CUDA_VISIBLE_DEVICES=0,1,2,3
python -m vllm.entrypoints.openai.api_server \
    --model scripts/local-biominer-instruct \
    --served-model-name local-biominer-instruct  \
    --trust-remote-code \
    --tensor-parallel-size 4 \
    --gpu-memory-utilization 0.6 \
    --max-model-len 128000 \
    --swap-space 32 \
    --port 8613 \
    --mm-encoder-tp-mode data \
    --async-scheduling \
    --allowed-local-media-path /data
