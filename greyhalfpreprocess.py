# -*- coding: utf-8 -*-
"""GreyHalfPreprocess.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JHvIixB9n4jIMhv3M_O-vqRk-Z25dBEb
"""

from google.colab import drive
drive.mount('/content/drive')



import os
import pandas as pd
import numpy as np
import librosa
import librosa.display
from tqdm import tqdm
import matplotlib.pyplot as plt
from PIL import Image  # Import the Image module from PIL
from multiprocessing import Pool

# Configuration
class Config:
    SR = 32000  # Sampling rate
    N_MELS = 128  # Number of Mel bands
    MAX_SEQ_LEN = 200  # Maximum sequence length for input to the model
    ROOT_FOLDER = '/content/drive/MyDrive/dataset/TeamDeepwave/dataset/open/'  # Dataset root folder
    SUBSET_SIZE = 50000  # Size of the subset to use
    OUTPUT_FOLDER = '/content/drive/MyDrive/dataset/TeamDeepwave/dataset/preprocessed/'  # Folder to save PNG images
    IMAGE_SIZE = (32, 32)  # Target image size for resizing

CONFIG = Config()

# Ensure output directories exist
os.makedirs(os.path.join(CONFIG.OUTPUT_FOLDER, 'train', 'real'), exist_ok=True)
os.makedirs(os.path.join(CONFIG.OUTPUT_FOLDER, 'train', 'fake'), exist_ok=True)
os.makedirs(os.path.join(CONFIG.OUTPUT_FOLDER, 'test'), exist_ok=True)

# Function to load file paths and labels from CSV and select a subset for training data
def load_train_file_paths_and_labels(csv_path, subset_size=CONFIG.SUBSET_SIZE):
    df = pd.read_csv(csv_path)
    df_subset = df.sample(n=subset_size)
    file_paths = df_subset['path'].apply(lambda x: os.path.join(CONFIG.ROOT_FOLDER, x)).tolist()
    labels = df_subset['label'].tolist()
    return file_paths, labels

# Function to load file paths from CSV and select a subset for testing data
def load_test_file_paths(csv_path, subset_size=CONFIG.SUBSET_SIZE):
    df = pd.read_csv(csv_path)
    df_subset = df.sample(n=subset_size)
    file_paths = df_subset['path'].apply(lambda x: os.path.join(CONFIG.ROOT_FOLDER, x)).tolist()
    return file_paths

# Function to save Mel-spectrogram as PNG
def save_mel_spectrogram(args):
    file_path, label, output_folder, is_test = args
    try:
        y, sr = librosa.load(file_path, sr=CONFIG.SR)
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=CONFIG.N_MELS)
        mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)

        plt.figure(figsize=(4, 4))  # Adjust figure size to match the target resolution
        librosa.display.specshow(mel_spectrogram_db, sr=sr, x_axis='time', y_axis='mel')
        plt.colorbar(format='%+2.0f dB')
        plt.tight_layout()

        filename = os.path.basename(file_path).replace('.ogg', '.png')
        if is_test:
            output_path = os.path.join(output_folder, filename)
        else:
            if label == 'fake':
                output_path = os.path.join(output_folder, 'fake', filename)
            else:
                output_path = os.path.join(output_folder, 'real', filename)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        plt.savefig(output_path, dpi=100)
        plt.close()

        # Load the saved image, convert to grayscale, and resize
        img = Image.open(output_path).convert('L')
        img = img.resize(CONFIG.IMAGE_SIZE)
        img.save(output_path)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Load file paths and labels for a subset of 50000 training files
train_files, train_labels = load_train_file_paths_and_labels('/content/drive/MyDrive/dataset/TeamDeepwave/dataset/open/train.csv')

# Load file paths for a subset of 50000 testing files
test_files = load_test_file_paths('/content/drive/MyDrive/dataset/TeamDeepwave/dataset/open/test.csv')

# Prepare arguments for multiprocessing
train_args = [(file_path, label, os.path.join(CONFIG.OUTPUT_FOLDER, 'train'), False) for file_path, label in zip(train_files, train_labels)]
test_args = [(file_path, None, os.path.join(CONFIG.OUTPUT_FOLDER, 'test'), True) for file_path in test_files]

# Use multiprocessing to speed up the process
with Pool() as pool:
    list(tqdm(pool.imap(save_mel_spectrogram, train_args), total=len(train_args)))
    list(tqdm(pool.imap(save_mel_spectrogram, test_args), total=len(test_args)))

print('Mel-spectrogram images saved successfully.')

def load_file_paths_and_labels(csv_path, subset_size=200):
    df = pd.read_csv(csv_path)
    print("CSV Columns:", df.columns)  # Debug print to check columns
    print(df.head())  # Print first few rows to check structure
    df_subset = df.sample(n=subset_size, random_state=CONFIG.SEED)
    file_paths = df_subset['filepath'].apply(lambda x: os.path.join(CONFIG.ROOT_FOLDER, x)).tolist()
    labels = df_subset['class'].apply(lambda x: [1, 0] if x == 'fake' else [0, 1]).tolist()
    return file_paths, labels
