/* Monthly Revenue Chart */
const revenueCtx = document.getElementById("revenueChart");

new Chart(revenueCtx, {
  type: "line",
  data: {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    datasets: [{
      label: "Revenue (₹)",
      data: [60000, 85000, 78000, 92000, 110000, 135000],
      tension: 0.4,
      borderWidth: 2
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false }
    }
  }
});

/* Product Sales Chart */
const productCtx = document.getElementById("productChart");

new Chart(productCtx, {
  type: "bar",
  data: {
    labels: ["Cement", "Steel", "Sand", "Sandstone", "Birla White Cement"],
    datasets: [{
      label: "Sales",
      data: [180, 140, 460, 400, 100]
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false }
    }
  }
});
