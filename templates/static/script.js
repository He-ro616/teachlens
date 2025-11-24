// frontend/script.js
(function() {
  const form = document.getElementById("uploadForm");
  const videoInput = document.getElementById("videoInput");
  const statusText = document.getElementById("statusText");
  const progressBar = document.getElementById("progressBar");
  const progressPct = document.getElementById("progressPct");
  const resultsCard = document.getElementById("resultCard");
  const resultsDiv = document.getElementById("results");
  const resetBtn = document.getElementById("resetBtn");
  const pastReportsDiv = document.getElementById("pastReports");
  const noReportsText = document.getElementById("noReports");

  async function fetchReports() {
    pastReportsDiv.innerHTML = ''; // Clear previous reports
    if (noReportsText) {
      noReportsText.classList.add("hidden");
    }
    try {
      const response = await fetch("/reports");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const reports = await response.json();
      if (reports.length === 0) {
        if (noReportsText) {
          noReportsText.classList.remove("hidden");
        }
      } else {
        reports.forEach(report => {
          const reportElement = document.createElement("div");
          reportElement.className = "flex justify-between items-center bg-white p-3 rounded-md shadow-sm";
          reportElement.innerHTML = `
            <span class="text-gray-700">${report.filename} (${new Date(report.timestamp).toLocaleDateString()})</span>
            <a href="/report/${report.id}" target="_blank" class="px-3 py-1 bg-blue-500 text-white text-sm rounded-md hover:bg-blue-600">Download PDF</a>
          `;
          pastReportsDiv.appendChild(reportElement);
        });
      }
    } catch (error) {
      console.error("Error fetching reports:", error);
      pastReportsDiv.innerHTML = `<p class="text-red-500">Error loading reports.</p>`;
    }
  }


  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!videoInput.files.length) {
        statusText.textContent = "Please select a video file.";
        return;
      }

      const file = videoInput.files[0];
      const fd = new FormData();
      fd.append("video", file);

      statusText.textContent = "Uploading & processing...";
      progressBar.style.width = "0%";
      progressPct.textContent = "0%";
      resultsCard.classList.add("hidden");

      try {
        await new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open("POST", "/upload");
          xhr.upload.onprogress = (evt) => {
            if (evt.lengthComputable) {
              const p = Math.round((evt.loaded / evt.total) * 100);
              progressBar.style.width = p + "%";
              progressPct.textContent = p + "%";
            }
          };
          xhr.onload = () => {
            if (xhr.status === 200) {
              const responseJson = JSON.parse(xhr.responseText);
              statusText.textContent = responseJson.message;
              progressBar.style.width = "100%";
              progressPct.textContent = "100%";
              resultsDiv.innerHTML = `<a href="/report/${responseJson.report_id}" target="_blank" class="text-blue-500 hover:underline">Download Latest Report (PDF)</a>`;
              resultsCard.classList.remove("hidden");
              fetchReports(); // Refresh the list of reports
              resolve();
            } else {
              xhr.text().then(t => {
                try {
                  const json = JSON.parse(t);
                  statusText.textContent = `Error: ${json.error || t}`;
                } catch {
                  statusText.textContent = `Server error: ${xhr.status}`;
                }
              });
              reject();
            }
          };
          xhr.onerror = () => { statusText.textContent = "Network error"; reject(); };
          xhr.send(fd);
        });

      } catch (err) {
        console.error(err);
      }
    });
  }


  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      videoInput.value = "";
      statusText.textContent = "";
      progressBar.style.width = "0%";
      progressPct.textContent = "0%";
      resultsCard.classList.add("hidden");
      fetchReports(); // Refresh reports on reset
    });
  }

  // Initial fetch of reports when the page loads, only if pastReportsDiv exists
  if (pastReportsDiv) {
    document.addEventListener("DOMContentLoaded", fetchReports);
  }
})();