/**
 * AI Sentinel - Frontend Logic
 * Authored by Arvind (https://github.com/Arvind208)
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const inputText = document.getElementById("input-text");
    const wordCount = document.getElementById("word-count");
    const charCount = document.getElementById("char-count");
    const btnAnalyze = document.getElementById("btn-analyze");
    const spinner = document.getElementById("spinner");
    const btnText = btnAnalyze.querySelector(".btn-text");
    const btnIcon = btnAnalyze.querySelector(".btn-icon");

    const btnSampleAi = document.getElementById("btn-sample-ai");
    const btnSampleHuman = document.getElementById("btn-sample-human");
    const btnSampleMixed = document.getElementById("btn-sample-mixed");
    const btnPaste = document.getElementById("btn-paste");
    const btnClear = document.getElementById("btn-clear");

    const emptyState = document.getElementById("empty-state");
    const resultsContent = document.getElementById("results-content");
    const heatmapPanel = document.getElementById("heatmap-panel");
    const heatmapContent = document.getElementById("heatmap-content");

    const scoreVal = document.getElementById("score-val");
    const radialProgress = document.getElementById("radial-progress");
    const verdictBadge = document.getElementById("verdict-badge");
    const verdictHeading = document.getElementById("verdict-heading");
    const verdictSummary = document.getElementById("verdict-summary");

    const valBurstiness = document.getElementById("val-burstiness");
    const subBurstiness = document.getElementById("sub-burstiness");
    const valPerplexity = document.getElementById("val-perplexity");
    const subPerplexity = document.getElementById("sub-perplexity");
    const valTtr = document.getElementById("val-ttr");
    const valReading = document.getElementById("val-reading");

    const markersBox = document.getElementById("markers-box");
    const markersCount = document.getElementById("markers-count");
    const markersTags = document.getElementById("markers-tags");

    const btnCopyReport = document.getElementById("btn-copy-report");
    const btnDownloadJson = document.getElementById("btn-download-json");
    const toast = document.getElementById("toast");

    const sentenceInspector = document.getElementById("sentence-inspector");
    const inspBadge = document.getElementById("insp-badge");
    const inspScore = document.getElementById("insp-score");
    const inspText = document.getElementById("insp-text");
    const inspReason = document.getElementById("insp-reason");

    let currentAnalysis = null;
    let samplesCache = null;

    // Circumference of radial progress circle (r = 50 -> 2 * PI * 50 = 314.159)
    const CIRCUMFERENCE = 2 * Math.PI * 50;

    // Update character & word counters
    function updateCounts() {
        const text = inputText.value.trim();
        const chars = inputText.value.length;
        const words = text ? text.split(/\s+/).length : 0;
        charCount.textContent = `${chars} characters`;
        wordCount.textContent = `${words} words`;
    }

    inputText.addEventListener("input", updateCounts);

    // Fetch Samples from API
    async function loadSamples() {
        try {
            const res = await fetch("/api/samples");
            if (res.ok) {
                samplesCache = await res.json();
            }
        } catch (err) {
            console.warn("Could not preload samples from API:", err);
        }
    }
    loadSamples();

    // Sample buttons
    btnSampleAi.addEventListener("click", () => {
        if (samplesCache && samplesCache.ai) {
            inputText.value = samplesCache.ai;
        } else {
            inputText.value = "In the rapidly evolving realm of artificial intelligence, machine learning stands as a testament to human ingenuity. Furthermore, as organizations embark on digital transformation journeys, it is crucial to remember that seamless integration plays a pivotal role. The intricate tapestry of neural networks fosters continuous innovation across multifaceted industries. In conclusion, embracing these advancements will unlock unprecedented potential for future generations.";
        }
        updateCounts();
        triggerAnalysis();
    });

    btnSampleHuman.addEventListener("click", () => {
        if (samplesCache && samplesCache.human) {
            inputText.value = samplesCache.human;
        } else {
            inputText.value = "I was sitting at the coffee shop yesterday morning, staring at my cold brew, wondering why my code kept crashing. Turns out, it was just a missing comma on line 42! Classic. Anyway, after three hours of banging my head against the desk, I finally got the script to run, grabbed my jacket, and went for a long walk in the rain. Sometimes the best debugging tool isn't another StackOverflow tab—it's just stepping away for a breath of fresh air.";
        }
        updateCounts();
        triggerAnalysis();
    });

    btnSampleMixed.addEventListener("click", () => {
        if (samplesCache && samplesCache.mixed) {
            inputText.value = samplesCache.mixed;
        } else {
            inputText.value = "Yesterday I started drafting a proposal for our new marketing campaign. We needed fresh ideas for user retention. It is important to note that customer engagement serves as a pivotal metric in determining brand loyalty. I wasn't totally sure how to phrase that part, so I had a chatbot reword my rough bullet points. The multifaceted approach seamlessly integrates social media outreach with personalized email sequences.";
        }
        updateCounts();
        triggerAnalysis();
    });

    // Clear and Paste
    btnClear.addEventListener("click", () => {
        inputText.value = "";
        updateCounts();
        emptyState.classList.remove("hidden");
        resultsContent.classList.add("hidden");
        heatmapPanel.classList.add("hidden");
        currentAnalysis = null;
    });

    btnPaste.addEventListener("click", async () => {
        try {
            const clipText = await navigator.clipboard.readText();
            if (clipText) {
                inputText.value = clipText;
                updateCounts();
            }
        } catch (err) {
            showToast("Clipboard access denied. Please paste manually.");
        }
    });

    // Analyze Action
    btnAnalyze.addEventListener("click", triggerAnalysis);

    async function triggerAnalysis() {
        const text = inputText.value.trim();
        if (!text) {
            showToast("Please enter some text to analyze.");
            return;
        }

        // Set Loading state
        setLoading(true);

        try {
            const res = await fetch("/api/detect", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || "Analysis request failed.");
            }

            const data = await res.json();
            currentAnalysis = data;
            renderResults(data);
        } catch (err) {
            alert(err.message || "An error occurred while analyzing.");
        } finally {
            setLoading(false);
        }
    }

    function setLoading(isLoading) {
        if (isLoading) {
            spinner.classList.remove("hidden");
            btnIcon.classList.add("hidden");
            btnText.textContent = "Analyzing...";
            btnAnalyze.disabled = true;
        } else {
            spinner.classList.add("hidden");
            btnIcon.classList.remove("hidden");
            btnText.textContent = "Analyze Content";
            btnAnalyze.disabled = false;
        }
    }

    function renderResults(data) {
        emptyState.classList.add("hidden");
        resultsContent.classList.remove("hidden");
        heatmapPanel.classList.remove("hidden");

        const score = data.score;

        // Animate counter
        animateCounter(scoreVal, score);

        // Radial gauge stroke offset & color
        const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
        radialProgress.style.strokeDashoffset = offset;

        let strokeColor = "var(--color-human)";
        let badgeClass = "";

        if (score >= 70) {
            strokeColor = "var(--color-ai)";
            badgeClass = "badge-ai";
        } else if (score >= 40) {
            strokeColor = "var(--color-mixed)";
            badgeClass = "badge-mixed";
        }

        radialProgress.style.stroke = strokeColor;

        // Verdict Badge & Headings
        verdictBadge.className = `verdict-badge ${badgeClass}`;
        verdictBadge.textContent = data.verdict;
        verdictHeading.textContent = data.verdict;
        verdictSummary.textContent = data.summary;

        // Metrics
        const m = data.metrics;
        valBurstiness.textContent = m.burstiness.toFixed(2);
        subBurstiness.textContent = m.burstiness_label;

        valPerplexity.textContent = m.perplexity.toFixed(1);
        subPerplexity.textContent = m.perplexity_label;

        valTtr.textContent = m.ttr.toFixed(2);
        valReading.textContent = `${m.reading_ease}`;

        // AI Marker words
        if (m.detected_markers && m.detected_markers.length > 0) {
            markersBox.classList.remove("hidden");
            markersCount.textContent = `${m.ai_markers_count} detected`;
            markersTags.innerHTML = m.detected_markers.map(tag => 
                `<span class="marker-tag">${escapeHtml(tag)}</span>`
            ).join("");
        } else {
            markersBox.classList.remove("hidden");
            markersCount.textContent = "0 detected";
            markersTags.innerHTML = `<span style="font-size:0.75rem; color: var(--text-muted);">No common AI signature phrases found.</span>`;
        }

        // Build Sentence Heatmap
        buildHeatmap(data.sentences);
    }

    function buildHeatmap(sentences) {
        heatmapContent.innerHTML = "";
        sentenceInspector.classList.add("hidden");

        sentences.forEach((s, idx) => {
            const span = document.createElement("span");
            let cls = "human";
            if (s.score >= 70) cls = "ai";
            else if (s.score >= 40) cls = "mixed";

            span.className = `sentence-span ${cls}`;
            span.textContent = s.sentence + " ";
            span.dataset.index = idx;

            span.addEventListener("click", () => {
                document.querySelectorAll(".sentence-span").forEach(el => el.classList.remove("active"));
                span.classList.add("active");
                showSentenceInspector(s, idx + 1);
            });

            heatmapContent.appendChild(span);
        });
    }

    function showSentenceInspector(sentenceData, index) {
        sentenceInspector.classList.remove("hidden");
        inspBadge.textContent = `Sentence #${index} (${sentenceData.word_count} words)`;
        inspScore.textContent = `${sentenceData.score}% AI Likelihood • ${sentenceData.label}`;
        inspText.textContent = `"${sentenceData.sentence}"`;
        inspReason.textContent = `Diagnostic: ${sentenceData.reason}`;

        // Smooth scroll to inspector
        sentenceInspector.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function animateCounter(element, target) {
        const start = 0;
        const duration = 800;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentVal = Math.round(start + (target - start) * progress);
            element.textContent = currentVal;

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        requestAnimationFrame(update);
    }

    // Export Actions
    btnCopyReport.addEventListener("click", () => {
        if (!currentAnalysis) return;
        const report = `AI SENTINEL DETECTION REPORT
Authored by: Arvind (@Arvind208)
--------------------------------------
Score: ${currentAnalysis.score}% (${currentAnalysis.verdict})
Summary: ${currentAnalysis.summary}

METRICS:
- Sentence Burstiness: ${currentAnalysis.metrics.burstiness} (${currentAnalysis.metrics.burstiness_label})
- Perplexity Index: ${currentAnalysis.metrics.perplexity} (${currentAnalysis.metrics.perplexity_label})
- Lexical Diversity (TTR): ${currentAnalysis.metrics.ttr}
- Flesch Reading Ease: ${currentAnalysis.metrics.reading_ease}
- Total Words: ${currentAnalysis.metrics.word_count}
- Total Sentences: ${currentAnalysis.metrics.sentence_count}
- AI Marker Words: ${currentAnalysis.metrics.detected_markers.join(", ") || "None"}
`;
        navigator.clipboard.writeText(report).then(() => {
            showToast("Analysis report copied to clipboard!");
        });
    });

    btnDownloadJson.addEventListener("click", () => {
        if (!currentAnalysis) return;
        const blob = new Blob([JSON.stringify(currentAnalysis, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `ai-sentinel-report-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast("JSON report downloaded.");
    });

    function showToast(message) {
        toast.textContent = message;
        toast.classList.remove("hidden");
        setTimeout(() => {
            toast.classList.add("hidden");
        }, 2800);
    }

    function escapeHtml(str) {
        return str.replace(/[&<>"']/g, m => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        }[m]));
    }
});
