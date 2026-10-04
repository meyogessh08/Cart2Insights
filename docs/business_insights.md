# Cart2Insights: Business Insights

Each finding follows: **Observation → Interpretation → Business Impact.**

---

## 1. Delivery delay is the strongest driver of customer dissatisfaction

**Observation:** On-time orders average 4.29★, delayed orders average 2.57★
(Welch's T-test, t=-89.41, p<0.000001). Mann-Whitney U confirms the same
result (p<0.000001), and the gap is visible directly in the delay-vs-review
correlation (-0.27).

**Interpretation:** Delivery performance has a larger, more statistically
certain effect on customer satisfaction than almost any other factor tested
in this analysis. The effect is not marginal — it's close to a 2-point swing
on a 5-point scale.

**Business Impact:** Delivery reliability should be treated as a
satisfaction lever, not just a logistics metric. Investing in carrier SLAs,
realistic estimated-delivery dates, or proactive delay notifications would
likely move review scores more than almost any product or pricing change.

---

## 2. Order value varies significantly by product category

**Observation:** One-Way ANOVA across the top 10 categories by volume:
F=310.3, p<0.000001 (raw), F=655.2, p<0.000001 (log-transformed to correct
for right-skew), and confirmed by Kruskal-Wallis (H=5522.6, p<0.000001) —
three independent methods agree. Average order value ranges from R$71.21
(telephony) to R$201.14 (watches_gifts) — nearly a 3x spread across the
top 10 categories by volume.

**Interpretation:** This isn't a borderline result sensitive to one test's
assumptions — it holds under the raw test, the normality-corrected version,
and a fully non-parametric alternative. Category genuinely drives order
value, and the spread is large enough to matter commercially, not just
statistically.

**Business Impact:** Watches_gifts, auto, and health_beauty sit at the
high-AOV end and warrant premium merchandising, bundling, or targeted ad
spend, since each sale carries more revenue. Telephony and furniture_decor
sit at the low-AOV end — growth there depends more on volume and
cross-sell than on per-order value, so strategies like "frequently bought
together" placements matter more for those categories than for watches_gifts.

---

## 3. Payment method is associated with order outcome

**Observation:** Chi-Square test of independence: χ²=209.99, dof=18,
p<0.000001. Converting the contingency table to problem-order rates
(canceled + unavailable, as a share of each payment type's total orders):
vouchers sit at 2.81%, boleto at 1.24%, credit card at 1.16%, and debit
card at 0.85%. 17.9% of expected cells fell below the common count-5
threshold — a minor caveat, noted rather than hidden, since the headline
pattern is large enough to not hinge on the borderline cells.

**Interpretation:** Voucher payments carry roughly 2.4x the problem-order
rate of credit card payments. This is a real, sizeable gap — not just
statistically detectable but practically meaningful.

**Business Impact:** Orders paid by voucher may warrant closer fulfillment
monitoring, or the voucher redemption flow itself may need review — this is
a concrete, prioritizable lead for operations, not just an abstract
"association" finding.

---

## 4. Repeat purchase rate is low — most customers buy once

**Observation:** Only 3.1% of customers (by `customer_unique_id`) placed
more than one order.

**Interpretation:** A low repeat rate is consistent with Olist's marketplace
structure — many independent sellers, varied catalogs, no strong reason for
a buyer to return to the same storefront. This is a structural pattern, not
a service failure, and it's a well-known characteristic of this dataset.

**Business Impact:** Growth here depends more on platform-level acquisition
and cross-seller loyalty programs than on any single seller's service
quality, since the platform — not individual sellers — controls most of the
repeat-purchase relationship. A 3.1% repeat rate also means customer
lifetime value is currently driven almost entirely by first-order size, not
retention — pricing and promotion strategy should reflect that.

---

## 5. Revenue grew steadily through the observed period, with a data artifact at the tail

**Observation:** Monthly revenue grew from near-zero in late 2016 to a peak
around late 2017/early 2018, holding roughly flat through mid-2018, before
a steep apparent drop in the final month.

**Interpretation:** The final-month drop is very likely incomplete data
coverage (the dataset's extraction cutoff falls mid-month), not a genuine
demand collapse — a one-month 80%+ revenue drop with no corresponding
operational event would be an extraordinary claim.

**Business Impact:** None directly — but this is an important analytical
caveat to state explicitly in any report or dashboard, so stakeholders don't
misread a data boundary as a business trend.

---

## 6. Delivery delay correlates with, but is distinct from, total delivery time

**Observation:** `delivery_days` and `delivery_delay_days` correlate at 0.6
— related but not redundant, since one measures absolute time and the other
measures lateness relative to the estimate.

**Interpretation:** A fast carrier can still be "late" if the estimate given
to the customer was too aggressive, and a slow carrier can still be "on
time" if the estimate was generous. The complaint driver is the promise
being broken, not raw speed.

**Business Impact:** Tightening the accuracy of estimated-delivery-date
calculations may improve satisfaction more cheaply than investing in faster
shipping — worth testing which lever has better ROI.