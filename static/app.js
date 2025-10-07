// -----------------------------
// IIUO Ads Dashboard JS
// -----------------------------

document.addEventListener("DOMContentLoaded", () => {
  console.log("IIUO Ads Dashboard JS loaded.");

  // -----------------------------
  // Add Website Form Validation
  // -----------------------------
  const addWebsiteForm = document.querySelector(".add-website-form");
  if (addWebsiteForm) {
    addWebsiteForm.addEventListener("submit", (e) => {
      const name = addWebsiteForm.querySelector("#name").value.trim();
      const domain = addWebsiteForm.querySelector("#domain").value.trim();

      if (!name || !domain) {
        e.preventDefault();
        alert("Please provide both website name and domain.");
      }
    });
  }

  // -----------------------------
  // Highlight Verified Websites
  // -----------------------------
  const websiteRows = document.querySelectorAll(".websites-table tbody tr");
  websiteRows.forEach((row) => {
    const verifiedCell = row.children[2]; // 3rd column: Verified
    if (verifiedCell.textContent.trim() === "✅") {
      row.style.backgroundColor = "#e6ffed"; // light green
    }
  });

  // -----------------------------
  // Copy Verification Token
  // -----------------------------
  document.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const token = btn.getAttribute("data-token");
      const snippet = `iiuo-verification=${token}`;
      navigator.clipboard.writeText(snippet).then(() => {
        alert(
          "Verification snippet copied to clipboard!\n" +
            "Add this line to your ads.txt file on your domain."
        );
      });
    });
  });
});
