// State
const state = {
  currentTenderText: "",
  currentTenderFilename: "",
  currentAnalysis: null,
  currentEligibility: null,
  currentBid: null,
  companyProfile: null,
  pastProposals: [],
  teamProfiles: []
};

// Initialize Application on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  initDropzone();
  checkSystemStatus();
  fetchSampleTenders();
  fetchCompanyKnowledge();
});

// Toast notification helper
function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  const icon = document.getElementById("toastIcon");
  const msg = document.getElementById("toastMessage");

  msg.innerText = message;
  if (type === "success") {
    icon.className = "fa-solid fa-circle-check text-emerald-400 text-lg";
    toast.className = toast.className.replace(/border-[a-z]+-500/, "") + " border-emerald-500/50";
  } else if (type === "error") {
    icon.className = "fa-solid fa-circle-exclamation text-rose-400 text-lg";
    toast.className = toast.className.replace(/border-[a-z]+-500/, "") + " border-rose-500/50";
  } else {
    icon.className = "fa-solid fa-circle-info text-brand-400 text-lg";
  }

  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, 4000);
}

// Tab Switching
function switchTab(tabId) {
  // Update tab buttons
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.remove("active-tab", "text-white", "bg-slate-800", "border-slate-700");
    btn.classList.add("text-slate-400");
  });

  const activeBtnId = "tab-btn-" + tabId.replace("-tab", "");
  const activeBtn = document.getElementById(activeBtnId);
  if (activeBtn) {
    activeBtn.classList.add("active-tab", "text-white", "bg-slate-800", "border-slate-700");
    activeBtn.classList.remove("text-slate-400");
  }

  // Update tab contents
  document.querySelectorAll(".tab-content").forEach(content => {
    content.classList.add("hidden");
  });

  const activeContent = document.getElementById(tabId);
  if (activeContent) {
    activeContent.classList.remove("hidden");
  }
}

// System Status & Connection Check
async function checkSystemStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    
    const dot = document.getElementById("apiStatusDot");
    const txt = document.getElementById("apiStatusText");
    const headerCompany = document.getElementById("headerCompanyName");

    if (data.company) {
      headerCompany.innerText = data.company;
    }

    if (data.has_api_key) {
      dot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500";
      txt.innerText = `Sarvam Live (${data.masked_key})`;
      txt.className = "font-medium text-emerald-300";
    } else {
      dot.className = "w-2.5 h-2.5 rounded-full bg-amber-400";
      txt.innerText = "Simulation Mode (Click to set key)";
      txt.className = "font-medium text-amber-300";
    }
  } catch (err) {
    console.error("Status check failed", err);
  }
}

// Sample Tenders Loader
async function fetchSampleTenders() {
  try {
    const res = await fetch("/api/sample-tenders");
    const data = await res.json();
    const select = document.getElementById("sampleTenderSelect");
    select.innerHTML = '<option value="">Select a benchmark tender...</option>';

    data.samples.forEach(sample => {
      const opt = document.createElement("option");
      opt.value = sample.id;
      opt.innerText = `${sample.title} (${sample.size_kb} KB)`;
      select.appendChild(opt);
    });

    // Auto-select first sample for immediate instant testing
    if (data.samples.length > 0) {
      select.value = data.samples[0].id;
      loadSelectedSample();
    }
  } catch (err) {
    console.error("Error loading sample tenders", err);
  }
}

async function loadSelectedSample() {
  const select = document.getElementById("sampleTenderSelect");
  const sampleId = select.value;
  if (!sampleId) return;

  try {
    const res = await fetch(`/api/sample-tenders/${sampleId}`);
    const data = await res.json();

    state.currentTenderText = data.text;
    state.currentTenderFilename = data.filename;

    document.getElementById("tenderTextEditor").value = data.text;
    document.getElementById("docLoadedName").innerText = data.filename;
    document.getElementById("docWordCount").innerText = `${data.metadata.word_count.toLocaleString()} words`;
    document.getElementById("analyzeBtn").disabled = false;

    showToast(`Loaded sample benchmark: ${data.filename}`);
  } catch (err) {
    showToast("Failed to load sample tender", "error");
  }
}

// Drag & Drop / File Upload Handler
function initDropzone() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("tenderFileInput");

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("border-brand-500", "bg-slate-900");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("border-brand-500", "bg-slate-900");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("border-brand-500", "bg-slate-900");
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });

  // Manual text changes in editor
  document.getElementById("tenderTextEditor").addEventListener("input", (e) => {
    state.currentTenderText = e.target.value;
    const words = e.target.value.trim().split(/\s+/).filter(Boolean).length;
    document.getElementById("docWordCount").innerText = `${words.toLocaleString()} words`;
    document.getElementById("analyzeBtn").disabled = words < 10;
  });
}

async function handleFileUpload(file) {
  const formData = new FormData();
  formData.append("file", file);

  const docName = document.getElementById("docLoadedName");
  docName.innerText = "Parsing " + file.name + "...";

  try {
    const res = await fetch("/api/upload-tender", {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || "Upload error");

    state.currentTenderText = data.text;
    state.currentTenderFilename = data.filename;

    document.getElementById("tenderTextEditor").value = data.text;
    docName.innerText = data.filename;
    document.getElementById("docWordCount").innerText = `${data.metadata.word_count.toLocaleString()} words (${data.metadata.page_count} pages)`;
    document.getElementById("analyzeBtn").disabled = false;

    showToast(`Successfully extracted ${file.name}`);
  } catch (err) {
    docName.innerText = "Upload failed";
    showToast(err.message, "error");
  }
}

function clearTenderText() {
  document.getElementById("tenderTextEditor").value = "";
  state.currentTenderText = "";
  state.currentTenderFilename = "";
  document.getElementById("docLoadedName").innerText = "No document loaded";
  document.getElementById("docWordCount").innerText = "0 words";
  document.getElementById("analyzeBtn").disabled = true;
}

// RUN TENDER ANALYSIS WITH SARVAM AI
async function runTenderAnalysis() {
  const text = state.currentTenderText || document.getElementById("tenderTextEditor").value;
  if (!text || text.length < 50) {
    showToast("Please provide sufficient tender text", "error");
    return;
  }

  const btn = document.getElementById("analyzeBtn");
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing with Sarvam AI...';

  try {
    const res = await fetch("/api/analyze-tender", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: text,
        filename: state.currentTenderFilename || "Uploaded_Tender"
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Analysis failed");

    state.currentAnalysis = data.analysis;
    renderAnalysisResults(data.analysis);

    // Automatically trigger eligibility evaluation
    await runEligibilityEvaluation(data.analysis);

    showToast("Tender requirements and deadlines extracted successfully!");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHtml;
  }
}

// Render Analysis Results
function renderAnalysisResults(analysis) {
  const container = document.getElementById("analysisResultsContainer");
  container.classList.remove("hidden");

  const meta = analysis.tender_metadata || {};
  const deadlines = analysis.deadlines || {};
  const elig = analysis.eligibility_criteria || {};
  const scope = analysis.scope_of_work || [];
  const checklist = analysis.submission_checklist || [];

  // Metadata Card
  document.getElementById("cardTenderId").innerText = meta.tender_id || "N/A";
  document.getElementById("cardPortal").innerText = meta.portal || "E-Procurement";
  document.getElementById("cardAuthority").innerText = meta.issuing_authority || "Authority";

  // Value & EMD
  document.getElementById("cardEstValue").innerText = meta.estimated_value_inr || "As per RFP";
  document.getElementById("cardEmd").innerText = meta.emd_amount_inr || "N/A";
  document.getElementById("cardPbg").innerText = meta.pbg_percentage || "3%";

  // Deadlines
  document.getElementById("cardSubmissionDeadline").innerText = deadlines.bid_submission_deadline || "As per RFP";
  document.getElementById("cardPreBid").innerText = deadlines.pre_bid_meeting_date || "N/A";
  document.getElementById("cardDaysRemaining").innerText = `${deadlines.calculated_days_remaining || 18} Days`;

  const urgencyBadge = document.getElementById("cardUrgencyBadge");
  const urgency = deadlines.urgency_status || "Standard Window";
  urgencyBadge.innerText = urgency;
  if (urgency.includes("Critical")) {
    urgencyBadge.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30";
  } else {
    urgencyBadge.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20";
  }

  // Evaluation Model
  document.getElementById("cardEvalMethod").innerText = analysis.evaluation_methodology ? analysis.evaluation_methodology.substring(0, 30) : "QCBS (70:30)";

  // Eligibility Criteria
  const fin = elig.financial || {};
  document.getElementById("eligTurnover").innerText = fin.min_annual_turnover_inr || "₹ 20.0 Crores";
  document.getElementById("eligNetWorth").innerText = fin.net_worth || "Positive net worth";
  document.getElementById("eligSolvency").innerText = fin.solvency_certificate || "₹ 5.0 Crores";
  document.getElementById("eligMsme").innerText = fin.msme_relaxation || "Relaxations applicable";

  // Past Works list
  const pwList = document.getElementById("eligPastWorksList");
  pwList.innerHTML = "";
  const pastWorks = (elig.technical && elig.technical.past_project_experience) || [];
  if (pastWorks.length > 0) {
    pastWorks.forEach(pw => {
      const li = document.createElement("li");
      li.innerText = pw;
      pwList.appendChild(li);
    });
  } else {
    pwList.innerHTML = "<li>5+ Years in Public Sector Systems Integration</li>";
  }

  // Certifications pills
  const certPills = document.getElementById("eligCertsPills");
  certPills.innerHTML = "";
  const certs = elig.certifications || ["ISO 9001:2015", "ISO 27001:2022", "CMMI Level 3"];
  certs.forEach(c => {
    const pill = document.createElement("span");
    pill.className = "px-2 py-1 rounded bg-slate-800 text-xs text-slate-200 border border-slate-700";
    pill.innerText = c;
    certPills.appendChild(pill);
  });

  // Scope of Work
  const scopeBox = document.getElementById("scopeListContainer");
  scopeBox.innerHTML = "";
  scope.forEach((item, idx) => {
    const div = document.createElement("div");
    div.className = "flex items-start gap-2 text-xs py-1 border-b border-slate-800/40 last:border-0";
    div.innerHTML = `<span class="text-indigo-400 font-bold mt-0.5">${idx + 1}.</span> <span>${item}</span>`;
    scopeBox.appendChild(div);
  });

  // Submission Checklist
  const checkList = document.getElementById("checklistContainer");
  checkList.innerHTML = "";
  checklist.forEach((item, idx) => {
    const div = document.createElement("label");
    div.className = "flex items-center gap-2.5 text-xs py-1 cursor-pointer hover:text-white transition";
    div.innerHTML = `
      <input type="checkbox" checked class="rounded border-slate-700 bg-slate-900 text-teal-500 focus:ring-0">
      <span class="flex-1">${item.name}</span>
      <span class="text-[10px] text-teal-400 uppercase font-semibold px-1 rounded bg-teal-500/10">Mandatory</span>
    `;
    checkList.appendChild(div);
  });

  // Scroll smoothly to results
  container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// RUN ELIGIBILITY EVALUATION
async function runEligibilityEvaluation(tenderData) {
  try {
    const res = await fetch("/api/evaluate-eligibility", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tender_data: tenderData })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Evaluation failed");

    state.currentEligibility = data.evaluation;
    renderEligibilityResults(data.evaluation);
  } catch (err) {
    console.error("Eligibility eval error", err);
  }
}

function renderEligibilityResults(evalData) {
  const score = evalData.overall_fit_score || 90;
  
  // Badge in Tab Header
  const scoreBadge = document.getElementById("fitScoreBadge");
  scoreBadge.innerText = `${score}%`;
  scoreBadge.classList.remove("hidden");

  // Verdict Banner
  const pill = document.getElementById("verdictPill");
  pill.innerText = evalData.strategic_verdict;
  document.getElementById("verdictRecommendation").innerText = evalData.executive_recommendation;

  // Fit score circle
  document.getElementById("fitScoreValue").innerText = `${score}%`;
  const circlePath = document.getElementById("fitScoreCirclePath");
  circlePath.setAttribute("stroke-dasharray", `${score}, 100`);

  // Financial pillar
  const fin = evalData.breakdown.financial;
  document.getElementById("evalReqTurnover").innerText = fin.required_turnover;
  document.getElementById("evalCompTurnover").innerText = fin.company_turnover;

  // Matching projects list
  const projBox = document.getElementById("evalMatchingProjects");
  projBox.innerHTML = "";
  const creds = evalData.breakdown.technical.top_matching_credentials || [];
  creds.forEach(p => {
    const div = document.createElement("div");
    div.className = "text-xs";
    div.innerHTML = `<span class="font-bold text-slate-200">${p.project}</span> <span class="text-brand-400 font-semibold">(${p.value})</span> • <span class="text-slate-400">${p.client}</span>`;
    projBox.appendChild(div);
  });

  // Win Themes List
  const winList = document.getElementById("winThemesList");
  winList.innerHTML = "";
  (evalData.win_themes || []).forEach(wt => {
    const li = document.createElement("li");
    li.className = "flex items-start gap-2";
    li.innerHTML = `<i class="fa-solid fa-check text-amber-400 mt-1 text-[11px]"></i> <span>${wt}</span>`;
    winList.appendChild(li);
  });

  // Risks List
  const riskList = document.getElementById("riskMitigationList");
  riskList.innerHTML = "";
  (evalData.compliance_risks_and_mitigation || []).forEach(rm => {
    const li = document.createElement("li");
    li.className = "flex items-start gap-2 bg-slate-950 p-2 rounded-lg border border-slate-800/60";
    li.innerHTML = `
      <i class="fa-solid fa-shield-virus text-rose-400 mt-0.5 text-xs"></i>
      <div>
        <strong class="text-rose-300 block">${rm.risk}</strong>
        <span class="text-slate-400 text-[11px] block mt-0.5">Mitigation: ${rm.mitigation}</span>
      </div>
    `;
    riskList.appendChild(li);
  });
}

// RUN BID GENERATION WITH SARVAM AI
async function runBidGeneration() {
  if (!state.currentAnalysis) {
    showToast("Please analyze a tender first before generating bid response", "error");
    switchTab("tender-tab");
    return;
  }

  const btn = document.getElementById("generateBidBtn");
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating 10-Section Proposal with Sarvam AI...';

  const tone = document.getElementById("bidToneSelect").value;
  const detail = document.getElementById("bidDetailSelect").value;
  const winFocus = document.getElementById("bidWinFocusInput").value;

  try {
    const res = await fetch("/api/generate-bid", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tender_data: state.currentAnalysis,
        tone: tone,
        detail_level: detail,
        custom_instructions: winFocus
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Bid generation failed");

    state.currentBid = data.bid;
    renderBidProposal(data.bid);

    document.getElementById("downloadDocxBtn").disabled = false;
    document.getElementById("downloadMdBtn").disabled = false;

    showToast("Complete Technical & Management Bid Proposal synthesized!");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHtml;
  }
}

function renderBidProposal(bid) {
  const container = document.getElementById("bidMarkdownOutput");
  const tocList = document.getElementById("bidTocList");
  
  // Render HTML via marked
  container.innerHTML = marked.parse(bid.markdown_content);

  // Render Table of Contents
  tocList.innerHTML = "";
  (bid.sections || []).forEach((sec, idx) => {
    const a = document.createElement("a");
    a.href = "#";
    a.className = "block px-2.5 py-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition truncate";
    a.innerText = `${idx + 1}. ${sec.title}`;
    a.onclick = (e) => {
      e.preventDefault();
      // Scroll to heading in container
      const headings = container.querySelectorAll("h1, h2");
      for (const h of headings) {
        if (h.innerText.includes(sec.title) || sec.title.includes(h.innerText)) {
          h.scrollIntoView({ behavior: 'smooth', block: 'start' });
          break;
        }
      }
    };
    tocList.appendChild(a);
  });

  document.getElementById("bidGeneratedMeta").innerText = `Proposal for ${bid.tender_id} • ${bid.sections.length} Sections Generated`;
}

// EXPORT TO MICROSOFT WORD (.DOCX)
async function downloadBidDocx() {
  if (!state.currentBid) return;

  const btn = document.getElementById("downloadDocxBtn");
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Formatting Word Doc...';

  try {
    const res = await fetch("/api/export-docx", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state.currentBid)
    });

    if (!res.ok) throw new Error("DOCX generation failed");

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Technical_Bid_Proposal_${(state.currentBid.tender_id || "NIT").replace(/\//g, "_")}.docx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    showToast("Downloaded official Word (.docx) proposal!");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHtml;
  }
}

function downloadBidMarkdown() {
  if (!state.currentBid) return;
  const blob = new Blob([state.currentBid.markdown_content], { type: "text/markdown;charset=utf-8" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `Technical_Bid_Proposal_${(state.currentBid.tender_id || "NIT").replace(/\//g, "_")}.md`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
  showToast("Downloaded Markdown file!");
}

function copyBidToClipboard() {
  if (!state.currentBid) return;
  navigator.clipboard.writeText(state.currentBid.markdown_content);
  showToast("Copied full proposal to clipboard!");
}

function printBidResponse() {
  window.print();
}

// SARVAM INDIC TRANSLATION (Mayura:v1)
async function translateTenderSummary() {
  const targetLang = document.getElementById("targetLanguageSelect").value;
  const textToTranslate = state.currentAnalysis 
    ? `Tender Ref: ${state.currentAnalysis.tender_metadata.tender_id}. Title: ${state.currentAnalysis.tender_metadata.title}. Issuing Authority: ${state.currentAnalysis.tender_metadata.issuing_authority}. Submission Deadline: ${state.currentAnalysis.deadlines.bid_submission_deadline}. Turnover Required: ${state.currentAnalysis.eligibility_criteria.financial.min_annual_turnover_inr}. Scope: ${state.currentAnalysis.scope_of_work.join('; ')}`
    : (state.currentTenderText.substring(0, 1000) || "Tender Notice");

  const outBox = document.getElementById("translatedOutput");
  outBox.innerHTML = '<div class="text-amber-400"><i class="fa-solid fa-spinner fa-spin"></i> Translating with Sarvam Mayura neural translation...</div>';

  try {
    const res = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: textToTranslate,
        target_language: targetLang,
        source_language: "en-IN"
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Translation failed");

    outBox.innerHTML = `
      <div class="space-y-3">
        <div class="text-amber-400 font-bold uppercase text-[11px] flex items-center justify-between">
          <span>${data.provider}</span>
          <span class="font-mono text-slate-400">${data.target_language}</span>
        </div>
        <div class="text-slate-100 whitespace-pre-wrap">${data.translated_text}</div>
      </div>
    `;
    showToast(`Translated to ${targetLang}!`);
  } catch (err) {
    outBox.innerHTML = `<div class="text-rose-400">${err.message}</div>`;
  }
}

// SARVAM TEXT-TO-SPEECH AUDIO BRIEFING (Bulbul:v2)
async function generateAudioBriefing() {
  const speaker = document.getElementById("ttsSpeakerSelect").value;
  const briefText = state.currentAnalysis
    ? `Tender Briefing for ${state.currentAnalysis.tender_metadata.title}. Submission deadline is ${state.currentAnalysis.deadlines.bid_submission_deadline}. Earnest money deposit is ${state.currentAnalysis.tender_metadata.emd_amount_inr}. Minimum turnover required is ${state.currentAnalysis.eligibility_criteria.financial.min_annual_turnover_inr}.`
    : "Tender Bidding Executive Briefing powered by Sarvam AI speech synthesis.";

  showToast("Synthesizing audio with Sarvam Bulbul:v2...");

  try {
    const res = await fetch("/api/text-to-speech", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: briefText,
        target_language: "hi-IN",
        speaker: speaker
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "TTS generation failed");

    if (data.audio_base64) {
      const audioPlayer = document.getElementById("ttsAudioPlayer");
      audioPlayer.src = `data:audio/wav;base64,${data.audio_base64}`;
      document.getElementById("audioPlayerContainer").classList.remove("hidden");
      document.getElementById("audioPlaceholder").classList.add("hidden");
      audioPlayer.play();
      showToast("Audio executive briefing ready!");
    } else {
      showToast(data.message || "TTS simulation: Sarvam API key required for live audio synthesis.", "info");
    }
  } catch (err) {
    showToast(err.message, "error");
  }
}

// COMPANY KNOWLEDGE MANAGEMENT
async function fetchCompanyKnowledge() {
  try {
    // 1. Profile
    const resProfile = await fetch("/api/company-profile");
    const cp = await resProfile.json();
    state.companyProfile = cp;

    document.getElementById("kbCompanyName").value = cp.company_name;
    document.getElementById("kbCin").value = cp.registration_number;
    document.getElementById("kbIncorp").value = `${cp.incorporation_year} (${cp.years_in_business} Years)`;
    document.getElementById("kbTurnover").value = cp.financials.average_turnover_crores;
    document.getElementById("kbNetWorth").value = cp.financials.net_worth_crores;
    document.getElementById("kbSolvency").value = cp.financials.solvency_crores;

    // 2. Past Proposals
    const resProps = await fetch("/api/past-proposals");
    const pData = await resProps.json();
    state.pastProposals = pData.proposals;
    renderPastProposalsList(pData.proposals);

    // 3. Team Profiles
    const resTeam = await fetch("/api/team-profiles");
    const tData = await resTeam.json();
    state.teamProfiles = tData.team;
    renderTeamProfilesList(tData.team);
  } catch (err) {
    console.error("Knowledge base fetch error", err);
  }
}

function renderPastProposalsList(proposals) {
  const container = document.getElementById("pastProposalsList");
  container.innerHTML = "";
  proposals.forEach(p => {
    const card = document.createElement("div");
    card.className = "bg-slate-950 border border-slate-800/80 rounded-xl p-4 text-xs space-y-2";
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-bold text-white text-sm">${p.project_name}</span>
        <span class="text-brand-400 font-extrabold bg-brand-500/10 px-2 py-0.5 rounded">₹ ${p.contract_value_crores} Cr</span>
      </div>
      <div class="text-slate-400">Client: <span class="text-slate-300 font-medium">${p.client}</span> (${p.completion_year})</div>
      <p class="text-slate-400 text-[11px] leading-relaxed line-clamp-2">${p.scope_summary}</p>
      <div class="flex flex-wrap gap-1 pt-1">
        ${p.technologies.map(t => `<span class="bg-slate-900 border border-slate-800 text-slate-300 px-1.5 py-0.5 rounded text-[10px]">${t}</span>`).join('')}
      </div>
    `;
    container.appendChild(card);
  });
  document.getElementById("kbProposalCount").innerText = `${proposals.length} Proposals Stored`;
}

function renderTeamProfilesList(team) {
  const container = document.getElementById("teamProfilesList");
  container.innerHTML = "";
  team.forEach(m => {
    const card = document.createElement("div");
    card.className = "bg-slate-950 border border-slate-800/80 rounded-xl p-4 text-xs space-y-1.5";
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-bold text-white text-sm">${m.name}</span>
        <span class="text-indigo-400 font-semibold">${m.experience_years} Years Exp</span>
      </div>
      <div class="text-brand-400 font-medium">${m.role}</div>
      <div class="text-slate-400 text-[11px]">${m.qualifications}</div>
      <div class="text-slate-300 text-[11px] pt-1">Certs: <span class="text-emerald-400 font-mono">${m.certifications.join(', ')}</span></div>
    `;
    container.appendChild(card);
  });
}

async function saveCompanyProfileChanges() {
  if (!state.companyProfile) return;
  state.companyProfile.company_name = document.getElementById("kbCompanyName").value;
  state.companyProfile.registration_number = document.getElementById("kbCin").value;
  state.companyProfile.financials.average_turnover_crores = parseFloat(document.getElementById("kbTurnover").value) || 35.57;
  state.companyProfile.financials.net_worth_crores = parseFloat(document.getElementById("kbNetWorth").value) || 18.2;
  state.companyProfile.financials.solvency_crores = parseFloat(document.getElementById("kbSolvency").value) || 15.0;

  try {
    const res = await fetch("/api/company-profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state.companyProfile)
    });
    if (!res.ok) throw new Error("Failed to save profile");
    showToast("Company knowledge profile updated & persisted!");
  } catch (err) {
    showToast(err.message, "error");
  }
}

// SARVAM SETTINGS MODAL
function openSettingsModal() {
  document.getElementById("settingsModal").classList.remove("hidden");
  document.getElementById("modalVerifyResult").classList.add("hidden");
}

function closeSettingsModal() {
  document.getElementById("settingsModal").classList.add("hidden");
}

async function saveSarvamSettings() {
  const apiKey = document.getElementById("modalApiKeyInput").value.trim();
  const model = document.getElementById("modalModelSelect").value;
  const resultBox = document.getElementById("modalVerifyResult");

  resultBox.className = "p-3 rounded-xl text-xs border bg-slate-950 border-amber-500/50 text-amber-300 flex items-center gap-2";
  resultBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Verifying key with Sarvam AI API...';
  resultBox.classList.remove("hidden");

  try {
    const res = await fetch("/api/settings/sarvam", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: apiKey, model: model })
    });

    const data = await res.json();
    const ver = data.verification || {};

    if (ver.valid) {
      resultBox.className = "p-3 rounded-xl text-xs border bg-emerald-950/40 border-emerald-500/50 text-emerald-300";
      resultBox.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-400 mr-1.5"></i> ${ver.message}`;
      showToast("Sarvam API Key verified and saved successfully!");
      setTimeout(() => {
        closeSettingsModal();
        checkSystemStatus();
      }, 1500);
    } else {
      resultBox.className = "p-3 rounded-xl text-xs border bg-amber-950/40 border-amber-500/50 text-amber-300";
      resultBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-amber-400 mr-1.5"></i> ${ver.message}`;
      showToast("Key saved. Prototype running with domain fallback.", "info");
      checkSystemStatus();
    }
  } catch (err) {
    resultBox.className = "p-3 rounded-xl text-xs border bg-rose-950/40 border-rose-500/50 text-rose-300";
    resultBox.innerHTML = `<i class="fa-solid fa-circle-xmark text-rose-400 mr-1.5"></i> ${err.message}`;
  }
}
