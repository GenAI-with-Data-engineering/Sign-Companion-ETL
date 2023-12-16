import torch
import cv2
import videotransforms
import numpy as np
import gradio as gr
from einops import rearrange
from torchvision import transforms
from pytorch_i3d import InceptionI3d


def preprocess(vidpath):
    # Fetch video
    cap = cv2.VideoCapture(vidpath)

    frames = []
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Extract frames from video
    for _ in range(num):
        _, img = cap.read()
        
        # Skip NoneType frames
        if img is None:
            continue

        # Resize if (w,h) < (226,226)
        w, h, c = img.shape
        if w < 226 or h < 226:
            d = 226. - min(w, h)
            sc = 1 + d / min(w, h)
            img = cv2.resize(img, dsize=(0, 0), fx=sc, fy=sc)

        # Normalize
        img = (img / 255.) * 2 - 1

        frames.append(img)
    
    frames = torch.Tensor(np.asarray(frames, dtype=np.float32))
    
    # Transform tensor and reshape to (1, c, t ,w, h)
    transform = transforms.Compose([videotransforms.CenterCrop(224)])
    frames = transform(frames)
    frames = rearrange(frames, 't w h c-> 1 c t w h')

    return frames

def classify(video,dataset='WLASL100'):
    to_load = {
        'WLASL100':{'logits':100,'path':'weights/asl100/FINAL_nslt_100_iters=896_top1=65.89_top5=84.11_top10=89.92.pt'},
        'WLASL2000':{'logits':2000,'path':'weights/asl2000/FINAL_nslt_2000_iters=5104_top1=32.48_top5=57.31_top10=66.31.pt'}
        }

    # Preprocess video
    input = preprocess(video)

    # Load model
    model = InceptionI3d()
    model.load_state_dict(torch.load('weights/rgb_imagenet.pt',map_location=torch.device('cpu')))
    model.replace_logits(to_load[dataset]['logits'])
    model.load_state_dict(torch.load(to_load[dataset]['path'],map_location=torch.device('cpu')))

    # Run on cpu. Spaces environment is limited to CPU for free users. 
    model.cpu()

    # Evaluation mode
    model.eval()

    with torch.no_grad(): # Disable gradient computation
        per_frame_logits = model(input) # Inference
    
    per_frame_logits.cpu()
    model.cpu()

    # Load predictions
    predictions = rearrange(per_frame_logits,'1 j k -> j k')
    predictions = torch.mean(predictions, dim = 1)

    # Fetch top 10 predictions
    _, index = torch.topk(predictions,10)
    index = index.cpu().numpy()

    # Load labels 
    with open('wlasl_class_list.txt') as f:
        idx2label = dict()
        for line in f:
            idx2label[int(line.split()[0])]=line.split()[1]
    
    # Get probabilities
    predictions = torch.nn.functional.softmax(predictions, dim=0).cpu().numpy()

    # Return dict {label:pred}
    return {idx2label[i]:float(predictions[i]) for i in index}

# Gradio App config
title = "I3D Sign Language Recognition"
description =   "Gradio demo of word-level sign language classification using I3D model pretrained on the WLASL video dataset. " \
                "WLASL is a large-scale dataset containing more than 2000 words in American Sign Language. " \
                "Examples used in the demo are videos from the the test subset. "  \
                "Note that WLASL100 contains 100 words while WLASL2000 contains 2000."
examples = [
        ['videos/no.mp4','WLASL100'],
        ['videos/all.mp4','WLASL100'],
        ['videos/before.mp4','WLASL100'],
        ['videos/blue.mp4','WLASL2000'],
        ['videos/white.mp4','WLASL2000'],
        ['videos/accident2.mp4','WLASL2000']
    ]

article =   "NOTE: This is not the official demonstration of the I3D sign language classification on the WLASL dataset. "\
            "More information about the WLASL dataset and pretrained I3D models can be found <a href=https://github.com/dxli94/WLASL>here</a>."

# Gradio App interface
gr.Interface(   fn=classify,
                inputs=[gr.inputs.Video(label="Video (*.mp4)"),gr.inputs.Radio(choices=['WLASL100','WLASL2000'], default='WLASL100', label='Trained on:')], 
                outputs=[gr.outputs.Label(num_top_classes=5, label='Top 5 Predictions')],
                allow_flagging="never",
                title=title, 
                description=description, 
                examples=examples,
                article=article).launch()
