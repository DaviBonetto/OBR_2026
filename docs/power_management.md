# Gerenciamento de Energia e Isolamento Elétrico

## Visão Geral

O sistema elétrico do robô utiliza uma arquitetura de **Dupla Bateria Isolada** para garantir estabilidade crítica no processamento (Raspberry Pi/Coral) independente das flutuações de alta corrente dos motores.

## Arquitetura de Potência

### 🟢 Circuito Lógico ("Clean Power")

Este circuito alimenta os componentes sensíveis que requerem tensão estável e livre de ruídos elétricos.

- **Fonte**: Bateria LiPo 2S (7.4V)
- **Regulação**: UBEC 5V/3A de alta eficiência
- **Cargas**:
  - Raspberry Pi 5 (Via GPIO 5V)
  - Coral USB Accelerator (Via USB 3.0 do Pi)
  - Câmeras e Sensores Lógicos
- **Benefício**: Previne "Brownouts" (queda de tensão) no Raspberry Pi quando os motores travam ou aceleram bruscamente.

### 🔴 Circuito de Potência ("Dirty Power")

Este circuito lida com as altas correntes indutivas dos motores.

- **Fonte**: Bateria LiPo 3S (11.1V, Alta Descarga)
- **Isolamento**: Optoacopladores no Driver de Motor
- **Cargas**:
  - Driver de Motor (L298N / TB6612FNG)
  - 4x Motores Pololu High Power
  - Servos de Alta Potência
- **Segurança**: Chave de emergência física dedicada para corte rápido dos motores.

## Diagrama de Distribuição

```mermaid
graph TD
    subgraph Power_Clean [⚡ Circuito Lógico (Estável)]
        Bat1[Bateria Lipo 2S 7.4V] --> UBEC[Regulador UBEC 5V/3A]
        UBEC --> RPI[Raspberry Pi 5]
        RPI --> Coral[Coral EdgeTPU]
        RPI --> Cam[Câmeras USB/CSI]
    end

    subgraph Power_Dirty [🔥 Circuito de Potência (Alto Ruído)]
        Bat2[Bateria Lipo 3S 11.1V] --> Switch[Chave de Emergência]
        Switch --> Driver[Driver de Motor]
        Driver --> M1[Motor FL]
        Driver --> M2[Motor FR]
        Driver --> M3[Motor BL]
        Driver --> M4[Motor BR]
    end

    RPI -- Sinais de Controle (Opto-isolados) --> Driver
```
