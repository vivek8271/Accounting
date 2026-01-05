
    // Base dataset (aligns with your dashboard)
    const DATA = [
      { product: "Cement (UltraTech)", inventory: 320, units_sold: 180, revenue: 90000 },
      { product: "TMT Steel",          inventory: 210, units_sold: 140, revenue: 140000 },
      { product: "River Sand",         inventory: 710, units_sold: 460, revenue: 250000 },
    ];

    // Summary (static for demo; can be computed from DATA)
    const SUMMARY = {
      total_revenue: 480000,
      total_products: 18,
      stock_available: 1240,
      monthly_growth_percent: 12.4
    };

    // Helpers
    const fmtINR = (n) =>
      "₹" + (n || 0).toLocaleString("en-IN");

    const badgeForInventory = (inv) => {
      if (inv >= 500) return { cls: "good", text: "Healthy" };
      if (inv >= 250) return { cls: "warn", text: "Watch" };
      return { cls: "low", text: "Low" };
    };

    // Render summary
    document.getElementById("sumRevenue").textContent = fmtINR(SUMMARY.total_revenue);
    document.getElementById("sumProducts").textContent = SUMMARY.total_products;
    document.getElementById("sumStock").textContent = `${SUMMARY.stock_available.toLocaleString("en-IN")} units`;
    document.getElementById("topProduct").textContent =
      DATA.slice().sort((a,b)=>b.revenue-a.revenue)[0]?.product || "—";

    // State
    const state = {
      qProduct: "",
      minRevenue: null,
      minInventory: null,
      sortBy: "",
      sortDir: "desc",
    };

    // DOM refs
    const tbody = document.getElementById("tableBody");
    const rowCount = document.getElementById("rowCount");
    const filteredRevenue = document.getElementById("filteredRevenue");
    const filteredUnits = document.getElementById("filteredUnits");
    const filteredInventory = document.getElementById("filteredInventory");

    // Controls
    const qProduct = document.getElementById("qProduct");
    const minRevenue = document.getElementById("minRevenue");
    const minInventory = document.getElementById("minInventory");
    const sortBy = document.getElementById("sortBy");
    const sortDir = document.getElementById("sortDir");
    const applyBtn = document.getElementById("applyBtn");
    const insertBtn = document.getElementById("insertBtn");

    // Filtering & sorting
    function applyFilters() {
      let rows = DATA.slice();

      // Text search
      if (state.qProduct?.trim()) {
        const needle = state.qProduct.trim().toLowerCase();
        rows = rows.filter(r => r.product.toLowerCase().includes(needle));
      }
      // Min revenue
      if (Number.isFinite(state.minRevenue)) {
        rows = rows.filter(r => r.revenue >= state.minRevenue);
      }
      // Min inventory
      if (Number.isFinite(state.minInventory)) {
        rows = rows.filter(r => r.inventory >= state.minInventory);
      }
      // Sort
      if (state.sortBy) {
        const key = state.sortBy;
        rows.sort((a,b) => {
          const av = a[key], bv = b[key];
          if (typeof av === "string" && typeof bv === "string") {
            return state.sortDir === "asc"
              ? av.localeCompare(bv)
              : bv.localeCompare(av);
          }
          return state.sortDir === "asc" ? av - bv : bv - av;
        });
      }

      renderTable(rows);
    }

    function renderTable(rows) {
      tbody.innerHTML = "";
      let totalRev = 0, totalUnits = 0, totalInv = 0;

      rows.forEach(r => {
        totalRev += r.revenue;
        totalUnits += r.units_sold;
        totalInv += r.inventory;

        const tr = document.createElement("tr");

        const tdProduct = document.createElement("td");
        tdProduct.textContent = r.product;

        const tdInv = document.createElement("td");
        tdInv.className = "num";
        tdInv.textContent = r.inventory.toLocaleString("en-IN");

        const tdUnits = document.createElement("td");
        tdUnits.className = "num";
        tdUnits.textContent = r.units_sold.toLocaleString("en-IN");

        const tdRevenue = document.createElement("td");
        tdRevenue.className = "num";
        tdRevenue.textContent = fmtINR(r.revenue);

        const tdStatus = document.createElement("td");
        const badge = badgeForInventory(r.inventory);
        tdStatus.innerHTML = `<span class="badge ${badge.cls}">${badge.text}</span>`;

        tr.appendChild(tdProduct);
        tr.appendChild(tdInv);
        tr.appendChild(tdUnits);
        tr.appendChild(tdRevenue);
        tr.appendChild(tdStatus);

        tbody.appendChild(tr);
      });

      rowCount.textContent = rows.length;
      filteredRevenue.textContent = fmtINR(totalRev);
      filteredUnits.textContent = totalUnits.toLocaleString("en-IN");
      filteredInventory.textContent = totalInv.toLocaleString("en-IN");
    }

    // Wire controls
    applyBtn.addEventListener("click", () => {
      state.qProduct = qProduct.value || "";
      state.minRevenue = minRevenue.value ? Number(minRevenue.value) : null;
      state.minInventory = minInventory.value ? Number(minInventory.value) : null;
      state.sortBy = sortBy.value || "";
      state.sortDir = sortDir.value || "desc";
      applyFilters();
    });

    // insertBtn.addEventListener("click", async() => {
    //     const res = await fetch('localhost:8080/insert');
    //   qProduct.value = "";
    //   minRevenue.value = "";
    //   minInventory.value = "";
    //   sortBy.value = "";
    //   sortDir.value = "desc";
    //   state.qProduct = "";
    //   state.minRevenue = null;
    //   state.minInventory = null;
    //   state.sortBy = "";
    //   state.sortDir = "desc";
    //   applyFilters();
    // });

    // Initial render
    applyFilters();