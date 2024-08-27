
from config import STOPWORDS
from nltk.tokenize import RegexpTokenizer
from botocore.exceptions import ClientError
from nltk.stem import porter
from pandas import DataFrame, Series, read_csv
from io import StringIO
import boto3
import joblib
import string
import json
import re
import io
import os

def read_s3_document(s3ID: str, bucket_name: str) -> str:

    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=s3ID)
    pdf_content = response['Body'].read()
    pdf_file = io.BytesIO(pdf_content)

    return pdf_file

def load_ml_model(bucket_name: str, model_filename: str):
    
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=model_filename)
    json_content = response['Body'].read()
    model = joblib.load(io.BytesIO(json_content))

    return model

def clean_text(text: str):
    '''Get rid of some additional punctuation and non-sensical text that was missed the first time around.'''
    
    text = text.lower()
    text = re.sub('\n', ' ', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\t', ' ', text)  # Replace tab with space
    text = re.sub('\s+', ' ', text)  # Replace multiple spaces with a single space
    
    return text.strip()

def stemmer_adapter(sent: str):

    stemmer = porter.PorterStemmer()
    list_token = []
    for word in sent:
        list_token.append(stemmer.stem(word))

    return list_token

def text_preprocessing(text: str):

    # convert text to dataframe object
    df = DataFrame([text], columns=['text'])
    
    # cleaning
    df['text'] = df['text'].apply(lambda x: clean_text(x))

    # token
    tokenizer = RegexpTokenizer('[^_\W0-9]+')
    corpus_tokens = [tokenizer.tokenize(pdf) for pdf in df['text']]
    df['text'] = corpus_tokens

    # Finally remove stop words from our corpus
    tokens_without_stp_words = [[word for word in sent if word not in STOPWORDS] for sent in df['text']]
    df['text'] = Series(tokens_without_stp_words)

    df['text'] = df['text'].apply(lambda x: stemmer_adapter(x))

    # construct the text 
    df['text'] = df['text'].apply(lambda x: ' '.join(elm for elm in x))
    
    return df

def string_to_dataframe_certifications(string):
    """
    This function used to convert string from the output of chatgpt api to dataframe.
    Use this function only for certifications.
    """
    if string == 'NA':
        return
    
    # Use StringIO to simulate reading from a file
    data = StringIO(string)
    
    # Use read_csv with appropriate parameters
    df = read_csv(data, sep="|", engine='python')
    
    return df

def string_to_dataframe_DPE(string):
    """
    This function used to convert string from the output of chatgpt api to dataframe.
    Use this function only for DPE.
    """
    if string == 'NA':
        return

    # Split the string into lines
    lines = [elm for elm in string.split('\n') if elm != '']

    # Split each line into key-value pairs
    data = {}
    for line in lines:
        key, value = line.split(':', 1)  # Split only on the first colon
        data[key.strip()] = value.strip()

    # Convert dictionary to dataframe
    df = DataFrame(list(data.items()), columns=['Parameter', 'Value'])
    
    return df

def string_to_dataframe(string):
    """
    This function used to convert string from the output of chatgpt api to dataframe.
    Use this function only for rapport d'expertise & fichier descriptif.
    """
    if string == 'NA':
        return
    
    data = StringIO(string)
    
    df = read_csv(data, sep="|", engine='python')
    
    df = df.drop(columns=[df.columns[0], df.columns[-1]])
    
    return df

def check_file_exists(s3ID: str, bucket_name: str):
    # Initialize the S3 client
    s3 = boto3.client('s3')

    try:
        # Try to head the object (this request doesn't download the file, just checks its existence)
        s3.head_object(Bucket=bucket_name, Key=s3ID)
        return {'error': False, 'message': f"File '{s3ID}' exists in bucket '{bucket_name}'."}
    except ClientError as e:
        # If a 404 error is thrown, then the file does not exist
        if e.response['Error']['Code'] == '404':
            return {'error': True, 'message': f"File '{s3ID}' does not exist in bucket '{bucket_name}'."}
        else:
            # If there's another error, re-raise it
            raise {'error': True, 'message': str(e)}

def get_secret():

    secret_name = f"rqr-lambdas-{os.getenv('RQR_ENV')}"
    #region_name = os.getenv('AWS_REGION')
    region_name = 'eu-west-1'
    
    if not secret_name or not region_name:
        raise ValueError("Secret name or region is not set in the environment variables.")

    # Create a Secrets Manager client
    client = boto3.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        # Retrieve the secret value
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(get_secret_value_response['SecretString'])

    except ClientError as e:
        raise e
    
    return secret_dict
