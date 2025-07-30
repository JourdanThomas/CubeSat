let satLogData = [];

async function loadLogData() {
  const response = await fetch('../donnees.txt');
  const text = await response.text();
  satLogData = parseCSV(text);
}

function parseCSV(text) {
  const lines = text.trim().split('\n');
  const headers = lines[0].split(',');
  return lines.slice(1).map(line => {
    const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
    let obj = {};
    headers.forEach((header, i) => obj[header] = values[i]);
    return obj;
  });
}

function extractBattery(comment) {
  const m = comment && comment.match(/BAT\s*([0-9.]+)/);
  return m ? m[1] : 'N/A';
}

// Nouvelle fonction : retourne la dernière ligne pour le bon satellite
function getLastSatRecordFor(satNum) {
  // satNum = 1, 2, 3 ou 4
  const nom = `MTU${satNum}-11`;
  for (let i = satLogData.length - 1; i >= 0; i--) {
    if ((satLogData[i].source || '') === nom) {
      return satLogData[i];
    }
  }
  // Par défaut (s'il n'y a aucune ligne pour ce sat)
  return null;
}

window.addEventListener('DOMContentLoaded', async () => {
  await loadLogData();

  // Masquer les ondes pour les cubesats sans data dès le chargement
  document.querySelectorAll('.sat-box').forEach((box, idx) => {
    const satNum = idx + 1;
    const waveImg = document.getElementById(`wave${satNum}`);
    const record = getLastSatRecordFor(satNum);
    if (!record && waveImg) waveImg.style.display = 'none';
    else if (waveImg) waveImg.style.display = '';
  });

  document.querySelectorAll('.sat-box').forEach((box, idx) => {
    // idx = 0 pour CubeSat1, 1 pour CubeSat2, etc.
    const satNum = idx + 1;

    const btnShow = box.querySelector('.see-more-btn');
    const btnMore = box.querySelector('.more-details-btn');
    const dataSection = box.querySelector('.data-section');
    const moreDataSection = box.querySelector('.more-data-section');
    const overlay = document.getElementById('overlay');

    btnShow.addEventListener('click', () => {
      const waveImg = document.getElementById(`wave${satNum}`);
      if (btnShow.textContent === "Show details") {
        const record = getLastSatRecordFor(satNum);
        if (record) {
          dataSection.innerHTML = `
            <p><strong>Time :</strong> ${record.isotime}</p>
            <p><strong>Battery :</strong> ${extractBattery(record.comment)} V</p>
            <p><strong>Position :</strong> ${record.latitude} / ${record.longitude}</p>
            <p><strong>Status :</strong> <span style="color: #66fcf1">OK</span></p>
          `;
          if (waveImg) waveImg.style.display = '';
        } else {
          dataSection.innerHTML = `<p>No data available for this cubesat.</p>`;
          if (waveImg) waveImg.style.display = 'none';
        }
        dataSection.classList.add('visible');
        moreDataSection.classList.remove('visible');
        btnShow.textContent = "Hide details";
        btnMore.style.display = "inline-block";
        btnMore.textContent = "More details";
        box.classList.add('translated');
        box.classList.remove('expanded');
        overlay.classList.remove('visible');
      } else {
        dataSection.classList.remove('visible');
        moreDataSection.classList.remove('visible');
        btnShow.textContent = "Show details";
        btnMore.style.display = "none";
        btnMore.textContent = "More details";
        box.classList.remove('translated');
        box.classList.remove('expanded');
        overlay.classList.remove('visible');
        // On réaffiche l'onde si elle était masquée
        if (waveImg) waveImg.style.display = '';
      }
    });

    btnMore.addEventListener('click', () => {
      if (btnMore.textContent === "More details") {
        const record = getLastSatRecordFor(satNum);
        if (record) {
          moreDataSection.innerHTML = `
            <table>
              <tr><th>Callsign</th><td>${record.source}</td></tr>
              <tr><th>Latitude</th><td>${record.latitude}</td></tr>
              <tr><th>Longitude</th><td>${record.longitude}</td></tr>
              <tr><th>Altitude</th><td>${record.altitude || ''}</td></tr>
              <tr><th>Battery</th><td>${extractBattery(record.comment)} V</td></tr>
              <tr><th>Time</th><td>${record.isotime}</td></tr>
              <tr><th>Status</th><td>${record.status || 'OK'}</td></tr>
              <tr><th>Comment</th><td>${record.comment || ''}</td></tr>
            </table>
          `;
        } else {
          moreDataSection.innerHTML = `<p>No data available for this cubesat.</p>`;
        }
        moreDataSection.classList.add('visible');
        btnMore.textContent = "Hide more details";
        dataSection.classList.remove('visible');
        btnShow.style.display = "none";
        box.classList.add('expanded');
        box.classList.remove('translated');
        overlay.classList.add('visible');
        document.body.style.overflow = 'hidden';
      } else {
        moreDataSection.classList.remove('visible');
        btnMore.textContent = "More details";
        dataSection.classList.add('visible');
        box.classList.remove('expanded');
        box.classList.add('translated');
        overlay.classList.remove('visible');
        document.body.style.overflow = '';
        btnShow.style.display = "inline-block";
      }
    });
  });

  // Overlay click : simule le clic sur le bouton "Hide more details" si une sat-box est en mode expanded
  document.getElementById('overlay').addEventListener('click', () => {
    document.querySelectorAll('.sat-box.expanded').forEach(box => {
      const btnMore = box.querySelector('.more-details-btn');
      if (btnMore && btnMore.textContent === "Hide more details") {
        btnMore.click();
      }
    });
    // Si aucune sat-box n'est expanded, on ferme tout comme avant
    if (!document.querySelector('.sat-box.expanded')) {
      document.querySelectorAll('.sat-box').forEach(box => {
        box.classList.remove('expanded');
        box.classList.remove('translated');
        box.querySelector('.data-section').classList.remove('visible');
        box.querySelector('.more-data-section').classList.remove('visible');
        box.querySelector('.see-more-btn').textContent = "Show details";
        box.querySelector('.more-details-btn').textContent = "More details";
        box.querySelector('.more-details-btn').style.display = "none";
      });
      document.getElementById('overlay').classList.remove('visible');
      document.body.style.overflow = '';
    }
  });
});


