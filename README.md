# ?? Resultados del Entrenamiento del Modelo de Clasificaci�n de Hate Speech

A continuaci�n se presentan las gr�ficas obtenidas durante el entrenamiento del modelo de clasificaci�n, que detecta mensajes ofensivos, de odio o neutros.

---

## ?? Precisi�n de Clasificaci�n

Esta gr�fica muestra c�mo mejor� la **precisi�n** del modelo en cada �poca, tanto para entrenamiento como validaci�n:

![Train vs Val Accuracy](resultados/accuracy_plot.png)

---

## ?? P�rdida Total

Aqu� se visualiza la **p�rdida (loss)** en ambas fases. Una p�rdida m�s baja indica mejor aprendizaje:

![Train vs Val Loss](resultados/loss_plot.png)

---

## ??? Uso de Recursos del Sistema

Se registraron m�tricas del sistema para monitorear el consumo durante el entrenamiento:

### CPU

![CPU Usage](resultados/cpu_usage.png)

---

### RAM

![RAM Usage](resultados/ram_usage.png)

---

### GPU

![GPU Usage](resultados/gpu_usage.png)

---

### Memoria de GPU

![GPU Memory Usage](resultados/gpu_memory_usage.png)

---

## ?? Duraci�n por �poca

Cada �poca del entrenamiento tom� aproximadamente entre 1 y 2 segundos:

![Epoch Time](resultados/epoch_time_plot.png)

---

## ? Conclusiones

- El modelo muestra una mejora progresiva sin signos de sobreajuste.
- El uso de recursos fue estable y eficiente.
- Puede ejecutarse en equipos con recursos moderados (CPU y GPU b�sica).
