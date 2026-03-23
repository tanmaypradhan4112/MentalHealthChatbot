import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load intents
try:
    with open("intents.json", "r") as json_data:
        intents = json.load(json_data)
except FileNotFoundError:
    print("Error: intents.json not found")
    intents = {"intents": []}

# Load trained model
FILE = "data.pth"
try:
    data = torch.load(FILE)
    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data["all_words"]
    tags = data["tags"]
    model_state = data["model_state"]
    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()
except FileNotFoundError:
    print(f"Error: {FILE} not found. Please train the model first using train.py")
    model = None
    all_words = []
    tags = []

bot_name = "Aura"


class ChatBot:
    def __init__(self):
        self.conversation_history = []
        self.emotion_state = None  # Track mood progression
    
    def get_response(self, msg):
        # Store and learn from conversation flow
        self.conversation_history.append(msg)
        # Use history to inform responses
        sentence = tokenize(msg)
        X = bag_of_words(sentence, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)
        output = model(X)
        probs = torch.softmax(output, dim=1)
        prob, predicted = torch.max(probs, dim=1)
        tag = tags[predicted.item()]
        
        if prob.item() > 0.6:  # Lower threshold for more engagement
            for intent in intents["intents"]:
                if tag == intent["tag"]:
                    # NEW: Vary responses based on confidence
                    response = intent["responses"]
                    if len(response) > 1:
                        # Use different responses based on confidence level
                        if prob.item() > 0.9:
                            return response[0]  # Most empathetic
                        elif prob.item() > 0.75:
                            return response[min(1, len(response)-1)]
                        else:
                            return response[-1]  # Least assumptive
                    return random.choice(response)
        else:
            return "I'm not sure I fully understand. Can you tell me more?"


# Standalone function for app.py
def get_response(msg):
    """Get response from the chatbot"""
    if model is None:
        return "Sorry, the chatbot model hasn't been trained yet. Please run train.py first."
    
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)
    output = model(X)
    probs = torch.softmax(output, dim=1)
    prob, predicted = torch.max(probs, dim=1)
    tag = tags[predicted.item()]
    
    if prob.item() > 0.6:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                response = intent["responses"]
                if len(response) > 1:
                    if prob.item() > 0.9:
                        return response[0]
                    elif prob.item() > 0.75:
                        return response[min(1, len(response)-1)]
                    else:
                        return response[-1]
                return random.choice(response)
    else:
        return "I'm not sure I fully understand. Can you tell me more?"
