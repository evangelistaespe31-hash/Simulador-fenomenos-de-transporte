import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="Simulador de Fenómenos de Transporte",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Simulador de Fenómenos de Transporte")
st.markdown("### Plataforma Educativa e Interactiva para Ingeniería Química")

# Pestañas principales
tab1, tab2, tab3 = st.tabs([
    "🌊 1. Cantidad de Movimiento",
    "🔥 2. Energía (Calor)",
    "🧪 3. Materia (Masa)"
])

# Base de datos de Preajustes de Fluidos
FLUID_PRESETS = {
    "Personalizado": None,
    "Agua (20°C) - 0.001 Pa·s": 0.001,
    "Aceite de Motor (SAE 30) - 0.290 Pa·s": 0.290,
    "Glicerina Pura - 1.410 Pa·s": 1.410,
    "Miel de Abeja - 10.000 Pa·s": 10.000
}

# Base de datos de Preajustes de Masa
MASS_PRESETS = {
    "Personalizado": None,
    "Acetona en Aire (25°C) - 1.10e-5 m²/s": (1.10e-5, 0.85, 0.02),
    "Vapor de Agua en Aire (25°C) - 2.50e-5 m²/s": (2.50e-5, 0.70, 0.05),
    "Etanol en Aire (25°C) - 1.32e-5 m²/s": (1.32e-5, 0.60, 0.01),
    "CO2 en Aire (25°C) - 1.60e-5 m²/s": (1.60e-5, 0.90, 0.10)
}

# ==========================================
# 1. MÓDULO DE CANTIDAD DE MOVIMIENTO
# ==========================================
with tab1:
    st.header("🌊 Transporte de Cantidad de Movimiento (Ley de Newton)")
    
    col_ctrl, col_chart = st.columns([1, 2])
    
    with col_ctrl:
        st.subheader("Parámetros del Sistema")
        
        geometria_mom = st.selectbox(
            "Geometría del Flujo:",
            [
                "Cilindros Concéntricos (Viscosímetro Rotacional)",
                "Tubería Cilíndrica (Hagen-Poiseuille)",
                "Placas Planas Paralelas (Couette / Poiseuille)"
            ]
        )
        
        # Preajuste de Fluido
        fluid_choice = st.selectbox("Preajuste de Fluido:", list(FLUID_PRESETS.keys()), index=2)
        default_mu = FLUID_PRESETS[fluid_choice] if FLUID_PRESETS[fluid_choice] is not None else 0.290
        
        viscosidad = st.number_input(
            "Viscosidad Dinámica (μ) [Pa·s]:",
            min_value=0.0001,
            value=float(default_mu),
            step=0.010,
            format="%.4f"
        )
        
        if "Cilindros Concéntricos" in geometria_mom:
            R1 = st.number_input("Radio Cilindro Int. (R1) [m]:", min_value=0.001, value=0.028, step=0.001, format="%.3f")
            R2 = st.number_input("Radio Cilindro Ext. (R2) [m]:", min_value=R1 + 0.001, value=0.052, step=0.001, format="%.3f")
            omega = st.number_input("Velocidad Angular Int. (ω) [rad/s]:", min_value=0.0, value=20.0, step=1.0, format="%.2f")
            
        elif "Tubería Cilíndrica" in geometria_mom:
            R_pipe = st.number_input("Radio Interno Tubo (R) [m]:", min_value=0.001, value=0.050, step=0.005, format="%.3f")
            dp_dz = st.number_input("Gradiente de Presión (-dP/dz) [Pa/m]:", min_value=0.0, value=120.0, step=10.0, format="%.2f")
            
        else: # Placas Planas
            dist_H = st.number_input("Distancia entre Placas (H) [m]:", min_value=0.001, value=0.020, step=0.001, format="%.3f")
            vel_V = st.number_input("Velocidad Placa Superior (V) [m/s]:", min_value=0.0, value=1.5, step=0.1, format="%.2f")

    with col_chart:
        if "Cilindros Concéntricos" in geometria_mom:
            v1_surf = omega * R1
            denom = (R2**2 - R1**2) if (R2**2 - R1**2) != 0 else 1e-6
            torque_per_L = (4 * np.pi * viscosidad * omega * (R1**2) * (R2**2)) / denom
            tau_max_r1 = (2 * viscosidad * omega * (R1**2) * (R2**2)) / ((R1**2) * denom)
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Velocidad Superficial Int.", f"{v1_surf:.3f} m/s")
            kpi2.metric("Esfuerzo Cortante Máx (r1)", f"{tau_max_r1:.2f} Pa")
            kpi3.metric("Torque por Unidad Longitud", f"{torque_per_L:.4f} N·m/m")
            
            r = np.linspace(R1, R2, 100)
            v_theta = (omega * R1**2 / denom) * ((R2**2 / r) - r)
            tau_r = (2 * viscosidad * omega * (R1**2) * (R2**2)) / ((r**2) * denom)
            
            y_pos = r
            x_vel = v_theta
            x_tau = tau_r
            y_label = "Posición Radial (m)"
            
        elif "Tubería Cilíndrica" in geometria_mom:
            v_max = (dp_dz * R_pipe**2) / (4 * viscosidad)
            tau_wall = (dp_dz * R_pipe) / 2
            Q_m3s = (np.pi * dp_dz * (R_pipe**4)) / (8 * viscosidad)
            Q_lmin = Q_m3s * 60000
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Velocidad Máxima (Centro)", f"{v_max:.3f} m/s")
            kpi2.metric("Esfuerzo Cortante Pared", f"{tau_wall:.2f} Pa")
            kpi3.metric("Caudal Volumétrico (Q)", f"{Q_lmin:.2f} L/min")
            
            r = np.linspace(-R_pipe, R_pipe, 100)
            v_z = v_max * (1 - (r / R_pipe)**2)
            tau_rz = (dp_dz * r) / 2
            
            y_pos = r
            x_vel = v_z
            x_tau = np.abs(tau_rz)
            y_label = "Posición Radial r (m)"
            
        else: # Placas Planas
            tau_const = viscosidad * (vel_V / dist_H)
            grad_vel = vel_V / dist_H
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Velocidad Placa Superior", f"{vel_V:.2f} m/s")
            kpi2.metric("Esfuerzo Cortante (Constante)", f"{tau_const:.2f} Pa")
            kpi3.metric("Gradiente de Velocidad", f"{grad_vel:.1f} s⁻¹")
            
            y = np.linspace(0, dist_H, 100)
            v_x = vel_V * (y / dist_H)
            
            y_pos = y
            x_vel = v_x
            x_tau = np.full_like(y, tau_const)
            y_label = "Posición Axial y (m)"

        fig_mom = go.Figure()
        
        fig_mom.add_trace(go.Scatter(
            x=x_vel, y=y_pos,
            mode='lines',
            name='Velocidad v(r) [m/s]',
            line=dict(color='#06b6d4', width=3)
        ))
        
        fig_mom.add_trace(go.Scatter(
            x=x_tau, y=y_pos,
            mode='lines',
            name='Esfuerzo Cortante |τ| [Pa]',
            xaxis='x2',
            line=dict(color='#f59e0b', width=2, dash='dot')
        ))
        
        fig_mom.update_layout(
            title="📈 PERFIL DE VELOCIDAD & ESFUERZO CORTANTE",
            xaxis=dict(
                title=dict(text="Velocidad (m/s)", font=dict(color="#06b6d4")),
                tickfont=dict(color="#06b6d4")
            ),
            xaxis2=dict(
                title=dict(text="Esfuerzo Cortante (Pa)", font=dict(color="#f59e0b")),
                tickfont=dict(color="#f59e0b"),
                overlaying='x',
                side='top'
            ),
            yaxis=dict(title=y_label),
            template="plotly_dark",
            height=400,
            legend=dict(x=0.02, y=0.98)
        )
        
        st.plotly_chart(fig_mom, use_container_width=True)

# ==========================================
# 2. MÓDULO DE ENERGÍA (CALOR)
# ==========================================
with tab2:
    st.header("🔥 Transporte de Energía (Conducción de Calor - Ley de Fourier)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parámetros Térmicos")
        
        # Selector de Geometría Térmica
        geometria_heat = st.selectbox(
            "Geometría del Sistema:",
            [
                "Pared Plana Multicapa (3 Capas)",
                "Cilindro Hueco Aislado (Tubería 2 Capas)"
            ]
        )
        
        T_in = st.number_input("Temperatura Interna T_in (°C):", value=180.0, step=1.0, format="%.2f")
        T_out = st.number_input("Temperatura Externa T_out (°C):", value=20.0, step=1.0, format="%.2f")
        
        st.markdown("---")
        
        if "Pared Plana" in geometria_heat:
            st.markdown("**Propiedades de Capas (Pared Multicapa):**")
            k1 = st.number_input("k1 (Aislante) [W/m·K]:", value=0.04, min_value=0.001, step=0.01, format="%.2f")
            L1 = st.number_input("Espesor Capa 1 L1 [m]:", value=0.05, min_value=0.001, step=0.01, format="%.2f")
            
            k2 = st.number_input("k2 (Ladrillo) [W/m·K]:", value=0.80, min_value=0.001, step=0.05, format="%.2f")
            L2 = st.number_input("Espesor Capa 2 L2 [m]:", value=0.10, min_value=0.001, step=0.01, format="%.2f")
            
            k3 = st.number_input("k3 (Concreto) [W/m·K]:", value=1.40, min_value=0.001, step=0.10, format="%.2f")
            L3 = st.number_input("Espesor Capa 3 L3 [m]:", value=0.15, min_value=0.001, step=0.01, format="%.2f")
            
        else: # Cilindro Hueco Aislado
            st.markdown("**Radios y Conductividades Térmicas:**")
            k_tubo = st.number_input("k_tubo (Acero) [W/m·K]:", value=45.0, min_value=0.1, step=1.0, format="%.2f")
            k_aislante = st.number_input("k_aislante (Lana) [W/m·K]:", value=0.05, min_value=0.001, step=0.01, format="%.2f")
            
            r1_mm = st.number_input("Radio Interno Tubo r1 [mm]:", value=25.0, min_value=1.0, step=1.0, format="%.1f")
            r2_mm = st.number_input("Radio Externo Tubo r2 [mm]:", value=30.0, min_value=r1_mm + 0.1, step=1.0, format="%.1f")
            r3_mm = st.number_input("Radio Externo Aislante r3 [mm]:", value=60.0, min_value=r2_mm + 0.1, step=1.0, format="%.1f")

    with col2:
        if "Pared Plana" in geometria_heat:
            R1 = L1 / k1
            R2 = L2 / k2
            R3 = L3 / k3
            R_total = R1 + R2 + R3
            
            q_flux = (T_in - T_out) / R_total
            T2 = T_in - q_flux * R1
            T3 = T2 - q_flux * R2
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Flujo Calórico (q'')", f"{q_flux:.1f} W/m²")
            kpi2.metric("Resistencia Térmica Total", f"{R_total:.4f} m²·K/W")
            kpi3.metric("Caída Térmica Capa 1", f"{(T_in - T2):.1f} °C")
            
            x_pts = [0, L1, L1 + L2, L1 + L2 + L3]
            T_pts = [T_in, T2, T3, T_out]
            x_label = "Espesor Acumulado x (m)"
            
        else: # Cilindro Hueco Aislado
            r1 = r1_mm / 1000.0
            r2 = r2_mm / 1000.0
            r3 = r3_mm / 1000.0
            
            R1 = np.log(r2 / r1) / (2 * np.pi * k_tubo)
            R2 = np.log(r3 / r2) / (2 * np.pi * k_aislante)
            R_total = R1 + R2
            
            Q_per_L = (T_in - T_out) / R_total  # W/m
            T2 = T_in - Q_per_L * R1
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Pérdida de Calor (q/L)", f"{Q_per_L:.2f} W/m")
            kpi2.metric("Temp. Interfaz Tubo-Aislante", f"{T2:.1f} °C")
            kpi3.metric("Resistencia Cilíndrica", f"{R_total:.3f} m·K/W")
            
            # Puntos logarítmicos continuos
            r_capa1 = np.linspace(r1, r2, 50)
            T_capa1 = T_in - (Q_per_L * np.log(r_capa1 / r1)) / (2 * np.pi * k_tubo)
            
            r_capa2 = np.linspace(r2, r3, 50)
            T_capa2 = T2 - (Q_per_L * np.log(r_capa2 / r2)) / (2 * np.pi * k_aislante)
            
            x_pts = np.concatenate([r_capa1, r_capa2]) * 1000.0  # Convertir a mm
            T_pts = np.concatenate([T_capa1, T_capa2])
            x_label = "Radio r (mm)"
        
        fig_heat = go.Figure()
        fig_heat.add_trace(go.Scatter(x=x_pts, y=T_pts, mode='lines+markers', line=dict(color='#f59e0b', width=3), marker=dict(size=6)))
        fig_heat.update_layout(
            title="🔥 PERFIL DE TEMPERATURA T(X)",
            xaxis_title=x_label,
            yaxis_title="Temperatura (°C)",
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig_heat, use_container_width=True)

# ==========================================
# 3. MÓDULO DE MATERIA (MASA)
# ==========================================
with tab3:
    st.header("🧪 Transporte de Materia (Difusión Binaria - Ley de Fick)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parámetros de Difusión")
        mass_choice = st.selectbox("Sistema Binario Predefinido:", list(MASS_PRESETS.keys()), index=1)
        
        if MASS_PRESETS[mass_choice] is not None:
            def_Dab, def_y0, def_yL = MASS_PRESETS[mass_choice]
        else:
            def_Dab, def_y0, def_yL = 1.10e-5, 0.85, 0.02
            
        D_AB = st.number_input("Difusividad Binaria DAB (m²/s):", value=float(def_Dab), format="%.2e")
        yA0 = st.number_input("Fracción Molar Interface yA(0):", min_value=0.0, max_value=1.0, value=float(def_y0), step=0.01, format="%.2f")
        yAL = st.number_input("Fracción Molar Exterior yA(L):", min_value=0.0, max_value=1.0, value=float(def_yL), step=0.01, format="%.2f")
        Z_length = st.number_input("Longitud del Tubo L (m):", min_value=0.001, value=0.10, step=0.01, format="%.2f")
        
        tipo_dif = st.selectbox(
            "Modelo de Transferencia de Masa:",
            [
                "Difusión de A en B Estancado (Tubo de Stefan)",
                "Contradifusión Equimolar (EMD)"
            ]
        )

    with col2:
        P_tot = 101325.0  # Pa
        R_gas = 8.314    # J/mol·K
        T_K = 298.15     # K
        C_tot = P_tot / (R_gas * T_K)
        
        z = np.linspace(0, Z_length, 100)
        
        if "Stefan" in tipo_dif:
            yA0_s = min(yA0, 0.999)
            yAL_s = min(yAL, 0.999)
            ratio = (1.0 - yAL_s) / (1.0 - yA0_s)
            yA_z = 1.0 - (1.0 - yA0_s) * (ratio ** (z / Z_length))
            NA_flux = (D_AB * C_tot / Z_length) * np.log((1.0 - yAL_s) / (1.0 - yA0_s))
        else:
            yA_z = yA0 - (yA0 - yAL) * (z / Z_length)
            NA_flux = (D_AB * C_tot / Z_length) * (yA0 - yAL)
            
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Flujo Molar (N_A)", f"{(NA_flux * 1000):.4f} mmol/m²·s")
        kpi2.metric("Concentración Molar Total", f"{C_tot:.2f} mol/m³")
        kpi3.metric("Gradiente Medio (ΔyA/L)", f"{((yA0 - yAL)/Z_length):.2f} m⁻¹")
        
        fig_mass = go.Figure()
        fig_mass.add_trace(go.Scatter(x=z, y=yA_z, mode='lines', line=dict(color='#10b981', width=3)))
        fig_mass.update_layout(
            title="🧪 PERFIL DE CONCENTRACIÓN / FRACCIÓN MOLAR yA(z)",
            xaxis_title="Posición en el Tubo z (m)",
            yaxis_title="Fracción Molar yA",
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig_mass, use_container_width=True)
