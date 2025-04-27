import torch
import gc

gc.collect()  # Run Python garbage collector to release unreferenced memory
torch.cuda.empty_cache()  # Release all unused cached memory from PyTorch
torch.cuda.ipc_collect()  # (Optional, for multi-process setups)
