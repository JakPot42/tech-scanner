"""Pre-baked demo items for the Emerging Tech Horizon Scanner.

Covers all three sources (arXiv, patent, DARPA) with realistic defense-relevant
technology items. All assessments are pre-populated so demo runs without an API key.

Framing: institutions and technology trends only. No individual researcher profiling.
"""
from __future__ import annotations

DEMO_SEEDS = [
    # ── arXiv preprints ──────────────────────────────────────────────────────

    {
        "source":       "arxiv",
        "external_id":  "2501.09871",
        "title":        "Quantum Transduction of Microwave to Optical Photons for Distributed Quantum Sensing Networks",
        "abstract":     "We demonstrate coherent transduction of itinerant microwave photons to optical photons "
                        "at 4 kelvin using a piezo-optomechanical interface. Achieved transduction efficiency of "
                        "18% with noise photon number below 0.5, enabling quantum networking links relevant to "
                        "distributed sensing and secure communications in GPS-denied environments.",
        "url":          "https://arxiv.org/abs/2501.09871",
        "published_date": "2026-01-17",
        "raw_institutions": ["MIT CSAIL", "Stanford Ginzton Laboratory"],
        "tech_domain":  "Quantum Computing & Sensing",
        "novelty_score": 8,
        "dual_use_tier": "HIGH",
        "trl":          3,
        "trend_label":  "Microwave-optical quantum transduction for distributed sensing",
        "key_finding":  "Coherent quantum transduction at 4K with sub-0.5 noise photons could enable "
                        "entangled sensor networks resilient to RF jamming, with implications for "
                        "covert undersea and underground sensing applications.",
        "canonical_institutions": ["Massachusetts Institute of Technology", "Stanford University"],
    },
    {
        "source":       "arxiv",
        "external_id":  "2502.03412",
        "title":        "Adversarially Robust Object Detection for Unmanned Combat Aerial Vehicle Target Acquisition",
        "abstract":     "We present DefenseNet, a hardened object detection architecture achieving 94.2% mAP "
                        "under adaptive adversarial perturbations designed to fool standard YOLOv8 models. "
                        "The framework combines certified defenses with domain-randomized synthetic training "
                        "data from X-Plane simulations. Evaluated on aerial imagery datasets including "
                        "vehicle, aircraft, and maritime target classes.",
        "url":          "https://arxiv.org/abs/2502.03412",
        "published_date": "2026-02-05",
        "raw_institutions": ["Georgia Institute of Technology", "DARPA Information Innovation Office"],
        "tech_domain":  "AI/ML for Defense Applications",
        "novelty_score": 7,
        "dual_use_tier": "CRITICAL",
        "trl":          4,
        "trend_label":  "Certified adversarial robustness for autonomous target acquisition",
        "key_finding":  "Adversarially robust detection with certified bounds under adaptive attack "
                        "addresses a key vulnerability in AI-enabled weapon systems; the DARPA I2O "
                        "affiliation suggests this is on an active transition pathway.",
        "canonical_institutions": ["Georgia Institute of Technology", "DARPA"],
    },
    {
        "source":       "arxiv",
        "external_id":  "2502.11045",
        "title":        "Hypersonic Boundary Layer Transition at Mach 8 via Direct Numerical Simulation",
        "abstract":     "Direct numerical simulation of a flat-plate hypersonic boundary layer at Mach 8 and "
                        "Re_x=2.8e6 reveals a second-mode instability growth rate 40% higher than predicted "
                        "by linear stability theory at elevated wall temperatures. Results directly inform "
                        "thermal protection system design margins for boost-glide reentry vehicles.",
        "url":          "https://arxiv.org/abs/2502.11045",
        "published_date": "2026-02-12",
        "raw_institutions": ["California Institute of Technology", "NASA Ames Research Center"],
        "tech_domain":  "Hypersonics & Advanced Propulsion",
        "novelty_score": 7,
        "dual_use_tier": "HIGH",
        "trl":          3,
        "trend_label":  "High-fidelity boundary layer transition modeling for boost-glide vehicles",
        "key_finding":  "A 40% discrepancy in second-mode growth rates versus linear stability theory "
                        "means current thermal protection margins for hypersonic glide vehicles may be "
                        "systematically under-designed; result has direct implications for HGV survivability.",
        "canonical_institutions": ["California Institute of Technology", "NASA"],
    },
    {
        "source":       "arxiv",
        "external_id":  "2503.00287",
        "title":        "Gallium Nitride Monolithic Microwave Integrated Circuit for High-Power Phased Array Radar",
        "abstract":     "We report a 50W GaN MMIC power amplifier operating from 9–12 GHz with 18 dB gain "
                        "and 52% PAE fabricated on a 100mm process node. The design targets X-band active "
                        "electronically scanned array (AESA) radar for surveillance and fire-control "
                        "applications. Thermal analysis confirms sustained operation at 200°C junction temperature.",
        "url":          "https://arxiv.org/abs/2503.00287",
        "published_date": "2026-03-02",
        "raw_institutions": ["Raytheon Technologies Research Center"],
        "tech_domain":  "Microelectronics & Semiconductors",
        "novelty_score": 6,
        "dual_use_tier": "HIGH",
        "trl":          5,
        "trend_label":  "High-power GaN MMIC for AESA fire-control radar",
        "key_finding":  "A 52% PAE GaN MMIC at TRL 5 from a prime contractor signals near-term "
                        "AESA radar power density improvements; performance at 200°C sustains "
                        "desert and high-altitude operational environments.",
        "canonical_institutions": ["Raytheon Technologies"],
    },
    {
        "source":       "arxiv",
        "external_id":  "2503.08864",
        "title":        "Cognitive Electronic Warfare: Adaptive Jamming via Deep Reinforcement Learning Against Agile Radar Waveforms",
        "abstract":     "We present a deep reinforcement learning framework for real-time adaptive jamming "
                        "policy generation against radar waveforms with agile frequency hopping patterns. "
                        "The agent achieves 89% jamming effectiveness against an adversary employing "
                        "cognitive radar with 1024 frequency bins and sub-microsecond hop rates, operating "
                        "within a 100ms reaction loop on an embedded GPU.",
        "url":          "https://arxiv.org/abs/2503.08864",
        "published_date": "2026-03-09",
        "raw_institutions": ["MIT Lincoln Laboratory", "Air Force Research Laboratory"],
        "tech_domain":  "Cyber & Electronic Warfare",
        "novelty_score": 8,
        "dual_use_tier": "CRITICAL",
        "trl":          4,
        "trend_label":  "RL-driven cognitive jamming against agile radar at embedded latency",
        "key_finding":  "Achieving 89% jamming effectiveness at sub-100ms loop latency on embedded "
                        "hardware represents a significant step toward autonomous EW pods capable "
                        "of defeating next-generation cognitive radar with no human-in-the-loop.",
        "canonical_institutions": ["Massachusetts Institute of Technology", "Air Force Research Laboratory"],
    },

    # ── USPTO patents ────────────────────────────────────────────────────────

    {
        "source":       "patent",
        "external_id":  "11928743",
        "title":        "Autonomous Swarm Coordination System for UAV Operations in GPS-Denied Environments",
        "abstract":     "A distributed multi-agent coordination architecture enabling cohesive swarm "
                        "behavior in unmanned aerial vehicles operating without GPS or external communications. "
                        "Uses onboard inertial-relative positioning, local mesh radio with cryptographic "
                        "authentication, and emergent task allocation via stigmergic signaling. Validated "
                        "in simulation with 64-agent swarms achieving 96% mission completion under "
                        "30% node attrition.",
        "url":          "https://patents.google.com/patent/US11928743",
        "published_date": "2026-01-21",
        "raw_institutions": ["Northrop Grumman Systems Corporation"],
        "tech_domain":  "Autonomous Systems & Robotics",
        "novelty_score": 8,
        "dual_use_tier": "CRITICAL",
        "trl":          6,
        "trend_label":  "GPS-denied swarm coordination for contested-environment UAV missions",
        "key_finding":  "A patented TRL-6 swarm architecture resilient to 30% node attrition and "
                        "GPS denial from a major prime contractor indicates this capability is "
                        "approaching field demonstration; the cryptographic mesh suggests "
                        "anti-jam/anti-spoofing hardening for peer-conflict scenarios.",
        "canonical_institutions": ["Northrop Grumman"],
    },
    {
        "source":       "patent",
        "external_id":  "11892311",
        "title":        "High-Energy Laser Beam Director with Adaptive Optics for Counter-UAS Applications",
        "abstract":     "A directed energy weapon system comprising a high-energy laser with megawatt-class "
                        "beam director, deformable mirror adaptive optics correcting atmospheric turbulence "
                        "at 5 kHz, and a target acquisition and tracking suite achieving sub-microradian "
                        "pointing stability. Configured for engagement of small unmanned aerial systems "
                        "at ranges up to 5 km under maritime boundary layer conditions.",
        "url":          "https://patents.google.com/patent/US11892311",
        "published_date": "2026-01-14",
        "raw_institutions": ["Lockheed Martin Corporation"],
        "tech_domain":  "Directed Energy Weapons",
        "novelty_score": 7,
        "dual_use_tier": "CRITICAL",
        "trl":          7,
        "trend_label":  "Megawatt-class HEL with adaptive optics for maritime counter-UAS",
        "key_finding":  "TRL-7 adaptive optics achieving sub-microradian stability under maritime "
                        "turbulence closes a long-standing atmospheric compensation gap; "
                        "5 km counter-UAS range makes this operationally relevant for ship defense.",
        "canonical_institutions": ["Lockheed Martin"],
    },
    {
        "source":       "patent",
        "external_id":  "11874052",
        "title":        "Quantum-Enhanced Radar Using Entangled Microwave Photon Pairs for Low-Observable Target Detection",
        "abstract":     "A quantum illumination radar system transmitting entangled microwave photon pairs "
                        "achieves 6 dB signal-to-noise improvement over classical radar at equivalent "
                        "transmit power against targets with radar cross-section below 0.01 m^2. The "
                        "receiver uses joint quantum measurement to exploit entanglement-breaking signatures "
                        "of background clutter. Patent covers transmitter, receiver, and quantum memory "
                        "hold time of 100 microseconds.",
        "url":          "https://patents.google.com/patent/US11874052",
        "published_date": "2026-01-07",
        "raw_institutions": ["MIT Lincoln Laboratory", "DARPA Microsystems Technology Office"],
        "tech_domain":  "Quantum Computing & Sensing",
        "novelty_score": 9,
        "dual_use_tier": "HIGH",
        "trl":          3,
        "trend_label":  "Quantum illumination radar with 6 dB SNR advantage over stealth targets",
        "key_finding":  "A patented quantum illumination system achieving 6 dB SNR gain against "
                        "sub-0.01 m² RCS targets could fundamentally undermine stealth aircraft "
                        "and missile effectiveness; DARPA MTO involvement signals active transition intent.",
        "canonical_institutions": ["Massachusetts Institute of Technology", "DARPA"],
    },
    {
        "source":       "patent",
        "external_id":  "11863987",
        "title":        "Combined Cycle Scramjet-Turbine Propulsion System for Mach 5-12 Cruise Missiles",
        "abstract":     "A propulsion system architecture transitioning from turbine mode at takeoff "
                        "through turbo-ramjet transition to scramjet mode above Mach 5. Addresses "
                        "the inlet-isolator thermal management challenge using actively cooled silicon "
                        "carbide composite structures. Demonstrated in subscale testing to Mach 6.2 "
                        "in a direct-connect facility.",
        "url":          "https://patents.google.com/patent/US11863987",
        "published_date": "2025-12-31",
        "raw_institutions": ["Aerojet Rocketdyne Holdings Inc"],
        "tech_domain":  "Hypersonics & Advanced Propulsion",
        "novelty_score": 8,
        "dual_use_tier": "CRITICAL",
        "trl":          5,
        "trend_label":  "Combined-cycle scramjet enabling Mach 5-12 sustained cruise for missiles",
        "key_finding":  "A patented combined-cycle architecture tested to Mach 6.2 in direct-connect "
                        "removes the critical propulsion gap between takeoff and hypersonic cruise, "
                        "enabling long-range hypersonic cruise missiles with conventional strike roles.",
        "canonical_institutions": ["Aerojet Rocketdyne"],
    },
    {
        "source":       "patent",
        "external_id":  "11849201",
        "title":        "Neuromorphic Processor Architecture for Real-Time Electronic Intelligence Signal Classification",
        "abstract":     "A neuromorphic processing unit implementing spiking neural networks on-chip for "
                        "real-time classification of electromagnetic emission signatures. Achieves 98.3% "
                        "classification accuracy across 512 signal types at 40 Gbps throughput with "
                        "60x lower power consumption versus GPU-based solutions. Designed for "
                        "airborne ELINT pod applications.",
        "url":          "https://patents.google.com/patent/US11849201",
        "published_date": "2025-12-24",
        "raw_institutions": ["Johns Hopkins University Applied Physics Laboratory", "DARPA Microsystems Technology Office"],
        "tech_domain":  "Microelectronics & Semiconductors",
        "novelty_score": 8,
        "dual_use_tier": "HIGH",
        "trl":          5,
        "trend_label":  "Low-SWaP neuromorphic ELINT classification at 40 Gbps",
        "key_finding":  "60x power reduction over GPU alternatives at 98.3% accuracy enables "
                        "neuromorphic ELINT on constrained airborne platforms; this closes a "
                        "critical SWaP gap for UAV-mounted electronic intelligence collection.",
        "canonical_institutions": ["Johns Hopkins University", "DARPA"],
    },

    # ── DARPA solicitations ──────────────────────────────────────────────────

    {
        "source":       "darpa",
        "external_id":  "BAA-DARPA-I2O-26-001",
        "title":        "AI-Enabled Multi-Domain Command and Control (AI-MDC2) — Broad Agency Announcement",
        "abstract":     "DARPA Information Innovation Office (I2O) seeks research in AI-enabled multi-domain "
                        "command and control systems capable of synthesizing data from space, air, land, sea, "
                        "and cyberspace at machine speed. Topics include human-machine teaming architectures, "
                        "explainable AI for operational decision support, and adversarial robustness in "
                        "contested communication environments. Maximum award $8M per awardee over 36 months.",
        "url":          "https://sam.gov/opp/BAA-DARPA-I2O-26-001",
        "published_date": "2026-02-01",
        "raw_institutions": ["DARPA"],
        "tech_domain":  "AI/ML for Defense Applications",
        "novelty_score": 7,
        "dual_use_tier": "CRITICAL",
        "trl":          3,
        "trend_label":  "AI-enabled multi-domain command and control at machine speed",
        "key_finding":  "DARPA I2O is funding the full stack from sensor fusion to decision support "
                        "under contested comms conditions — this represents a direct pathway for "
                        "AI to enter lethal force decision chains at machine timescales.",
        "canonical_institutions": ["DARPA"],
    },
    {
        "source":       "darpa",
        "external_id":  "BAA-DARPA-DSO-26-002",
        "title":        "Advanced Thermal Protection Materials for Mach 10+ Reentry Vehicles — BAA",
        "abstract":     "DARPA Defense Sciences Office solicits proposals for ultra-high-temperature "
                        "ceramic composite materials capable of sustained exposure at 2200°C with "
                        "thermal shock resistance. Research focus: hafnium boride and zirconium "
                        "carbide compositions, oxidation-resistant coatings, and additive manufacturing "
                        "of complex geometries. Target TRL 4 deliverable in 24 months.",
        "url":          "https://sam.gov/opp/BAA-DARPA-DSO-26-002",
        "published_date": "2026-02-15",
        "raw_institutions": ["DARPA"],
        "tech_domain":  "Advanced Materials & Manufacturing",
        "novelty_score": 7,
        "dual_use_tier": "HIGH",
        "trl":          2,
        "trend_label":  "Ultra-high-temp ceramics for Mach 10+ reentry survivability",
        "key_finding":  "Soliciting HfB2/ZrC compositions with AM fabrication reflects a "
                        "gap in existing TPS materials for hypersonic reentry; additive manufacturing "
                        "of complex geometries is the key enabling step for conformal heat shields.",
        "canonical_institutions": ["DARPA"],
    },
    {
        "source":       "darpa",
        "external_id":  "BAA-DARPA-I2O-26-003",
        "title":        "Quantum Networking for Resilient Military Communications (QuaNReC) — BAA",
        "abstract":     "DARPA I2O announces a new program to develop quantum networking infrastructure "
                        "for resilient, eavesdropping-resistant military communications. Research topics "
                        "include quantum key distribution over fiber and free-space, quantum repeater "
                        "development, and entanglement distribution protocols for tactical networks. "
                        "Coordination with NSA quantum-resistant cryptography standards required.",
        "url":          "https://sam.gov/opp/BAA-DARPA-I2O-26-003",
        "published_date": "2026-03-01",
        "raw_institutions": ["DARPA"],
        "tech_domain":  "Quantum Computing & Sensing",
        "novelty_score": 8,
        "dual_use_tier": "HIGH",
        "trl":          3,
        "trend_label":  "Quantum networking for tamper-evident tactical military communications",
        "key_finding":  "DARPA funding quantum repeaters and free-space QKD in coordination with "
                        "NSA signals a push to integrate quantum cryptography into operational "
                        "military networks; the NSA coordination requirement is notable given "
                        "concurrent post-quantum classical cryptography standardization.",
        "canonical_institutions": ["DARPA"],
    },
    {
        "source":       "darpa",
        "external_id":  "BAA-DARPA-BTO-26-004",
        "title":        "Programmable Biological Sensors for Chemical and Biological Threat Detection — BAA",
        "abstract":     "DARPA Biological Technologies Office (BTO) solicits proposals for engineered "
                        "biological systems capable of detecting chemical and biological threat agents "
                        "at sub-nanomolar concentrations in field conditions. Research areas include "
                        "cell-free biosensor platforms, CRISPR-based nucleic acid detection, and "
                        "synthetic biology sensor-reporter circuits. All research subject to DURC "
                        "policy review.",
        "url":          "https://sam.gov/opp/BAA-DARPA-BTO-26-004",
        "published_date": "2026-03-10",
        "raw_institutions": ["DARPA"],
        "tech_domain":  "Biotechnology & Synthetic Biology",
        "novelty_score": 8,
        "dual_use_tier": "CRITICAL",
        "trl":          2,
        "trend_label":  "CRISPR-based field biosensors for sub-nanomolar chem-bio detection",
        "key_finding":  "CRISPR-based nucleic acid detection at sub-nanomolar sensitivity in "
                        "field conditions could enable early warning of biological agent release "
                        "with 10-100x faster turnaround than current assays; the explicit DURC "
                        "review requirement flags meaningful dual-use risk in the enabling biology.",
        "canonical_institutions": ["DARPA"],
    },
]
