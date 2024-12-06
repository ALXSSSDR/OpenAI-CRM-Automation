import json
from config import Config
from .helpers import count_tokens, load_json_data, trim_conversation_history
from models.conversation_manager import ConversationManager
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model_gpt4o = Config.MODEL_GPT4O
        self.model_gpt4omini = Config.MODEL_GPT4OMINI
        self.conversation_manager = ConversationManager()

    def ask_openai(self, messages, model):

        try:
            chat_completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=150
            )
        except Exception as e:
            print(f"Error communicating with OpenAI: {e}")
            return "Произошла ошибка при обработке запроса.", 0, 0

        response_text = chat_completion.choices[0].message.content.strip()
        prompt = " ".join([msg['content'] for msg in messages])
        input_tokens, output_tokens = count_tokens(prompt, response_text)
        print(f"Ответ от {model}: {response_text}")
        print(f"Входных токенов: {input_tokens}, Выходных токенов: {output_tokens}")
        return response_text, input_tokens, output_tokens

    def handle_question(self, question):

        parsed_data_1 = load_json_data()
        mini_prompt = f"""
        Ты помощник, работающий с базой знаний. Твоя задача — найти ответ в базе знаний на следующие вопросы пользователя: жилые комплексы, квартиры, площади, цены, район, адрес и подготовить краткое резюме задачи. Если ответ найден, добавь его в резюме. Если нет, напиши "Ответ не найден". Названия жилых комплексов не соответствуют их месторасположению. Пример: название ЖК Central park не означает что он расположен в центре.
    Используй только те данные о районе, которые есть в базе знаний, и не допускай предположений. Если информации о районе нет.
    JSON: {json.dumps(parsed_data_1, ensure_ascii=False, indent=2)}
    Вопрос пользователя: {question}
    Результат анализа:
    - Статус: [Ответ найден/Ответ не найден]
    - Ответ: [Текст ответа или пусто]
        """

        mini_response, input_tokens, output_tokens = self.ask_openai(
            [{"role": "user", "content": mini_prompt}],
            model=self.model_gpt4omini
        )

        return mini_response, input_tokens, output_tokens

    def create_gpt4o_response(self, question, mini_response, chat_id):

        gpt4_prompt = f"""
        Пользователь задал вопрос:
        {question}
        GPT-4 Mini предоставила следующий анализ и их надо использовать для ответа:
        {mini_response}
        """

        # Инициализация истории диалога, если её ещё нет
        self.conversation_manager.initialize_conversation(chat_id)

        # Добавляем новое сообщение пользователя
        self.conversation_manager.add_message(chat_id, "user", gpt4_prompt)

        # Ограничиваем историю, чтобы не превышать лимит токенов
        self.conversation_manager.trim_history(chat_id, max_tokens=Config.MAX_TOKENS)

        # Отправляем всю историю вместе с новым сообщением для GPT-4o
        gpt4_response, input_tokens, output_tokens = self.ask_openai(
            self.conversation_manager.get_history(chat_id),
            model=self.model_gpt4o
        )

        # Добавляем ответ ассистента в историю
        self.conversation_manager.add_message(chat_id, "assistant", gpt4_response)

        print(f"История диалога для chat_id {chat_id}:")
        for msg in self.conversation_manager.get_history(chat_id):
            print(f"{msg['role'].capitalize()}: {msg['content']}")

        return gpt4_response, input_tokens, output_tokens