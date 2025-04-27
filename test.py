import torch

if torch.cuda.is_available():
    gpu_id = 0  # Change if you have multiple GPUs
    total = torch.cuda.get_device_properties(gpu_id).total_memory / 1024**2  # MB
    reserved = torch.cuda.memory_reserved(gpu_id) / 1024**2  # MB
    allocated = torch.cuda.memory_allocated(gpu_id) / 1024**2  # MB
    free = reserved - allocated
    print(f"GPU {gpu_id}:")
    print(f"  Total Memory: {total:.2f} MB")
    print(f"  Reserved Memory: {reserved:.2f} MB")
    print(f"  Allocated Memory: {allocated:.2f} MB")
    print(f"  Free (Unallocated in reserved): {free:.2f} MB")
else:
    print("No CUDA-compatible GPU is available.")
