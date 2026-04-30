/* ════════════════════════════════
   disease.js — Disease Detection
   ════════════════════════════════ */

let selectedFile = null;

function handleImageFile(file) {
    if (!file.type.match('image.*')) {
        showToast('Please select an image file. / படக் கோப்பை தேர்ந்தெடுக்கவும்.', 'error');
        return;
    }
    if (file.size > 5 * 1024 * 1024) {
        showToast('Image too large (max 5MB). / கோப்பு மிகவும் பெரியது.', 'error');
        return;
    }
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('uploadContent').classList.add('hidden');
        const preview = document.getElementById('uploadPreview');
        preview.classList.remove('hidden');
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('detectBtn').disabled = false;
        showToast('Image ready for analysis. / படம் பகுப்பாய்வுக்கு தயார்.', 'info');
    };
    reader.readAsDataURL(file);
}

function clearUpload() {
    selectedFile = null;
    document.getElementById('uploadContent').classList.remove('hidden');
    document.getElementById('uploadPreview').classList.add('hidden');
    document.getElementById('previewImg').src = '';
    document.getElementById('detectBtn').disabled = true;
    document.getElementById('diseaseResults').classList.add('hidden');
    document.getElementById('diseaseImageInput').value = '';
}

function openCamera() {
    const input = document.getElementById('diseaseImageInput');
    input.setAttribute('capture', 'environment');
    input.click();
}

async function runDiseaseDetection() {
    if (!selectedFile) return;
    const btn = document.getElementById('detectBtn');
    setLoading(btn, true);

    try {
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('language', currentLang);

        const resp = await fetch('/api/disease/detect', {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();

        if (data.success) {
            renderDiseaseResult(data.result);
            showToast('Disease analysis complete! / நோய் பகுப்பாய்வு முடிந்தது!', 'success');
        } else {
            showToast(data.error || 'Detection failed.', 'error');
        }
    } catch (err) {
        showToast('Analysis failed. Please try again.', 'error');
    } finally {
        setLoading(btn, false);
    }
}

function renderDiseaseResult(result) {
    const container = document.getElementById('diseaseResults');
    container.classList.remove('hidden');

    const sev = result.severity;
    const sevLabel = sev === 'high' ? '🔴 High Severity' : sev === 'medium' ? '🟡 Medium Severity' : '🟢 Healthy';

    container.innerHTML = `
        <div class="disease-result severity-${sev}">
            <div class="disease-image-panel">
                <img src="${result.image_url || ''}" alt="Analyzed leaf" onerror="this.style.display='none'">
                <div style="margin-top:12px;">
                    <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;">AI Confidence</div>
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div class="confidence-bar" style="flex:1;height:6px;">
                            <div class="confidence-fill" data-width="${result.confidence}" style="width:${result.confidence}%"></div>
                        </div>
                        <span style="font-weight:700;color:var(--amber-400)">${result.confidence}%</span>
                    </div>
                </div>
                ${result.is_demo ? `<div style="margin-top:10px;font-size:0.72rem;color:var(--text-muted)">
                    ⚡ AI Simulation Mode
                </div>` : ''}
            </div>
            <div class="disease-info-panel">
                <div class="disease-name-en">${result.disease_name_en}</div>
                <div class="disease-name-ta">${result.disease_name_ta}</div>
                <div class="severity-badge severity-${sev}">${sevLabel}</div>
                <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:4px;">Cause: ${result.cause}</div>
                <div style="font-size:0.82rem;color:var(--text-secondary);margin-bottom:14px;font-family:var(--font-tamil)">
                    ${currentLang === 'ta' ? result.symptoms : result.symptoms}
                </div>
                <div class="treatment-sections">
                    <div class="treatment-section" style="background:rgba(59,130,246,0.1); border-left:3px solid var(--blue-500); margin-bottom:10px;">
                        <div class="treatment-label" style="color:var(--blue-400);">🛡️ Crop Protection Guidance</div>
                        <div class="treatment-text">${result.crop_protection || 'Standard protection recommended.'}</div>
                    </div>
                    <div class="treatment-section chemical">
                        <div class="treatment-label">💊 Pesticide / Chemical Solution</div>
                        <div class="treatment-text">${result.treatment.chemical}</div>
                    </div>
                    <div class="treatment-section organic">
                        <div class="treatment-label">🌿 Organic Solution</div>
                        <div class="treatment-text">${result.treatment.organic}</div>
                    </div>
                    <div class="treatment-section preventive">
                        <div class="treatment-label">🚜 Prevention Tips</div>
                        <div class="treatment-text">${result.treatment.preventive}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}
