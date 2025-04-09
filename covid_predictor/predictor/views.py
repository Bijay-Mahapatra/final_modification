from django.contrib.auth.decorators import login_required
import pandas as pd
from django.shortcuts import render,redirect
from django.http import JsonResponse
from sklearn.tree import DecisionTreeClassifier
import joblib
import os
from django.conf import settings
import logging
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# View functions for rendering pages
def home(request):
    return render(request, 'index.html')

#def dash(request):
    #return render(request, 'dashboard.html')

def acc(request):
    return render(request, 'account.html')

def medical(request):
    return render(request, 'medical-history.html')

def log(request):
    return render(request, 'logout.html')
@login_required
def prediction_result(request):
    if request.method == 'POST':
        # Get all selected symptoms from POST data
        symptom_mapping = {
            'breathing_problem': 'Breathing problem',
            'fever': 'Fever',
            'dry_cough': 'Dry cough',
            'sore_throat': 'Sore throat',
            'runny_nose': 'Runny nose',
            'asthma': 'Asthma',
            'headache': 'Headache',
            'heart_disease': 'Heart disease',
            'diabetes': 'Diabetes',
            'hypertension': 'Hypertension',
            'abroad_travel': 'Abroad travel',
            'attended_gathering': 'Attended gathering',
            'visited_public_areas': 'Visited public areas',
            'family_working_in_public': 'Family working in public'
        }
        
        selected_symptoms = []
        for field_name, symptom_name in symptom_mapping.items():
            if request.POST.get(field_name) == '1':
                selected_symptoms.append(symptom_name)
        
        # Determine result (simplified for demo)
        result = 'positive' if len(selected_symptoms) >= 3 else 'negative'
        
        context = {
            'result': result,
            'selected_symptoms': selected_symptoms
        }
        return render(request, 'prediction_result.html', context)
    
    return redirect('home')
# Load and preprocess the dataset
def load_and_preprocess_data():
    dataset_path = os.path.join(settings.BASE_DIR, 'Covid_dataset.csv')
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset file not found at: {dataset_path}")
        raise FileNotFoundError(f"Dataset file not found at: {dataset_path}")
    
    df = pd.read_csv(dataset_path)
    logger.debug(f"Dataset loaded with shape: {df.shape}")
    
    # Map categorical values to numerical
    mappings = {'No': 0, 'Yes': 1}
    columns_to_map = [
        'Breathing Problem', 'Fever', 'Dry Cough', 'Sore throat', 'Running Nose',
        'Asthma', 'Headache', 'Heart Disease', 'Diabetes', 'Hyper Tension',
        'Abroad travel', 'Contact with COVID Patient', 'Attended Large Gathering',
        'Visited Public Exposed Places', 'Family working in Public Exposed Places'
    ]
    
    for column in columns_to_map:
        if column in df.columns:
            df[column] = df[column].map(mappings)
        else:
            logger.warning(f"Column {column} not found in dataset")
    
    # Ensure target column exists
    if 'COVID-19' not in df.columns:
        logger.error("Target column 'COVID-19' not found in dataset")
        raise ValueError("Target column 'COVID-19' not found in dataset")
    
    return df

# Train and save the model (run this once or when needed)
def train_and_save_model():
    try:
        df = load_and_preprocess_data()
        X = df.drop(columns=['COVID-19'])
        y = df['COVID-19']
        
        model = DecisionTreeClassifier(random_state=5)
        model.fit(X, y)
        
        model_path = os.path.join(settings.BASE_DIR, 'covid_model.joblib')
        joblib.dump(model, model_path)
        logger.info(f"Model trained and saved to: {model_path}")
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise

# Prediction view
@login_required
def predict_covid(request):
    if request.method == 'POST':
        try:
            # Define all expected features
            feature_names = [
                'Breathing Problem', 'Fever', 'Dry Cough', 'Sore throat', 'Running Nose',
                'Asthma', 'Headache', 'Heart Disease', 'Diabetes', 'Hyper Tension',
                'Abroad travel', 'Contact with COVID Patient', 'Attended Large Gathering',
                'Visited Public Exposed Places', 'Family working in Public Exposed Places'
            ]
            
            # Get symptoms from POST data (default to 0 if not present)
            symptoms = {
                'Breathing Problem': int(request.POST.get('breathing_problem', 0)),
                'Fever': int(request.POST.get('fever', 0)),
                'Dry Cough': int(request.POST.get('dry_cough', 0)),
                'Sore throat': int(request.POST.get('sore_throat', 0)),
                'Running Nose': int(request.POST.get('runny_nose', 0)),
                'Asthma': int(request.POST.get('asthma', 0)),
                'Headache': int(request.POST.get('headache', 0)),
                'Heart Disease': int(request.POST.get('heart_disease', 0)),
                'Diabetes': int(request.POST.get('diabetes', 0)),
                'Hyper Tension': int(request.POST.get('hypertension', 0)),
                'Abroad travel': int(request.POST.get('abroad_travel', 0)),
                'Contact with COVID Patient': int(request.POST.get('attended_gathering', 0)),  # Fixed mapping
                'Attended Large Gathering': int(request.POST.get('attended_gathering', 0)),
                'Visited Public Exposed Places': int(request.POST.get('visited_public_areas', 0)),
                'Family working in Public Exposed Places': int(request.POST.get('family_working_in_public', 0))
            }
            logger.debug(f"Received symptoms: {symptoms}")
            
            # Load the trained model
            model_path = os.path.join(settings.BASE_DIR, 'covid_model.joblib')
            if not os.path.exists(model_path):
                logger.info("Model file not found, training new model")
                train_and_save_model()
            
            model = joblib.load(model_path)
            logger.debug("Model loaded successfully")
            
            # Create input DataFrame with all required columns in correct order
            input_data = pd.DataFrame([symptoms], columns=feature_names)
            
            # Make prediction
            prediction = model.predict(input_data)[0]
            logger.debug(f"Prediction: {prediction}")
            
            # Get patient info (optional for authenticated users)
            patient_info = {
                'name': request.POST.get('patientName', request.user.get_full_name()),
                'age': request.POST.get('patientAge', ''),
                'gender': request.POST.get('patientGender', ''),
                'notes': request.POST.get('patientNotes', '')
            }
            
            # Calculate risk percentage based on symptom count
            symptom_count = sum(symptoms.values())
            if prediction == 0:
                result = "negative"
                message = "Be happy - You are COVID Negative"
                risk_percent = max(5, min(30, symptom_count * 3))
            else:
                result = "positive"
                message = "Sorry to say - You are COVID Positive"
                risk_percent = min(95, 50 + (symptom_count * 5))
            
            return JsonResponse({
                'status': 'success',
                'result': result,
                'message': message,
                'risk_percent': risk_percent,
                'patient_info': patient_info
            })
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"Prediction failed: {str(e)}"
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


@require_POST
@ensure_csrf_cookie
def logout_view(request):
    try:
        logout(request)  # This clears the user's session
        return JsonResponse({
            'status': 'success',
            'message': 'Successfully logged out'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)