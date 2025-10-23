from mosqlimate_assistant.main import assistant_pipeline
import time

question = "Quero visualizar os casos de dengue em SP no ano de 2022, com um gráfico de linhas mostrando a evolução semanal."

start = time.time()
res = assistant_pipeline(question)
end = time.time()

print(res)
print(f"Tempo de resposta: {end - start:.2f} segundos")

start_2 = time.time()
response_2 = assistant_pipeline(question)
end_2 = time.time()

print(response_2)
print(f"Tempo de resposta (cache): {end_2 - start_2:.2f} segundos")
