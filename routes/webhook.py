from flask import Blueprint, request, jsonify
import logging
from utils.amocrm_client import AmoCRMClient
from utils.wazzup_client import WazzupClient
from utils.openai_client import OpenAIClient
from utils.statistics_manager import StatisticsManager
from utils.helpers import extract_phone_from_text
from config import Config

webhook_bp = Blueprint('webhook', __name__)
amocrm_client = AmoCRMClient()
wazzup_client = WazzupClient()
openai_client = OpenAIClient()
stats_manager = StatisticsManager()

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    logging.info(f"Received webhook: {request.form}")
    logging.info(f"Request Headers: {request.headers}")

    user_agent = request.headers.get('User-Agent')
    lead_ID = request.form.get("message[add][0][entity_id]", "")

    is_successful = False
    lead = amocrm_client.get_deal_by_id(lead_ID)
    print(lead)

    if lead != 25584559:
        print("Статус сделки не соответствует ожидаемому. Завершаем выполнение.")
        print(lead)
        return '', 200

    if user_agent == 'amoCRM-WebHook-client/2.0':
        return '', 200

    try:
        logging.debug(f"Request Body: {request.data}")

        if "message[add][0][text]" in request.form and "message[add][0][chat_id]" in request.form:
            client_message = request.form["message[add][0][text]"]
            account_ID = request.form["message[add][0][contact_id]"]

            if extract_phone_from_text(client_message):
                amocrm_client.change_deal_status(lead_ID, 7243308)

                stats_manager.update_statistics(
                    input_tokens_mini=0,
                    output_tokens_mini=0,
                    input_tokens_o=0,
                    output_tokens_o=0,
                    is_successful=True,
                    phone_number=amocrm_client.get_contact_phone(account_ID)
                )
                return '', 200

            logging.info(f"Received message: {client_message} from contact_id: {account_ID}")

            chat_ID = amocrm_client.get_contact_phone(account_ID)

            mini_response, input_tokens, output_tokens = openai_client.handle_question(client_message)
            final_response, input_tokens_o, output_tokens_o = openai_client.create_gpt4o_response(client_message, mini_response, chat_ID)

            wazzup_client.send_message(chat_ID, final_response)

            stats_manager.update_statistics(
                input_tokens_mini=input_tokens,
                output_tokens_mini=output_tokens,
                input_tokens_o=input_tokens_o,
                output_tokens_o=output_tokens_o,
                is_successful=False,
                phone_number=chat_ID
            )

            stats_manager.save_statistics()
            return '', 200
        else:
            logging.error("Ошибка: не получены ожидаемые данные.")
            return jsonify({"status": "error", "message": "No valid data received."}), 400

    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
