import io
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from backend.model import predict
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyAiOoXEXngVmPDLhPp6LtK0gFhdkGlFrJ0")
chat_model = genai.GenerativeModel('gemini-2.5-flash')

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session
app.template_folder = 'frontend/templates'
app.static_folder = 'frontend/static'

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_heart():
    data = request.json

    input_data = [
        float(data['age']), float(data['sex']), float(data['cp']),
        float(data['trestbps']), float(data['chol']), float(data['fbs']),
        float(data['restecg']), float(data['thalach']), float(data['exang']),
        float(data['oldpeak']), float(data['slope']), float(data['ca']),
        float(data['thal'])
    ]

    result, acc, prob, importances = predict(input_data)

    prediction_data = {
        "prediction": int(result),
        "accuracy": round(acc * 100, 2),
        "probability": round(prob, 4),
        "feature_importances": importances,
        "input_data": data
    }

    session['prediction_data'] = prediction_data
    
    # Store in history
    if 'history' not in session:
        session['history'] = []
    
    # Add timestamp to the data
    from datetime import datetime
    history_item = prediction_data.copy()
    history_item['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Keep only last 10 reports to avoid session size limits
    session['history'] = ([history_item] + session['history'])[:10]
    session.modified = True

    return jsonify({"redirect": "/result"})

@app.route('/reports')
def reports_page():
    history = session.get('history', [])
    return render_template('reports.html', history=history)

@app.route('/result')
def result_page():
    prediction_data = session.get('prediction_data')
    if not prediction_data:
        return redirect(url_for('home'))
    return render_template('result.html', **prediction_data)
@app.route('/download', methods=['POST'])
def download_report():
    try:
        data = request.json
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()

        content = []
        content.append(Paragraph("Heart Disease Prediction Report", styles['Title']))
        content.append(Spacer(1, 0.2 * inch))
        
        # Ensure all values are strings and handle potential missing keys
        prediction = str(data.get('prediction', 'N/A'))
        accuracy = str(data.get('accuracy', 'N/A'))
        score = str(data.get('score', 'N/A'))
        suggestion = str(data.get('suggestion', 'N/A'))

        content.append(Paragraph(f"<b>Prediction:</b> {prediction}", styles['Normal']))
        content.append(Spacer(1, 0.1 * inch))
        content.append(Paragraph(f"<b>Accuracy:</b> {accuracy}", styles['Normal']))
        content.append(Spacer(1, 0.1 * inch))
        content.append(Paragraph(f"<b>Risk Score:</b> {score}", styles['Normal']))
        content.append(Spacer(1, 0.1 * inch))
        content.append(Paragraph(f"<b>Suggestion:</b> {suggestion}", styles['Normal']))

        doc.build(content)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="Heart_Report.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"response": "I didn't catch that. Can you repeat?"})
        
    try:
        # Context to ensure Gemini behaves like a Heart Disease assistant
        prompt = f"You are a helpful AI assistant for a Heart Disease Prediction System. Keep your answers concise, informative, and friendly. Answer the following question: {user_message}"
        response = chat_model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"response": "Sorry, I'm having trouble connecting to my brain right now.", "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)