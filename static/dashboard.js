// ============================================================
// Dashboard Navigation
// ============================================================

function showSection(sectionId, element) {

    document.querySelectorAll(".page-section").forEach(section => {

        section.classList.add("hidden");

    });

    document.getElementById(sectionId).classList.remove("hidden");

    document.querySelectorAll(".menu li").forEach(item => {

        item.classList.remove("active");

    });

    if(element){

        element.classList.add("active");

    }

}

document.addEventListener("DOMContentLoaded", () => {

    showSection(
        "home",
        document.querySelector(".menu li")
    );

});

// ============================================================
// Manual Transaction Analysis
// ============================================================

async function predictTransaction(){

    const button = document.getElementById("predictButton");

    button.disabled = true;

    button.innerHTML = "Analyzing...";

    const payload = {

        Time: parseFloat(document.getElementById("Time").value) || 0,

        Amount: parseFloat(document.getElementById("Amount").value) || 0

    };


    try{

        const response = await fetch("/predict",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify(payload)

        });

        const data = await response.json();

        document.getElementById("predictionResult").innerHTML = `

            <h2>${data.prediction}</h2>

            <br>

            <p><strong>Fraud Probability</strong></p>

            <h1>${data.fraud_probability}%</h1>

            <br>

            <p><strong>Risk Level</strong></p>

            <h3>${data.risk_level}</h3>

            <br>

            <p>${data.recommendation}</p>

            <br>

            <small>

            Model Used : ${data.model_used}

            </small>

        `;

    }

    catch(error){

        document.getElementById("predictionResult").innerHTML=`

        <h2>Prediction Failed</h2>

        <h3>Please check the server logs.</h3>

        <p>${error}</p>

        `;

    }

    button.disabled=false;

    button.innerHTML="Analyze Transaction";

}

// ============================================================
// Batch Transaction Analysis
// ============================================================

async function uploadCSV(){

    const file=document.getElementById("csvFile").files[0];

    const button = document.getElementById("uploadButton");


    button.disabled = true;

    button.innerHTML = "⏳ Processing...";

    if(!file){

        alert("Please choose a CSV file.");

        return;

    }

    const formData=new FormData();

    formData.append("file",file);

    try{

                const response = await fetch("/predict_csv", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error);
            return;
        }

        alert(

        `Prediction Complete!

        Total Transactions : ${data.total_transactions}

        Fraud Detected : ${data.fraud_detected}

        Legitimate : ${data.legitimate}`

        );

        createSummaryCards(data);
        document.getElementById(

        "rowMessage"

        ).innerHTML=

        `Showing first ${data.displayed_rows}
        of
        ${data.total_transactions}
        transactions.

        Download the CSV to view all prediction results.`;
        createTable(data.results);

        document.getElementById("downloadButton").style.display = "block";

        button.disabled = false;

        button.innerHTML = "Analyze CSV";

    }

    catch{

        alert("CSV Upload Failed.");
        button.disabled = false;
        button.innerHTML = "Analyze CSV";

    }

}

// ============================================================
// Summary Cards
// ============================================================

function createSummaryCards(data){

    document.getElementById("summaryCards").innerHTML=`

    <div class="summary-card">

        <h3>Total Transactions</h3>

        <h1>${data.total_transactions}</h1>

    </div>

    <div class="summary-card">

        <h3>Fraud Detected</h3>

        <h1>${data.fraud_detected}</h1>

    </div>

    <div class="summary-card">

        <h3>Legitimate</h3>

        <h1>${data.legitimate}</h1>

    </div>

    `;

}

// ============================================================
// Results Table
// ============================================================

function createTable(results){

    if(results.length===0){

        return;

    }

    let html="<table>";

    html+="<thead><tr>";

    Object.keys(results[0]).forEach(key=>{

        html+=`<th>${key}</th>`;

    });

    html+="</tr></thead>";

    html+="<tbody>";

    results.forEach(row=>{

        html+="<tr>";

        Object.values(row).forEach(value=>{

            html+=`<td>${value}</td>`;

        });

        html+="</tr>";

    });

    html+="</tbody></table>";

    document.getElementById(

        "resultsTable"

    ).innerHTML=html;

}

// ============================================================
// Download Results
// ============================================================

function downloadResults(){

    window.location.href="/download";

}

async function checkBackend(){

    const response = await fetch("/health");

    const data = await response.json();

    console.log(data);

}

document.addEventListener("DOMContentLoaded",()=>{

    checkBackend();

});