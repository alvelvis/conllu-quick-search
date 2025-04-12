from flask import Flask, render_template, request
import glob
import os, subprocess, sys
import json
import requests
import urllib
import time

app = Flask(__name__)
app_path = os.path.dirname(os.path.abspath(__file__))
conllu_path = os.path.join(app_path, "conllu")

# Delete the patterns folder if it exists
patterns_dir = os.path.join(app_path, "patterns")
if os.path.exists(patterns_dir):
    for file in os.listdir(patterns_dir):
        file_path = os.path.join(patterns_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    os.rmdir(patterns_dir)

def fetch_conllu_files():
    if not os.path.exists(conllu_path):
        os.mkdir(conllu_path)

    conllu_files = glob.glob(os.path.join(conllu_path, "*.conllu"))

    # Deleting files older than 2 days
    two_days_ago = time.time() - 2 * 24 * 60 * 60
    for file_path in conllu_files:
        if os.path.getmtime(file_path) < two_days_ago:
            os.remove(file_path)

    conllu_files = glob.glob(os.path.join(conllu_path, "*.conllu"))
    return [os.path.basename(x) for x in conllu_files]

@app.route('/', methods="POST GET".split())
def home():
    conllu_files = fetch_conllu_files()
    conllu_file = ""
    error = ""
    pattern = request.form.get("pattern", "").strip().replace("without{  }", "")
    results = []
    grep_output = ""
    highlight_labels = ""

    if request.method == "POST":
        uploaded_file = request.files.get("conllu_file")
        if uploaded_file:
            if not uploaded_file.filename.endswith(".conllu"):
                error = "Please upload or select a valid .conllu file."
            else:
                file_path = os.path.join(conllu_path, uploaded_file.filename)
                uploaded_file.save(file_path)
                conllu_file = uploaded_file.filename
                conllu_files = fetch_conllu_files()
        else:
            conllu_file = request.form.get("conllu_file_selection")

        if not os.path.exists(os.path.join(conllu_path, conllu_file)):
            error = "The CoNLL-U file does not exist anymore. Please upload it again."

        if not error:
            # Save the pattern to a file with a unique name
            unique_name = f"pattern_{int(time.time())}.req"
            patterns_dir = os.path.join(app_path, "patterns")
            if not os.path.exists(patterns_dir):
                os.mkdir(patterns_dir)
            pattern_file_path = os.path.join(patterns_dir, unique_name)
            with open(pattern_file_path, "w") as pattern_file:
                pattern_file.write(pattern)

            # Run the pattern matching script
            try:
                result = subprocess.run(
                    ["grew", "grep", "-request", pattern_file_path, "-i", os.path.join(conllu_path, conllu_file)],
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding="utf-8",
                    errors="replace"
                )
                grep_output = result.stdout
            except subprocess.CalledProcessError as e:
                error = f"Error executing grew grep: {e.stderr}"
                grep_output = ""
            finally:
                os.remove(pattern_file_path)

        if grep_output and not error:
            sentences = process_conllu(os.path.join(conllu_path, conllu_file))
            grep_output = json.loads(grep_output)
            matches = []
            highlight_labels = request.form.get("highlight_labels", "").strip()
            for match in grep_output:
                if match in matches:
                    continue
                matches.append(match)
                sentence = sentences[match["sent_id"]]
                sent_id = match["sent_id"]
                node_numbers = [y for x, y in match["matching"]["nodes"].items() if x in highlight_labels.replace(" ", "").split(",") or not highlight_labels]
                node_text = " ".join([f"[{y}-{x}, {sentence['tokens'][y]}]" for x, y in sorted(match["matching"]["nodes"].items(), key=lambda item: int(item[1].split(".")[0]))])
                text = " ".join([("<b>%s</b>" % form) if token_id in node_numbers else form for token_id, form in sentence["tokens"].items()])
                result_dict = {
                    "sent_id": sent_id,
                    "sentence": sentence,
                    "encoded_conllu": urllib.parse.quote(sentence["conllu"]),
                    "node_text": node_text,
                    "text": text.replace("<", "&lt;").replace(">", "&gt;").replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
                }
                if not result_dict in results:
                    results.append(result_dict)
        
        if not error and not grep_output:
            error = "No matches found for the given pattern."

    return render_template(
        'index.html', 
        conllu_files=conllu_files,
        selected_conllu=conllu_file,
        error=error,
        pattern=pattern,
        results=results,
        highlight_labels=highlight_labels,
    )

def process_conllu(conllu_path):
    with open(conllu_path, 'r') as f:
        sentences = {x.split("# sent_id = ")[1].split("\n")[0]: {"conllu": x} for x in f.read().strip().split("\n\n")}

    for sentence in sentences:
        tokens = {x.split("\t")[0]: x.split("\t")[1] for x in sentences[sentence]["conllu"].split("\n") if "\t" in x and not '-' in x.split("\t")[0]}
        sentences[sentence]["tokens"] = tokens

    return sentences

