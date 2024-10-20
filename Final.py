# REUIRMENT_1
# 1. PDF_Downloading_from_JSON
import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# path of given json file
json_file_path = r"C:\Users\majhi\OneDrive\Desktop\ai_intern\Dataset.json"  

#extraction pdf file location
output_folder = r"C:\Users\majhi\OneDrive\Desktop\ai_intern\pdfs" 


MAX_RETRIES = 3


# Function to download a single PDF
def download_pdf(pdf_key, pdf_url):
    try:
        print(f"Downloading {pdf_key} from: {pdf_url}")
        response = requests.get(pdf_url, timeout=15)

        if response.status_code == 200:
            pdf_filename = os.path.join(output_folder, f"{pdf_key}.pdf")  
            with open(pdf_filename, 'wb') as pdf_file:
                pdf_file.write(response.content)
            print(f"Successfully downloaded: {pdf_filename}")
            return pdf_filename  
        else:
            print(f"Failed to download PDF from: {pdf_url} - Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {pdf_key} from {pdf_url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while downloading {pdf_key}: {e}")
        return None


# Read JSON and download PDF using threading

try:
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

       
        os.makedirs(output_folder, exist_ok=True)

       
        fail_pdf = []

        # Download each PDF ony by one
        with ThreadPoolExecutor(max_workers=5) as executor:  
            files = {executor.submit(download_pdf, pdf_key, pdf_url): pdf_key for pdf_key, pdf_url in data.items()}

            for future in as_completed(files):
                pdf_key = files[future]
                try:
                    result = future.result() 
                    if result is None:
                        fail_pdf.append(pdf_key)
                except Exception as e:
                    print(f"Error processing {pdf_key}: {e}")
                    fail_pdf.append(pdf_key)

       
        
except FileNotFoundError:
    print(f"The file {json_file_path}  not found.")



# REUIRMENT_2

# 2. Storing_Metadata_in_MongoDB


import pymongo
from datetime import datetime

# Connecting  to MongoDB programatically
client = pymongo.MongoClient("mongodb://localhost:27017/")
# Access  database
db = client["AI_Intern"]
# Access collection
collection = db["Extracted"]



# Function to get metadata(name,size,path) for all PDF
def get_pdf_metadata(pdf_folder):
    pdf_metadata = []
    
    for file_name in os.listdir(pdf_folder):
        if file_name.endswith(".pdf"):  
            file_path = os.path.join(pdf_folder, file_name)
            file_size = os.path.getsize(file_path)  
            
           
            pdf_metadata.append({
                "name": file_name,
                "path": file_path,
                "size": file_size
                
            })
    
    return pdf_metadata


metadata = get_pdf_metadata(output_folder)


for data in metadata:
    collection.insert_one(data)  
    print(f"Metadata for {data['name']} stored successfully.")


# REUIRMENT_3
# 3. PDF_Summarization_and_Keyword_Extraction


import PyPDF2
import string
from collections import Counter
from heapq import nlargest

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    pdf_text = ''
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in range(len(reader.pages)):
            pdf_text += reader.pages[page].extract_text()
    return pdf_text


def clean_and_tokenize(text):
    stop_words = set([
        'the', 'and', 'is', 'in', 'it', 'of', 'to', 'a', 'that', 'this', 'with', 'as', 'for', 'on', 'was', 'are', 'by', 'an', 'be', 'or', 'at', 'which', 'from', 'not'
    ])  # Basic stopwords, can be extended
    tokens = text.lower().split()
    tokens = [word.strip(string.punctuation) for word in tokens if word.isalpha() and word not in stop_words]
    return tokens


def summarize_text(text, summary_ratio=0.2):
    sentences = text.split('. ')
    word_frequencies = {}
    
 
    tokens = clean_and_tokenize(text)
    word_frequencies = Counter(tokens)
    
   
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency
    
  
    sentence_scores = {}
    for sentence in sentences:
        sentence_word_count = 0
        for word in clean_and_tokenize(sentence):
            if word in word_frequencies:
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_frequencies[word]
                sentence_word_count += 1
        if sentence_word_count > 0:
            sentence_scores[sentence] /= sentence_word_count 

   
    num_sentences = int(len(sentences) * summary_ratio)
    summary_sentences = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    
    return '. '.join(summary_sentences)


def extract_keywords(text, top_n=10):
   
    tokens = clean_and_tokenize(text)
    
    # Get word frequencies
    word_frequencies = Counter(tokens)
    
   
    keywords = nlargest(top_n, word_frequencies.items(), key=lambda x: x[1])
    
    return [word for word, freq in keywords]

# Function to save summary and keywords to a JSON file in the specified directory
def save_to_json(summary, keywords, output_file_name, output_dir):
    output_data = {
        "summary": summary,
        "keywords": keywords
    }
    
  
    output_file_path = os.path.join(output_dir, output_file_name)
    
    with open(output_file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)
    print(f"Summary and keywords have been saved to {output_file_path}")

# Main function to read multiple PDFs, summarize, and extract keywords
def process_multiple_pdfs(pdf_dir, output_dir):
    # Loop through all files in the directory
    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, pdf_file)
            print(f"Processing {pdf_file}...")

           
            text = extract_text_from_pdf(pdf_path)
            
           
            summary = summarize_text(text, summary_ratio=0.2)
            print(f"Summary for {pdf_file}:\n", summary)
            
           
            keywords = extract_keywords(text, top_n=10)
            print(f"\nKeywords for {pdf_file}:\n", keywords)
            
        
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_file_name = f"{base_name}.json"
            
         
            save_to_json(summary, keywords, output_file_name, output_dir)

# Replace with your local path to the directory containing PDFs and output directory
pdf_dir = r"C:\Users\majhi\OneDrive\Desktop\ai_intern\pdfs" 
output_dir = r"C:\Users\majhi\OneDrive\Desktop\ai_intern\pdf_summaries" 


if __name__ == "__main__":
    os.makedirs(output_dir, exist_ok=True)  
    process_multiple_pdfs(pdf_dir, output_dir)




# REUIRMENT_4

# update_in_mongoDB_summaries_and_keyword


import os
import json
import pymongo


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["AI_Intern"]
collection = db["Extracted"]


json_directory = r"C:\Users\majhi\OneDrive\Desktop\ai_intern\pdf_summaries" 


for json_file in os.listdir(json_directory):
    if json_file.endswith('.json'):  
        file_path = os.path.join(json_directory, json_file)
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)  
                
              
                pdf_name = json_file.replace('.json', '.pdf')
                
               
                update_data = {
                    "summary": data.get("summary"),
                    "keywords": data.get("keywords")
                }
                
                
                result = collection.update_one(
                    {"name": pdf_name}, 
                    {"$set": update_data} 
                )
                
                if result.matched_count > 0:
                    print(f"Updated {pdf_name} with summary and keywords.")
                else:
                    print(f"No matching document found for {pdf_name}.")
                    
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file {json_file}.")
        
