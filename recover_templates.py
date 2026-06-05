import os
import json
import re

log_dir = r'C:\Users\Saptarsha\.gemini\antigravity\brain\866c3589-d2ef-44a8-86ed-5449abc2207a\.system_generated\logs'
transcript_path = os.path.join(log_dir, 'transcript.jsonl')

if not os.path.exists(transcript_path):
    print("Transcript not found")
    exit(1)

print("Recovering templates from transcript...")

# Let's read all JSON objects
steps = []
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            steps.append(json.loads(line))
        except Exception:
            pass

# We want to trace all modifications to index.html, reports.html, and result.html.
# In git status, we saw index.html, reports.html, result.html were modified before we ran restore.
# Let's find the tool calls in the logs that edited these files.
# Let's inspect the tools in order:

for step in steps:
    tool_calls = step.get('tool_calls', [])
    for call in tool_calls:
        name = call.get('name')
        args = call.get('args', {})
        target = args.get('TargetFile', '') or args.get('absolute_path', '') or args.get('AbsolutePath', '')
        if target and any(x in target for x in ['index.html', 'reports.html', 'result.html']):
            # Let's dump the edits
            print(f"Step {step.get('step_index')}: {name} targeting {os.path.basename(target)}")
            # If it's replace_file_content or multi_replace_file_content, let's save the chunks
            out_dir = 'recovered_chunks'
            os.makedirs(out_dir, exist_ok=True)
            out_file = f"{out_dir}/step_{step.get('step_index')}_{os.path.basename(target)}.json"
            with open(out_file, 'w', encoding='utf-8') as out_f:
                json.dump(args, out_f, indent=2)
            print(f"  Saved JSON to {out_file}")

print("Recovery dump complete. Check the 'recovered_chunks' folder.")
