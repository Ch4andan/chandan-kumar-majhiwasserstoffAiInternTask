PDF Processing Pipeline
This project provides an end-to-end solution for downloading, processing, and storing PDFs with parallel processing to manage multiple files and high volumes efficiently. Below is the detailed explanation of each requirement:

Requirement 1: PDF Ingestion & Parsing
PDF Downloading
The system downloads PDFs from URLs provided in a JSON file and saves them to a specified local folder. It can handle varying document lengths:

Short PDFs (1-10 pages): Quickly processed with concise summaries.
Medium PDFs (10-30 pages): Requires moderate processing power.
Long PDFs (30+ pages): Involves more intensive processing for summarization and keyword extraction.
Concurrency
The pipeline supports multi-threading, using Python's ThreadPoolExecutor to manage multiple PDF downloads concurrently. This improves efficiency by allowing several PDFs to be downloaded simultaneously. The system also implements retry logic to handle failed downloads, retrying up to a specified number of times if there are issues with network requests.

Concurrency Benefits:

Faster PDF downloading and processing.
Efficient resource utilization.
Scalable for high-volume PDF handling.
Error Handling
The system handles potential errors during downloading (e.g., network issues, invalid URLs) by catching exceptions and logging failed downloads. These files are added to a retry list for further attempts or logged as failures if retries exceed the limit.

Requirement 2: MongoDB Dataset Storage & JSON Updates
Metadata Storage
Once PDFs are downloaded, the system extracts the following metadata for each PDF:

Document name: The file name of the PDF.
Path: The location of the PDF file on the local system.
Size: The file size in bytes.
This metadata is stored in a MongoDB collection for future reference. The system uses PyMongo to connect to MongoDB and insert metadata as soon as the PDFs are downloaded.

Post-Processing MongoDB Updates
After the PDFs are processed (summarization and keyword extraction), the MongoDB entries are updated with the output data (summary and keywords). The MongoDB update_one() operation is used to add or modify the document with the new data.

MongoDB allows easy querying and management of PDF metadata and extracted information, making it a central repository for tracking all processed documents.

Requirement 3: Summarization & Keyword Extraction
Summarization
The pipeline uses a basic text summarization technique by extracting the text from the PDF using PyPDF2. It splits the text into sentences, calculates word frequencies, and scores each sentence based on the frequency of its words.

Dynamic Summaries: The summary length is proportional to the length of the document. Short PDFs get concise summaries, while longer PDFs are summarized more comprehensively.
Text Cleaning: The text is cleaned and tokenized to remove common stopwords (e.g., 'the', 'and', 'is') to focus on important content.
How Summarization Works:

Tokenizes the text and calculates the frequency of each word.
Scores sentences based on word frequency.
Extracts the top-scoring sentences as the summary (about 20% of the total sentences).
Keyword Extraction
Keywords are extracted from the PDF text by identifying frequently occurring, domain-specific words. A similar tokenization and frequency calculation is used, but the focus is on extracting unique and non-generic terms relevant to the PDF’s content.

Top N Keywords: You can customize how many top keywords (e.g., top 10) should be extracted.
Stopword Removal: Common, irrelevant words (like 'a', 'the', etc.) are excluded to ensure only significant terms are chosen.
The extracted keywords and summary are then saved in JSON format for each PDF. This allows the output to be structured and stored efficiently.

Requirement 4: JSON Structure & MongoDB Updates
JSON Format
Once the summarization and keyword extraction are complete, the results are formatted into JSON files. Each JSON file contains two main fields:

Summary: A text summary of the document.
Keywords: A list of top extracted keywords.
The JSON files are stored locally and later used to update the MongoDB collection corresponding to each PDF.

Efficient MongoDB Updates
Using the update_one() method in MongoDB, the existing entries for each PDF are updated with the new fields (summary and keywords). If a document doesn't already exist in MongoDB (i.e., if there was an error during ingestion), the system logs this to ensure consistency between the file system and database.

Error Handling:

Logs any issues during JSON parsing (e.g., malformed files) to ensure MongoDB records remain unaffected.
Ensures that updates happen only after successful PDF processing.
Requirement 5: Concurrency & Performance
Concurrency
To enhance the pipeline’s performance, the project employs concurrent processing in two main areas:

PDF Downloading: Multiple PDFs are downloaded in parallel, using Python’s concurrent.futures module.
PDF Processing: Summarization and keyword extraction are also handled in parallel, ensuring that large datasets are processed in a reasonable time frame.
This reduces the overall execution time significantly, especially when dealing with a large number of files.

Performance
The system is designed to efficiently handle:

Short PDFs: Quick to process with minimal resource use.
Medium PDFs: Managed efficiently with parallel threads.
Large PDFs: Scalable to handle even 30+ page documents without crashing, though processing time is proportional to the document length.
Scalability:

Can be easily extended to process even larger datasets by increasing the number of concurrent threads.
Proper resource management ensures that large-scale operations (high volume of PDFs) do not overwhelm the system.
Summary
This PDF processing pipeline is designed to:

Efficiently handle the download, processing, and storage of PDFs, including document metadata, summaries, and keywords.
Use concurrency to process large volumes of files simultaneously, improving performance and scalability.
Maintain robust error handling to manage failures during downloading, parsing, or storing, ensuring data integrity.
Key Features:
Parallel PDF Processing: Multiple PDFs are processed simultaneously.
MongoDB Integration: Stores PDF metadata and processed output (summary and keywords).
Dynamic Summarization: Summaries scale with document size.
Efficient Keyword Extraction: Extracts key, domain-specific terms.
Error Logging: Logs any issues, ensuring MongoDB records remain consistent.
This project is scalable and optimized for real-world scenarios requiring large-scale PDF management and processing.
