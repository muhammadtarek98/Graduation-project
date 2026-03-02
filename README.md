# I-MRI Scan — Intelligent Magnetic Resonance Imaging Scan

> **Academic project — not intended for commercial use.**

A deep-learning-powered desktop application that automatically diagnoses three types of knee injuries from MRI scans.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Diagnosed Conditions](#2-diagnosed-conditions)
3. [Model Architecture](#3-model-architecture)
4. [Dataset](#4-dataset)
5. [Training Results](#5-training-results)
6. [Desktop Application (GUI)](#6-desktop-application-gui)
7. [Project Structure](#7-project-structure)
8. [Installation & Usage](#8-installation--usage)
9. [Team](#9-team)
10. [License](#10-license)

---

## 1. Project Overview

**I-MRI Scan** is a graduation project that uses convolutional neural networks to help clinicians detect knee injuries from MRI scans. Users can load a patient's MRI series through the desktop application, and the system will predict the likelihood of each of the three supported injury types.

Key highlights:

- Three independent binary-classification models, one per injury type.
- PyTorch-based deep learning pipeline trained on the [MRNet dataset](https://stanfordmlgroup.github.io/competitions/mrnet/).
- Cross-platform desktop GUI built with PyQt5.
- Patient record management backed by a local SQLite / MySQL database.

---

## 2. Diagnosed Conditions

| # | Condition | Description |
|---|-----------|-------------|
| 1 | **ACL (Anterior Cruciate Ligament)** | Detects tears or damage to the ACL, one of the major knee ligaments. |
| 2 | **Meniscus** | Identifies meniscal tears, which are common sports-related cartilage injuries. |
| 3 | **Abnormality** | Flags any general abnormality present in the knee MRI. |

Each model outputs a binary prediction (positive / negative) along with a confidence score.

---

## 3. Model Architecture

All three models share the same underlying architecture but are trained independently with their respective labels:

- **Base network:** AlexNet (pre-trained on ImageNet, fine-tuned on MRI data)
- **Input:** Series of 2-D MRI slices treated as a 3-D volume
- **Output:** Single sigmoid neuron → binary classification
- **Training platform:** Google Colaboratory (GPU runtime)
- **Model storage:** Google Drive

Detailed notebooks for each experiment are available in the [`notebook/`](notebook/) directory.

---

## 4. Dataset

The project uses the publicly available **[MRNet dataset](https://stanfordmlgroup.github.io/competitions/mrnet/)** released by Stanford ML Group.

- **Modality:** Knee MRI (axial, coronal, sagittal planes)
- **Labels:** ACL tear, meniscal tear, general abnormality
- **Task type:** Binary classification per label

> **Note:** You must agree to Stanford's terms of use and download the dataset separately. It is not included in this repository.

---

## 5. Training Results

### ACL — Loss Curve

![ACL train and validation loss](https://github.com/muhammadtarek98/Graduation-project/blob/master/training%20results/ACL%20train%20and%20validation%20loss.png)

### Abnormality — Accuracy & Loss

| Training Accuracy | Training Loss |
|:-----------------:|:-------------:|
| ![Abnormal training accuracy](https://github.com/muhammadtarek98/Graduation-project/blob/master/training%20results/abnormal%20training%20accuracy.png) | ![Abnormal training loss](https://github.com/muhammadtarek98/Graduation-project/blob/master/training%20results/abnormal%20training%20loss.png) |

| Validation Accuracy | Validation Loss |
|:-------------------:|:---------------:|
| ![Abnormal validation accuracy](https://github.com/muhammadtarek98/Graduation-project/blob/master/training%20results/abnormal%20validation%20accuracy.png) | ![Abnormal validation loss](https://github.com/muhammadtarek98/Graduation-project/blob/master/training%20results/abnormal%20validation%20loss.png) |

### Meniscus — Accuracy & Loss

| Training Accuracy | Training Loss |
|:-----------------:|:-------------:|
| ![Meniscus training accuracy](https://github.com/muhammadtarek98/Graduation-project/blob/master/training%20results/meniscus%20training%20accuracy.png) | ![Meniscus training loss](https://github.com/muhammadtarek98/Graduation-project/blob/master/training%20results/meniscus%20training%20loss.png) |

| Validation Accuracy | Validation Loss |
|:-------------------:|:---------------:|
| ![Meniscus validation accuracy](https://github.com/muhammadtarek98/Graduation-project/blob/master/training%20results/meniscus%20validation%20accuracy.png) | ![Meniscus validation loss](https://github.com/muhammadtarek98/Graduation-project/blob/master/training%20results/meniscus%20validation%20loss.png) |

---

## 6. Desktop Application (GUI)

The desktop application is built with **PyQt5** and provides the following features:

- Load and preview MRI scan files.
- Run inference using the three trained models simultaneously.
- Display diagnosis results with confidence scores.
- Save patient records to a local database.
- Export reports to Excel (`.xlsx`) format.

### Application Screenshots

![App screenshot 1](https://github.com/muhammadtarek98/Graduation-project/blob/master/GUI/screen%20shoots/110318190_577748672918099_8411829493594774902_n.png)

![App screenshot 2](https://github.com/muhammadtarek98/Graduation-project/blob/master/GUI/screen%20shoots/110540300_2710977769180005_3079856452306795655_n.png)

![App screenshot 3](https://github.com/muhammadtarek98/Graduation-project/blob/master/GUI/screen%20shoots/115804054_1439182366271556_7750834540292366294_n.png)

![App screenshot 4](https://github.com/muhammadtarek98/Graduation-project/blob/master/GUI/screen%20shoots/116108948_701642877049470_7470068119339727989_n.png)

---

## 7. Project Structure

```
Graduation-project/
│
├── GUI/                        # Desktop application source code
│   ├── design.py               # PyQt5 UI layout definitions
│   ├── init.py                 # Application entry point
│   ├── models.py               # Model loading and inference helpers
│   ├── preprocessing.py        # MRI preprocessing pipeline
│   ├── threads.py              # Background worker threads for inference
│   ├── database.py             # Database connection and queries
│   ├── exports.py              # Excel report export utilities
│   ├── database/               # SQLite database files
│   ├── resources/              # Icons and UI assets
│   ├── screen shoots/          # Application screenshots
│   └── requirements.txt        # Python dependencies for the GUI
│
├── notebook/                   # Jupyter notebooks for training & EDA
│   ├── MRNet_exploratory_data_analysis.ipynb
│   ├── MRnet_Models_Alexnet.ipynb
│   ├── triple_MRInet.ipynb
│   ├── triple_MRInet_V2.ipynb
│   ├── triple_MRInet_last_version.ipynb
│   ├── predication_notebook.ipynb
│   ├── utils.py                # Shared utility functions
│   └── scripts/                # Standalone Python scripts
│       ├── alexnet.py          # AlexNet model definition
│       ├── Data loader.py      # MRNet data loader
│       └── Dataset_creation.py # Dataset preparation helpers
│
├── training results/           # Saved training/validation plots
├── I-MRI-Scan-documentation.pdf
├── Graduation-presentation.pdf
└── README.md
```

---

## 8. Installation & Usage

### Prerequisites

- Python 3.7+
- A CUDA-capable GPU is recommended for training; CPU-only is supported for inference.

### Install Dependencies

```bash
cd GUI
pip install -r requirements.txt
```

### Run the Application

```bash
cd GUI
python init.py
```

### Run Training Notebooks

Open any notebook inside the `notebook/` directory in **Jupyter Notebook** or upload it to **Google Colab** for GPU-accelerated training.

---

## 9. Team

| Name | Role |
|------|------|
| **Mohammed Adry Ahmed** | Deep Learning Engineering |
| **Mohammed Abd-Elnaby Abd-Elwahab** | System Analysis |
| **Mohammed Mustafa Megahd El-Ewasy** | Desktop Application Development |
| **Muhammad Tarek Refaat** | Deep Learning Engineering |

---

## 10. License

This project is licensed under the terms of the [LICENSE](LICENSE) file included in this repository.
It is intended **solely for academic and research purposes** and must not be used in any clinical or commercial setting without proper validation and regulatory approval.

