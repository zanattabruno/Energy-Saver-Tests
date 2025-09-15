# Energy-Saver-Tests

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Energy--Saver--Tests-blue.svg)](https://github.com/zanattabruno/Energy-Saver-Tests)

Welcome to the **Energy-Saver-Tests** repository! This repository contains all the necessary scripts, Helm charts, Docker configurations, and resources required to deploy, manage, and test the Energy Saver application within a Kubernetes environment. The repository supports the experimental evaluations and results presented in the paper:

```bibtex
@ARTICLE{bruno2024energy,
  author={Bruno, Gustavo Z. and Almeida, Gabriel M. and da Silva, Aloízio P. and DaSilva, Luiz A. and Santos, Joao F. and Huff, Alexandre and Cardoso, Kleber V. and Both, Cristiano B.},
  journal={In submission process to IEEE Transactions on Network and Service Management},
  title={Towards Energy- and QoS-aware Load Balancing for 6G: Leveraging O-RAN to Achieve Sustainable and Energy-Efficient 6G},
  year={2024},
  volume={XX},
  number={Y},
  pages={1-1},
  keywords={6G, O-RAN, Network Management, Energy Efficiency, QoS, Load Balancing},
  doi={}
}
```

---

## Table of Contents

- [Introduction](#introduction)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Navigate to the Scripts Directory](#2-navigate-to-the-scripts-directory)
  - [3. Configure Environment](#3-configure-environment)
  - [4. Run the Deployment Script](#4-run-the-deployment-script)
- [Detailed Deployment Steps](#detailed-deployment-steps)
- [Usage](#usage)
  - [Accessing Services](#accessing-services)
  - [Monitoring and Logs](#monitoring-and-logs)
  - [Running Tests](#running-tests)
- [Results](#results)
  - [Example Results](#example-results)
  - [Key Results](#key-results)
  - [Handover Delay Scope](#handover-delay-scope)
- [Reproduction](#reproduction)
- [Limitations](#limitations)
- [Optimization and Solvers](#optimization-and-solvers)
- [Tested Environment](#tested-environment)
- [Citation](#citation)
- [Scripts Overview](#scripts-overview)
  - [Key Scripts](#key-scripts)
  - [Environment Management](#environment-management)
  - [Additional Resources](#additional-resources)
- [Related Repositories](#related-repositories)
- [Docker Configuration](#docker-configuration)
  - [CPLEX Docker Configuration](#cplex-docker-configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Introduction

The **Energy-Saver-Tests** repository streamlines deployment and testing of the Energy Saver application using Kubernetes and Helm. It automates the setup of O-RAN-aligned components and reproduces the experimental evaluations reported in our paper on adaptive, energy-efficient network management for B5G/6G. This repository includes the scripts, Helm charts, and result artifacts used to generate the figures and metrics discussed in the manuscript.

## Repository Structure

```
├── Dockerfiles
│   └── CPLEX
│       ├── build_container_image.sh
│       ├── cplex_studio2210.linux_x86_64.bin
│       ├── Dockerfile
│       └── installer.properties
├── Energy-Saver-Tests.code-workspace
├── helm-charts
│   ├── bouncer-xapp
│   │   ├── Chart.yaml
│   │   ├── config
│   │   ├── descriptors
│   │   ├── templates
│   │   └── values.yaml
│   ├── e2sim-helm
│   │   ├── Chart.yaml
│   │   ├── templates
│   │   └── values.yaml
│   ├── e2term
│   │   ├── charts
│   │   ├── Chart.yaml
│   │   ├── requirements.lock
│   │   ├── requirements.yaml
│   │   ├── resources
│   │   ├── templates
│   │   └── values.yaml
│   ├── energy-saver-rapp
│   │   ├── charts
│   │   ├── Chart.yaml
│   │   ├── templates
│   │   └── values.yaml
│   └── handover-xapp
│       ├── Chart.yaml
│       ├── config
│       ├── descriptors
│       ├── templates
│       └── values.yaml
├── LICENSE
├── README.md
├── results
│   ├── energy-results
│   │   ├── out
│   │   ├── Plot1.ipynb
│   │   ├── Plot2.ipynb
│   │   └── Plot3.ipynb
│   ├── net-time-detailed
│   │   ├── out
│   │   ├── Plot2.ipynb
│   │   ├── Plot3.ipynb
│   │   ├── Plot4.ipynb
│   │   ├── Plot5.ipynb
│   │   ├── Plot6.ipynb
│   │   ├── Plot7.ipynb
│   │   └── Plot.ipynb
│   ├── net-time-overral
│   │   ├── out
│   │   └── Plot.ipynb
│   ├── radar-results
│   │   ├── out
│   │   └── Plot.ipynb
│   ├── rApp-energy-saver
│   │   ├── out
│   │   ├── Plot2.ipynb
│   │   └── Plot.ipynb
│   ├── xApp-handover
│   │   ├── out
│   │   ├── Plot2.ipynb
│   │   └── Plot.ipynb
│   └── xApp-Monitoring
│       ├── out
│       └── Plot.ipynb
└── scripts
    ├── archive
    ├── deploy-e2term.py
    ├── deploy-energy-enviroment.sh
    ├── deploy-initial.py
    ├── deployment-map.json
    ├── deploy-use-case.sh
    ├── envmanager
    ├── file.pcap
    ├── handover_payload.json
    ├── handover.sh
    ├── O1-post.sh
    ├── policy_enode_ue
    ├── remove_opt.sh
    ├── restart_RIC.sh
    ├── scrape-output1.txt
    ├── scrape-output2.txt
    ├── scrape-output3.txt
    ├── scrape-output4.txt
    ├── scrape-time.sh
    └── trigger.sh
```

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Operating System**: Linux or macOS
- **Software**:
  - [Docker](https://docs.docker.com/get-docker/) installed and running
  - [Kubernetes](https://kubernetes.io/docs/tasks/tools/) cluster set up
  - [Helm](https://helm.sh/docs/intro/install/) installed
  - [Python 3](https://www.python.org/downloads/) installed
  - [kubectl](https://kubernetes.io/docs/tasks/tools/) installed and configured
  - **O-RAN Components**:
    - [Near-RT RIC](https://www.o-ran-sc.org/)
    - [Non-RT RIC](https://www.o-ran-sc.org/)
  - **Additional Services**:
    - [Stadium RF Simulator](https://github.com/alexandre-huff/stadium-rf-sim/tree/TNSM-25)
    - [VES Collector](https://github.com/zanattabruno/ves-collector)
    - [Apache Kafka](https://kafka.apache.org/)
    - [InfluxDB Collector](https://github.com/zanattabruno/influxdb-connector)
    - [InfluxDB](https://www.influxdata.com/)
- **Permissions**:
  - Sufficient permissions to deploy resources to the Kubernetes cluster
  - Access to Docker Hub or relevant container registries

## Installation

Follow these steps to get the Energy Saver application up and running.

### 1. Clone the Repository

```bash
git clone https://github.com/zanattabruno/Energy-Saver-Tests.git
cd Energy-Saver-Tests
```

### 2. Navigate to the Scripts Directory

All deployment scripts are located within the `scripts` directory.

```bash
cd scripts
```

### 3. Configure Environment

Before running the deployment script, ensure that all necessary configurations are set. This might involve editing Helm `values.yaml` files located in the `helm-charts` directory to match your environment-specific settings.

### 4. Run the Deployment Script

Execute the main deployment script to initiate the deployment process.

```bash
./deploy-energy-enviroment.sh
```

> **Note**: Ensure that you have execute permissions for the script. If not, you can add execute permissions using:

> ```bash
> chmod +x deploy-energy-enviroment.sh
> ```

## Detailed Deployment Steps

The `deploy-energy-enviroment.sh` script automates the following steps:

1. **Deploy E2Termination Component**:

   ```bash
   python3 deploy-e2term.py 
   ```

2. **Create Policy Types**:

   ```bash
   bash policy_enode_ue/create_policy_type.bash
   ```

3. **Deploy E2 Nodes**:

   Deploys four E2 nodes (`e2node1` to `e2node4`) using the `e2sim-helm` chart with specific configurations for each node.

   ```bash
   helm upgrade --install e2node1 ../helm-charts/e2sim-helm \
       --set image.args.e2term=10.43.0.225 \
       --set image.args.mcc=724 \
       --set image.args.mnc=011 \
       --set image.args.nodebid=1 \
       --set image.args.port=30001 \
       -n ricplt --wait

   helm upgrade --install e2node2 ../helm-charts/e2sim-helm \
       --set image.args.e2term=10.43.0.225 \
       --set image.args.mcc=724 \
       --set image.args.mnc=011 \
       --set image.args.nodebid=2 \
       --set image.args.port=30001 \
       -n ricplt --wait

   helm upgrade --install e2node3 ../helm-charts/e2sim-helm \
       --set image.args.e2term=10.43.0.225 \
       --set image.args.mcc=724 \
       --set image.args.mnc=011 \
       --set image.args.nodebid=3 \
       --set image.args.port=30001 \
       -n ricplt --wait

   helm upgrade --install e2node4 ../helm-charts/e2sim-helm \
       --set image.args.e2term=10.43.0.225 \
       --set image.args.mcc=724 \
       --set image.args.mnc=011 \
       --set image.args.nodebid=4 \
       --set image.args.port=30001 \
       -n ricplt --wait
   ```

4. **Deploy XApp Monitoring Instances**:

   Deploys four XApp Monitoring instances (`xappmonitoring1` to `xappmonitoring4`) using the `bouncer-xapp` chart with tailored settings.

   ```bash
   helm upgrade --install xappmonitoring1 ../helm-charts/bouncer-xapp \
       --set containers[0].image.name="zanattabruno/bouncer-rc" \
       --set containers[0].image.registry="registry.hub.docker.com" \
       --set containers[0].image.tag="TNSM-24" \
       --set containers[0].name="bouncer-xapp" \
       --set containers[0].command[0]="b_xapp_main" \
       --set containers[0].args[0]="--mcc" \
       --set containers[0].args[1]="724" \
       --set containers[0].args[2]="--mnc" \
       --set containers[0].args[3]="011" \
       --set containers[0].args[4]="--nodebid" \
       --set containers[0].args[5]="1" \
       -n ricxapp --wait

   helm upgrade --install xappmonitoring2 ../helm-charts/bouncer-xapp \
       --set containers[0].image.name="zanattabruno/bouncer-rc" \
       --set containers[0].image.registry="registry.hub.docker.com" \
       --set containers[0].image.tag="TNSM-24" \
       --set containers[0].name="bouncer-xapp" \
       --set containers[0].command[0]="b_xapp_main" \
       --set containers[0].args[0]="--mcc" \
       --set containers[0].args[1]="724" \
       --set containers[0].args[2]="--mnc" \
       --set containers[0].args[3]="011" \
       --set containers[0].args[4]="--nodebid" \
       --set containers[0].args[5]="2" \
       -n ricxapp --wait

   helm upgrade --install xappmonitoring3 ../helm-charts/bouncer-xapp \
       --set containers[0].image.name="zanattabruno/bouncer-rc" \
       --set containers[0].image.registry="registry.hub.docker.com" \
       --set containers[0].image.tag="TNSM-24" \
       --set containers[0].name="bouncer-xapp" \
       --set containers[0].command[0]="b_xapp_main" \
       --set containers[0].args[0]="--mcc" \
       --set containers[0].args[1]="724" \
       --set containers[0].args[2]="--mnc" \
       --set containers[0].args[3]="011" \
       --set containers[0].args[4]="--nodebid" \
       --set containers[0].args[5]="3" \
       -n ricxapp --wait

   helm upgrade --install xappmonitoring4 ../helm-charts/bouncer-xapp \
       --set containers[0].image.name="zanattabruno/bouncer-rc" \
       --set containers[0].image.registry="registry.hub.docker.com" \
       --set containers[0].image.tag="TNSM-24" \
       --set containers[0].name="bouncer-xapp" \
       --set containers[0].command[0]="b_xapp_main" \
       --set containers[0].args[0]="--mcc" \
       --set containers[0].args[1]="724" \
       --set containers[0].args[2]="--mnc" \
       --set containers[0].args[3]="011" \
       --set containers[0].args[4]="--nodebid" \
       --set containers[0].args[5]="4" \
       -n ricxapp --wait
   ```

5. **Deploy Handover XApp**:

   ```bash
   helm upgrade --install handover-xapp ../helm-charts/handover-xapp -n ricxapp --wait
   ```

6. **Apply Environment Manager Configuration**:

   ```bash
   kubectl apply -f envmanager -n ricplt
   ```

7. **Final Wait**:

   The script waits for 45 seconds to ensure all components are up and running.

   ```bash
   sleep 45
   ```

8. **Optional Deployment**:

   The script contains a commented-out line to deploy the `energy-saver-rapp`. Uncomment if needed.

   ```bash
   #helm upgrade --install energy-saver-rapp ../helm-charts/energy-saver-rapp -n ricrapp --wait
   ```

## Usage

After successful deployment, you can interact with the Energy Saver application and its components through Kubernetes and Helm commands. Refer to individual Helm chart `values.yaml` files for customization options.

### Accessing Services

- **XApp Monitoring**: Access via the services created in the `ricxapp` namespace.
- **Handover XApp**: Managed within the `ricxapp` namespace.
- **Environment Manager**: Configured in the `ricplt` namespace.

### Monitoring and Logs

Use `kubectl` to monitor pods and view logs:

```bash
kubectl get pods -n ricplt
kubectl logs <pod-name> -n ricplt
```

Replace `<pod-name>` with the name of the pod you wish to inspect.

### Running Tests

The repository includes various Jupyter notebooks (`.ipynb`) located in the `results` directory for analyzing deployment performance and results. To run these notebooks:

1. Ensure you have [Jupyter Notebook](https://jupyter.org/install) installed.
2. Navigate to the desired notebook directory.
3. Start Jupyter Notebook:

   ```bash
   jupyter notebook
   ```

4. Open and run the notebooks in your browser.

## Results

The `results` directory contains various outputs and analyses related to the deployment and performance of the Energy Saver application. This includes PDF reports, PNG images, and Jupyter notebooks (`.ipynb`) for detailed analyses.

### Example Results

- **Energy Analysis**:
  - `results/energy-results/out/energy-analysis.pdf`
  - `results/energy-results/out/energy-analysis.png`
- **Network Time Detailed**:
  - `results/net-time-detailed/out/detailed-times-side.pdf`
  - `results/net-time-detailed/out/detailed-times-stacked.png`
- **Radar Results**:
  - `results/radar-results/out/energy-radar.pdf`
- **RApp Energy Saver**:
  - `results/rApp-energy-saver/out/rApp-energy-saver.pdf`
- **XApp Handover & Monitoring**:
  - `results/xApp-handover/out/xApp-handover.pdf`
  - `results/xApp-Monitoring/out/xApp-Monitoring.pdf`

These results validate the effectiveness of the adaptive network management framework in optimizing energy efficiency within O-RAN architectures, as detailed in our research.

### Key Results

- Scenario: stadium with up to 56 cells (RUs) and up to 8,192 UEs.
- Energy savings over a 24-hour trace: 72.08% (≈65.44 kWh → ≈18.27 kWh).
- Active cells: off-peak 3–6 vs. ~35–37 at peak load.
- Handover delay: ≈0.123–0.204 s per UE across 256–8,192 UEs.
- Throughput: all UE throughput demands met across all experiments.

Note on energy accounting: the savings metric is first computed in a scale-free manner (from the EIRP trajectory); absolute site energy figures incorporate PA efficiency, BBU/control, and cooling overheads, yielding the 24-hour totals above.

### Handover Delay Scope

The handover delay reported here measures pure RAN handover signaling and execution—from Handover Preparation to Handover Complete and path switch on X2/Xn—plus associated UE procedures (e.g., UL synchronization/RACH and PDCP SN status transfer). It explicitly excludes any xApp/rApp decision or computation time.

## Reproduction

- Full monitoring pipeline (≤ 1,024 UEs): VESPA Manager → ONAP VES → Kafka → rApp. Expect the Monitoring stage to dominate the E2E loop (≈76–84%).
- Direct Prometheus collection (≥ 2,048 UEs): rApp scrapes Prometheus directly, bypassing VES/VESPA due to ONAP VES payload limits (~1 MB/event) and observed VESPA overhead (~672 s/iteration). In this regime, the loop is handover-bound.
- Configuration: for ≤ 1,024 UEs, deploy with VES/VESPA enabled; for ≥ 2,048 UEs, bypass VES/VESPA and have the rApp scrape Prometheus directly (see the rApp configuration/README). Ensure image tags (e.g., `TNSM-24`) and service IPs (e.g., `e2term`) match your cluster.
- Simulator: the stadium scenario is produced with [stadium-rf-sim](https://github.com/alexandre-huff/stadium-rf-sim/tree/TNSM-25), which generates UE distributions, radio metrics (e.g., RSRP/RSRQ/CQI/SINR/BLER), and handover events consumed by E2Sim and the xApps.

## Limitations

- Within each optimization–handover cycle, per-UE locations and per-UE throughput demands are static (no continuous mobility model). Between cycles, users may arrive/depart and cells may be (de)activated.
- Interference dynamics reflect static placements within a cycle (no motion-induced fluctuations).
- Cell on/off decisions are applied only after a feasibility check that guarantees every UE’s throughput demand via a Shannon-based throughput constraint.
- Reported QoS metrics focus on successful demand satisfaction and RAN handover execution delay. Not yet reported: packet-level latency/jitter, throughput percentiles (95/99th), outage probability, BLER, handover success/failure and ping-pong rates, radio link failures (RLF), or transients during simultaneous multi-UE migrations.
- The optimization objective currently has no explicit penalty for handover overheads or QoS risk.

## Optimization and Solvers

- The formulation including the Shannon-based throughput mapping is an MINLP (NP-hard) and does not scale to very large instances. CPLEX artifacts are provided for smaller benchmarking/validation.
- The large-scale results reported in the paper use a fast heuristic executed in the rApp (compute time ≤ ~5.8 s across 256–8,192 UEs), while xApp-side processing remains ≤ ~1.9 s.

## Tested Environment

The following versions were used in our experiments (replace with your exact versions if they differ):

- Kubernetes: vX.Y.Z
- Helm: vA.B.C
- Prometheus: vP.Q.R
- Kafka: vK.L.M
- ONAP VES: tag/commit …
- VESPA Manager: tag/commit …
- Docker images: use tag `TNSM-24` for bouncer-rc, e2sim-rc, etc.

## Citation

If you use this repository, please cite our paper:

```bibtex
@ARTICLE{bruno2024energy,
  author = {Bruno, Gustavo Z. and Almeida, Gabriel M. and da Silva, Aloízio P. and DaSilva, Luiz A. and Santos, Joao F. and Huff, Alexandre and Cardoso, Kleber V. and Both, Cristiano B.},
  journal = {In submission process to IEEE Transactions on Network and Service Management},
  title = {Towards Energy- and QoS-aware Load Balancing for 6G: Leveraging O-RAN to Achieve Sustainable and Energy-Efficient 6G},
  year = {2024},
  volume = {XX},
  number = {Y},
  pages = {1-1},
  keywords = {6G, O-RAN, Network Management, Energy Efficiency, QoS, Load Balancing},
  doi = {}
}
```

## Scripts Overview

The `scripts` directory contains various scripts to manage the deployment and operations of the Energy Saver application.

### Key Scripts

- **deploy-energy-enviroment.sh**: Main deployment script orchestrating the setup of all components.
- **deploy-e2term.py**: Python script for deploying the E2Termination component.
- **deploy-initial.py**: Initial deployment configurations.
- **deploy-use-case.sh**: Deploys specific use-case scenarios.
- **handover.sh**: Manages handover operations.
- **policy_enode_ue/create_policy_type.bash**: Script to create policy types.
- **restart_RIC.sh**: Restarts the RIC components.
- **trigger.sh**: Triggers specific deployment or test actions.

### Environment Management

Located in the `scripts/envmanager` directory, these scripts handle environment-specific configurations:

- **configmap.yaml**: ConfigMaps for environment variables.
- **deployment.yaml**: Deployment configurations.
- **service.yaml**: Service definitions.

### Additional Resources

- **archive/experiment.yaml**: Archived experiment configurations.
- **deployment-map.json**: Maps deployments for reference.
- **handover_payload.json**: Payload configurations for handover operations.
- **file.pcap**: Packet capture files for network analysis.
- **scrape-output*.txt**: Output files from scraping operations.
- **scrape-time.sh**: Script to scrape timing data.

## Related Repositories

This project utilizes several other repositories that contain components essential for the deployment and functioning of the Energy Saver application. Below is a list of these repositories along with brief descriptions:

- [**Energy-Saver-rApp**](https://github.com/zanattabruno/Energy-Saver-rApp/tree/TNSM-25): Repository for the **Energy Saver rApp**, which implements energy-efficient algorithms and interfaces with the RIC platform to optimize energy usage in 6G networks.

- [**Handover XApp**](https://github.com/alexandre-huff/handover-xapp/tree/TNSM-25): Contains the **Handover XApp**, responsible for managing the handover processes between network cells, ensuring seamless connectivity and quality of service.

- [**Monitoring XApp (Bouncer RC)**](https://github.com/alexandre-huff/bouncer-rc/tree/TNSM-25): The repository for the **Monitoring XApp**, also known as Bouncer RC. This component monitors network conditions and performance metrics, providing vital data for adaptive network management.

- [**E2 Simulator (E2Sim RC)**](https://github.com/alexandre-huff/e2sim-rc/tree/TNSM-25): Repository for the **E2 Node Simulator** used in the deployment, simulating the behavior of E2 Nodes in the network to test and validate xApps and rApps.

- [**RIC Platform VESPA Manager**](https://github.com/zanattabruno/ric-plt-vespamgr): An updated version of the **VESPA Manager** from the O-RAN Software Community. It manages the VES agents on the RIC platform, handling event streaming and processing.

- [**VES Collector**](https://github.com/zanattabruno/ves-collector): Repository for the **VES (Virtual Event Streaming) Collector**, which collects and processes event data from various network components, facilitating analytics and decision-making processes.

- [**InfluxDB Connector**](https://github.com/zanattabruno/influxdb-connector): The **InfluxDB Connector** interfaces with InfluxDB to store and retrieve time-series data for analysis, essential for monitoring network performance and energy consumption.

- [**E2Sim Environment Manager**](https://github.com/LABORA-INF-UFG/e2sim_environment_manager): Contains the **Environment Manager** for the E2 Simulator, handling environment-specific configurations and deployments to streamline simulation processes.

- [**Stadium RF Simulator**](https://github.com/alexandre-huff/stadium-rf-sim/tree/TNSM-25): Simulator used to emulate high-density stadium scenarios (UE distribution, radio metrics, and mobility events) for developing and testing the O-RAN closed-loop and energy-saving policies.

## Docker Configuration

The `Dockerfiles` directory contains Docker configurations for building container images required by the application.

### CPLEX Docker Configuration

Located in `Dockerfiles/CPLEX`, this includes:

- **Dockerfile**: Defines the Docker image for CPLEX.
- **build_container_image.sh**: Script to build the Docker image.
- **cplex_studio2210.linux_x86_64.bin**: CPLEX installer binary.
- **installer.properties**: Configuration properties for the CPLEX installer.

To build the CPLEX Docker image:

```bash
cd Dockerfiles/CPLEX
./build_container_image.sh
```

Ensure you have the necessary permissions and dependencies installed.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the Repository**: Click the "Fork" button at the top right of this page.
2. **Create a Branch**:

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Make Changes**: Implement your feature or bug fix.
4. **Commit Changes**:

   ```bash
   git commit -m "Add your message here"
   ```

5. **Push to Branch**:

   ```bash
   git push origin feature/YourFeatureName
   ```

6. **Open a Pull Request**: Navigate to the original repository and open a pull request.

Please ensure your contributions adhere to the repository's coding standards and include appropriate documentation and tests.

## License

This project is licensed under the [MIT License](LICENSE).
