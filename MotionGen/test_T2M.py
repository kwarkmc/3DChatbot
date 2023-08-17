
# change the text here
clip_text = ["a person is jumping"]



import sys
sys.argv = ['GPT_eval_multi.py']
import options.option_transformer as option_trans
args = option_trans.get_args_parser()

args.dataname = 't2m'
args.resume_pth = 'pretrained/VQVAE/net_last.pth'
args.resume_trans = 'pretrained/VQTransformer_corruption05/net_best_fid.pth'
args.down_t = 2
args.depth = 3
args.block_size = 51
import clip
import torch
import numpy as np
import models.vqvae as vqvae
import models.t2m_trans as trans
import warnings
warnings.filterwarnings('ignore')

## load clip model and datasets
clip_model, clip_preprocess = clip.load("ViT-B/32", device=torch.device('cuda'), jit=False, download_root='./')  # Must set jit=False for training
clip.model.convert_weights(clip_model)  # Actually this line is unnecessary since clip by default already on float16
clip_model.eval()
for p in clip_model.parameters():
    p.requires_grad = False

net = vqvae.HumanVQVAE(args, ## use args to define different parameters in different quantizers
                       args.nb_code,
                       args.code_dim,
                       args.output_emb_width,
                       args.down_t,
                       args.stride_t,
                       args.width,
                       args.depth,
                       args.dilation_growth_rate)


trans_encoder = trans.Text2Motion_Transformer(num_vq=args.nb_code, 
                                embed_dim=1024, 
                                clip_dim=args.clip_dim, 
                                block_size=args.block_size, 
                                num_layers=9, 
                                n_head=16, 
                                drop_out_rate=args.drop_out_rate, 
                                fc_rate=args.ff_rate)


print ('loading checkpoint from {}'.format(args.resume_pth))
ckpt = torch.load(args.resume_pth, map_location='cpu')
net.load_state_dict(ckpt['net'], strict=True)
net.eval()
net.cuda()

print ('loading transformer checkpoint from {}'.format(args.resume_trans))
ckpt = torch.load(args.resume_trans, map_location='cpu')
trans_encoder.load_state_dict(ckpt['trans'], strict=True)
trans_encoder.eval()
trans_encoder.cuda()

mean = torch.from_numpy(np.load('./checkpoints/t2m/VQVAEV3_CB1024_CMT_H1024_NRES3/meta/mean.npy')).cuda()
std = torch.from_numpy(np.load('./checkpoints/t2m/VQVAEV3_CB1024_CMT_H1024_NRES3/meta/std.npy')).cuda()

print('model loaded - Ready to Generate Motion')

import glob
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#watchdogs=3.0.0
#TEXT 폴더 내에 파일이 생성되면, 파일을 읽어서 motion을 생성하고, motion.npy를 생성한다.

def new_file(event):
    if event.is_directory:
        return
    print("New file %s detected" % event.src_path)

    start_time = time.time()

    path = './TEXT/*.txt'
    file_list = glob.glob(path)

    for file_name in file_list:
        with open(file_name, 'r') as f:
            clip_text = f.readlines()
            clip_text = [x.strip() for x in clip_text]
            print(clip_text)

            txt_name = file_name.split('/')[-1].split('.')[0]

            print('Generating Motion for', txt_name)

            text = clip.tokenize(clip_text, truncate=True).cuda()

            feat_clip_text = clip_model.encode_text(text).float()
            index_motion = trans_encoder.sample(feat_clip_text[0:1], False)
            pred_pose = net.forward_decoder(index_motion)

            from utils.motion_process import recover_from_ric
            pred_xyz = recover_from_ric((pred_pose*std+mean).float(), 22)
            xyz = pred_xyz.reshape(1, -1, 22, 3)

            np.save(f'./MOTION/{txt_name}_motion.npy', xyz.detach().cpu().numpy())

            import visualization.plot_3d_global as plot_3d
            pose_vis = plot_3d.draw_to_batch(xyz.detach().cpu().numpy(),clip_text, [f'./GIF/{txt_name}_example.gif'])
    
    print("Processing Time :", time.time() - start_time)

event_handler = FileSystemEventHandler()
event_handler.on_created = new_file

folder_to_track = "./TEXT"
observer = Observer()
observer.schedule(event_handler, folder_to_track, recursive=True)

observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()

