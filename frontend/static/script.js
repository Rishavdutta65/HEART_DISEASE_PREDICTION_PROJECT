let barChart, radarChart, pieChart;

function calculateHealthScore(bp, chol, hr, age) {
    let score = 100;
    if (bp > 120) score -= 20;
    if (chol > 200) score -= 20;
    if (hr < 60 || hr > 100) score -= 20;
    if (age > 50) score -= 10;
    return Math.max(score, 0);
}

function getSuggestion(bp, chol, hr) {
    if (bp > 140) return "Reduce salt intake.";
    if (chol > 240) return "Avoid oily food.";
    if (hr < 60) return "Consult doctor.";
    if (hr > 100) return "Do relaxation.";
    return "Your health looks good!";
}

async function predict() {

    const age = parseFloat(document.getElementById("age").value);
    const bp = parseFloat(document.getElementById("trestbps").value);
    const chol = parseFloat(document.getElementById("chol").value);
    const hr = parseFloat(document.getElementById("thalach").value);

    if (isNaN(age) || isNaN(bp) || isNaN(chol) || isNaN(hr)) {
        alert("Enter valid numbers!");
        return;
    }

    document.getElementById("bpStatus").innerText =
        (bp >= 80 && bp <= 120) ? "BP Normal ✅" : "BP Abnormal ❌";

    document.getElementById("cholStatus").innerText =
        (chol < 200) ? "Cholesterol Normal ✅" : "Cholesterol High ❌";

    document.getElementById("hrStatus").innerText =
        (hr >= 60 && hr <= 100) ? "Heart Rate Normal ✅" : "Heart Rate Abnormal ❌";

    const score = calculateHealthScore(bp, chol, hr, age);
    const suggestion = getSuggestion(bp, chol, hr);

    const res = await fetch("/predict", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            age, sex:1, cp:1, trestbps:bp, chol,
            fbs:0, restecg:1, thalach:hr,
            exang:0, oldpeak:1, slope:2, ca:0, thal:2
        })
    });

    const result = await res.json();

    document.getElementById("result").innerText =
        result.prediction ? "⚠️ Disease Detected" : "✅ Healthy";

    document.getElementById("accuracy").innerText =
        "Accuracy: " + result.accuracy + "%";

    document.getElementById("suggestion").innerText =
        suggestion;

    if (barChart) barChart.destroy();
    if (radarChart) radarChart.destroy();
    if (pieChart) pieChart.destroy();

    barChart = new Chart(document.getElementById("barChart"), {
        type: 'bar',
        data: {
            labels: ["BP","Cholesterol","Heart Rate"],
            datasets: [{
                label: "Health Metrics",
                data: [bp, chol, hr]
            }]
        }
    });

    radarChart = new Chart(document.getElementById("radarChart"), {
        type: 'radar',
        data: {
            labels: ["Age","BP","Cholesterol","Heart Rate"],
            datasets: [{
                label: "Health Overview",
                data: [age, bp, chol, hr]
            }]
        }
    });

    pieChart = new Chart(document.getElementById("pieChart"), {
        type: 'pie',
        data: {
            labels: ["Healthy","Risk"],
            datasets: [{
                label: "Risk Level",
                data: [score, 100-score]
            }]
        }
    });

    window.reportData = {
        prediction: document.getElementById("result").innerText,
        accuracy: result.accuracy,
        score: score,
        suggestion: suggestion
    };
}

async function downloadReport() {
    const res = await fetch("/download", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(window.reportData)
    });

    const blob = await res.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "report.pdf";
    link.click();
}