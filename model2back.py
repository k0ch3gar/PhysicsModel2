from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

r = 0.06 
R = 0.13   
L = 0.21  
V0 = 3.5e6   
m_e = 9.1093837e-31  
e = 1.602e-19  

d = R - r  

epsi_0 = 8.854e-12  

ln_ratio = np.log(R / r)
V_min = (m_e * V0**2 / (2 * e)) / (ln_ratio / (2 * np.pi * epsi_0 * L))

def calculate_acceleration(V):
    E = V / d
    a_y = (e * E) / m_e
    return a_y

def calculate_trajectory(V):
    a_y = calculate_acceleration(V)
    t = (2 * L) / V0  
    return t, a_y

def generate_plot(x, y, title, xlabel, ylabel):
    plt.figure()
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

app = FastAPI()

class VoltageRequest(BaseModel):
    voltage: float

@app.post("/calculate/trajectory")
def calculate_trajectory_endpoint(data: VoltageRequest):
    voltage = (m_e * V0**2 / (2 * e)) / (ln_ratio / (2 * np.pi * epsi_0 * L)) 
    t_min, a_y_min = calculate_trajectory(voltage)

    t = np.linspace(0, (2 * L) / V0, 100)
    x = V0 * t  
    y = -(1 / 2) * a_y_min * t**2  
    V_y = -a_y_min * t  
    a_y_plot = np.full_like(t, a_y_min)  

    trajectory_plot = generate_plot(x, y, "Траектория движения y(x)", "x (м)", "y (м)")
    velocity_plot = generate_plot(t, V_y, "Проекция скорости V_y(t)", "t (с)", "V_y (м/с)")
    acceleration_plot = generate_plot(t, a_y_plot, "Проекция ускорения a_y(t)", "t (с)", "a_y (м/с^2)")
    y_t_plot = generate_plot(t, y, "Зависимость y(t)", "t (с)", "y (м)")

    return {
        "trajectory_plot": trajectory_plot,
        "velocity_plot": velocity_plot,
        "acceleration_plot": acceleration_plot,
        "y_t_plot": y_t_plot
    }
