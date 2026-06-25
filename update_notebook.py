import json
import sys

def modify_notebook(file_path):
    with open(file_path, "r") as f:
        nb = json.load(f)

    # El código a insertar
    imports_and_class = """
import sys
import os

# Asegurar que TimeMAE esté clonado si estamos en Colab o no existe localmente
if not os.path.exists('TimeMAE'):
    os.system('git clone https://github.com/ustc-time-series/TimeMAE.git')

if 'TimeMAE' not in sys.path:
    sys.path.append('TimeMAE')

import torch
import torch.nn as nn
from TimeMAE.model.TimeMAE import Encoder
from TimeMAE.model.layers import PositionalEmbedding

class TimeMAEPatchEmbed(nn.Module):
    def __init__(self, in_ch=3, patch_len=8, emb_dim=128, max_patches=5000):
        super().__init__()
        self.patch_len = patch_len
        self.input_projection = nn.Conv1d(in_ch, emb_dim, kernel_size=patch_len, stride=patch_len)
        self.position = PositionalEmbedding(max_patches, emb_dim)
        
        class Args: pass
        args = Args()
        args.d_model = emb_dim
        args.attn_heads = 4
        args.layers = 2
        args.dropout = 0.1
        args.enable_res_parameter = 1
        self.encoder = Encoder(args)

    def forward(self, x):
        B, T, C = x.shape
        P = self.patch_len
        T2 = (T // P) * P
        x = x[:, :T2, :]
        x = self.input_projection(x.transpose(1, 2)).transpose(1, 2).contiguous()
        pos_emb = self.position(x)
        x += pos_emb[:, :x.size(1), :]
        x = self.encoder(x)
        return x
"""

    modified = False
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if "class TimePatchTransformer" in source and "self.patch = PatchEmbed1D" in source:
                # Modificamos el source
                new_source = source.replace(
                    "self.patch = PatchEmbed1D(in_ch, patch_len, emb_dim)", 
                    "self.patch = TimeMAEPatchEmbed(in_ch, patch_len, emb_dim)"
                )
                
                # Prepend the imports and new class to this cell
                final_source = imports_and_class + "\n" + new_source
                
                # Update cell source correctly
                # Jupyter expects list of lines, so we split and append \n
                lines = final_source.splitlines(keepends=True)
                cell["source"] = lines
                modified = True
                break

    if modified:
        with open(file_path, "w") as f:
            json.dump(nb, f, indent=1)
        print(f"Modificado exitosamente: {file_path}")
    else:
        print(f"No se encontró PatchEmbed1D en TimePatchTransformer o ya fue modificado en: {file_path}")

modify_notebook("wesad_ssl_timepatch_colab_profa.ipynb")
modify_notebook("wesad_ssl_timepatch_colab_final.ipynb")
modify_notebook("TimePatch_SSL_WESAD_StressPredict.ipynb")
