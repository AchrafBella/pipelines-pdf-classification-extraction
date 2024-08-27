from utils import load_ml_model, text_preprocessing
from config import OUTPUT_LABEL

def ml_classification_pipeline(text: str, bucket_name: str):

    clean_text_df = text_preprocessing(text)
    tfidf = load_ml_model(bucket_name, model_filename='TFIDF_20240802.joblib')
    features = tfidf.transform(clean_text_df['text']).toarray()
    clf = load_ml_model(bucket_name, model_filename='ExtraTreesClassifier_optuna_20240802.joblib')
    predictions = clf.predict(features)

    return OUTPUT_LABEL[predictions[0]]
