
# Tratamiento de datos
# -----------------------------------------------------------------------
import pandas as pd
import numpy as np
np.set_printoptions(formatter={'float_kind': lambda x: f"{float(x):.4f}"})

# Visualizaciones
# -----------------------------------------------------------------------
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import tree

# Para realizar la regresión lineal y la evaluación del modelo
# -----------------------------------------------------------------------
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import KFold,LeaveOneOut, cross_val_score
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

def metricas(y_train, y_train_pred, y_test, y_test_pred):
    # Calcular métricas
    train_metricas = {
        'r2_score': round(r2_score(y_train, y_train_pred), 4),
        'MAE': round(mean_absolute_error(y_train, y_train_pred), 4),
        'MSE': round(mean_squared_error(y_train, y_train_pred), 4),
        'RMSE': round(np.sqrt(mean_squared_error(y_train, y_train_pred)), 4)
    }
    
    test_metricas = {
        'r2_score': round(r2_score(y_test, y_test_pred), 4),
        'MAE': round(mean_absolute_error(y_test, y_test_pred), 4),
        'MSE': round(mean_squared_error(y_test, y_test_pred), 4),
        'RMSE': round(np.sqrt(mean_squared_error(y_test, y_test_pred)), 4)
    }
    
    # Calcular diferencias
    diferencias = {
        metric: round(train_metricas[metric] - test_metricas[metric], 4) for metric in train_metricas
    }
    
    # Calcular porcentaje de diferencia relativa al valor mayor promedio
    porcentaje = {
        metric: round((diferencias[metric] / min(train_metricas[metric], test_metricas[metric])) * 100, 4)
        for metric in train_metricas
    }
    
    # Calcular el valor minimo de la media y mediana de la variable respuesta (entre y_train y y_test)
    media_respuesta = round((np.mean(y_train) + np.mean(y_test)) / 2, 4)
    mediana_respuesta = round((np.median(y_train) + np.median(y_test)) / 2, 4)
    
    # Calcular porcentaje de influencia basado en la referencia
    porcentaje2 = {
        metric: round((abs(diferencias[metric]) / media_respuesta) * 100, 4)
        for metric in diferencias
    }

    # Calcular porcentaje de influencia basado en la referencia
    porcentaje3 = {
        metric: round((abs(diferencias[metric]) / mediana_respuesta) * 100, 4)
        for metric in diferencias
    }

    # Combinar resultados
    metricas = {
        'Train': train_metricas,
        'Test': test_metricas,
        'Diferenceias': diferencias,
        'Porcentaje diferencia (%)': porcentaje,
        'Media':media_respuesta,
        'Influencia media (%)': porcentaje2,
        'Mediana':mediana_respuesta,
        'Influencia mediana (%)': porcentaje3,    
    }
    return pd.DataFrame(metricas).T

def analizar_correlaciones(df, target_column, threshold=0.05):
    """
    Analiza la correlación de las columnas con respecto a la variable objetivo.
    
    Parámetros:
    - df (DataFrame): Dataset que contiene las variables.
    - target_column (str): Nombre de la columna objetivo para calcular las correlaciones.
    - threshold (float): Umbral para identificar columnas con baja correlación (por defecto, 0.05).
    
    Retorna:
    - low_correlation_columns (list): Lista de columnas con correlación baja con la columna objetivo.
    """
    # Calcular la matriz de correlación
    correlation_matrix = df.corr()
    
    # Correlación con la variable objetivo
    correlation_with_target = correlation_matrix[target_column].sort_values(ascending=False)
    
    # Mostrar las correlaciones
    print(f"Correlaciones con '{target_column}':")
    print(correlation_with_target)
    
    # Visualizar correlaciones
    plt.figure(figsize=(10, 6))
    sns.barplot(x=correlation_with_target.index, y=correlation_with_target.values, palette="viridis")
    plt.xticks(rotation=90, ha='right')
    plt.title(f'Correlaciones de cada columna con "{target_column}"')
    plt.ylabel('Correlación')
    plt.xlabel('Columnas')
    plt.grid()
    plt.tight_layout()
    plt.show()
    
    # Identificar columnas con baja correlación
    low_correlation_columns = correlation_with_target[correlation_with_target.abs() < threshold].index.tolist()
    print(f"\nColumnas con baja correlación (abs < {threshold}):")
    print(low_correlation_columns)
    
    return low_correlation_columns

def comparativa_graficos(y_test, y_pred_test):
    """
    Genera 4 gráficos comparativos entre valores reales y predicciones:
    1. Dispersión (Scatter Plot)
    2. Errores residuales
    3. Línea de valores reales vs predicciones
    4. KDE para comparar distribuciones de valores reales y predicciones
    """
    # Asegurarse de que y_test y y_pred_test sean unidimensionales
    if isinstance(y_test, (pd.DataFrame, pd.Series)):
        y_test = y_test.to_numpy().ravel()
    if isinstance(y_pred_test, (pd.DataFrame, pd.Series)):
        y_pred_test = y_pred_test.to_numpy().ravel()

    # Figura con subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.ravel()
    
    # 1. Gráfico de dispersión
    sns.scatterplot(x=y_test, y=y_pred_test, alpha=0.6, ax=axes[0])
    axes[0].plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label='Línea de identidad')
    axes[0].set_title('Dispersión: Predicciones vs Valores Reales')
    axes[0].set_xlabel('Valores Reales')
    axes[0].set_ylabel('Predicciones')
    axes[0].legend()
    axes[0].grid()
    
    # 2. Gráfico de errores residuales
    residuos = y_test - y_pred_test
    sns.scatterplot(x=y_pred_test, y=residuos, alpha=0.6, ax=axes[1])
    axes[1].axhline(0, color='red', linestyle='--')
    axes[1].set_title('Errores Residuales')
    axes[1].set_xlabel('Predicciones')
    axes[1].set_ylabel('Residuos')
    axes[1].grid()
    
    # 3. Gráfico de barras de diferencia absoluta
    diferencias = abs(y_test - y_pred_test)
    sns.lineplot(x=range(len(diferencias)), y=diferencias, ax=axes[2], color='purple', alpha=0.7)
    axes[2].set_title('Diferencia Absoluta Suavizada')
    axes[2].set_xlabel('Índice')
    axes[2].set_ylabel('Diferencia Absoluta')
    axes[2].grid()

    # 4. KDE de distribuciones
    sns.kdeplot(y_test, color='blue', label='Valores Reales', fill=True, alpha=0.3, ax=axes[3])
    sns.kdeplot(y_pred_test, color='orange', label='Predicciones', fill=True, alpha=0.3, ax=axes[3])
    axes[3].set_title('Distribución (KDE) de Valores Reales y Predicciones')
    axes[3].set_xlabel('Valor')
    axes[3].set_ylabel('Densidad')
    axes[3].legend()
    axes[3].grid()
    
    # Ajustar diseño
    plt.tight_layout()
    plt.show()