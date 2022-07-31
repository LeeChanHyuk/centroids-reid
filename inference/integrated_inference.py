import argparse
import logging
import os
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.append(".")

from config import cfg
from train_ctl_model import CTLModel
from utils.reid_metric import get_dist_func

from inference_utils import (
    ImageDataset,
    ImageFolderWithPaths,
    calculate_centroids,
    create_pid_path_index,
    make_inference_data_loader,
    run_inference,
)

### Prepare logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

### Functions used to extract pair_id
exctract_func = (
    lambda x: (x).rsplit(".", 1)[0].rsplit("_", 1)[0]
)  ## To extract pid from filename. Example: /path/to/dir/product001_04.jpg -> pid = product001
exctract_func = lambda x: Path(
    x
).parent.name  ## To extract pid from parent directory of an iamge. Example: /path/to/root/001/image_04.jpg -> pid = 001

################################ Gallery ###################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create embeddings for images that will serve as the database (gallery)"
    )
    parser.add_argument(
        "--config_file", default="configs/256_resnet50_gallery.yml", help="path to config file", type=str
    )
    parser.add_argument(
        "--images-in-subfolders",
        help="if images are stored in the subfloders use this flag. If images are directly under DATASETS.ROOT_DIR path do not use it.",
        action="store_true",
    )
    parser.add_argument(
        "--print_freq",
        help="number of batches the logging message is printed",
        type=int,
        default=10,
    )
    parser.add_argument(
        "opts",
        help="Modify config options using the command-line",
        default=None,
        nargs=argparse.REMAINDER,
    )
    args = parser.parse_args()
    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)

    ### Data preparation
    if args.images_in_subfolders:
        dataset_type = ImageFolderWithPaths
    else:
        dataset_type = ImageDataset
    log.info(f"Preparing data using {dataset_type} dataset class")
    val_loader = make_inference_data_loader(cfg, cfg.DATASETS.ROOT_DIR, dataset_type)
    if len(val_loader) == 0:
        raise RuntimeError("Lenght of dataloader = 0")

    ### Build model
    model = CTLModel.load_from_checkpoint(cfg.MODEL.PRETRAIN_PATH)
    use_cuda = True if torch.cuda.is_available() and cfg.GPU_IDS else False

    ### Inference
    log.info("Running inference")
    embeddings_gallery, paths_gallery = run_inference(
        model, val_loader, cfg, print_freq=args.print_freq, use_cuda=use_cuda
    )

    ### Create centroids
    log.info("Creating centroids")
    if cfg.MODEL.USE_CENTROIDS:
        pid_path_index = create_pid_path_index(paths=paths_gallery, func=exctract_func)
        embeddings_gallery, paths_gallery = calculate_centroids(embeddings_gallery, pid_path_index)

    ################################ Query ###################################

    parser = argparse.ArgumentParser(
        description="Create embeddings for images that will serve as the database (gallery)"
    )
    parser.add_argument(
        "--config_file", default="configs/256_resnet50_query.yml", help="path to config file", type=str
    )
    parser.add_argument(
        "--images-in-subfolders",
        help="if images are stored in the subfloders use this flag. If images are directly under DATASETS.ROOT_DIR path do not use it.",
        action="store_true",
    )
    parser.add_argument(
        "--print_freq",
        help="number of batches the logging message is printed",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--gallery_data",
        help="path to root where previously prepared embeddings and paths were saved",
        type=str,
        default='data/market1501/output'
    )
    parser.add_argument(
        "--normalize_features",
        help="whether to normalize the gallery and query embeddings",
        action="store_true",
    )
    parser.add_argument(
        "--topk",
        help="number of top k similar ids to return per query. If set to 0 all ids per query will be returned",
        type=int,
        default=100,
    )
    parser.add_argument(
        "opts",
        help="Modify config options using the command-line",
        default=None,
        nargs=argparse.REMAINDER,
    )
    args = parser.parse_args()
    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)

    ### Data preparation
    if args.images_in_subfolders:
        dataset_type = ImageFolderWithPaths
    else:
        dataset_type = ImageDataset
    log.info(f"Preparing data using {type(dataset_type)} dataset class")
    val_loader = make_inference_data_loader(cfg, cfg.DATASETS.ROOT_DIR, dataset_type)

    ### Build model
    model = CTLModel.load_from_checkpoint(cfg.MODEL.PRETRAIN_PATH)

    ### Inference
    log.info("Running inference")
    embeddings, paths = run_inference(
        model, val_loader, cfg, print_freq=args.print_freq
    )

    ### Load gallery data
    LOAD_PATH = Path(args.gallery_data)
    embeddings_gallery = torch.from_numpy(embeddings_gallery)

    if args.normalize_features:
        embeddings_gallery = torch.nn.functional.normalize(
            embeddings_gallery, dim=1, p=2
        )
        embeddings = torch.nn.functional.normalize(
            torch.from_numpy(embeddings), dim=1, p=2
        )
    else:
        embeddings = torch.from_numpy(embeddings)

    # Use GPU if available
    device = torch.device("cuda") if cfg.GPU_IDS else torch.device("cpu")
    embeddings_gallery = embeddings_gallery.to(device)
    embeddings = embeddings.to(device)

    ### Calculate similarity
    log.info("Calculating distance and getting the most similar ids per query")
    dist_func = get_dist_func(cfg.SOLVER.DISTANCE_FUNC)
    distmat = dist_func(x=embeddings, y=embeddings_gallery).cpu().numpy()
    indices = np.argsort(distmat, axis=1)

    ### Constrain the results to only topk most similar ids
    indices = indices[:, : args.topk] if args.topk else indices

    out = {
        query_path: {
            "indices": indices[q_num, :],
            "paths": paths_gallery[indices[q_num, :]],
            "distances": distmat[q_num, indices[q_num, :]],
        }
        for q_num, query_path in enumerate(paths)
    }
    for key in out.keys():
        query_name = key
        gallery_names = out[key]['paths']
        print(query_name)
        print(gallery_names)

    ### Save
    SAVE_DIR = Path(cfg.OUTPUT_DIR)
    SAVE_DIR.mkdir(exist_ok=True, parents=True)

    log.info(f"Saving results to {str(SAVE_DIR)}")
    np.save(SAVE_DIR / "results.npy", out)
    np.save(SAVE_DIR / "query_embeddings.npy", embeddings.cpu())
    np.save(SAVE_DIR / "query_paths.npy", paths)
