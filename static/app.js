ICON_COPY = `
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
    viewBox="0 0 24 24" fill="none" stroke="currentColor"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="8" y="8" width="13" height="13" rx="2"/>
    <path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>
  </svg>`;

ICON_CHECK = `
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
    viewBox="0 0 24 24" fill="none" stroke="currentColor"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>`;

// <=10 min green, <=30 min orange, <=60 min red, otherwise grey
function pingColor(iso) {
  const mins = (Date.now() - new Date(iso).getTime()) / 60000;
  if (mins <= 10) return "green";
  if (mins <= 30) return "orange";
  if (mins <= 60) return "red";
  return "grey";
}

// Handle 
document.addEventListener("click", async (event) => {
  const button = event.target.closest(".copy-ip");
  if (!button) return;

  try {
    await navigator.clipboard.writeText(button.dataset.ip ?? "");

    // Check box for 1000ms, then revert to original icon
    button.innerHTML = ICON_CHECK;
    setTimeout(() => {
      button.innerHTML = ICON_COPY;
    }, 1000);
  } catch (error) {
    console.error("Failed to copy IP:", error);
  }
});

function currentFilter() {
  return new URLSearchParams(location.search).get("filter") ?? "";
}

function robotsUrl() {
  const f = currentFilter();
  return f ? "/api/robots?filter=" + encodeURIComponent(f) : "/api/robots";
}

function updateDownloadLink() {
  const f = currentFilter();
  document.getElementById("download-inventory").href =
    f ? "/api/inventory?filter=" + encodeURIComponent(f) : "/api/inventory";
}

const table = new DataTable("#robots", {
  ajax: { url: robotsUrl(), dataSrc: "" },
  search: { search: currentFilter() },
  pageLength: 25,
  createdRow: (row, data) => row.classList.add("row-" + pingColor(data.lastPing)),
  columns: [
    {
      data: "name",
      render: (name, type) => {
        if (type !== "display") return name;
        return `<strong>${name}</strong>`;
      }
    },
    {
      data: "privateIP",
      render: (ip, type) => {
        if (type !== "display") return ip;

        return `
          <span class="ip-cell">
          <code>${ip}</code>
          <button type="button" class="copy-ip" data-ip="${ip}" title="Copy IP" aria-label="Copy IP">
            ${ICON_COPY}
          </button>
        </span>
        `;
      }
    },
    {
      data: "publicIP",
      render: (ip, type, row) => {
        if (type !== "display" || !row.asn) return ip;
        return `<span class="ip-cell">
                  <code>${ip}</code>
                  <img 
                    class="asn-icon"
                    src="https://static.ui.com/asn/${encodeURIComponent(row.asn)}_101x101.png"
                    alt=""
                    title="AS${row.asn}"
                    onerror="this.style.display='none'"
                    />
                </span>`;
      },
    },
    { data: "location", defaultContent: "Unknown", render: d => d || "Unknown" },
    {
      data: "lastPing",
      render: (d, type) => {
        if (type !== "display") return d;
        return `${new Date(d).toLocaleString()}`;
      },
    },
  ],
  // Last ping (newest first), then hostname, then private IP
  order: [[4, "desc"], [0, "asc"], [1, "asc"]],
});

setInterval(() => table.ajax.reload(null, false), 5000);

updateDownloadLink();

// Keep the URL's ?filter= in sync with the search box
table.on("search.dt", () => {
  const value = table.search();
  const url = new URL(location.href);
  if (value) url.searchParams.set("filter", value);
  else url.searchParams.delete("filter");
  history.replaceState(null, "", url);
  updateDownloadLink();
});
