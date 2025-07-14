from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .models import DetectionHistory
import joblib
import os

model_path = os.path.join(os.path.dirname(__file__), '..', 'ML', 'model.pkl')
model = joblib.load(model_path)

def home(request):
    return render(request, 'detection_app/home.html')

def about(request):
    return render(request, 'detection_app/about.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'detection_app/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('detect')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    return render(request, 'detection_app/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

import xgboost as xgb
import numpy as np
import joblib
import csv # for saving user entered data for future training the model
@login_required
def detect_fake_profile(request):
    if request.method == 'POST':
        username = request.POST['username']
        followers = float(request.POST['followers'])
        following = float(request.POST['following'])
        posts = float(request.POST['posts'])
        bio_length = float(request.POST['bio_length'])
        profile_pic = float(request.POST['profile_pic'])
        account_age_days = float(request.POST['account_age_days'])
        engagement_ratio = float(request.POST['engagement_ratio'])

        input_array = np.array([[followers, following, posts, bio_length, profile_pic, account_age_days, engagement_ratio]])

        # Load scaler
        scaler = joblib.load(os.path.join(os.path.dirname(__file__), '..', 'ML', 'model.pkl'))
        scaled_input = scaler.transform(input_array)

        # Load Booster model
        booster = xgb.Booster()
        booster.load_model(os.path.join(os.path.dirname(__file__), '..', 'ML', 'xgb_model.json'))

        # Convert to DMatrix
        dmatrix_input = xgb.DMatrix(scaled_input)

        # Predict
        preds = booster.predict(dmatrix_input)
        prediction = 'Fake Profile' if preds[0] > 0.5 else 'Genuine Profile'

        # After preds generated store in the history
        DetectionHistory.objects.create(
        user=request.user,
        username=username,
        followers=followers,
        following=following,
        posts=posts,
        bio_length=bio_length,
        profile_pic=profile_pic,
        account_age_days=account_age_days,
        engagement_ratio=engagement_ratio,
        result=prediction
        )

         # Save detection to CSV
        with open(os.path.join(os.path.dirname(__file__), '..', 'ML/updating_dataset', 'altered_realistic_dataset.csv'), mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([followers, following, posts, bio_length, profile_pic, account_age_days, engagement_ratio, int(preds[0])])

        return render(request, 'detection_app/detect.html', {'prediction': prediction})

    return render(request, 'detection_app/detect.html')


@login_required
def history(request):
    records = DetectionHistory.objects.filter(user=request.user).order_by('-detected_at')
    return render(request, 'detection_app/history.html', {'records': records})