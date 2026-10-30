/*
 * rules.js — Faithful JavaScript port of the Python code in the repo.
 *
 * Ported from:
 *   app1_unemployment/wba.py         (CUIC section 1280 table + formula)
 *   app1_unemployment/base_period.py (standard / alternate base period)
 *   app1_unemployment/claim_flow.py  (waiting week, certify + pay, timeline)
 *   app2_parking/parking.py          (zones, fees, plate rules, office)
 *
 * Same public rules. No rules added. Demo only.
 * Works in the browser (attaches to window) and in Node (require()).
 */
(function (global) {
  "use strict";

  /* ------------------------------------------------------------------ */
  /* Money helpers                                                       */
  /* ------------------------------------------------------------------ */

  // Dollars -> cents, the way the task spec defines the port.
  function toCents(x) {
    return Math.round(Number(x) * 100);
  }

  // Python style: f"${x:.2f}" — dollar sign, two decimals, no commas.
  function formatMoney(x) {
    return "$" + Number(x).toFixed(2);
  }

  /* ------------------------------------------------------------------ */
  /* App 1 — Weekly Benefit Amount (wba.py, CUIC section 1280)           */
  /* ------------------------------------------------------------------ */

  var MIN_WBA = 40;
  var MAX_WBA = 450;
  var TABLE_TOP_CENTS = 183299; // $1,832.99 -> $70, last table bracket

  // Published step table: [low_cents_inclusive, high_cents_inclusive, wba]
  // Transcribed exactly from wba.py — all 31 brackets.
  var WBA_TABLE = [
    [90000, 94899, 40], [94900, 97499, 41], [97500, 100099, 42],
    [100100, 102699, 43], [102700, 105299, 44], [105300, 107899, 45],
    [107900, 111799, 46], [111800, 114399, 47], [114400, 116999, 48],
    [117000, 119599, 49], [119600, 122199, 50], [122200, 124799, 51],
    [124800, 128699, 52], [128700, 131299, 53], [131300, 133899, 54],
    [133900, 136499, 55], [136500, 140399, 56], [140400, 142999, 57],
    [143000, 145599, 58], [145600, 149499, 59], [149500, 152099, 60],
    [152100, 154699, 61], [154700, 158599, 62], [158600, 161199, 63],
    [161200, 163799, 64], [163800, 167699, 65], [167700, 170299, 66],
    [170300, 174199, 67], [174200, 176799, 68], [176800, 180699, 69],
    [180700, 183299, 70]
  ];

  function weeklyBenefitAmount(highestQuarterWages) {
    var cents = toCents(highestQuarterWages);
    if (cents < 0) {
      throw new Error("wages must not be negative");
    }
    if (cents < 90000) {
      return 0;
    }
    if (cents <= TABLE_TOP_CENTS) {
      for (var i = 0; i < WBA_TABLE.length; i++) {
        var low = WBA_TABLE[i][0], high = WBA_TABLE[i][1], wba = WBA_TABLE[i][2];
        if (low <= cents && cents <= high) {
          return wba;
        }
      }
      throw new Error("table gap"); // brackets are contiguous
    }
    // Above the table: ceil(highest quarter dollars / 26), clamped.
    var above = Math.ceil(cents / 100 / 26);
    return Math.max(MIN_WBA, Math.min(MAX_WBA, above));
  }

  function monetarilyQualifies(highestQuarterWages, totalBasePeriodWages) {
    var hq = Number(highestQuarterWages);
    var total = Number(totalBasePeriodWages);
    if (hq < 0 || total < 0) {
      throw new Error("wages must not be negative");
    }
    if (hq >= 1300) {
      return true; // Branch A
    }
    if (hq >= 900 && total >= 1.25 * hq) {
      return true; // Branch B
    }
    return false;
  }

  function maxBenefitAmount(wba) {
    return 26 * parseInt(wba, 10);
  }

  /* ------------------------------------------------------------------ */
  /* App 1 — Base period (base_period.py)                                */
  /* ------------------------------------------------------------------ */

  var QUARTER_START = { 1: [1, 1], 2: [4, 1], 3: [7, 1], 4: [10, 1] };
  var QUARTER_END = { 1: [3, 31], 2: [6, 30], 3: [9, 30], 4: [12, 31] };

  function pad2(n) {
    return (n < 10 ? "0" : "") + n;
  }
  function isoDate(year, month, day) {
    return year + "-" + pad2(month) + "-" + pad2(day);
  }

  function shiftQuarter(q, n) {
    var idx = q[0] * 4 + (q[1] - 1) + n;
    return [Math.floor(idx / 4), (idx % 4) + 1];
  }
  function fourEndingAt(end) {
    return [shiftQuarter(end, -3), shiftQuarter(end, -2),
            shiftQuarter(end, -1), end.slice()];
  }
  function periodFromQuarters(quarters) {
    var first = quarters[0], last = quarters[quarters.length - 1];
    var s = QUARTER_START[first[1]];
    var e = QUARTER_END[last[1]];
    return {
      quarters: quarters.map(function (q) { return q.slice(); }),
      start: isoDate(first[0], s[0], s[1]),
      end: isoDate(last[0], e[0], e[1])
    };
  }
  function claimYearMonth(claim) {
    if (claim && typeof claim === "object" && !Array.isArray(claim) &&
        !(claim instanceof Date)) {
      return [parseInt(claim.year, 10), parseInt(claim.month, 10)];
    }
    if (claim instanceof Date) {
      return [claim.getFullYear(), claim.getMonth() + 1];
    }
    if (Array.isArray(claim)) {
      return [parseInt(claim[0], 10), parseInt(claim[1], 10)];
    }
    throw new Error("claim must be {year, month}");
  }
  function checkMonth(month) {
    if (!(month >= 1 && month <= 12)) {
      throw new Error("month must be 1-12");
    }
  }

  function standardBasePeriod(claim) {
    var ym = claimYearMonth(claim), year = ym[0], month = ym[1];
    checkMonth(month);
    var end;
    if (month <= 3) { end = [year - 1, 3]; }
    else if (month <= 6) { end = [year - 1, 4]; }
    else if (month <= 9) { end = [year, 1]; }
    else { end = [year, 2]; }
    return periodFromQuarters(fourEndingAt(end));
  }

  function alternateBasePeriod(claim) {
    var ym = claimYearMonth(claim), year = ym[0], month = ym[1];
    checkMonth(month);
    var end;
    if (month <= 3) { end = [year - 1, 4]; }
    else if (month <= 6) { end = [year, 1]; }
    else if (month <= 9) { end = [year, 2]; }
    else { end = [year, 3]; }
    return periodFromQuarters(fourEndingAt(end));
  }

  function highestQuarter(wagesByQuarter) {
    var vals = Array.prototype.slice.call(wagesByQuarter || []);
    if (!vals.length) { return 0; }
    return Math.max.apply(null, vals.map(Number));
  }

  /* ------------------------------------------------------------------ */
  /* App 1 — Claim flow (claim_flow.py)                                  */
  /* ------------------------------------------------------------------ */

  var MAX_WEEKS = 26;

  // Money math in cents. The disregard can produce fractional cents
  // (25% of an odd-cent amount), exactly like Python's Decimal;
  // those fractions are kept, not rounded away.
  function partialEarningsDeduction(wba, earnings) {
    var e = Number(earnings);
    if (e < 0) {
      throw new Error("earnings must not be negative");
    }
    var earningsCents = toCents(e);
    var disregardCents = Math.max(2500, earningsCents * 0.25);
    var deductionCents = earningsCents - disregardCents;
    if (deductionCents < 0) { deductionCents = 0; }
    deductionCents = Math.min(deductionCents, Number(wba) * 100);
    return deductionCents / 100;
  }

  function weeklyPayment(wba, earnings) {
    if (earnings === undefined) { earnings = 0; }
    return Number(wba) - partialEarningsDeduction(wba, earnings);
  }

  function Claim(claimant, wba) {
    if (!(Number(wba) > 0)) {
      throw new Error("claim needs a positive WBA");
    }
    this.claimant = claimant;
    this.wba = parseInt(wba, 10);
    this._state = "Filed";
    this.waitingWeekCertified = false;
    this.waiting_week_certified = false;
    this._weeksPaid = 0;
    this._totalPaidCents = 0; // may carry fractional cents, like Decimal
    this.payments = {};       // week -> {week, amount, earnings}
    this.maxTotal = maxBenefitAmount(this.wba);
    this.max_total = this.maxTotal;
    this._timeline = [
      "Claim filed for " + this.claimant + ". Weekly benefit: $" + this.wba + ".",
      "Next: certify for the waiting week. It must be certified, " +
        "but it is not paid."
    ];
  }

  Object.defineProperties(Claim.prototype, {
    state: {
      get: function () { return this._state; }
    },
    timeline: {
      get: function () { return this._timeline.slice(); }
    },
    weeksPaid: {
      get: function () { return this._weeksPaid; }
    },
    weeks_paid: {
      get: function () { return this._weeksPaid; }
    },
    totalPaid: {
      get: function () { return this._totalPaidCents / 100; }
    },
    total_paid: {
      get: function () { return this._totalPaidCents / 100; }
    },
    balance: {
      get: function () {
        return (this.maxTotal * 100 - this._totalPaidCents) / 100;
      }
    }
  });

  Claim.prototype.certifyWaitingWeek = function () {
    if (this.waitingWeekCertified) {
      throw new Error("waiting week already certified");
    }
    if (this._state !== "Filed") {
      throw new Error("cannot serve waiting week from state " + this._state);
    }
    this._state = "WaitingWeek"; // Filed -> WaitingWeek
    this.waitingWeekCertified = true;
    this.waiting_week_certified = true;
    this.payments[0] = { week: 0, amount: 0, earnings: 0 };
    this._state = "Certified";   // WaitingWeek -> Certified
    this._timeline.push("Waiting week certified. Payment: $0 (unpaid week).");
    this._timeline.push("Next: certify every two weeks to keep payments going.");
    return 0;
  };
  // Python name, kept as an alias.
  Claim.prototype.certify_waiting_week = Claim.prototype.certifyWaitingWeek;

  Claim.prototype.certifyAndPay = function (week, earnings) {
    if (earnings === undefined) { earnings = 0; }
    if (!this.waitingWeekCertified) {
      throw new Error("waiting week must be certified before any paid week");
    }
    if (week < 1 || week > MAX_WEEKS) {
      throw new Error("week must be 1-" + MAX_WEEKS);
    }
    if (Object.prototype.hasOwnProperty.call(this.payments, week)) {
      // DoublePayBlocked in Python — paying the same week twice is blocked.
      var blocked = new Error("week " + week + " already paid — no second payment");
      blocked.name = "DoublePayBlocked";
      throw blocked;
    }
    if (this._weeksPaid >= MAX_WEEKS) {
      throw new Error("all 26 weeks used");
    }
    var amount = weeklyPayment(this.wba, earnings);
    // Balance cap: never pay past 26 x WBA in total.
    var remaining = (this.maxTotal * 100 - this._totalPaidCents) / 100;
    if (amount > remaining) { amount = remaining; }

    var payment = { week: week, amount: amount, earnings: Number(earnings) };
    this.payments[week] = payment;
    this._weeksPaid += 1;
    this._totalPaidCents += amount * 100;
    if (this._state !== "Paid") {
      this._state = "Paid"; // Certified -> Paid
    }
    var e = Number(earnings);
    if (e > 0) {
      this._timeline.push(
        "Week " + week + " certified. Earnings " + formatMoney(e) +
        " reported; payment: " + formatMoney(amount) + "."
      );
    } else {
      this._timeline.push(
        "Week " + week + " certified. Payment: " + formatMoney(amount) + "."
      );
    }
    if (this._weeksPaid >= MAX_WEEKS || this.totalPaid >= this.maxTotal) {
      this._timeline.push("Benefit year amount used up. Claim complete.");
    }
    return payment;
  };
  Claim.prototype.certify_and_pay = Claim.prototype.certifyAndPay;

  Claim.prototype.renderTimeline = function () {
    return this._timeline.map(function (line, i) {
      return (i + 1) + ". " + line;
    }).join("\n");
  };
  Claim.prototype.render_timeline = Claim.prototype.renderTimeline;

  /* ------------------------------------------------------------------ */
  /* App 2 — Parking permits (parking.py)                                */
  /* ------------------------------------------------------------------ */

  var RULES = {
    allowed_zones: ["North Lot", "Downtown", "Campus West"],
    allowedZones: ["North Lot", "Downtown", "Campus West"],
    fee_by_type: { resident: 30, visitor: 10, employee: 0 },
    feeByType: { resident: 30, visitor: 10, employee: 0 },
    exempt_types: ["employee"],
    exemptTypes: ["employee"],
    plate_min_length: 4,
    plate_max_length: 10,
    plateMinLength: 4,
    plateMaxLength: 10,
    plate_pattern: /^[A-Z0-9]+$/,
    one_active_per_plate_per_zone: true
  };

  var PARKING_STEPS = ["Applied", "Checked", "Approved", "Denied"];

  function cleanPlate(raw) {
    return String(raw || "").toUpperCase().replace(/[\s-]/g, "");
  }

  function permitTypeOf(app) {
    if (app.permit_type !== undefined) { return app.permit_type; }
    return app.permitType;
  }

  function PermitOffice() {
    this._nextNumber = 1;
    this._active = {};   // "plate|zone" -> application id
    this._payments = {}; // application id -> Payment
    this._results = {};  // application id -> PermitResult
  }

  Object.defineProperties(PermitOffice.prototype, {
    payments: {
      get: function () {
        var copy = {};
        for (var k in this._payments) {
          if (Object.prototype.hasOwnProperty.call(this._payments, k)) {
            copy[k] = this._payments[k];
          }
        }
        return copy;
      }
    },
    paymentsCount: {
      get: function () { return Object.keys(this._payments).length; }
    },
    results: {
      get: function () {
        var self = this;
        return Object.keys(this._results).map(function (k) {
          return self._results[k];
        });
      }
    }
  });

  PermitOffice.prototype.checkRules = function (app) {
    var reasons = [];
    var permitType = permitTypeOf(app);
    if (!String(app.driver || "").trim()) {
      reasons.push("No driver name on the form.");
    }
    if (!String(app.address || "").trim()) {
      reasons.push("No address on the form.");
    }
    if (RULES.allowed_zones.indexOf(app.zone) === -1) {
      reasons.push(
        "Address is not in an allowed zone. " +
        "Allowed zones: " + RULES.allowed_zones.join(", ") + "."
      );
    }
    if (!Object.prototype.hasOwnProperty.call(RULES.fee_by_type, permitType)) {
      reasons.push(
        "Permit type '" + permitType + "' is not known. " +
        "Types: " + Object.keys(RULES.fee_by_type).join(", ") + "."
      );
    }
    var plate = cleanPlate(app.plate);
    if (!(RULES.plate_min_length <= plate.length &&
          plate.length <= RULES.plate_max_length)) {
      reasons.push(
        "Plate must be " + RULES.plate_min_length + "-" +
        RULES.plate_max_length + " characters long."
      );
    } else if (!RULES.plate_pattern.test(plate)) {
      reasons.push("Plate may use letters and numbers only.");
    }
    if (RULES.one_active_per_plate_per_zone &&
        Object.prototype.hasOwnProperty.call(this._active, plate + "|" + app.zone)) {
      reasons.push("This car already has an active permit for this zone.");
    }
    return reasons;
  };
  PermitOffice.prototype.check_rules = PermitOffice.prototype.checkRules;

  PermitOffice.prototype.submit = function (app) {
    var appId = "APP-" + ("00" + this._nextNumber).slice(-3);
    // APP-001 … APP-999, then APP-1000 etc. (Python zero-pads to 3).
    if (this._nextNumber > 999) { appId = "APP-" + this._nextNumber; }
    this._nextNumber += 1;

    var permitType = permitTypeOf(app);
    var reasons = this.checkRules(app);
    var timeline = [
      "Applied: " + app.driver + " — " + permitType + " permit " +
      "for plate " + cleanPlate(app.plate) + " in " + app.zone + "."
    ];
    var result;

    if (reasons.length) {
      timeline.push("Checked: the rules say no.");
      reasons.forEach(function (reason) {
        timeline.push("Denied: " + reason);
      });
      timeline.push("Status: Denied. No money was taken.");
      result = {
        applicationId: appId,
        application_id: appId,
        status: "Denied",
        fee: 0,
        reasons: reasons.slice(),
        steps: ["Applied", "Checked", "Denied"],
        timeline: timeline.slice(),
        payment: null
      };
      this._results[appId] = result;
      return result;
    }

    var fee = RULES.fee_by_type[permitType];
    timeline.push("Checked: the rules say yes.");
    timeline.push("Approved: permit is approved. Fee is $" + fee + ".");
    this._active[cleanPlate(app.plate) + "|" + app.zone] = appId;
    result = {
      applicationId: appId,
      application_id: appId,
      status: "Approved",
      fee: fee,
      reasons: [],
      steps: ["Applied", "Checked", "Approved"],
      timeline: [],
      payment: null
    };
    this._results[appId] = result;

    // Step 4: money moves.
    if (fee === 0) {
      timeline.push("Money: $0 — exempt. No payment needed. Permit is free.");
      timeline.push("Status: Approved and active. You can park.");
    } else {
      this.pay(appId); // the demo's one payment step
      timeline.push("Money: driver paid $" + fee + " (demo payment, not a real charge).");
      timeline.push("Status: Approved, paid, and active. You can park.");
    }
    result.timeline = timeline.slice();
    return result;
  };

  // Pay once only. Idempotent: a second call returns the SAME payment.
  // Exempt ($0) applications return null — no payment is ever created.
  PermitOffice.prototype.pay = function (applicationId) {
    if (Object.prototype.hasOwnProperty.call(this._payments, applicationId)) {
      return this._payments[applicationId];
    }
    var result = this._results[applicationId];
    if (!result || result.status !== "Approved" || result.fee === 0) {
      return null;
    }
    var payment = {
      paymentId: "PAY-" + applicationId,
      payment_id: "PAY-" + applicationId,
      applicationId: applicationId,
      application_id: applicationId,
      amount: result.fee,
      kind: "demo-payment"
    };
    this._payments[applicationId] = payment;
    result.payment = payment;
    return payment;
  };

  PermitOffice.prototype.statusTimeline = function (applicationId) {
    var result = this._results[applicationId];
    return result ? result.timeline.slice()
                  : ["No application " + applicationId + "."];
  };
  PermitOffice.prototype.status_timeline = PermitOffice.prototype.statusTimeline;

  /* ------------------------------------------------------------------ */
  /* Exports                                                             */
  /* ------------------------------------------------------------------ */

  var api = {
    // shared
    formatMoney: formatMoney,
    // app 1
    MIN_WBA: MIN_WBA,
    MAX_WBA: MAX_WBA,
    MAX_WEEKS: MAX_WEEKS,
    WBA_TABLE: WBA_TABLE,
    weeklyBenefitAmount: weeklyBenefitAmount,
    weekly_benefit_amount: weeklyBenefitAmount,
    monetarilyQualifies: monetarilyQualifies,
    monetarily_qualifies: monetarilyQualifies,
    maxBenefitAmount: maxBenefitAmount,
    max_benefit_amount: maxBenefitAmount,
    standardBasePeriod: standardBasePeriod,
    standard_base_period: standardBasePeriod,
    alternateBasePeriod: alternateBasePeriod,
    alternate_base_period: alternateBasePeriod,
    highestQuarter: highestQuarter,
    highest_quarter: highestQuarter,
    partialEarningsDeduction: partialEarningsDeduction,
    partial_earnings_deduction: partialEarningsDeduction,
    weeklyPayment: weeklyPayment,
    weekly_payment: weeklyPayment,
    Claim: Claim,
    // app 2
    RULES: RULES,
    PARKING_STEPS: PARKING_STEPS,
    STEPS: PARKING_STEPS,
    cleanPlate: cleanPlate,
    clean_plate: cleanPlate,
    PermitOffice: PermitOffice
  };

  for (var key in api) {
    if (Object.prototype.hasOwnProperty.call(api, key)) {
      global[key] = api[key];
    }
  }
  global.SkeletonRules = api;

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window :
   (typeof globalThis !== "undefined" ? globalThis : this));
