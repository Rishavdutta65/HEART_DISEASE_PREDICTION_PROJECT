import os
import json

log_dir = r'C:\Users\Saptarsha\.gemini\antigravity\brain\866c3589-d2ef-44a8-86ed-5449abc2207a\.system_generated\logs'
transcript_path = os.path.join(log_dir, 'transcript.jsonl')

if not os.path.exists(transcript_path):
    print("Transcript not found")
    exit(1)

print("Searching transcript for file edits...")
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f):
        try:
            data = json.loads(line)
            tool_calls = data.get('tool_calls', [])
            for call in tool_calls:
                method = call.get('name') or call.get('method')
                args = call.get('args', {})
                target = args.get('TargetFile', '') or args.get('absolute_path', '') or args.get('AbsolutePath', '')
                if target and any(x in target for x in ['index.html', 'reports.html', 'result.html']):
                    print(f"Line {line_num}: Tool {method} targeting {target}")
                    # Write out the contents to a recovery folder
                    os.makedirs('recovered', exist_ok=True)
                    # Let's save the args to a JSON file
                    out_name = f"recovered/{line_num}_{os.path.basename(target)}.json"
                    with open(out_name, 'w', encoding='utf-8') as out_f:
                        json.dump(args, out_f, indent=2)
                    print(f"  Saved args to {out_name}")
        except Exception as e:
            pass
