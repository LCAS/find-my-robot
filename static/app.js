// <=10 min green, <=30 min orange, <=60 min red, otherwise grey
function pingColor(iso) {
  const mins = (Date.now() - new Date(iso).getTime()) / 60000;
  if (mins <= 10) return "green";
  if (mins <= 30) return "orange";
  if (mins <= 60) return "red";
  return "grey";
}

const table = new DataTable("#robots", {
  ajax: { url: "/api/robots", dataSrc: "" },
  pageLength: 25,
  createdRow: (row, data) => row.classList.add("row-" + pingColor(data.lastPing)),
  columns: [
    { data: "name" },
    { data: "privateIP" },
    { data: "publicIP" },
    { data: "location", defaultContent: "Unknown", render: d => d || "Unknown" },
    {
      data: "lastPing",
      render: (d, type) => {
        if (type !== "display") return d;
        return `${new Date(d).toLocaleString()}`;
      },
    },
  ],
  // Last ping (newest first), then hostname, then wireless IP
  order: [[4, "desc"], [0, "asc"], [1, "asc"]],
});

setInterval(() => table.ajax.reload(null, false), 5000);
