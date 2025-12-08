import torch
import pickle
from torchvision.utils import save_image

url = "https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl"
with open("ffhq.pkl", "wb") as f:
    f.write(torch.hub.load_state_dict_from_url(url, progress=True))


with open("ffhq.pkl", "rb") as f:
    G = pickle.load(f)['G_ema'].cuda()  

z = torch.randn(1, G.z_dim).cuda()
img = G(z, None)
save_image((img + 1) / 2, 'face.png') 