# CMMS and SAP PM data reality

The failure history that survival models need almost never exists as a
table. It has to be reconstructed from a CMMS, and in mining and heavy
industry that CMMS is usually SAP PM. This file records what the extract
actually contains and the reconstruction recipe. Source IDs resolve in
`sources.md`.

## The object model you will receive

SAP PM hangs records off a hierarchy: functional location (the slot in the
plant, e.g. "crusher 1 drive end") holds an equipment number (the physical
serial that currently occupies the slot). Notifications record that
something was observed; work orders record that work was planned and done.
Notification types (M1 maintenance request, M2 malfunction report, M3
activity report) and order types (PM01/PM02/PM03 and friends) are
site-configured conventions: one site's PM01 is corrective, another's is
preventive. Read the site's type mapping from the maintenance
superintendent before writing a single query; never assume the textbook
mapping.

Damage codes, cause codes, and object-part codes come from catalogue
profiles attached to the equipment class. Their population is optional at
most sites, and the code lists are often so long that technicians pick the
first plausible entry. A petrochemical case reported in trade press (S9)
raised failure-coding accuracy from 41% to 89% by cutting the code list
from 87 options to 22, which says the accuracy problem is form design as
much as technician effort.

## Date fields and which one to trust

| field | what it records | typical offset from the true failure instant |
|---|---|---|
| malfunction start (notification) | user-entered onset | best available when populated; often defaulted to creation time |
| notification created | when someone typed it in | hours to days late; clusters at shift end |
| order created | when planning acted | days late |
| order basic start / finish | the plan | scheduling fiction; unrelated to failure time |
| actual work confirmations | labour bookings | during repair, days after failure |
| TECO (technical completion) | administrative closure | days to weeks late |

Use malfunction start where present, sanity-checked against the equipment
<!-- allow:CAN hour-meter is the equipment device -->
hour-meter reading on the order; fall back to notification created; never
use TECO or basic dates as event times. Back-dating is endemic: orders get
raised in batches at shift end or week end, so plot the histogram of
creation hour and weekday before trusting any timestamp, and treat a spike
at 06:00/18:00 or on Mondays as batch entry. Getting the event time wrong
by days matters more in maintenance than elsewhere because the sensor
precursors you want as features live in exactly that window; a label placed
at order creation teaches the model to detect paperwork. This is the
maintenance-specific instance of target-timing leakage; the general
taxonomy lives in the feature-engineering skill.

## Reconstructing lifetimes with censoring

Survival analysis needs component service segments, and the recipe is:

1. Segment: for each functional location and component class, order the
   change-out work orders by (checked) date and cut service intervals from
<!-- allow:CAN hour meter is the equipment device -->
   installation to removal. Hour-meter readings beat calendar time for
   mobile equipment; watch for meter resets and rollovers, and rebuild a
   monotone counter per equipment before differencing.
2. Label each segment end: corrective order with damage evidence in codes
   or text means failure (delta = 1). Preventive change-out, component
   transferred to another asset, or still in service at the extract date
   all mean right-censored (delta = 0).
3. Audit a sample of 50 to 100 segments against the free text with a
   maintenance engineer. Labels from codes alone routinely misclassify
   preventive swaps as failures and vice versa.

The 40-character short text plus long text is where the truth lives, in
abbreviations and misspellings ("R&R fnl drv LH", "chgout u/s motor").
Hodkiewicz and Ho documented the cleaning pipeline this takes on real
mining work orders (S8), and LLM classification of failure modes from
work-order text now reaches accuracy usable for label audit when checked
against expert annotation (S10). Budget the cleaning as a first-class work
package: on real engagements it is one to three weeks, and it decides
whether anything downstream is real.

## Rarity, heterogeneity, and what they do to fits

Failure counts per component class are small: a 100-truck fleet with final
drives lasting years yields tens of failures in a decade of history, and
under 0.5% of asset-weeks contain a failure. Fits must pool the fleet, and
pooling brings heterogeneity: the same truck model works different ore
bodies, haul profiles, and operators. Pooling heterogeneous wear-out
populations biases the apparent Weibull shape toward 1 (the mixture spreads
the failure times), which reads as "random failures" and wrongly kills the
case for age-based replacement. Stratify by site and duty, or fit a frailty
or AFT model with those covariates, before concluding the hazard is flat.

## Label leakage after deployment

Once a model triggers inspections, the work orders it causes become
training labels: model-flagged trucks get inspected, inspections find and
fix incipient defects, and the "failure" the model predicted never occurs
or occurs as a cheap planned repair logged with a different code. Retraining
on this history rewards the model for its own interventions and punishes it
for its saves. Keep a permanent record of which work orders were
model-initiated, hold out a slice of the fleet from model-triggered
inspection where operationally defensible, and route retraining decisions
through the model-operations skill, which owns the intervention-feedback
problem in general form.
