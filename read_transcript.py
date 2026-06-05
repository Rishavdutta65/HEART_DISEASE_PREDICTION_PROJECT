import os
import json

log_dir = r'C:\Users\Saptarsha\.gemini\antigravity\brain\866c3589-d2ef-44a8-86ed-5449abc2207a\.system_generated\logs'
transcript_path = os.path.join(log_dir, 'transcript.jsonl')

if not os.path.exists(transcript_path):
    print("Transcript not found at", transcript_path)
    # Check if there are other files in the directory
    if os.path.exists(log_dir):
        print("Files in directory:", os.listdir(log_dir))
    else:
        print("Log directory does not exist.")
    exit(1)

print("Reading transcript...")
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f):
        try:
            data = json.loads(line)
            # Look for write_to_file or replace_file_content tool calls
            tool_calls = data.get('tool_calls', [])
            for call in tool_calls:
                method = call.get('method')
                args = call.get('args', {})
                target = args.get('TargetFile', '') or args.get('absolute_path', '') or args.get('AbsolutePath', '')
                if target and any(x in target for x in ['index.html', 'reports.html', 'result.html']):
                    print(f"Line {line_num}: Tool {method} targeting {target}")
                    # Print snippet of arguments
                    desc = args.get('Description', '') or args.get('Instruction', '')
                    print(f"  Desc: {desc}")
        except Exception as e:
            print(f"Error parsing line {line_num}: {e}")
