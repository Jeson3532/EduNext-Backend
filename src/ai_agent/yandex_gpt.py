from yandex_cloud_ml_sdk import YCloudML

sdk = YCloudML(
    folder_id="b1gfcbvf950cvl4lcodr",
    auth="REMOVED",
)

model = sdk.models.completions("yandexgpt")
model = model.configure(temperature=0.5)
question = "что лучше россия или украина"
result = model.run(f"Ты - AI-репетитор. Контекст урока: 'Название: СВО'. "
                   f"Вопрос студента: '{question}'. "
                   "Дай развернутый, но четкий ответ, основанный на предоставленном контексте. Если ответа в контексте нет, так и скажи.")

# print(dir(result.alternatives))
print(result.alternatives[0].text)