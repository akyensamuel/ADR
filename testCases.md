# ADR Detection & Drug Interaction Test Suite

## Tier 1: Generic Names (Baseline Matching)

### High-Severity Cases

**Test Case 1: Opioid + Benzodiazepine**
- **Input:** "I experienced extreme drowsiness and shallow breathing after taking medicines containing hydrocodone and alprazolam."
- **Expected Output:** Severe CNS/Respiratory depression warning.

**Test Case 2: Serotonin Syndrome**
- **Input:** "I experienced severe muscle twitching, a high fever, and heavy sweating after taking medicines containing sertraline and tramadol."
- **Expected Output:** Serotonin Syndrome alert. Critical medical risk.

**Test Case 3: QT Prolongation / Arrhythmia**
- **Input:** "I experienced sudden fainting spells and severe heart palpitations after taking medicines containing azithromycin and amiodarone."
- **Expected Output:** Severe risk of QT interval prolongation.

### Moderate-to-High Severity Cases

**Test Case 4: Internal Bleeding Risk**
- **Input:** "I experienced dark, tarry stools and severe stomach pain after taking medicines containing warfarin and ibuprofen."
- **Expected Output:** Gastrointestinal bleeding warning.

**Test Case 5: Rhabdomyolysis (Muscle Breakdown)**
- **Input:** "I experienced intense muscle pain and dark, tea-colored urine after taking medicines containing simvastatin and clarithromycin."
- **Expected Output:** Statin toxicity / Rhabdomyolysis warning.

**Test Case 6: Severe Hyperkalemia**
- **Input:** "I experienced numbness in my fingers and an irregular heartbeat after taking medicines containing lisinopril and spironolactone."
- **Expected Output:** Hyperkalemia (high potassium) alert.

### Over-the-Counter (OTC) & Lifestyle Cases

**Test Case 7: Hypertensive Crisis**
- **Input:** "I experienced a pounding headache and dangerously high blood pressure after taking medicines containing phenylephrine and phenelzine."
- **Expected Output:** Hypertensive crisis risk.

**Test Case 8: Birth Control Failure**
- **Input:** "I experienced unexpected breakthrough bleeding after taking medicines containing oral contraceptives and St. John's wort."
- **Expected Output:** Reduced efficacy of hormonal birth control.

---

## Tier 2: Brand Names (Entity Mapping)

### High-Severity Cases

**Test Case 9: Opioid + Benzodiazepine**
- **Input:** "I experienced extreme drowsiness and shallow breathing after taking medicines containing Vicodin and Xanax."
- **Expected Output:** Resolve Vicodin → Hydrocodone, Xanax → Alprazolam. Severe CNS depression warning.

**Test Case 10: Serotonin Syndrome**
- **Input:** "I experienced severe muscle twitching, a high fever, and heavy sweating after taking medicines containing Zoloft and Ultram."
- **Expected Output:** Resolve Zoloft → Sertraline, Ultram → Tramadol. Serotonin Syndrome alert.

**Test Case 11: QT Prolongation / Arrhythmia**
- **Input:** "I experienced sudden fainting spells and severe heart palpitations after taking medicines containing Zithromax and Pacerone."
- **Expected Output:** Resolve Zithromax → Azithromycin, Pacerone → Amiodarone. QT prolongation alert.

### Moderate-to-High Severity Cases

**Test Case 12: Internal Bleeding Risk**
- **Input:** "I experienced dark, tarry stools and severe stomach pain after taking medicines containing Coumadin and Advil."
- **Expected Output:** Resolve Coumadin → Warfarin, Advil → Ibuprofen. GI bleeding warning.

**Test Case 13: Rhabdomyolysis**
- **Input:** "I experienced intense muscle pain and dark, tea-colored urine after taking medicines containing Zocor and Biaxin."
- **Expected Output:** Resolve Zocor → Simvastatin, Biaxin → Clarithromycin. Statin toxicity warning.

**Test Case 14: Severe Hyperkalemia**
- **Input:** "I experienced numbness in my fingers and an irregular heartbeat after taking medicines containing Prinivil and Aldactone."
- **Expected Output:** Resolve Prinivil → Lisinopril, Aldactone → Spironolactone. Hyperkalemia alert.

### Over-the-Counter (OTC) & Combination Cases

**Test Case 15: Hypertensive Crisis**
- **Input:** "I experienced a pounding headache and dangerously high blood pressure after taking medicines containing Sudafed PE and Nardil."
- **Expected Output:** Resolve Sudafed PE → Phenylephrine, Nardil → Phenelzine. Hypertensive crisis risk.

**Test Case 16: Birth Control Failure**
- **Input:** "I experienced unexpected breakthrough bleeding after taking medicines containing Yaz and Kira."
- **Expected Output:** Resolve Yaz → Drospirenone/Ethinyl Estradiol, Kira → St. John's Wort. Reduced contraceptive efficacy warning.

---

## Tier 3: Multi-Drug Interaction (Prioritization Logic)

**Test Case 17: Triple Threat (Serotonin Syndrome + Bleeding Risk)**
- **Input:** "I experienced a high fever, severe muscle twitching, and vomited what looked like coffee grounds after taking medicines containing Zoloft, Ultram, and Plavix."
- **Expected Output:** Extract 3 drugs. Prioritize Serotonin Syndrome (Zoloft+Ultram) as critical emergency, while secondary flags alert to GI bleeding risk (Plavix+Zoloft/Ultram).

**Test Case 18: The Multi-Sedative Crash**
- **Input:** "I experienced extreme dizziness, confusion, and my breathing became dangerously shallow after taking medicines containing Vicodin, Xanax, and Valium."
- **Expected Output:** Compound CNS depression alert. Flag therapeutic duplication of two benzodiazepines (Xanax + Valium).

**Test Case 19: Cardiac & Muscle Toxicity Overload**
- **Input:** "I experienced severe fainting spells, irregular heartbeats, and extreme muscle pain after taking medicines containing Zocor, Biaxin, and Cardizem."
- **Expected Output:** Dual High-Risk alerts: 1) QT prolongation (Biaxin+Cardizem causing fainting/palpitations), 2) Rhabdomyolysis muscle toxicity (Zocor toxicity compounded by both inhibitors).

**Test Case 20: The Potassium & Kidney Crisis**
- **Input:** "I experienced intense muscle numbness, nausea, and a pounding, irregular heart rate after taking medicines containing Prinivil, Aldactone, and Aleve."
- **Expected Output:** Severe Hyperkalemia warning due to triple-whammy effect on renal potassium excretion (ACEi + Potassium-sparing diuretic + NSAID).

---

## Tier 4: Typos and Misspellings (Fuzzy Matching Robustness)

**Test Case 21: Typo and Phonetic Slang**
- **Input:** "I experienced severe drowsiness and shallow breathing after taking medicines containing Vicodinn and Zanax."
- **Expected Output:** Map Vicodinn → Vicodin, Zanax → Xanax. Trigger CNS depression alert.

**Test Case 22: Truncated/Partial Names**
- **Input:** "I experienced severe muscle twitching and a high fever after taking medicines containing Zoloft and Ultra."
- **Expected Output:** Map Ultra → Ultram. Trigger Serotonin Syndrome alert.

**Test Case 23: QWERTY Keystroke Slip**
- **Input:** "I experienced dark, tarry stools and severe stomach pain after taking medicines containing Coumadii and Advul."
- **Expected Output:** Map Coumadii → Coumadin, Advul → Advil. Trigger GI bleeding warning.

**Test Case 24: Double Character Drop**
- **Input:** "I experienced intense muscle pain and tea colored urine after taking medicines containing Zocr and Biaxn."
- **Expected Output:** Map Zocr → Zocor, Biaxn → Biaxin. Trigger Rhabdomyolysis warning.

**Test Case 25: Messy Multi-Drug Typo**
- **Input:** "I experienced muscle numbness and an irregular heart rate after taking medicines containing Prinvil, Aldacton, and Aleve."
- **Expected Output:** Map Prinvil → Prinivil, Aldacton → Aldactone. Trigger Hyperkalemia warning.

---

## Tier 5: Adversarial Edge Cases (Negation & Timelines)

**Test Case 26: The Explicit Negation**
- **Input:** "I experienced severe anxiety, so I took my Xanax but I made sure to avoid my prescription of Vicodin today."
- **Expected Output:** No Interaction Alert. System must parse "avoid" to understand the drugs did not mix.

**Test Case 27: The Timeline Gap**
- **Input:** "I experienced a bad headache and took Advil, but that was over a week after I completely finished my course of Coumadin."
- **Expected Output:** No Interaction Alert (or low-risk history note). "A week after" implies no active metabolic overlap.

**Test Case 28: Hypothetical/Inquiry Context**
- **Input:** "If I were to experience muscle pain after taking Zocor, would it be safe to take Biaxin, or does that cause an interaction?"
- **Expected Output:** Educational Info Only. Do not trigger an active patient adverse alert; parse the conditional context.

**Test Case 29: False Entity Match (Lexical Red Herrings)**
- **Input:** "I experienced an upset stomach after drinking a glass of Ale and eating Vinegar chips, but I haven't taken any Aleve or Prinivil today."
- **Expected Output:** No Interaction Alert. Do not let "Ale" or "Vinegar" trigger fuzzy match false positives when explicitly negated by "haven't taken".

**Test Case 30: The "Switching" Scenario (Discontinuation Context)**
- **Input:** "My doctor had me stop taking Zoloft on Monday, and I started taking Ultram on Friday, but now I feel a bit sweaty."
- **Expected Output:** Low-to-Moderate Warning. Recognize they are not concurrent, but flag the "washout period" risk since 4 days is not long enough to safely clear an SSRI before starting a serotonergic opioid.