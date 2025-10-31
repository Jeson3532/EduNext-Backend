from yandex_cloud_ml_sdk import YCloudML

sdk = YCloudML(
    folder_id="b1gfcbvf950cvl4lcodr",
    auth="REMOVED",
)

model = sdk.models.completions("yandexgpt")
model = model.configure(temperature=0.5)
result = model.run("Ты - AI-репетитор. Сгенерируй одну практическую задачу по теме: 'Backend-разработка'. Задача должна быть "
                   "уникальной и проверять понимание ключевых концепций. Уровень сложности - начальный. Предоставь также эталонное решение для проверки.")
print(dir(result.alternatives))
print(result.alternatives[0].text)