document.getElementById("start-scan").addEventListener("click", function () {
    const scanResult = document.getElementById("scan-result");
    
    // Prevent multiple scans
    if (window.scanning) return;
    window.scanning = true;

    // Stop previous scanner instance if it exists
    if (window.qrScanner) {
        window.qrScanner.clear();
        window.qrScanner = null;
    }

    // Initialize the scanner
    window.qrScanner = new Html5QrcodeScanner("qr-video", {
        fps: 10,
        qrbox: { width: 250, height: 250 }
    });

    window.qrScanner.render((decodedText) => {
        console.log("Scanned QR Code:", decodedText);
        scanResult.innerText = ""; 

        const idMatch = decodedText.match(/ID:\s*(\d+)/);
        const nameMatch = decodedText.match(/Name:\s*([^\d,]+)/);
        const emailMatch = decodedText.match(/Email:\s*([\w@.]+)/);

        const scannedData = {
            id: idMatch ? idMatch[1].trim() : null,
            name: nameMatch ? nameMatch[1].trim() : "Unknown",
            email: emailMatch ? emailMatch[1].trim() : "Not provided"
        };

        if (!scannedData.id) {
            scanResult.innerHTML = "<span style='color: red;'>❌ Invalid QR Code!</span>";
            window.scanning = false; // Reset flag
            return;
        }

        scanResult.innerHTML = `<span style='color: blue;'>🔍 Scanned ID: ${scannedData.id}, Checking...</span>`;

        // ✅ STOP Scanner after reading the QR code
        window.qrScanner.clear();
        window.qrScanner = null;

        // ✅ Send data to backend and check for duplicates
        fetch("/mark-attendance", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(scannedData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                scanResult.innerHTML = `<span style='color: green;'>✅ Attendance Marked for ${scannedData.name}!</span>`;
            } else if (data.message === "Already marked present!") {
                scanResult.innerHTML = `<span style='color: orange;'>⚠️ Already marked for ${scannedData.name}!</span>`;
            } else {
                scanResult.innerHTML = `<span style='color: red;'>❌ ${data.message}</span>`;
            }
            window.scanning = false; // Reset flag
        })
        .catch(error => {
            console.error("Error:", error);
            scanResult.innerHTML = `<span style='color: red;'>⚠️ Error marking attendance!</span>`;
            window.scanning = false; // Reset flag
        });
    });
});
