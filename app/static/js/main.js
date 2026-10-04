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

    const langSelector = document.getElementById("langSelector");
    if (langSelector) {
        langSelector.addEventListener("change", (e) => {
            applyLanguage(e.target.value);
        });
    }

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
});
