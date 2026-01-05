const category = document.getElementById("category");
const unit = document.getElementById("unit");
const stoneCount = document.getElementById("stoneCount");
const stoneWeight = document.getElementById("stoneWeight");

const qty = document.getElementById("quantity");
const rate = document.getElementById("rate");
const materialCost = document.getElementById("materialCost");
const transportCost = document.getElementById("transportCost");
const totalCost = document.getElementById("totalCost");

category.addEventListener("change", () => {
  unit.innerHTML = "";
  stoneCount.classList.add("hidden");
  stoneWeight.classList.add("hidden");

  const map = {
    cement: ["Bag"],
    sand: ["Ton"],
    steel: ["Ton", "Quintal"],
    stone: ["Number"]
  };

  if (category.value === "stone") {
    stoneCount.classList.remove("hidden");
    stoneWeight.classList.remove("hidden");
  }

  (map[category.value] || []).forEach(u => {
    const opt = document.createElement("option");
    opt.textContent = u;
    unit.appendChild(opt);
  });
});

function calculate() {
  const mCost = (qty.value || 0) * (rate.value || 0);
  materialCost.value = mCost;
  totalCost.value = mCost + (+transportCost.value || 0);
}

[qty, rate, transportCost].forEach(el =>
  el && el.addEventListener("input", calculate)
);
