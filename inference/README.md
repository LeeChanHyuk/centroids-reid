# Inference

## Creating embeddings
Example command to create embeddings using pretrained model.

Path to images is controlled by  `DATASETS.ROOT_DIR` and may be path to a single image file or to directory, which contains valid images.  
Additional flag can be set `--images-in-subfolders` – only images in subfolders in the `DATASETS.ROOT_DIR` will be used.ag can be set `--images-in-subfolders` – only images in subfolders in the `DATASETS.ROOT_DIR` will be used.

**NOTE:** at the beggining of the script, there is `exctract_func` specified, which is used to extracy `pair_id` either from filename or from subfolder name. See the examples in the script and customize if needed.

```bash
python inference/create_embeddings.py \
--config_file="configs/256_resnet50.yml" \
GPU_IDS [0] \
DATASETS.ROOT_DIR 'data/market1501/query/' \
TEST.IMS_PER_BATCH 128 \
OUTPUT_DIR 'data/market1501/output' \
TEST.ONLY_TEST True \
MODEL.PRETRAIN_PATH "logs/market1501/train_ctl_model/version_50/checkpoints/epoch=119.ckpt"
```

## Running similarity serach
Example command to run similarity search using pretrained model and query images.  
Path to images is controlled by  `DATASETS.ROOT_DIR` and may be path to a single image file or to directory, which contains valid images.   
Additional flag can be set `--images-in-subfolders` – only images in subfolders in the `DATASETS.ROOT_DIR` will be used.

```bash
python inference/get_similar.py \
--config_file="configs/256_resnet50.yml" \
--gallery_data='data/market1501/output' \
--normalize_features \
--topk=100 \
GPU_IDS [0] \
DATASETS.ROOT_DIR 'data/market1501/query'  \
TEST.IMS_PER_BATCH 128 \
OUTPUT_DIR 'data/market1501/similarity' \
TEST.ONLY_TEST True \
MODEL.PRETRAIN_PATH "logs/market1501/train_ctl_model/version_50/checkpoints/epoch=119.ckpt" \
SOLVER.DISTANCE_FUNC 'cosine'
```
