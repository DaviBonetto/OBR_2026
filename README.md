```text
  _______  _______  _______           _______  _______  _______   ______
 (  ___  )(  ____ \(  ____ )         (  __   )(  __   )(  __   ) / ____ \
 | (   ) || (    \/| (    )|         | (  )  || (  )  || (  )  |( (    \/
 | |   | || (__    | (____)|         | | /   || | /   || | /   || (____
 | |   | ||  __)   |     __)         | (/ /) || (/ /) || (/ /) ||  ___ \
 | |   | || (      | (\ (            |   / | ||   / | ||   / | || (   ) )
 | (___) || (____/\| ) \ \__         |  (__) ||  (__) ||  (__) |( (___) )
 (_______)(_______/|/   \__/         (_______)(_______)(_______) \_____/

   HIGH PERFORMANCE RESCUE ROBOT | OVERENGINEERING-SQUARED ARCHITECTURE
```

![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-00FFFF?style=for-the-badge)
![Raspberry Pi 5](https://img.shields.io/badge/Hardware-Raspberry%20Pi%205-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white)
![Coral Edge TPU](https://img.shields.io/badge/Accelerator-Coral%20Edge%20TPU-blue?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status: Development](https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge)

# 🚀 Visão Geral

Sistema autônomo de resgate projetado para a OBR 2026. Focado em **latência zero** e **robustez extrema**.

---

# 🧠 Arquitetura do Sistema (Fluxo de Dados)

```text
+---------------------+      +--------------------------+      +---------------------+
|  PERCEPÇÃO (Vision) |      |    DECISÃO (Logic)       |      |   ATUAÇÃO (Motion)  |
+---------------------+      +--------------------------+      +---------------------+
|                     |      |                          |      |                     |
|  [Câmera CSI/USB]   |      |   [Raspberry Pi 5]       |      |   [Arduino Nano]    |
|         |           |      |        (Master)          |      |      (Slave)        |
|         v           |      |           |              |      |         ^           |
|  [Coral Edge TPU]   |----->|    Processamento AI      |----->|    Controle PID     |
| (Inferência YOLOv8) | USB3 | (Multiprocessamento/SHM) | USB  | (Cinemática Robô)   |
|                     |      |           |              |      |         |           |
+---------------------+      +-----------+--------------+      +---------+-----------+
                                         |                               |
                                         v                               v
                                  [Logs & GUI]                    [Drivers L298N]
                                (Debug em Tempo Real)                    |
                                                                         v
                                                                  [Motores Pololu]
```

---

# ⚡ Sistema de Energia (Isolamento Elétrico)

O sistema utiliza **duas baterias independentes** para garantir que o ruído dos motores nunca trave o processador.

```text
       SISTEMA LÓGICO (LIMPO)                   SISTEMA DE POTÊNCIA (SUJO)
      ========================                 ============================

      [ Bateria LiPo 2S 7.4V ]                   [ Bateria LiPo 3S 11.1V ]
                 |                                           |
                 v                                           v
        [ UBEC 5V/3A Blindado ]                    [ Chave de Emergência ]
                 |                                           |
                 v                                           v
        ( Raspberry Pi 5 ) <--- OBRIGATÓRIO ------- [ Driver Ponte H ]
                 |              ISOLAMENTO                   |
                 |            OPTOACOPALDOR                  v
      +----------+----------+                        ( Motores Pololu )
      |          |          |                        ( Servos High Torque )
   [Coral]    [Câmera]   [Display]
```

---

# 🗺️ Roadmap & Checklist

### 🛠️ Hardware

- [x] **Chassi**: Híbrido Tanque/Omni (Design Finalizado)
- [x] **Sensores**: Matriz ToF Frontal + Ultrassom Lateral
- [ ] **Manipulador**: Garra de Resgate (Em montagem)

### 🧠 Software & AI

- [x] **Modelo**: YOLOv8n treinado para Vítimas e Silver Tape
- [x] **Performance**: 30+ FPS com Coral TPU
- [ ] **Navegação**: Algoritmo de desvio de obstáculos (Lidar/Ultrassom)

---

# 📥 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/DaviBonetto/OBR_2026.git

# 2. Instalação Automática (Raspberry Pi 5)
cd OBR-2026-Rescue-HighPerformance
chmod +x scripts/setup_pi.sh
./scripts/setup_pi.sh

# 3. Rodar
source venv/bin/activate
python src/Python/main/main.py
```
