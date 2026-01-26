# <img src="./custom_components/ventilation_advisor/icon.png" width="32" align="center" alt="Ventilation Advisor Icon"> Ventilation Advisor

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

Empowering you to balance **Health**, **Drying Speed**, and **Energy Efficiency** using real building physics.


---

**✨ Develop in the cloud:** Want to contribute or customize this integration? Open it directly in GitHub Codespaces - no local setup required!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Infraviored/ventialation_adviser?quickstart=1)

---

## 🌬️ Smart Ventilation Strategy

The integration uses three distinct metrics to give you a complete picture of your room's climate.

### 1. Mould Risk (The "Need")

**What is it?** A health score. It tells you if your room is in danger of growing mould.

* **Example:** At 75% RH, risk is **High**. You *need* to ventilate, even if it's cold outside.
* **Example:** At 45% RH, risk is **Zero**. You can relax.

<details>
<summary><b>🧪 Deep Dive: The Probability Curve</b></summary>

We map Indoor Relative Humidity (RH) to a risk probability based on biological growth standards (IEA).

* **Safe Zone (< 55% RH):** Risk is 0%.
* **Caution Zone (55% - 80% RH):** Risk climbs linearly. Spores accumulate but germination is slow.
* **Critical Zone (> 80% RH):** Risk is 100%. Mould germinates within days.

</details>

### 2. Drying Potential (The "Power")

**What is it?** The raw power of the outside air to remove water from your room.

* **Example:** Outside is cold and crisp. Power is **High**. A 3-minute "Stoßlüften" will dry the room instantly.
* **Example:** Outside is foggy/muggy. Power is **Negative**. Opening the window will actually make your walls wetter. "Hold!"

<details>
<summary><b>🧪 Deep Dive: The Magnus Formula</b></summary>

We use the **Magnus Formula** to calculate Absolute Humidity (water mass in $g/m^3$) because RH is misleading when temperatures differ.

$$ P_{sat} = 6.112 \times e^{\frac{17.67 \times T}{T + 243.5}} $$
$$ AH = \frac{216.7 \times (RH/100 \times P_{sat})}{273.15 + T} $$

**Drying Potential** = $AH_{indoor} - AH_{outdoor}$
</details>

### 3. Ventilation Efficiency (The "Cost")

**What is it?** The trade-off. How much water do you remove for every degree of heat you lose?

* **Example:** It's winter, but the air is super dry. You lose some heat, but remove a TON of water. **Efficiency: High**.
* **Example:** It's cool and damp outside. You lose heat, but barely remove any water. **Efficiency: Low (Wasteful)**.

<details>
<summary><b>🧪 Deep Dive: Enthalpy & Latent Heat</b></summary>

Ventilation isn't just about temperature loss ($\Delta T$). It's about Energy Loss (Enthalpy).
Humid air holds more energy (Latent Heat) than dry air.

**The Penalty:** If Indoor RH > 40%, we multiply the "Cost" by a penalty factor.
$$ \text{Effective Cost} = \Delta T \times (1 + (RH_{in} - 40) \times 0.005) $$
$$ \text{Efficiency Ratio} = \frac{\Delta AH}{\text{Effective Cost}} $$
</details>

---

## 🕹️ Strategy: Suggestion Frequency

Decide how often you want suggestions using the dropdown menu.

| Mode | Behavior |
| :--- | :--- |
| **Energy Saver** | Only alerts if **Mould Risk is Critical**. Saves every Joule of heat. |
| **Balanced (Eco)** | Prefers high efficiency, tolerates moderate risk. |
| **Balanced** | (Default) Standard balance of health and air quality. |
| **Fresh Air Lover** | Frequent suggestions. Will vent for fresh air even if drying is slow. |
| **Aggressive** | Maximum drying. Suggests ventilation whenever it's physically possible ($\Delta AH > 0$). |

---

## 🤖 Master Advice

The "Brain" optimizes for **Health > Physics > Comfort**.

1. **Safety Override**: If Mould Risk > 80% OR CO2 > 1500ppm (Critical) $\to$ **URGENT**.
2. **Physics Block**: If $\Delta AH$ is negative (Outside is wetter) $\to$ **HOLD**.
   * *Note: If CO2 > 1000ppm (Warning), we still recommend venting for fresh air.*
3. **Efficiency Gate**: If Safety is okay, only recommend if efficiency meets your **Suggestion Frequency** setting.

---

## 🛠️ Installation

### Method 1: HACS (Recommended)

**Prerequisites:** This integration requires [HACS](https://hacs.xyz/) (Home Assistant Community Store) to be installed.

Click the button below to open the integration directly in HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Infraviored&repository=ventialation_adviser&category=integration)

Alternatively, follow manual steps:
1. Ensure [HACS](https://hacs.xyz/) is installed.
2. Go to **HACS** → **Integrations**.
3. Click the three dots in the top right and select **Custom repositories**.
4. Add `https://github.com/Infraviored/ventialation_adviser` with category **Integration**.
5. Find **Ventilation Advisor** and click **Download**.
6. Restart Home Assistant.

### Method 2: Manual

1. Download the `custom_components/ventilation_advisor/` folder from this repository.
2. Copy it to your Home Assistant configuration directory under `custom_components/ventilation_advisor`.
3. Restart Home Assistant.

---

## ⚙️ Configuration

### Option 1: One-Click Setup (Quick)

Click the button below to open the setup dialog:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ventilation_advisor)

### Option 2: Manual Configuration

1. In Home Assistant, go to **Settings** → **Devices & Services**.
2. Click **+ Add Integration**.
3. Search for **Ventilation Advisor**.
4. Configure your outdoor sensors first, then add rooms as needed.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request if you have suggestions or improvements.

### 🛠️ Development Setup

The easiest way to get started is by developing directly in your browser with GitHub Codespaces:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Infraviored/ventialation_adviser?quickstart=1)

---


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [@Infraviored][user_profile]**

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/Infraviored/ventialation_adviser.svg?style=for-the-badge
[commits]: https://github.com/Infraviored/ventialation_adviser/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/Infraviored/ventialation_adviser.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40Infraviored-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/Infraviored/ventialation_adviser.svg?style=for-the-badge
[releases]: https://github.com/Infraviored/ventialation_adviser/releases
[user_profile]: https://github.com/Infraviored
