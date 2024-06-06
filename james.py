import os
import re
from datetime import datetime
import glob

def preprocess_chat(chat_lines):
    """ Preprocess chat lines to ensure multi-line messages are correctly formatted. """
    processed_lines = []
    buffer = ""

    timestamp_pattern = re.compile(r'^\[\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}:\d{2}(\s?(AM|PM|am|pm))?\]')
    
    for line in chat_lines:
        if timestamp_pattern.match(line):
            if buffer:
                processed_lines.append(buffer.strip())
                buffer = ""
            buffer = line.strip()
        else:
            buffer += " " + line.strip()
    
    if buffer:
        processed_lines.append(buffer.strip())

    return processed_lines

def parse_chat_line(line):
    """ Parse a single chat line into a dictionary with timestamp, sender, and message. """
    match = re.match(r'^\[(.*?)\] (.*?): (.*)', line)
    if match:
        timestamp_str, sender, message = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%d/%m/%y, %I:%M:%S %p')
        return {'timestamp': timestamp, 'sender': sender, 'message': message}
    return None

def remove_duplicate_lines(lines):
    """ Remove duplicate lines from the raw chat lines. """
    seen_lines = set()
    unique_lines = []
    
    for line in lines:
        if line not in seen_lines:
            seen_lines.add(line)
            unique_lines.append(line)
    
    return unique_lines

def combine_chats(chat_files):
    """ Combine multiple chat files into one list of messages. """
    all_messages = []
    
    for chat_file in chat_files:
        with open(chat_file, 'r', encoding='utf-8') as file:
            chat_lines = file.readlines()
            unique_lines = remove_duplicate_lines(chat_lines)
            processed_lines = preprocess_chat(unique_lines)
            for line in processed_lines:
                parsed_line = parse_chat_line(line)
                if parsed_line:
                    all_messages.append(parsed_line)
    
    return all_messages

def remove_duplicate_messages(messages):
    """ Remove duplicate messages based on timestamp, sender, and message. """
    seen = set()
    unique_messages = []
    
    for message in messages:
        identifier = (message['timestamp'], message['sender'], message['message'])
        if identifier not in seen:
            seen.add(identifier)
            unique_messages.append(message)
    
    return unique_messages

def sort_by_timestamp(messages):
    """ Sort messages by their timestamp. """
    return sorted(messages, key=lambda x: x['timestamp'])

def save_to_file(messages, output_file):
    """ Save the sorted messages to an output file. """
    with open(output_file, 'w', encoding='utf-8') as file:
        for message in messages:
            timestamp_str = message['timestamp'].strftime('%d/%m/%y, %I:%M:%S %p')
            file.write(f"[{timestamp_str}] {message['sender']}: {message['message']}\n")

# Retrieve all .txt files from the "chat logs" folder
chat_folder = 'chat logs'
chat_files = glob.glob(os.path.join(chat_folder, '*.txt'))

# Combine, remove duplicates, sort, and save
all_messages = combine_chats(chat_files)
unique_messages = remove_duplicate_messages(all_messages)
sorted_messages = sort_by_timestamp(unique_messages)
save_to_file(sorted_messages, 'combined_chat.txt')
