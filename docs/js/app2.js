/* App 2 — Parking permits page. Uses js/rules.js (window.SkeletonRules). */
(function () {
  "use strict";
  var R = window.SkeletonRules;

  var $ = function (id) { return document.getElementById(id); };

  var office = new R.PermitOffice();
  var applications = []; // {driver, result} in submit order

  function showResult(result) {
    $("result-panel").hidden = false;
    $("r-id").textContent = result.applicationId;

    var status = $("r-status");
    status.textContent = result.status;
    status.className = result.status === "Approved"
      ? "status-approved" : "status-denied";

    $("r-fee").textContent = "$" + result.fee;
    $("r-payment").textContent = result.payment
      ? result.payment.paymentId + " — $" + result.payment.amount +
        " (demo payment, not a real charge)"
      : "No payment";

    $("r-steps").textContent = result.steps.join(" → ");

    var list = $("r-timeline");
    list.innerHTML = "";
    result.timeline.forEach(function (line) {
      var li = document.createElement("li");
      li.textContent = line;
      list.appendChild(li);
    });
  }

  function refreshList() {
    $("ledger-count").textContent =
      "Payments in the ledger: " + office.paymentsCount;

    var body = $("apps-body");
    body.innerHTML = "";
    if (!applications.length) {
      body.innerHTML = '<tr><td colspan="5">No applications yet.</td></tr>';
      return;
    }
    applications.forEach(function (entry) {
      var r = entry.result;
      var tr = document.createElement("tr");
      [r.applicationId, entry.driver, r.status, "$" + r.fee,
       r.payment ? r.payment.paymentId : "No payment"].forEach(function (text, i) {
        var td = document.createElement("td");
        td.textContent = text;
        if (i === 2) {
          td.className = r.status === "Approved"
            ? "status-approved" : "status-denied";
        }
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
  }

  function runApplication(app) {
    var result = office.submit(app);
    applications.push({ driver: app.driver, result: result });
    showResult(result);
    refreshList();
    return result;
  }

  $("permit-form").addEventListener("submit", function (ev) {
    ev.preventDefault();
    runApplication({
      driver: $("driver").value,
      plate: $("plate").value,
      address: $("address").value,
      zone: $("zone").value,
      permit_type: $("permit-type").value
    });
  });

  function resetOffice() {
    office = new R.PermitOffice();
    applications = [];
    $("result-panel").hidden = true;
    refreshList();
  }

  $("reset-btn").addEventListener("click", resetOffice);

  $("demo-btn").addEventListener("click", function () {
    // Start fresh, then run the exact demo cases from parking/demo.py.
    resetOffice();
    runApplication({
      driver: "Ana Ruiz", plate: "8XYZ123", address: "12 Pine St",
      zone: "North Lot", permit_type: "resident"
    });
    runApplication({
      driver: "Ben Cole", plate: "4ABC99", address: "1 Far Away Rd",
      zone: "Airport", permit_type: "visitor"
    });
    runApplication({
      driver: "Cy Park", plate: "7EMP001", address: "9 Oak Ave",
      zone: "Downtown", permit_type: "employee"
    });
  });

  refreshList();
})();
