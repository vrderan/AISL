import os
import time
import random
import streamlit as st
import joblib
import torch
import torch.nn as nn
from utils.data import get_category_signs

# --- 1. Define the LSTM Class ---
# This MUST match the class definition used during training exactly.
# If you used the updated version with Dropout and hidden_size=128, use this:
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(LSTMModel, self).__init__()
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        
        # LSTM Layer
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        
        # Dropout Layer
        self.dropout = nn.Dropout(p=0.4) 
        
        # Fully Connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, num_classes)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = out[:, -1, :] 
        out = self.dropout(out)
        
        out = self.fc1(out)
        out = self.relu(out)
        out = self.fc2(out)
        out = self.relu(out)
        out = self.fc3(out)
        return out

# --- 2. Dummy Model for Fallback ---
class DummyModel:
    def __init__(self, lang, category):
        self.lang = lang
        self.category = category
        self.labels = get_category_signs(category, lang)
        
    def predict(self, landmarks):
        if not landmarks:
            return None, 0.0
        if self.labels:
            label = random.choice(self.labels)
            conf = random.uniform(0.7, 0.99)
            return label, conf
        return "Unknown", 0.0

# --- 3. The Loader Function ---
@st.cache_resource(max_entries=1, show_spinner=False)
def load_model(lang, category):
    model_dir = os.path.join("utils", "trained models")   
     
    # Check if directory exists
    if not os.path.exists(model_dir):
        print(f'model_dir does not exist: {model_dir}')
        return DummyModel(lang, category)

    print(f"Loading model for {lang}/{category}...")
    prefix = f"{lang}_{category}_model"

    # --- LOGIC SPLIT ---
    # Case A: 'ABC' Category -> Random Forest (Joblib)
    if category == 'ABC':
        for f in os.listdir(model_dir):
            if f.startswith(prefix) and (f.endswith('.pkl') or f.endswith('.joblib')):
                try:
                    model = joblib.load(os.path.join(model_dir, f))
                    print(f"Loaded Random Forest model from {f}")
                    return model
                except Exception as e:
                    print(f"Failed to load RF model: {e}", flush=True)
    
    # Case B: All Other Categories -> LSTM (PyTorch)
    else:        
        # Let's try to find a .pth file that matches the category, or default to a generic name
        target_file = None
        for f in os.listdir(model_dir):
            # Logic: Look for file starting with 'ASL_Greetings' (example) and ending in .pth
            if f.startswith(f"{lang}_{category}") and f.endswith('.pth'):
                target_file = f
                break

        if target_file:
            try:
                model_path = os.path.join(model_dir, target_file)
                
                # 1. Get Labels
                labels = get_category_signs(category, lang).copy()
                # Add "No Class" class
                labels.append("No Class")
                num_classes = len(labels)
                
                # 2. Instantiate Model (Architecture must match training!)
                # Input Size: 126 (Hands Only), Hidden: 128, Layers: 2
                model = LSTMModel(input_size=126, hidden_size=128, num_layers=2, num_classes=num_classes)
                
                # 3. Load Weights
                # map_location='cpu' ensures it works even if trained on GPU
                model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
                model.eval() # Set to evaluation mode
                
                # 4. Attach classes to the model object (Compatibility with App)
                model.classes_ = labels
                
                print(f"Loaded LSTM model from {target_file}")
                return model
                
            except Exception as e:
                print(f"Failed to load PyTorch model: {e}", flush=True)

    # Fallback
    print(f"No specific model found for {lang}/{category}, using dummy.")
    return DummyModel(lang, category)