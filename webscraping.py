from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import matplotlib.pyplot as plt
import pandas as pd

# Configuración del WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Extraer URLs desde el archivo
urls = []
with open('urls.txt', 'r') as file:  # Cambiado a 'urls.txt'
    content = file.read()
    urls = [url.strip().strip("'\"") for url in content.split(',')]

# Inicializar el archivo CSV
open('results.csv', 'w').close()

# Función para limpiar comas de los valores extraídos
def clean_value(value):
    return value.replace(",", "")

# Función para formatear números con comas
def format_number(value):
    return "{:,}".format(int(value.replace("#", "").replace(",", "")))

# Iterar sobre las URLs y extraer datos
for url in urls:
    scrape_url = 'https://www.similarweb.com/website/' + url + '/#overview'
    driver.get(scrape_url)

    wait = WebDriverWait(driver, 10)
    
    try:
        # Extraer las métricas principales
        total_visits_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".engagement-list__item-value")))
        bounce_rate_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".engagement-list__item:nth-of-type(2) .engagement-list__item-value")))
        pages_per_visit_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".engagement-list__item:nth-of-type(3) .engagement-list__item-value")))
        average_visit_duration_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".engagement-list__item:nth-of-type(4) .engagement-list__item-value")))

        total_visits = clean_value(total_visits_element.text)
        bounce_rate = clean_value(bounce_rate_element.text)
        pages_per_visit = clean_value(pages_per_visit_element.text)
        average_visit_duration = clean_value(average_visit_duration_element.text)

        # Extraer las métricas de ranking
        global_rank_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".wa-rank-list__item--global .wa-rank-list__value")))
        country_rank_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".wa-rank-list__item--country .wa-rank-list__value")))

        global_rank = format_number(global_rank_element.text)
        country_rank = format_number(country_rank_element.text)

        # Imprimir los resultados para depuración
        print(f"URL: {url}")
        print(f"Total Visits: {total_visits}")
        print(f"Bounce Rate: {bounce_rate}")
        print(f"Pages per Visit: {pages_per_visit}")
        print(f"Average Visit Duration: {average_visit_duration}")
        print(f"Global Rank: {global_rank}")
        print(f"Country Rank: {country_rank}")
        
        # Guardar los resultados en el archivo CSV
        with open('results.csv', 'a') as f:
            f.write(f'"{url}",')
            f.write(f'"{total_visits}",')
            f.write(f'"{bounce_rate}",')
            f.write(f'"{pages_per_visit}",')
            f.write(f'"{average_visit_duration}",')
            f.write(f'"{global_rank}",')
            f.write(f'"{country_rank}"\n')

    except Exception as e:
        print(f"Error al procesar {url}: {e}")
        continue

    time.sleep(1)

driver.quit()

# Leer los datos del archivo CSV
df = pd.read_csv('results.csv', names=[
    "URL", "Total Visits", "Bounce Rate", "Pages per Visit", "Average Visit Duration", "Global Rank", "Country Rank"])

# Configurar la figura
fig, ax = plt.subplots(figsize=(12, 6))

# Ocultar el eje
ax.axis('off')

# Crear la tabla
table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

# Ajustar el tamaño de las celdas
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)

# Establecer un estilo para las celdas
for key, cell in table.get_celld().items():
    cell.set_edgecolor('black')
    cell.set_linewidth(1)
    cell.set_height(0.1)  # Aumentar el espaciado vertical
    if key[0] == 0:  # Encabezado
        cell.set_fontsize(12)
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('#4b8bbe')
        cell.set_edgecolor('black')
        cell.set_linewidth(2)  # Bordes más gruesos para el encabezado
    else:  # Filas de datos
        cell.set_fontsize(10)
        if key[0] % 2 == 0:  # Filas pares
            cell.set_facecolor('#f9f9f9')
        else:  # Filas impares
            cell.set_facecolor('#ffffff')

# Ajustar el ancho de las columnas
table.auto_set_column_width([i for i in range(len(df.columns))])

# Guardar la imagen
plt.savefig('resultados.png', bbox_inches='tight', dpi=300)
plt.show()
