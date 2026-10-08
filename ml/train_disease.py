"""
Train Binary Leaf Disease Classifier (Healthy vs Diseased)
==========================================================
Dataset layout expected:
    ml/data/raw/dataset/Plant/
        Pepper__bell___healthy/         <-- healthy
        Pepper__bell___Bacterial_spot_disease/  <-- diseased
        Potato___healthy/
        Potato___Early_blight_disease/
        Tomato_healthy/
        Tomato_Late_blight_disease/
        ... etc.

Rules:
  - Folders whose name ends with '_healthy'  -> label: "Healthy"
  - All other folders                         -> label: "Diseased"

Output (saved to ml/):
  - plant_disease_model.keras   (trained MobileNetV2 model)
  - classes.json                (["Diseased", "Healthy"])
  - training_metrics.json       (val_accuracy, val_loss, epochs)
"""

import os
import sys
import json
import time
from pathlib import Path

import numpy as np

# -- Paths --
ROOT        = Path(__file__).parent                          # ml/
DATASET_DIR = ROOT / "data" / "raw" / "dataset" / "Plant"
MODEL_OUT   = ROOT / "plant_disease_model.keras"
CLASSES_OUT = ROOT / "classes.json"
METRICS_OUT = ROOT / "training_metrics.json"

# -- Hyper-parameters --
IMG_SIZE    = (224, 224)
BATCH_SIZE  = 32
EPOCHS_HEAD = 10          # train only the new top layers first
EPOCHS_FT   = 10          # fine-tune last few MobileNetV2 blocks
LR_HEAD     = 1e-3
LR_FT       = 1e-5
VAL_SPLIT   = 0.2
SEED        = 42

CLASS_NAMES = ["Diseased", "Healthy"]   # alphabetical -> index 0 / 1


def label_for_folder(folder_name: str) -> str:
    """Map folder name -> binary label."""
    name_lower = folder_name.lower()
    if name_lower.endswith("_healthy") or name_lower == "healthy":
        return "Healthy"
    return "Diseased"


def collect_files(dataset_dir: Path):
    """Walk dataset_dir, collect (image_path, label) pairs."""
    samples = []
    if not dataset_dir.exists():
        print(f"[ERROR] Dataset directory not found: {dataset_dir}")
        sys.exit(1)

    folders = [d for d in dataset_dir.iterdir() if d.is_dir()]
    if not folders:
        print(f"[ERROR] No sub-folders found in {dataset_dir}")
        sys.exit(1)

    print(f"\nFound {len(folders)} class folders:")
    for folder in sorted(folders):
        label = label_for_folder(folder.name)
        exts  = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
        imgs  = [f for f in folder.iterdir() if f.suffix.lower() in exts]
        print(f"  [{label:8s}]  {folder.name}  ({len(imgs)} images)")
        for img in imgs:
            samples.append((str(img), label))

    return samples


def build_tf_dataset(samples, class_names, val_split, batch_size, img_size, seed):
    """Build train/val tf.data.Dataset from file paths."""
    import tensorflow as tf

    paths  = [s[0] for s in samples]
    labels = [class_names.index(s[1]) for s in samples]

    # Shuffle deterministically
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(paths))
    paths  = [paths[i]  for i in idx]
    labels = [labels[i] for i in idx]

    split = int(len(paths) * (1 - val_split))
    train_paths,  val_paths  = paths[:split],  paths[split:]
    train_labels, val_labels = labels[:split], labels[split:]

    def parse_image(path, label):
        raw  = tf.io.read_file(path)
        img  = tf.image.decode_image(raw, channels=3, expand_animations=False)
        img  = tf.image.resize(img, img_size)
        img  = tf.cast(img, tf.float32) / 255.0
        return img, label

    def augment(img, label):
        img = tf.image.random_flip_left_right(img)
        img = tf.image.random_flip_up_down(img)
        img = tf.image.random_brightness(img, 0.15)
        img = tf.image.random_contrast(img, 0.8, 1.2)
        img = tf.clip_by_value(img, 0.0, 1.0)
        return img, label

    AUTOTUNE = tf.data.AUTOTUNE

    train_ds = (
        tf.data.Dataset.from_tensor_slices((train_paths, train_labels))
        .map(parse_image, num_parallel_calls=AUTOTUNE)
        .map(augment,     num_parallel_calls=AUTOTUNE)
        .shuffle(1000, seed=seed)
        .batch(batch_size)
        .prefetch(AUTOTUNE)
    )
    val_ds = (
        tf.data.Dataset.from_tensor_slices((val_paths, val_labels))
        .map(parse_image, num_parallel_calls=AUTOTUNE)
        .batch(batch_size)
        .prefetch(AUTOTUNE)
    )

    print(f"\nTrain samples : {len(train_paths)}")
    print(f"Val   samples : {len(val_paths)}")
    print(f"Classes       : {class_names}")
    return train_ds, val_ds


def build_model(num_classes: int):
    """MobileNetV2 with custom binary head."""
    import tensorflow as tf
    from tensorflow.keras import layers, models

    base = tf.keras.applications.MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False  # freeze initially

    inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs * 255.0)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs)
    return model, base


def main():
    import tensorflow as tf

    print("=" * 60)
    print("  Agro-Vision AI -- Binary Disease Classifier Training")
    print("=" * 60)
    print(f"TensorFlow  : {tf.__version__}")
    print(f"Dataset dir : {DATASET_DIR}")
    print(f"Model output: {MODEL_OUT}")

    # 1. Collect files
    samples = collect_files(DATASET_DIR)
    if len(samples) < 10:
        print(f"[ERROR] Too few images found ({len(samples)}). Check your dataset path.")
        sys.exit(1)

    healthy_count  = sum(1 for _, lbl in samples if lbl == "Healthy")
    diseased_count = sum(1 for _, lbl in samples if lbl == "Diseased")
    print(f"\nTotal images  : {len(samples)}")
    print(f"  Healthy     : {healthy_count}")
    print(f"  Diseased    : {diseased_count}")

    # 2. Build datasets
    train_ds, val_ds = build_tf_dataset(
        samples, CLASS_NAMES, VAL_SPLIT, BATCH_SIZE, IMG_SIZE, SEED
    )

    # 3. Build model
    print("\nBuilding MobileNetV2 model...")
    model, base_model = build_model(num_classes=len(CLASS_NAMES))
    model.summary(line_length=80)

    # 4. Phase 1: Train head only
    print(f"\n[Phase 1] Training classification head ({EPOCHS_HEAD} epochs)...")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(LR_HEAD),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks_p1 = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=4, restore_best_weights=True, verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=2, verbose=1
        ),
    ]

    t0 = time.time()
    hist1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_HEAD,
        callbacks=callbacks_p1,
    )

    # 5. Phase 2: Fine-tune last 30 layers of MobileNetV2
    print(f"\n[Phase 2] Fine-tuning last 30 layers ({EPOCHS_FT} epochs)...")
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(LR_FT),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks_p2 = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=5, restore_best_weights=True, verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, verbose=1
        ),
    ]

    hist2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_FT,
        callbacks=callbacks_p2,
    )
    elapsed = time.time() - t0

    # 6. Evaluate
    print("\nEvaluating on validation set...")
    val_loss, val_acc = model.evaluate(val_ds, verbose=1)
    print(f"\nFinal val accuracy : {val_acc:.4f}")
    print(f"Final val loss     : {val_loss:.4f}")
    print(f"Training time      : {elapsed:.1f}s")

    # 7. Save model
    print(f"\nSaving model -> {MODEL_OUT}")
    model.save(str(MODEL_OUT))

    # 8. Save classes.json
    print(f"Saving classes -> {CLASSES_OUT}")
    with open(CLASSES_OUT, "w") as f:
        json.dump(CLASS_NAMES, f)

    # 9. Save metrics
    metrics = {
        "val_accuracy": round(float(val_acc), 4),
        "val_loss":     round(float(val_loss), 4),
        "total_images": len(samples),
        "healthy_images": healthy_count,
        "diseased_images": diseased_count,
        "classes": CLASS_NAMES,
        "epochs_head": len(hist1.history["loss"]),
        "epochs_ft":   len(hist2.history["loss"]),
        "training_time_sec": round(elapsed, 1),
        "model_type": "MobileNetV2-binary",
        "img_size": list(IMG_SIZE),
    }
    with open(METRICS_OUT, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics -> {METRICS_OUT}")

    print("\nTraining complete!")
    print(f"   Model saved : {MODEL_OUT}")
    print(f"   Val Accuracy: {val_acc*100:.2f}%")
    print("\nNext step: restart the Flask app to load the new model.")


if __name__ == "__main__":
    main()
