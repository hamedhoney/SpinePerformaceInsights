# How to download Mistral 7B Instruct (Q4_K_M)
Use this command to download the package and put in the model folder:
mkdir -p ./models && curl -L https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf -o ./models/mistral.gguf
mkdir -p ./models && curl -L -o ./models/openhermes.gguf https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF/resolve/main/openhermes-2.5-mistral-7b.Q4_K_M.gguf
