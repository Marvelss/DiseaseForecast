<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

[//]: # (<img src="readmeai/assets/logos/purple.svg" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>)

## Multi-Scenario Crop Disease Forecasting Modeling System

<em></em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=default&logo=Streamlit&logoColor=white" alt="Streamlit">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/NumPy-013243.svg?style=default&logo=NumPy&logoColor=white" alt="NumPy">
<img src="https://img.shields.io/badge/pandas-150458.svg?style=default&logo=pandas&logoColor=white" alt="pandas">
<img src="https://img.shields.io/badge/GeoPandas-139C5A.svg?style=default&logo=GeoPandas&logoColor=white" alt="GeoPandas">
<img src="https://img.shields.io/badge/Folium-77B829.svg?style=default&logo=Folium&logoColor=white" alt="Folium">

</div>
<br>


---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## Overview
   Frequent outbreaks of crop diseases threaten global food security, yet user-friendly tools for developing data-driven forecasting models remain limited. We present an open-source multi-scenario crop disease forecasting modeling system that offers, for the first time, an end-to-end solution supporting four scenarios: static point-based, static grid-based, dynamic point-based, and dynamic grid-based. The system adopts a modular architecture with standardized interfaces to seamlessly integrate data ingestion, preprocessing, feature engineering, training, and evaluation, while providing parameter-tuning utilities and interactive visualization. A distinctive feature is the embedded weather scenario generator, which enables rigorous testing of model adaptability under extreme climatic conditions. Case studies demonstrate overall accuracies ranging from 73% to 93%. By lowering technical barriers, the system is designed to serve plant protection managers and agricultural producers without advanced programming expertise, providing a practical modeling tool that supports the construction of smart plant protection systems.


---

## Features

- Developed an open-source multi-scenario crop disease forecasting modeling system
- Compatible with multi-sources point-based and grid-based data
- Facilitate construction of static and dynamic disease forecasting models
- Provide comprehensive model evaluation under both actual and simulated weather scenarios
- Enable flexible customization and deployment of the forecasting models
---

## Project Structure

```sh
└── project
    └── app.py
    └── pages/
        ├── DataPreparation.py
        ├── DataPreparationFacet.py
        ├── DataSet.py
        ├── DataSetFacet.py
        ├── FeatureCalculation-en.py
        ├── FeatureCalculation.py
        ├── FeatureCalculationFacet.py
        ├── FeatureOptimization.py
        ├── FeatureOptimizationFacet.py
        ├── modelandmethod
        │   ├── FeatureCalculationMethod.py
        │   ├── FeatureOptimizationMethod.py
        │   ├── Model.py
        │   ├── PretreatmentMethod.py
        │   └── seir_parameter_search
        ├── ModelApplication.py
        ├── ModelApplicationFacet.py
        ├── ModelBuilding.py
        ├── ModelBuildingFacet.py
        ├── ModelEvaluation.py
        ├── ModelingReport.py
        ├── ModelingReportFacet.py
        ├── modelmethodfacet
        │   ├── FeatureCalculationMethodFacet.py
        │   ├── FeatureOptimizationFacet.py
        │   └── PretreatmentMethodFacet.py
        ├── pages_utils.py
        ├── ui.py
        ├── Visualization.py
        ├── VisualizationFacet.py
        ├── WeatherGenerator.py
        └── WeatherGeneratorFacet.py
```


---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python

### Installation

Build pages from the source and intsall dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone ../pages
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd pages
    ```

3. **Install the dependencies:**

echo 'pip install -r requirements.txt'

### Usage

Run the project with:

echo 'streamlit run ./myproject/app.py'



## Contributing

- **💬 [Join the Discussions](https://LOCAL/myproject/pages/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://LOCAL/myproject/pages/issues)**: Submit bugs found or log feature requests for the `pages` project.
- **💡 [Submit Pull Requests](https://LOCAL/myproject/pages/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.


---

## License

Copyright © 2023-2025 [Marvelss](https://github.com/Marvelss).
Protected under the [MIT](https://github.com/Marvelss/DiseaseForecast?tab=readme-ov-file#MIT-1-ov-file) License. 

---

</div>

[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square

