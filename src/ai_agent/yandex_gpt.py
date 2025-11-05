from yandex_cloud_ml_sdk import YCloudML
from dotenv import load_dotenv
from .__init__ import env_path
import os

load_dotenv(dotenv_path=env_path)

FOLDER_ID = os.getenv("AI_FOLDER_ID")
TOKEN = os.getenv("AI_TOKEN")

sdk = YCloudML(
    folder_id=FOLDER_ID,
    auth=TOKEN,
)
model = sdk.models.completions("yandexgpt")


def preprocess_text(text: str):
    return text.replace("\n", "").replace("```", "")


def get_answer_ai(lesson_name: str, desc: str, material: str, user_question: str, temp=0.5):
    global model
    model = model.configure(temperature=temp)
    ai_answer = model.run(f"Ты - AI-репетитор. \n"
                          f"Название урока: {lesson_name}\n"
                          f"Описание урока: {desc}\n"
                          f"Контекст урока: '{material}\n'."
                          f"Вопрос студента: '{user_question}'.\n"
                          "Дай развернутый, но четкий ответ, основанный на предоставленных данных. Если ответа в данных нет, так и скажи.")
    return preprocess_text(ai_answer.alternatives[0].text)


def generate_task(lesson_name: str, desc: str, temp=0.5):
    global model
    model = model.configure(temperature=temp)
    ai_answer = model.run(f"Ты - AI-репетитор. Сгенерируй одну практическую задачу по теме: "
                          f" '{lesson_name}, описание темы: {desc}'. Задача должна быть уникальной и проверять понимание ключевых концепций. "
                          f"Уровень сложности - начальный. Предоставь также эталонное решение для проверки. Ответ пришли СТРОГО В JSON формате с ключом 'task' и 'answer'. В ответе должен быть чиствый JSON без форматирования текста и специальных символов.")
    return preprocess_text(ai_answer.alternatives[0].text)


def compare_answers(user_answer, true_answer, temp=0.5):
    global model
    model = model.configure(temperature=temp)
    ai_answer = model.run(
        f"Ты - AI-репетитор. Сравни ответ студента '{user_answer}' с эталонным решением '{true_answer}'. Является ли ответ студента верным? Ответь ТОЛЬКО 'true' или 'false'.")
    return preprocess_text(ai_answer.alternatives[0].text)
