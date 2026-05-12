import os
import glob
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHUNKS_DIR = os.path.join(os.path.dirname(__file__), 'chunks')

def clean_text(raw_text):
    """
    Remove the generic Groww header and footer noise from the scraped text.
    """
    # Find the start of the relevant data
    start_marker = "NAV:"
    start_idx = raw_text.find(start_marker)
    
    # If we found NAV, we want to include the returns right before it. 
    # Backing up ~50 characters usually catches the 1Y/3Y returns.
    if start_idx != -1:
        start_idx = max(0, start_idx - 50)
    else:
        # Fallback if NAV is missing
        start_idx = 0
        
    # Find the end of the relevant data (start of the footer breadcrumbs)
    end_marker = "Home > Mutual Funds >"
    end_idx = raw_text.find(end_marker)
    
    if end_idx == -1:
        end_idx = len(raw_text)
        
    cleaned = raw_text[start_idx:end_idx].strip()
    return cleaned

def chunk_text(text, chunk_size=500, chunk_overlap=100):
    """
    Splits text into overlapping chunks.
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # Try to snap the end to a space to avoid cutting words in half
        if end < text_length:
            last_space = text.rfind(' ', start, end)
            if last_space != -1 and last_space > start + (chunk_size // 2):
                end = last_space
                
        chunks.append(text[start:end].strip())
        
        if end == text_length:
            break
            
        # Move start forward, considering overlap
        start = end - chunk_overlap
        
        # Try to snap the start to a space
        next_space = text.find(' ', start)
        if next_space != -1 and next_space < start + (chunk_overlap // 2):
            start = next_space + 1
            
    return chunks

def process_files():
    os.makedirs(CHUNKS_DIR, exist_ok=True)
    
    txt_files = glob.glob(os.path.join(DATA_DIR, '*.txt'))
    print(f"Found {len(txt_files)} files to process.")
    
    total_chunks = 0
    
    for filepath in txt_files:
        filename = os.path.basename(filepath)
        slug = filename.replace('.txt', '')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract metadata from our custom header
        parts = content.split('-' * 50 + '\n\n', 1)
        if len(parts) != 2:
            print(f"Skipping {filename} - invalid format")
            continue
            
        header_text = parts[0]
        raw_body = parts[1]
        
        # Parse metadata
        metadata = {}
        for line in header_text.strip().split('\n'):
            if ': ' in line:
                key, val = line.split(': ', 1)
                metadata[key] = val
                
        # Clean the noise
        cleaned_body = clean_text(raw_body)
        
        # Chunk the text
        text_chunks = chunk_text(cleaned_body, chunk_size=500, chunk_overlap=100)
        
        # Prepare the final JSON structure
        output_data = []
        for i, chunk in enumerate(text_chunks):
            output_data.append({
                "chunk_id": f"{slug}-chunk-{i+1}",
                "metadata": metadata,
                "text": chunk
            })
            
        # Save to chunks directory
        out_filepath = os.path.join(CHUNKS_DIR, f"{slug}.json")
        with open(out_filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            
        print(f"Processed {filename} -> {len(text_chunks)} chunks saved to {out_filepath}")
        total_chunks += len(text_chunks)
        
    print(f"Done! Generated a total of {total_chunks} chunks.")

if __name__ == '__main__':
    process_files()
