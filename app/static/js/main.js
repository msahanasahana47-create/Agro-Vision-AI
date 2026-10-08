/**
 * Agro-Vision AI: Client-side JavaScript
 * - Dynamic i18n switching
 * - Client-side image compression (~1024px) for mobile uploads
 */

const i18nCache = {};

async function loadTranslations(lang) {
    if (i18nCache[lang]) return i18nCache[lang];
    try {
        const resp = await fetch(`/static/i18n/${lang}.json`);
        if (!resp.ok) throw new Error(`HTTP error ${resp.status}`);
        const data = await resp.json();
        i18nCache[lang] = data;
        return data;
    } catch (err) {
        console.warn(`Could not load translations for ${lang}`, err);
        return {};
    }
}

async function applyLanguage(lang) {
    const dict = await loadTranslations(lang);
    document.querySelectorAll("[data-i18n]").forEach(elem => {
        const key = elem.getAttribute("data-i18n");
        if (dict[key]) {
            if (elem.tagName === "INPUT" && elem.getAttribute("placeholder")) {
                elem.setAttribute("placeholder", dict[key]);
            } else {
                elem.textContent = dict[key];
            }
        }
    });
    localStorage.setItem("agrovision_lang", lang);
    const sel = document.getElementById("langSelector");
    if (sel && sel.value !== lang) {
        sel.value = lang;
    }
}

/**
 * Compresses an image file client-side to maximum width/height of 1024px.
 * Optimizes mobile network bandwidth and server upload time.
 */
function compressImage(file, maxDimension = 1024, quality = 0.85) {
    return new Promise((resolve, reject) => {
        if (!file.type.match(/image.*/)) {
            return reject(new Error("File is not an image"));
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                let width = img.width;
                let height = img.height;

                if (width > maxDimension || height > maxDimension) {
                    if (width > height) {
                        height = Math.round((height * maxDimension) / width);
                        width = maxDimension;
                    } else {
                        width = Math.round((width * maxDimension) / height);
                        height = maxDimension;
                    }
                }

                const canvas = document.createElement("canvas");
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0, width, height);

                canvas.toBlob(
                    (blob) => {
                        if (!blob) {
                            return reject(new Error("Canvas toBlob failed"));
                        }
                        const compressedFile = new File([blob], file.name, {
                            type: "image/jpeg",
                            lastModified: Date.now(),
                        });
                        resolve(compressedFile);
                    },
                    "image/jpeg",
                    quality
                );
            };
            img.onerror = reject;
            img.src = e.target.result;
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    // Initialize language from localStorage or default
    const savedLang = localStorage.getItem("agrovision_lang") || "en";
    applyLanguage(savedLang);



    // Toggle disease risk note input on advisor page
    const diseaseCheck = document.getElementById("diseaseCheck");
    const diseaseInputGroup = document.getElementById("diseaseInputGroup");
    if (diseaseCheck && diseaseInputGroup) {
        diseaseCheck.addEventListener("change", () => {
            if (diseaseCheck.checked) {
                diseaseInputGroup.classList.remove("d-none");
            } else {
                diseaseInputGroup.classList.add("d-none");
            }
        });
    }

    // ── Disease Detection ─────────────────────────────────────────────────────

    const scanBtn = document.getElementById("scanBtn");
    const leafImageInput = document.getElementById("leafImageInput");
    const diseaseResultArea = document.getElementById("diseaseResultArea");

    if (scanBtn && leafImageInput && diseaseResultArea) {
        // Show preview when user picks a file
        leafImageInput.addEventListener("change", () => {
            const file = leafImageInput.files[0];
            if (!file) return;
            const previewUrl = URL.createObjectURL(file);
            diseaseResultArea.innerHTML = `
                <div class="text-center mt-3">
                    <img src="${previewUrl}" alt="Leaf preview"
                         class="img-fluid rounded-3 shadow-sm"
                         style="max-height:220px; object-fit:cover;">
                    <p class="text-muted small mt-2">Image ready. Click <strong>Analyze Leaf</strong> to scan.</p>
                </div>`;
        });

        const origLabel = scanBtn.innerHTML;

        scanBtn.addEventListener("click", async () => {
            const file = leafImageInput.files[0];
            if (!file) {
                diseaseResultArea.innerHTML = `<div class="alert alert-warning mt-3">⚠️ Please select or capture a leaf image first.</div>`;
                return;
            }

            // Compress before upload
            scanBtn.disabled = true;
            scanBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Compressing…`;
            let compressed;
            try {
                compressed = await compressImage(file);
            } catch (err) {
                compressed = file; // fallback to original if compression fails
            }

            scanBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Analyzing…`;
            diseaseResultArea.innerHTML = "";

            try {
                const formData = new FormData();
                formData.append("image", compressed, compressed.name);

                const resp = await fetch("/api/disease", {
                    method: "POST",
                    body: formData,
                });
                const data = await resp.json();
                if (!resp.ok) throw new Error(data.error || resp.statusText);

                // Determine single verdict: Healthy or Diseased
                const healthyPct = Math.round(data.healthy_percentage || 0);
                const diseasePct  = Math.round(data.disease_percentage  || 0);

                // Pick the dominant verdict
                let verdict, verdictIcon, verdictColor, verdictBg, verdictPct;
                if (diseasePct > healthyPct) {
                    verdict     = "Diseased Leaf";
                    verdictIcon = "⚠️";
                    verdictColor = "danger";
                    verdictBg   = "#fff5f5";
                    verdictPct  = diseasePct;
                } else if (healthyPct > 0 || diseasePct > 0) {
                    verdict     = "Healthy Leaf";
                    verdictIcon = "✅";
                    verdictColor = "success";
                    verdictBg   = "#f0fff4";
                    verdictPct  = healthyPct;
                } else {
                    verdict     = "No Leaf Detected";
                    verdictIcon = "❓";
                    verdictColor = "secondary";
                    verdictBg   = "#f8f9fa";
                    verdictPct  = 0;
                }

                const isUncertain = data.uncertain;
                const isStub      = data.is_stub;
                const treatment   = data.treatment || {};

                const uncertainBanner = isUncertain
                    ? `<div class="alert alert-warning small mt-3">⚠️ <strong>Low confidence</strong> — ${data.uncertain_message || "Please retake the photo in better lighting."}</div>`
                    : "";

                const stubNote = isStub
                    ? `<div class="alert alert-info small mt-3">ℹ️ <strong>Stub mode:</strong> No trained model loaded.</div>`
                    : "";

                const heatmapHtml = data.heatmap_url
                    ? `<div class="mt-3"><p class="fw-semibold small mb-1">🔥 Grad-CAM Heatmap</p><img src="${data.heatmap_url}" class="img-fluid rounded-3 shadow-sm" alt="Grad-CAM"></div>`
                    : "";

                const treatmentHtml = treatment.disease_name ? `
                <div class="mt-3 border-top pt-3">
                    <h6 class="fw-bold text-success">💊 Advisory Treatment</h6>
                    <p class="small mb-1"><strong>Disease:</strong> ${treatment.disease_name}</p>
                    ${treatment.symptoms ? `<p class="small mb-1"><strong>Symptoms:</strong> ${treatment.symptoms}</p>` : ""}
                    ${treatment.organic_control ? `<p class="small mb-1"><strong>Organic Control:</strong> ${treatment.organic_control}</p>` : ""}
                    ${treatment.chemical_control ? `<p class="small mb-1"><strong>Chemical Control:</strong> ${treatment.chemical_control}</p>` : ""}
                    ${treatment.prevention ? `<p class="small mb-1"><strong>Prevention:</strong> ${treatment.prevention}</p>` : ""}
                    <p class="text-muted small fst-italic mt-2 mb-0">⚠️ ${data.disclaimer || treatment.disclaimer || ""}</p>
                </div>` : "";

                diseaseResultArea.innerHTML = `
                <div class="card border-0 shadow-sm rounded-4 p-4 mt-3" style="background:${verdictBg};">
                    <h5 class="fw-bold text-success mb-3">🔬 Leaf Scan Result</h5>
                    <div class="text-center py-3">
                        <div style="font-size:3.5rem; line-height:1;">${verdictIcon}</div>
                        <div class="fw-bold mt-2" style="font-size:1.6rem; color: var(--bs-${verdictColor});">
                            ${verdict}
                        </div>
                        <div class="text-muted small mt-1">Confidence: <strong>${verdictPct}%</strong></div>
                    </div>
                    ${uncertainBanner}
                    ${stubNote}
                    ${heatmapHtml}
                    ${treatmentHtml}
                </div>`;
            } catch (err) {
                diseaseResultArea.innerHTML = `<div class="alert alert-danger rounded-3 mt-3"><strong>Error:</strong> ${err.message}</div>`;
            } finally {
                scanBtn.disabled = false;
                scanBtn.innerHTML = origLabel;
            }
        });
    }

    // ── Shared helpers ────────────────────────────────────────────────────────

    function formToJson(form) {
        const obj = {};
        new FormData(form).forEach((v, k) => { obj[k] = v; });
        return JSON.stringify(obj);
    }

    function setLoading(btn, area, msg = "Processing…") {
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${msg}`;
        area.innerHTML = "";
    }

    function resetBtn(btn, label) {
        btn.disabled = false;
        btn.innerHTML = label;
    }

    function errorCard(msg) {
        return `<div class="alert alert-danger rounded-3 mt-3"><strong>Error:</strong> ${msg}</div>`;
    }

    async function postJson(url, body) {
        const r = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body,
        });
        const data = await r.json();
        if (!r.ok) throw new Error(data.error || r.statusText);
        return data;
    }

    // ── Yield Prediction ──────────────────────────────────────────────────────

    const yieldForm = document.getElementById("yieldForm");
    const yieldResultArea = document.getElementById("yieldResultArea");
    if (yieldForm && yieldResultArea) {
        const btn = yieldForm.querySelector("button[type=submit]");
        const origLabel = btn.innerHTML;
        yieldForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            setLoading(btn, yieldResultArea, "Calculating…");
            try {
                const d = await postJson("/api/yield", formToJson(yieldForm));
                const bars = (d.top_features || []).map(f => {
                    const pct = Math.round(f.importance * 100);
                    return `<div class="mb-2">
                        <div class="d-flex justify-content-between small mb-1">
                            <span>${f.feature}</span><span class="fw-bold">${pct}%</span>
                        </div>
                        <div class="progress" style="height:8px">
                            <div class="progress-bar bg-success" style="width:${pct}%"></div>
                        </div>
                    </div>`;
                }).join("");
                yieldResultArea.innerHTML = `
                <div class="card border-0 shadow-sm rounded-4 p-4 mt-3">
                    <h5 class="fw-bold text-success mb-3">📊 Yield Prediction Result</h5>
                    <div class="row g-3 mb-3">
                        <div class="col-6">
                            <div class="card text-center bg-success text-white rounded-3 p-3">
                                <div class="display-6 fw-bold">${d.predicted_yield}</div>
                                <div class="small">Total Yield (metric tons)</div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="card text-center bg-primary text-white rounded-3 p-3">
                                <div class="display-6 fw-bold">${d.yield_per_hectare}</div>
                                <div class="small">Yield per Hectare (t/ha)</div>
                            </div>
                        </div>
                    </div>
                    <h6 class="fw-bold mt-3 mb-2">Top Feature Importances</h6>
                    ${bars}
                    ${d.is_stub ? '<p class="text-muted small mt-3 mb-0">⚠️ Using stub model — train the ML pipeline for real predictions.</p>' : ""}
                </div>`;
            } catch (err) {
                yieldResultArea.innerHTML = errorCard(err.message);
            } finally {
                resetBtn(btn, origLabel);
            }
        });
    }

    // ── Crop Recommendation ───────────────────────────────────────────────────

    const recForm = document.getElementById("recommendForm");
    const recResultArea = document.getElementById("recResultArea");
    if (recForm && recResultArea) {
        const btn = recForm.querySelector("button[type=submit]");
        const origLabel = btn.innerHTML;
        const colors = ["success", "primary", "warning"];
        const medals = ["🥇", "🥈", "🥉"];
        recForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            setLoading(btn, recResultArea, "Analysing…");
            try {
                const d = await postJson("/api/recommend", formToJson(recForm));
                const cards = (d.top_crops || []).map((c, i) => {
                    const pct = Math.round(c.probability * 100);
                    return `<div class="col-md-4">
                        <div class="card border-0 shadow-sm rounded-4 p-3 text-center h-100">
                            <div class="fs-2">${medals[i] || "🌾"}</div>
                            <h5 class="fw-bold text-${colors[i]} mt-2">${c.crop}</h5>
                            <div class="progress mt-2 mb-1" style="height:10px">
                                <div class="progress-bar bg-${colors[i]}" style="width:${pct}%"></div>
                            </div>
                            <div class="small text-muted">${pct}% suitability</div>
                        </div>
                    </div>`;
                }).join("");
                recResultArea.innerHTML = `
                <div class="card border-0 shadow-sm rounded-4 p-4 mt-3">
                    <h5 class="fw-bold text-success mb-3">🌾 Top Crop Recommendations</h5>
                    <div class="row g-3">${cards}</div>
                    ${d.is_stub ? '<p class="text-muted small mt-3 mb-0">⚠️ Using stub model — train the ML pipeline for real predictions.</p>' : ""}
                </div>`;
            } catch (err) {
                recResultArea.innerHTML = errorCard(err.message);
            } finally {
                resetBtn(btn, origLabel);
            }
        });
    }

    // ── Mandi Price Forecast ──────────────────────────────────────────────────

    const fetchPriceBtn = document.getElementById("fetchPriceBtn");
    const priceCropSelect = document.getElementById("priceCropSelect");
    const priceChartContainer = document.getElementById("priceChartContainer");
    const priceMetricsNote = document.getElementById("priceMetricsNote");
    let priceChartInstance = null;

    if (fetchPriceBtn && priceCropSelect && priceChartContainer) {
        const origLabel = fetchPriceBtn.innerHTML;
        fetchPriceBtn.addEventListener("click", async () => {
            const crop = priceCropSelect.value;
            fetchPriceBtn.disabled = true;
            fetchPriceBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Loading…`;
            priceChartContainer.classList.add("d-none");
            try {
                const d = await postJson("/api/price", JSON.stringify({ crop }));
                const labels = [
                    ...(d.historical || []).map(h => h.date),
                    ...(d.forecast || []).map(f => f.date),
                ];
                const histPrices = (d.historical || []).map(h => h.price);
                const forecastPrices = (d.forecast || []).map(f => f.predicted_price);
                const baselinePrices = (d.forecast || []).map(f => f.naive_baseline);

                const histData = [...histPrices, ...Array(forecastPrices.length).fill(null)];
                const foreData = [...Array(histPrices.length).fill(null), ...forecastPrices];
                const baseData = [...Array(histPrices.length).fill(null), ...baselinePrices];

                const ctx = document.getElementById("priceChart").getContext("2d");
                if (priceChartInstance) priceChartInstance.destroy();
                priceChartInstance = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels,
                        datasets: [
                            { label: "Historical", data: histData, borderColor: "#198754", backgroundColor: "rgba(25,135,84,0.08)", tension: 0.3, pointRadius: 2 },
                            { label: "LSTM Forecast", data: foreData, borderColor: "#0d6efd", backgroundColor: "rgba(13,110,253,0.10)", borderDash: [5,3], tension: 0.3, pointRadius: 4 },
                            { label: "Naive Baseline", data: baseData, borderColor: "#ffc107", borderDash: [3,3], tension: 0, pointRadius: 2 },
                        ],
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: "top" },
                            title: { display: true, text: `${d.crop} Price Forecast — ${d.unit}` },
                        },
                        scales: { y: { ticks: { callback: v => "₹" + v } } },
                    },
                });
                const bc = d.baseline_comparison || {};
                priceMetricsNote.innerHTML = `Model: <strong>${bc.model_type || "LSTM"}</strong> | MAE: <strong>${bc.model_mae}</strong> | Naive MAE: ${bc.naive_mae} | Beats baseline: <strong class="text-${bc.beats_baseline ? "success" : "danger"}">${bc.beats_baseline ? "✅ Yes" : "❌ No"}</strong>`;
                priceChartContainer.classList.remove("d-none");
            } catch (err) {
                priceMetricsNote.innerHTML = `<span class="text-danger">Error: ${err.message}</span>`;
                priceChartContainer.classList.remove("d-none");
            } finally {
                resetBtn(fetchPriceBtn, origLabel);
            }
        });
    }

    // ── Cross-Module Advisor ──────────────────────────────────────────────────

    const advisorForm = document.getElementById("advisorForm");
    const advisorResultArea = document.getElementById("advisorResultArea");
    if (advisorForm && advisorResultArea) {
        const btn = advisorForm.querySelector("button[type=submit]");
        const origLabel = btn.innerHTML;
        advisorForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            setLoading(btn, advisorResultArea, "Generating report…");
            try {
                const d = await postJson("/api/advisor", formToJson(advisorForm));
                const rows = (d.candidates || []).map((c, i) => {
                    const medals = ["🥇", "🥈", "🥉"];
                    const pct = Math.round((c.suitability_probability || 0) * 100);
                    return `<tr>
                        <td>${medals[i] || ""} <strong>${c.crop}</strong></td>
                        <td>${pct}%</td>
                        <td>${c.base_yield_tons} t</td>
                        <td>${c.adjusted_yield_tons} t</td>
                        <td>₹${(c.projected_price_per_ton_inr || 0).toLocaleString()}/t</td>
                        <td class="text-success fw-bold">₹${(c.projected_revenue_inr || 0).toLocaleString()}</td>
                    </tr>`;
                }).join("");
                const soilS = d.soil_climate_summary || {};
                const diseaseNote = d.disease_risk_note
                    ? `<div class="alert alert-warning mt-3 small"><strong>⚠️ Disease Risk:</strong> ${d.disease_risk_note}</div>`
                    : "";
                advisorResultArea.innerHTML = `
                <div class="card border-0 shadow-sm rounded-4 p-4 mt-3">
                    <h5 class="fw-bold text-success mb-1">🌾 Farm Intelligence Report</h5>
                    <p class="text-muted small mb-3">Area: <strong>${d.area_hectares} ha</strong> | N:${soilS.N} P:${soilS.P} K:${soilS.K} | Temp:${soilS.temperature}°C | Humidity:${soilS.humidity}% | pH:${soilS.ph} | Rainfall:${soilS.rainfall}mm</p>
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Crop</th>
                                    <th>Suitability</th>
                                    <th>Base Yield</th>
                                    <th>Adj. Yield</th>
                                    <th>Price/ton</th>
                                    <th>Est. Revenue</th>
                                </tr>
                            </thead>
                            <tbody>${rows}</tbody>
                        </table>
                    </div>
                    ${diseaseNote}
                    <p class="text-muted small mt-3 mb-0">⚠️ Advisory only — consult a local agricultural officer for formal field verification.</p>
                    ${d.is_stub ? '<p class="text-muted small mb-0">ℹ️ Using stub model — train the ML pipeline for real predictions.</p>' : ""}
                </div>`;
            } catch (err) {
                advisorResultArea.innerHTML = errorCard(err.message);
            } finally {
                resetBtn(btn, origLabel);
            }
        });
    }
});
