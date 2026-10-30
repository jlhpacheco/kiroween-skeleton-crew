/* App 1 — Unemployment claim page. Uses js/rules.js (window.SkeletonRules). */
(function () {
  "use strict";
  var R = window.SkeletonRules;

  var $ = function (id) { return document.getElementById(id); };

  // UI totals: $ with commas and 2 decimals, e.g. $4,750.00
  function moneyUI(x) {
    return "$" + Number(x).toLocaleString("en-US", {
      minimumFractionDigits: 2, maximumFractionDigits: 2
    });
  }
  // Plain amounts for the result table, e.g. $5,200.00
  function moneyPlain(x) { return moneyUI(x); }

  var QUARTER_NAMES = {
    1: "Q1 (Jan–Mar)", 2: "Q2 (Apr–Jun)", 3: "Q3 (Jul–Sep)", 4: "Q4 (Oct–Dec)"
  };

  var claim = null;

  function parseClaimDate() {
    var v = $("claim-date").value; // "2026-11-02"
    if (!v) { return null; }
    var parts = v.split("-");
    return { year: parseInt(parts[0], 10), month: parseInt(parts[1], 10),
             day: parseInt(parts[2], 10), text: v };
  }

  function quarterText(q) {
    return QUARTER_NAMES[q[1]] + " " + q[0];
  }

  function updateQuarterLabels() {
    var d = parseClaimDate();
    if (!d) { return; }
    var std = R.standardBasePeriod({ year: d.year, month: d.month });
    for (var i = 0; i < 4; i++) {
      var label = document.querySelector('label[for="wage-' + (i + 1) + '"]');
      if (label) {
        label.textContent = "Quarter " + (i + 1) + " wages ($) — " +
          quarterText(std.quarters[i]);
      }
    }
  }

  function wages() {
    var out = [];
    for (var i = 1; i <= 4; i++) {
      var v = parseFloat($("wage-" + i).value);
      out.push(isNaN(v) ? 0 : v);
    }
    return out;
  }

  function showMessage(id, text) {
    var el = $(id);
    el.textContent = text;
    el.hidden = !text;
  }

  function buildWeekRows() {
    var wrap = $("week-rows");
    wrap.innerHTML = "";
    for (var week = 1; week <= 26; week++) {
      (function (week) {
        var row = document.createElement("div");
        row.className = "week-row";

        var label = document.createElement("span");
        label.className = "week-label";
        label.textContent = "Week " + week;
        row.appendChild(label);

        var inputLabel = document.createElement("label");
        inputLabel.setAttribute("for", "earn-" + week);
        inputLabel.textContent = "Earnings $";
        inputLabel.style.margin = "0";
        row.appendChild(inputLabel);

        var input = document.createElement("input");
        input.type = "number";
        input.id = "earn-" + week;
        input.min = "0";
        input.step = "0.01";
        input.value = "0";
        row.appendChild(input);

        var btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = "Certify & pay week " + week;
        btn.addEventListener("click", function () { payWeek(week); });
        row.appendChild(btn);

        var tag = document.createElement("span");
        tag.className = "paid-tag";
        tag.id = "paid-" + week;
        row.appendChild(tag);

        wrap.appendChild(row);
      })(week);
    }
  }

  function refreshClaim() {
    if (!claim) { return; }
    $("t-paid").textContent = moneyUI(claim.totalPaid);
    $("t-balance").textContent = moneyUI(claim.balance);
    $("t-weeks").textContent = claim.weeksPaid + " of 26";

    var list = $("timeline");
    list.innerHTML = "";
    claim.timeline.forEach(function (line) {
      var li = document.createElement("li");
      li.textContent = line;
      list.appendChild(li);
    });

    for (var week = 1; week <= 26; week++) {
      var tag = $("paid-" + week);
      if (tag && claim.payments[week]) {
        tag.textContent = "Paid: " + moneyUI(claim.payments[week].amount);
      }
    }
    var wtag = $("waiting-btn");
    if (claim.waitingWeekCertified) {
      wtag.textContent = "Waiting week — certified (paid $0)";
    }
  }

  function checkClaim() {
    showMessage("check-message", "");
    showMessage("claim-message", "");
    showMessage("claim-ok", "");
    claim = null;
    $("claim-panel").hidden = true;

    var d = parseClaimDate();
    if (!d) {
      showMessage("check-message", "Pick a claim date first.");
      return null;
    }
    var w = wages();
    var std = R.standardBasePeriod({ year: d.year, month: d.month });
    var alt = R.alternateBasePeriod({ year: d.year, month: d.month });
    var hq = R.highestQuarter(w);
    var total = w.reduce(function (a, b) { return a + b; }, 0);

    var qualifies, wba;
    try {
      qualifies = R.monetarilyQualifies(hq, total);
      wba = R.weeklyBenefitAmount(hq);
    } catch (err) {
      showMessage("check-message", err.message);
      return null;
    }

    $("r-std").textContent = std.quarters.map(quarterText).join(", ");
    $("r-std-dates").textContent = std.start + " to " + std.end;
    $("r-alt-dates").textContent = alt.start + " to " + alt.end;
    $("r-hq").textContent = moneyPlain(hq);
    $("r-total").textContent = moneyPlain(total);
    $("r-qualifies").textContent = qualifies ? "Yes" : "No";
    if (hq >= 1300) {
      $("r-branch").textContent =
        "Branch A — highest quarter is at or over $1,300.";
    } else if (hq >= 900 && total >= 1.25 * hq) {
      $("r-branch").textContent =
        "Branch B — highest quarter is at or over $900, and total wages " +
        "are at least 1.25 × the highest quarter.";
    } else {
      $("r-branch").textContent =
        "No branch passes. Branch A needs a highest quarter of $1,300 or more. " +
        "Branch B needs $900 or more, plus total wages of at least " +
        "1.25 × the highest quarter.";
    }
    $("r-wba").textContent = "$" + wba;
    $("r-max").textContent = qualifies ? "$" + R.maxBenefitAmount(wba) : "$0";
    $("result-panel").hidden = false;

    if (!qualifies) {
      showMessage("check-message",
        "This claim does not qualify. The timeline stops here.");
      return null;
    }

    var name = $("claimant").value.trim() || "Demo Claimant";
    claim = new R.Claim(name, wba);
    buildWeekRows();
    $("claim-panel").hidden = false;
    refreshClaim();
    return claim;
  }

  function payWeek(week) {
    showMessage("claim-message", "");
    showMessage("claim-ok", "");
    if (!claim) {
      showMessage("claim-message", "Check your claim first.");
      return;
    }
    var v = parseFloat($("earn-" + week).value);
    var earnings = isNaN(v) ? 0 : v;
    try {
      var payment = claim.certifyAndPay(week, earnings);
      showMessage("claim-ok",
        "Week " + week + " paid: " + moneyUI(payment.amount) + ".");
    } catch (err) {
      // Clear blocked message — e.g. same week twice, or no waiting week yet.
      showMessage("claim-message", "Blocked: " + err.message);
    }
    refreshClaim();
  }

  $("claim-form").addEventListener("submit", function (ev) {
    ev.preventDefault();
    checkClaim();
  });
  $("claim-date").addEventListener("change", updateQuarterLabels);

  $("waiting-btn").addEventListener("click", function () {
    showMessage("claim-message", "");
    showMessage("claim-ok", "");
    if (!claim) {
      showMessage("claim-message", "Check your claim first.");
      return;
    }
    try {
      claim.certifyWaitingWeek();
      showMessage("claim-ok", "Waiting week certified. Payment: $0.");
    } catch (err) {
      showMessage("claim-message", "Blocked: " + err.message);
    }
    refreshClaim();
  });

  $("demo-btn").addEventListener("click", function () {
    $("claimant").value = "Demo Claimant";
    $("claim-date").value = "2026-11-02";
    updateQuarterLabels();
    var demoWages = [3200, 4100, 5200, 4800];
    for (var i = 0; i < 4; i++) {
      $("wage-" + (i + 1)).value = demoWages[i];
    }
    var c = checkClaim();
    if (!c) { return; }
    c.certifyWaitingWeek();
    c.certifyAndPay(1, 0);
    $("earn-2").value = "200";
    c.certifyAndPay(2, 200);
    c.certifyAndPay(3, 0);
    showMessage("claim-ok",
      "Demo case loaded. Total paid: " + moneyUI(c.totalPaid) +
      ". Balance left: " + moneyUI(c.balance) + ".");
    refreshClaim();
  });

  updateQuarterLabels();
})();
